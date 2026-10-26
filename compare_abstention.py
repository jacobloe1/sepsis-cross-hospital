"""Paired patient CIs for withholding versus the unchanged unselective model."""
import argparse,csv,itertools,json
from pathlib import Path
import numpy as np
from evaluation import utility_parts


def compare(path,seed,nboot=1000):
    statistics=[]
    with path.open() as f:
        for pid,group in itertools.groupby(csv.DictReader(f),key=lambda r:r['patient_id']):
            rows=list(group)
            y=[int(r['label']) for r in rows]
            raw=[int(r['logistic']) for r in rows]
            gated=[int(r['logistic_abstain']) for r in rows]
            u,best,inactive=utility_parts(y,raw)
            g=utility_parts(y,gated)[0]
            statistics.append([g-u,best-inactive,
                               sum(label*(b-a) for label,a,b in zip(y,raw,gated)),sum(y)])
    stats=np.asarray(statistics,dtype=float)
    rng=np.random.default_rng(seed)
    values=[]
    # Small chunks bound index-array memory, independent of patient length.
    for start in range(0,nboot,20):
        indices=rng.integers(0,len(stats),size=(min(20,nboot-start),len(stats)))
        sums=stats[indices].sum(axis=1)
        valid=(sums[:,1]>0)&(sums[:,3]>0)
        values.extend((sums[valid,0]/sums[valid,1]).tolist())
    totals=stats.sum(axis=0)
    return dict(patients=len(stats),bootstrap_replicates=nboot,valid_replicates=len(values),
                normalized_utility_delta_gate_minus_unselective=float(totals[0]/totals[1]),
                normalized_utility_delta_ci95=np.quantile(values,[.025,.975]).tolist(),
                hourly_sensitivity_delta_gate_minus_unselective=float(totals[2]/totals[3]),
                method='paired whole-patient percentile bootstrap; NumPy default_rng; fixed model and rule; linear quantiles')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);args=p.parse_args()
    result={}
    for seed in (7,42,2026):
        result[str(seed)]={}
        for regime,cohort in [('A_only','A_test'),('A_only','B_transfer'),('pooled','pooled_random_test')]:
            result[str(seed)][cohort]=compare(args.root/f'seed{seed}'/regime/f'{cohort}_predictions.csv',seed)
    (args.root/'abstention_vs_unselective_ci.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
