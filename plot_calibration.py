import csv,json,hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--metrics',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
source=args.metrics
root=args.out
root.mkdir(parents=True,exist_ok=True)
d=json.loads(source.read_text());rows=[]
fig,axes=plt.subplots(1,2,figsize=(9,3.6),layout='constrained')
for name,color in [('A_test','#2274a5'),('B_transfer','#d1495b')]:
 bins=d['evaluations'][name]['models']['logistic']['calibration_bins']
 nonempty=[b for b in bins if b['n']]
 axes[0].plot([b['predicted'] for b in nonempty],[b['observed'] for b in nonempty],marker='o',label=name,color=color)
 axes[1].plot([(b['low']+b['high'])/2 for b in nonempty],[b['n'] for b in nonempty],marker='o',label=name,color=color)
 for b in bins:rows.append(dict(cohort=name,**b))
axes[0].plot([0,.7],[0,.7],color='gray',linestyle='--',lw=1)
axes[0].set(xlabel='Mean predicted probability',ylabel='Observed hourly positive fraction',xlim=(0,.7),ylim=(0,.7),title='Reliability: original seed42')
axes[1].set(xlabel='Probability-bin midpoint',ylabel='Patient-hours (log scale)',yscale='log',title='Most predictions occupy the lowest bin')
for ax in axes:
 ax.legend(fontsize=8);ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2)
fig.savefig(root/'original_calibration.png',dpi=180)
with (root/'original_calibration_bins.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('Calibration figure and bin-count table saved. Counts are descriptive; no independent-hour confidence intervals assumed.')
