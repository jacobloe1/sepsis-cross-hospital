"""Patient-clustered evaluation; undefined metrics are None, never zero."""
import math
import random
import statistics
from core import quantile


def ratio(a, b):
    return a/b if b else None


def utility(labels, predictions):
    """Independent implementation of Challenge default per-patient utility.

    Definition: https://github.com/physionetchallenges/evaluation-2019
    Verify against official Python scorer with run.py --official-scorer before
    citing real-data utility. Includes the official zero-utility tail after +3h.
    Labels are already advanced by six hours; inferred onset = first positive+6.
    """
    if len(labels) != len(predictions):
        raise ValueError('Unequal prediction and label lengths')
    if not any(labels):
        return -.05*sum(predictions)
    onset = labels.index(1) + 6
    score = 0.
    for t, pred in enumerate(predictions):
        dt = t-onset
        if dt > 3:
            continue
        if pred:
            score += max((dt+12)/6, -.05) if dt <= -6 else (3-dt)/9
        elif dt > -6:
            score += -2*(dt+6)/9
    return score


def utility_parts(labels, predictions):
    best = [0]*len(labels)
    if any(labels):
        onset = labels.index(1)+6
        best = [int(onset-12 <= t <= onset+3) for t in range(len(labels))]
    return (utility(labels, predictions), utility(labels, best), utility(labels, [0]*len(labels)))


def normalized(parts):
    observed, best, inactive = (sum(p[j] for p in parts) for j in range(3))
    return ratio(observed-inactive, best-inactive)


def auc(labels, scores):
    npos = sum(labels)
    nneg = len(labels)-npos
    if not npos or not nneg:
        return None
    pairs = sorted(zip(scores, labels))
    rank_sum, i = 0., 0
    while i < len(pairs):
        j = i+1
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        rank_sum += sum(y for _, y in pairs[i:j])*(i+j+1)/2
        i = j
    return (rank_sum-npos*(npos+1)/2)/(npos*nneg)


def calibration(labels, scores, bins=10):
    cells = [[] for _ in range(bins)]
    for y, s in zip(labels, scores):
        cells[min(bins-1, int(s*bins))].append((y, s))
    table = [dict(low=i/bins, high=(i+1)/bins, n=len(c),
                  observed=statistics.fmean(y for y, s in c) if c else None,
                  predicted=statistics.fmean(s for y, s in c) if c else None)
             for i, c in enumerate(cells)]
    ece = sum(c['n']*abs(c['observed']-c['predicted']) for c in table if c['n'])/len(labels) if labels else None
    return ece, table


def matched_threshold(records):
    """Tune-only negative-hour FPR matching, conservative treatment of ties."""
    negatives = [(s, b) for r in records for y, s, b in zip(r['labels'], r['scores'], r['sirs']) if not y]
    if not negatives:
        raise ValueError('Threshold set has no label-negative hours')
    budget = sum(b for s, b in negatives)
    scores = sorted((s for s, b in negatives), reverse=True)
    threshold = 0. if budget == len(scores) else math.nextafter(scores[budget], math.inf)
    return threshold, dict(target_fpr=budget/len(scores),
                           achieved_fpr=sum(s >= threshold for s in scores)/len(scores),
                           negative_hours=len(scores))


def predictions(r, model, threshold):
    if model == 'sirs':
        return r['sirs']
    return [int(s >= threshold and (model != 'logistic_abstain' or not a)) for s, a in zip(r['scores'], r['abstain'])]


def summary(records, model, threshold):
    labels, scores, preds, parts = [], [], [], []
    leads, detected, septic, false_patients, nonseptic = [], 0, 0, 0, 0
    abstained = 0
    for r in records:
        y = r['labels']
        pred = predictions(r, model, threshold)
        labels.extend(y)
        scores.extend(r['scores'] if model != 'sirs' else r['sirs'])
        preds.extend(pred)
        parts.append(utility_parts(y, pred))
        abstained += sum(r['abstain'])
        if any(y):
            septic += 1
            onset = y.index(1)+6
            # Only alerts in the prespecified [-12, 0]h window count as early detection.
            alerts = [t for t, v in enumerate(pred) if v and onset-12 <= t <= onset]
            if alerts:
                detected += 1
                leads.append(onset-min(alerts))
        else:
            nonseptic += 1
            false_patients += int(any(pred))
    tp = sum(y and p for y, p in zip(labels, preds))
    fp = sum(not y and p for y, p in zip(labels, preds))
    ece, table = calibration(labels, scores)
    n = len(labels)
    result = dict(patients=len(records), hours=n, septic_patients=septic,
                  positive_hours=sum(labels), auroc=auc(labels, scores),
                  sensitivity_hour=ratio(tp, sum(labels)), ppv=ratio(tp, tp+fp),
                  fpr_hour=ratio(fp, n-sum(labels)), alert_hours_per_100=ratio(100*sum(preds), n),
                  nonseptic_patients_alerted_fraction=ratio(false_patients, nonseptic),
                  early_case_sensitivity=ratio(detected, septic), median_warning_hours=statistics.median(leads) if leads else None,
                  normalized_utility=normalized(parts),
                  abstention_fraction=ratio(abstained, n) if model == 'logistic_abstain' else 0.)
    # A binary SIRS proxy is not a risk probability; never call it calibrated.
    result['ece_10_bins'] = ece if model != 'sirs' else None
    result['brier'] = statistics.fmean((s-y)**2 for y, s in zip(labels, scores)) if n and model != 'sirs' else None
    result['calibration_bins'] = table if model != 'sirs' else []
    # ECE for abstention model above uses ALL latent probabilities, coverage separate.
    if model == 'logistic_abstain':
        kept = [(y, s) for r in records for y, s, a in zip(r['labels'], r['scores'], r['abstain']) if not a]
        result['covered_ece_10_bins'] = calibration([y for y, s in kept], [s for y, s in kept])[0]
    return result


def paired_bootstrap(records, threshold, model, nboot, seed):
    """Resample entire patients; fixed fitted model/threshold. No refitting CI."""
    rng = random.Random(seed)
    cached = []
    for r in records:
        y = r['labels']
        m = predictions(r, model, threshold)
        b = r['sirs']
        cached.append((utility_parts(y, m), utility_parts(y, b),
                       sum(a and c for a, c in zip(y, m)), sum(a and c for a, c in zip(y, b)), sum(y)))
    deltas, sens = [], []
    for _ in range(nboot):
        draw = [cached[rng.randrange(len(cached))] for _ in cached]
        um, ub = normalized([d[0] for d in draw]), normalized([d[1] for d in draw])
        if um is not None and ub is not None:
            deltas.append(um-ub)
        total = sum(d[4] for d in draw)
        if total:
            sens.append((sum(d[2] for d in draw)-sum(d[3] for d in draw))/total)
    def ci(v):
        return [quantile(v, .025), quantile(v, .975)] if v else [None, None]
    return dict(replicates=nboot, valid_utility_replicates=len(deltas), utility_delta_vs_sirs_ci95=ci(deltas),
                sensitivity_delta_vs_sirs_ci95=ci(sens), method='paired patient percentile bootstrap; fixed model')


def subgroups(records, model, threshold):
    groups = {}
    for r in records:
        for key in r['groups']:
            groups.setdefault(key, []).append(r)
    output = {}
    for key, members in sorted(groups.items()):
        s = summary(members, model, threshold)
        s['adequate_for_sensitivity_gate'] = s['septic_patients'] >= 30 and s['patients']-s['septic_patients'] >= 30
        output[key] = s
    return output
