"""Aggregate all prespecified seeds; no best-seed selection."""
import argparse
import csv
import json
import statistics
from pathlib import Path


def main(root):
    rows=[]
    for seed in (7,42,2026):
        for regime in ('A_only','pooled'):
            path=root/f'seed{seed}'/regime/'metrics.json'
            d=json.loads(path.read_text())
            for cohort,e in d['evaluations'].items():
                if not isinstance(e['utility_verification'],dict):
                    raise AssertionError('Missing official score verification')
                for model,m in e['models'].items():
                    row=dict(seed=seed,regime=regime,cohort=cohort,model=model,
                             recent_vitals95=d['recent_vitals95'],
                             training_sample_hours=d['training_sample_hours'],
                             coverage=1-m['abstention_fraction'])
                    for metric in ('patients','hours','auroc','normalized_utility','sensitivity_hour','ppv','ece_10_bins',
                                   'alert_hours_per_100','early_case_sensitivity','median_warning_hours'):
                        row[metric]=m[metric]
                    row['worst_adequate_subgroup_gap']=max((m['sensitivity_hour']-g['sensitivity_hour'] for g in m['subgroups'].values() if g['adequate_for_sensitivity_gate']),default=None)
                    row['utility_delta_vs_sirs']=m['normalized_utility']-e['models']['sirs']['normalized_utility']
                    rows.append(row)
    with (root/'seed_comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    grouped={}
    for row in rows:
        grouped.setdefault((row['regime'],row['cohort'],row['model']),[]).append(row)
    aggregates=[]
    for (regime,cohort,model),members in grouped.items():
        a=dict(regime=regime,cohort=cohort,model=model,n_seeds=len(members),seeds=[r['seed'] for r in members])
        for metric in ('auroc','normalized_utility','sensitivity_hour','coverage','ppv','alert_hours_per_100','worst_adequate_subgroup_gap'):
            values=[r[metric] for r in members if r[metric] is not None]
            a[metric]=dict(mean=statistics.fmean(values),sd=statistics.stdev(values) if len(values)>1 else None,min=min(values),max=max(values))
        aggregates.append(a)
    (root/'aggregate.json').write_text(json.dumps(aggregates,indent=2)+'\n')
    lines=['# Exploratory follow-up results — October 26, 2026','',
           'All three planned seeds are included. Seed variation combines split, sampling, and SGD effects.',
           'Hospital B had already been inspected before the missingness revision. These are exploratory results.','',
           '| Cohort | Method | AUROC mean ± SD | Utility mean ± SD | Hour sensitivity | Coverage |',
           '|---|---|---:|---:|---:|---:|']
    for a in aggregates:
        def ms(k): return f'{a[k]["mean"]:.4f} ± {a[k]["sd"]:.4f}'
        lines.append(f'| {a["cohort"]} | {a["model"]} | {ms("auroc")} | {ms("normalized_utility")} | {100*a["sensitivity_hour"]["mean"]:.1f}% | {100*a["coverage"]["mean"]:.1f}% |')
    lines += ['', 'Utility was checked against the official NumPy scorer. SD across three seeds is descriptive, not a confidence interval.',
              'For abstaining predictions, AUROC uses latent risks on all hours; it does not describe a selective ranking score.',
              'Whole-cohort utility and sensitivity retain withheld hours as no-alert decisions. Patient-level CIs remain in each metrics.json.','',
              '## Seed-level transfer and withholding','',
              '| Seed | A utility | B utility | B utility with abstention | B coverage | B sensitivity without / with abstention |',
              '|---|---:|---:|---:|---:|---:|']
    for seed in (7,42,2026):
        def get(cohort,model):return next(r for r in rows if r['seed']==seed and r['cohort']==cohort and r['model']==model)
        a,b,s=get('A_test','logistic'),get('B_transfer','logistic'),get('B_transfer','logistic_abstain')
        lines.append(f'| {seed} | {a["normalized_utility"]:.4f} | {b["normalized_utility"]:.4f} | {s["normalized_utility"]:.4f} | {100*s["coverage"]:.2f}% | {100*b["sensitivity_hour"]:.1f}% / {100*s["sensitivity_hour"]:.1f}% |')
    (root/'followup_summary.md').write_text('\n'.join(lines)+'\n')
    make_plot(root,rows)
    print((root/'followup_summary.md').read_text())


def make_plot(root,rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(9,3.6),layout='constrained')
    colors={'A_test':'#2274a5','B_transfer':'#d1495b','pooled_random_test':'#367d56'}
    for cohort in colors:
        data=sorted([r for r in rows if r['cohort']==cohort and r['model']=='logistic'],key=lambda r:r['seed'])
        axes[0].plot(range(3),[r['normalized_utility'] for r in data],marker='o',label=cohort,color=colors[cohort])
    axes[0].set(xticks=range(3),xticklabels=['7','42','2026'],xlabel='Seed',ylabel='Normalized utility',title='Hospital comparison')
    axes[0].axhline(0,color='gray',lw=.7);axes[0].legend(fontsize=8)
    for seed in (7,42,2026):
        m=next(r for r in rows if r['seed']==seed and r['cohort']=='B_transfer' and r['model']=='logistic')
        s=next(r for r in rows if r['seed']==seed and r['cohort']=='B_transfer' and r['model']=='logistic_abstain')
        axes[1].plot([0,1],[m['normalized_utility'],s['normalized_utility']],marker='o',label=f'Seed {seed}')
    axes[1].set(xticks=[0,1],xticklabels=['All predictions','Recent-vitals gate'],ylabel='Normalized utility',title='Withholding on B (zoomed y-axis)')
    axes[1].legend(fontsize=8)
    for ax in axes:ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2)
    fig.savefig(root/'transfer_and_abstention.png',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();main(a.root)
