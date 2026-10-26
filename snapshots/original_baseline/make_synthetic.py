"""Artificial PSV fixtures for software verification, never scientific results."""
import argparse
import csv
import random
from pathlib import Path
from core import DYNAMIC, STATIC


def generate(root, n=80, seed=9):
    root = Path(root)
    if root.exists() and any(root.iterdir()):
        raise ValueError('Use an empty directory')
    root.mkdir(parents=True, exist_ok=True)
    (root/'SYNTHETIC_ONLY.txt').write_text('Artificial data. No clinical conclusions or preliminary project findings.\n')
    rng = random.Random(seed)
    for hospital in ('A', 'B'):
        target = root/f'training_set{hospital}'
        target.mkdir()
        for i in range(n):
            positive = i % 4 == 0
            onset = rng.randrange(18, 28)
            age, gender, unit = rng.uniform(20, 90), rng.randrange(2), rng.randrange(2)
            with open(target/f'p{i:06d}.psv', 'w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=DYNAMIC+STATIC+['SepsisLabel'], delimiter='|')
                w.writeheader()
                for t in range(36):
                    deteriorating = positive and t >= onset-8
                    row = {c: 'NaN' for c in DYNAMIC}
                    row.update(HR=rng.gauss(83+20*deteriorating, 9), O2Sat=rng.gauss(97, 2),
                               Temp=rng.gauss(37+1.3*deteriorating, .5), Resp=rng.gauss(17+6*deteriorating, 3),
                               MAP=rng.gauss(80-12*deteriorating, 10), WBC=rng.gauss(8+6*deteriorating, 2))
                    for c in ('HR','O2Sat','Temp','Resp','MAP','WBC'):
                        if rng.random() < (.2 if hospital == 'A' else .5):
                            row[c] = 'NaN'
                    row.update(Age=age, Gender=gender, Unit1=unit, Unit2=1-unit,
                               HospAdmTime=-rng.uniform(1, 60), ICULOS=t+1,
                               SepsisLabel=int(positive and t >= onset-6))
                    w.writerow(row)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--patients-per-hospital', type=int, default=80)
    a = p.parse_args()
    generate(a.out, a.patients_per_hospital)
