"""Verify saved prediction CSV utility against unmodified official NumPy scorer."""
import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import numpy as np
from evaluation import utility, utility_parts, normalized


def verify(root, scorer_path):
    spec = importlib.util.spec_from_file_location('official', scorer_path)
    official = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(official)
    report = dict(scorer_sha256=hashlib.sha256(scorer_path.read_bytes()).hexdigest(),
                  scorer_source='physionetchallenges/evaluation-2019/evaluate_sepsis_score.py', numpy_version=np.__version__, cohorts={})
    for regime in ('A_only', 'pooled'):
        metrics = json.loads((root/regime/'metrics.json').read_text())
        for csv_path in sorted((root/regime).glob('*_predictions.csv')):
            parts = {m: [] for m in ('sirs','logistic','logistic_abstain')}
            patients, maximum_error = 0, 0.
            with csv_path.open() as f:
                for pid, group in itertools.groupby(csv.DictReader(f), key=lambda r: r['patient_id']):
                    rows = list(group)
                    labels = [int(r['label']) for r in rows]
                    best = np.zeros(len(labels))
                    if any(labels):
                        onset = labels.index(1)+6
                        best[max(0,onset-12):min(onset+4,len(labels))] = 1
                    inactive = np.zeros(len(labels))
                    best_utility = float(official.compute_prediction_utility(labels, best))
                    inactive_utility = float(official.compute_prediction_utility(labels, inactive))
                    for method in parts:
                        pred = [int(r[method]) for r in rows]
                        value = float(official.compute_prediction_utility(labels,pred))
                        error = abs(value-utility(labels,pred))
                        independent = utility_parts(labels,pred)
                        error = max(error,abs(best_utility-independent[1]),abs(inactive_utility-independent[2]))
                        maximum_error = max(maximum_error,error)
                        if error > 1e-8:
                            raise AssertionError((pid,method,error))
                        parts[method].append((value,best_utility,inactive_utility))
                    patients += 1
            cohort = csv_path.name.removesuffix('_predictions.csv')
            scores = {m: normalized(v) for m,v in parts.items()}
            for method,value in scores.items():
                expected = metrics['evaluations'][cohort]['models'][method]['normalized_utility']
                if abs(value-expected)>1e-8:
                    raise AssertionError((cohort,method,value,expected))
            report['cohorts'][f'{regime}/{cohort}'] = dict(patients=patients,max_absolute_per_patient_error=maximum_error,
                                                        normalized_utilities=scores,status='PASS: observed, best, and no-action utility verified; saved cohort normalization matched')
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--results',type=Path,required=True)
    p.add_argument('--scorer',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    report=verify(a.results,a.scorer)
    a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
