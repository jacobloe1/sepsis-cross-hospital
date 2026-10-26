#!/usr/bin/env python3
"""Run from project directory. Real data are never substituted with synthetic."""
import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import sys
from pathlib import Path
from core import DYNAMIC, FEATURES, Logistic, Preprocessor, load, quantile, reservoir_examples, sirs, split
from evaluation import matched_threshold, paired_bootstrap, predictions, subgroups, summary, utility


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')


def score(patients, pre, model, calibrator, policy):
    records = []
    for p in patients:
        logits = [model.logit(x) for x in pre.transform(p['rows'])]
        scores = [calibrator.predict([max(-35., min(35., z))]) for z in logits]
        first = p['rows'][0]
        age = first['Age']
        sex = first['Gender']
        unit = '1' if first['Unit1'] == 1 else ('2' if first['Unit2'] == 1 else 'unknown')
        completeness = 1-sum(row[c] is None for row in p['rows'] for c in DYNAMIC)/(len(DYNAMIC)*len(p['rows']))
        records.append(dict(id=p['id'], labels=p['labels'], scores=scores,
                            sirs=list(sirs(p['rows'])), abstain=[pre.abstain(row, policy) for row in p['rows']],
                            groups=[f'age:{"unknown" if age is None else ("under65" if age < 65 else "65plus")}',
                                    f'sex:{"unknown" if sex is None else int(sex)}', f'unit:{unit}',
                                    f'completeness:{"below_training_median" if completeness < pre.completeness_cut else "at_or_above_training_median"}']))
    return records


