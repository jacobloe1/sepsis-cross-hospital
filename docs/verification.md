# Verification record — October 23, 2026

Executed with Python 3.11.15:

- `python3.11 -m unittest discover -s sepsis_shift/tests -v`: 13 passed.
- `make_synthetic.py`: 80 artificial patients per hospital, 36 hours each.
- `run.py --epochs 3 --bootstrap 100 --pooled`: completed A-only/A-test, A-only/B-transfer, and pooled-random evaluation; generated split hashes, models, prediction CSVs, metrics, calibration bins, subgroup counts, paired bootstrap intervals, and a summary table.
- `download_data.py`: failed with hostname resolution error before training_setA.zip could be downloaded. No original data available.

Limits: synthetic runs use three training epochs, not the default fifteen. Synthetic observations do not establish discrimination, calibration, transfer degradation, or benefit on actual ICU patients. No real dataset, full-scale memory benchmark, official NumPy scorer, boosted model, clinical review, or NeurIPS report has been completed. Utility equivalence is deliberately flagged as unverified in the generated results.
