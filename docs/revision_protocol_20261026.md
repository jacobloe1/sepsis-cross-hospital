# Exploratory revision protocol — October 26, 2026

The original seed42 results were inspected before this revision. Hospital B is now an exploratory external benchmark, not an untouched final test. No revision parameter is selected using B utility, sensitivity, or labels.

## Fixed revision, specified before revised runs

Keep all features, imputation, model, calibration, training-hour cap (50,000), 15 model epochs, separate tuning patients, and SIRS comparator unchanged. Evaluate seeds 7,42,2026 with 1,000 whole-patient bootstrap replicates each. Each seed changes the patient splits, training reservoir, and SGD shuffle, so the variation combines these sources; it does not isolate optimization randomness. Run both A-only and pooled development, maintaining their distinct interpretation. Do not select a best seed.

Replace the ineffective raw-hour missingness rule for this exploratory comparison with **recent-vitals**:

- Seven vital signs: HR, O2Sat, Temp, SBP, MAP, DBP, Resp.
- An observation is recent if it appears in the current or previous five hourly rows, i.e. a causal six-hour window. This matches the existing engineering freshness horizon for the SIRS vitals; clinical review remains pending.
- At an hour with no recent vital signs, withhold the model alert unconditionally.
- Otherwise, compute the fraction of the seven vital signs not recently observed. Withhold when that fraction is strictly greater than the training 95th percentile among training hours with at least one recent vital sign. This conditional reference prevents the cutoff saturating at 100%; it is a documented change in the abstention definition.
- Fit the reference using only each regime's training partition (A only for transfer; pooled A/B for the separate pooled regime). No threshold changes after viewing evaluation performance.
- Preserve all patient-hours in utility/sensitivity denominators; withhold means no model alert. Also evaluate the original model without abstention.
- Retain the original rate and rate-pattern implementations for reproducibility. Do not interpret recent vital availability as complete laboratory or out-of-distribution support.

First verify original prediction CSVs using the unmodified official Python implementation with NumPy. Check per-patient observed, ideal, and no-action utilities and compare the cohort-normalized score with saved metrics. Retain upstream BSD license and file hashes. Revised runs also verify actual patient utilities against that scorer.

## Interpretation requirements

Report coverage, burden, and utility differences together. If withholding reduces useful warnings, retain and interpret that negative result rather than tuning against B. Inspect subgroup sensitivity and high-risk calibration bins. Three seeds provide a descriptive range/standard deviation; they are not independent patient samples or a precise confidence interval for generalization.