def official_check(path, records, threshold):
    if not path:
        return 'NOT VERIFIED against official Python implementation; do not cite utility yet'
    spec = importlib.util.spec_from_file_location('official_scorer', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for r in records:
        for model in ('sirs', 'logistic', 'logistic_abstain'):
            pred = predictions(r, model, threshold)
            expected = float(module.compute_prediction_utility(r['labels'], pred))
            if abs(utility(r['labels'], pred)-expected) > 1e-8:
                raise AssertionError(f'Official utility mismatch: {r["id"]}')
    return dict(status='verified per-patient utility for every evaluated model and patient',
                scorer_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def run_experiment(patients, b, args, out, regime):
    out.mkdir(parents=True, exist_ok=True)
    splits = split(patients, args.seed)
    save(out/'split_manifest.json', {k: [dict(id=p['id'], hospital=p['hospital'], sha256=p['sha256'],
                                           hours=len(p['rows']), septic=bool(any(p['labels']))) for p in v] for k, v in splits.items()})
    pre = Preprocessor().fit(splits['train'], args.max_train_hours, args.seed)
    pre.completeness_cut = quantile([1-sum(row[c] is None for row in p['rows'] for c in DYNAMIC)/(len(DYNAMIC)*len(p['rows'])) for p in splits['train']], .5)
    examples = reservoir_examples(splits['train'], pre, args.max_train_hours, args.seed)
    print(f'{regime}: fitting logistic on {len(examples)} sampled training hours', flush=True)
    model = Logistic().fit(examples, epochs=args.epochs, seed=args.seed)
    # Calibration patients are disjoint from model fitting AND threshold tuning.
    calibration_examples = [([max(-35., min(35., model.logit(x)))], y)
                            for p in splits['calibration'] for x, y in zip(pre.transform(p['rows']), p['labels'])]
    calibrator = Logistic().fit(calibration_examples, epochs=40, l2=0., seed=args.seed)
    tune = score(splits['tune'], pre, model, calibrator, args.abstention)
    threshold, matching = matched_threshold(tune)
    evaluations = {'A_test' if regime == 'A_only' else 'pooled_random_test': splits['test']}
    if regime == 'A_only':
        evaluations['B_transfer'] = b
    result = dict(regime=regime, threshold=threshold, tuning=matching, training_sample_hours=len(examples),
                  training_total_hours=pre.training_hours, missing95=pre.missing95,
                  all_missing_training_features=pre.all_missing, evaluations={})
    save(out/'model.json', dict(feature_names=FEATURES, medians=pre.medians, means=pre.means, scales=pre.scales,
                               weights=model.weights, bias=model.bias, calibration_weights=calibrator.weights,
                               calibration_bias=calibrator.bias, training_logloss=model.losses,
                               threshold=threshold, missing95=pre.missing95,
                               training_masks=[list(m) for m in sorted(pre.masks)],
                               completeness_cut=pre.completeness_cut, abstention_policy=args.abstention))
    for name, cohort in evaluations.items():
        print(f'{regime}: evaluating {name} ({len(cohort)} patients)', flush=True)
        records = score(cohort, pre, model, calibrator, args.abstention)
        evaluated = {'utility_verification': official_check(args.official_scorer, records, threshold), 'models': {}}
        for method in ('sirs', 'logistic', 'logistic_abstain'):
            s = summary(records, method, threshold)
            s['subgroups'] = subgroups(records, method, threshold)
            if method != 'sirs':
                s['bootstrap'] = paired_bootstrap(records, threshold, method, args.bootstrap, args.seed)
            evaluated['models'][method] = s
        result['evaluations'][name] = evaluated
        with open(out/f'{name}_predictions.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'hour', 'label', 'probability', 'sirs', 'logistic', 'abstain', 'logistic_abstain'])
            for r in records:
                for t, (y, s, base, abst) in enumerate(zip(r['labels'], r['scores'], r['sirs'], r['abstain'])):
                    writer.writerow([r['id'], t+1, y, s, base, int(s >= threshold), int(abst), int(s >= threshold and not abst)])
    save(out/'metrics.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--epochs', type=int, default=15)
    parser.add_argument('--max-train-hours', type=int, default=50000)
    parser.add_argument('--bootstrap', type=int, default=500)
    parser.add_argument('--abstention', choices=['rate', 'rate-pattern'], default='rate')
    parser.add_argument('--pooled', action='store_true', help='Secondary experiment; exposes B labels to separate model. Never tune A-only model from this.')
    parser.add_argument('--official-scorer', type=Path)
    args = parser.parse_args()
    if args.epochs < 1 or args.max_train_hours < 2 or args.bootstrap < 1:
        parser.error('epochs, max-train-hours, and bootstrap must be positive')
    if args.out.exists() and any(args.out.iterdir()):
        parser.error('Output directory must be empty; use a new name to preserve prior runs')
    patients = load(args.data)
    synthetic = (args.data/'SYNTHETIC_ONLY.txt').exists()
    args.out.mkdir(parents=True, exist_ok=True)
    save(args.out/'run_record.json', dict(data_kind='SYNTHETIC SOFTWARE CHECK ONLY' if synthetic else 'USER-SUPPLIED PSV: provenance requires review',
                                        python=sys.version, platform=platform.platform(), config={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                                        code_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}))
    a = [p for p in patients if p['hospital'] == 'A']
    b = [p for p in patients if p['hospital'] == 'B']
    save(args.out/'cohort_manifest.json', [dict(id=p['id'], sha256=p['sha256'], hours=len(p['rows'])) for p in patients])
    results = [run_experiment(a, b, args, args.out/'A_only', 'A_only')]
    if args.pooled:
        results.append(run_experiment(patients, [], args, args.out/'pooled', 'pooled'))
    lines = ['# '+('SYNTHETIC SOFTWARE CHECK — NOT PROJECT EVIDENCE' if synthetic else 'Preliminary evaluation'), '',
             '| Regime | Cohort | Model | AUROC | Utility* | Hour sensitivity | PPV | ECE | Coverage |',
             '|---|---|---|---:|---:|---:|---:|---:|---:|']
    def fmt(v):
        return 'NA' if v is None else f'{v:.4f}'
    for r in results:
        for cohort, e in r['evaluations'].items():
            for method, m in e['models'].items():
                lines.append('| '+' | '.join([r['regime'], cohort, method]+[fmt(m[k]) for k in ('auroc','normalized_utility','sensitivity_hour','ppv','ece_10_bins')]+[fmt(1-m['abstention_fraction'])])+' |')
    lines += ['', '*Utility is an independent implementation. Check utility_verification in metrics.json before citing.',
              'Bootstrap intervals and subgroup counts are in metrics.json. Abstentions remain in the denominator as no alert.',
              'Warning times describe detected cases only. None of these results establishes clinical safety or benefit.']
    (args.out/'summary.md').write_text('\n'.join(lines)+'\n')
    print(f'Finished: {args.out}/summary.md', flush=True)


if __name__ == '__main__':
    main()
