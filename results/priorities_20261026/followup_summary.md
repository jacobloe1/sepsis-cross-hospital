# Exploratory follow-up results — October 26, 2026

All three planned seeds are included. Seed variation combines split, sampling, and SGD effects.
Hospital B had already been inspected before the missingness revision. These are exploratory results.

| Cohort | Method | AUROC mean ± SD | Utility mean ± SD | Hour sensitivity | Coverage |
|---|---|---:|---:|---:|---:|
| A_test | sirs | 0.5897 ± 0.0054 | 0.0794 ± 0.0074 | 51.5% | 100.0% |
| A_test | logistic | 0.7257 ± 0.0105 | 0.2460 ± 0.0239 | 67.3% | 100.0% |
| A_test | logistic_abstain | 0.7257 ± 0.0105 | 0.2383 ± 0.0270 | 65.8% | 96.9% |
| B_transfer | sirs | 0.6223 ± 0.0000 | -0.0159 ± 0.0000 | 49.6% | 100.0% |
| B_transfer | logistic | 0.6951 ± 0.0031 | 0.0756 ± 0.0174 | 52.9% | 100.0% |
| B_transfer | logistic_abstain | 0.6951 ± 0.0031 | 0.0741 ± 0.0167 | 52.4% | 96.5% |
| pooled_random_test | sirs | 0.6061 ± 0.0023 | 0.0410 ± 0.0005 | 50.6% | 100.0% |
| pooled_random_test | logistic | 0.7424 ± 0.0045 | 0.2094 ± 0.0162 | 66.5% | 100.0% |
| pooled_random_test | logistic_abstain | 0.7424 ± 0.0045 | 0.2032 ± 0.0175 | 65.3% | 96.7% |

Utility was checked against the official NumPy scorer. SD across three seeds is descriptive, not a confidence interval.
For abstaining predictions, AUROC uses latent risks on all hours; it does not describe a selective ranking score.
Whole-cohort utility and sensitivity retain withheld hours as no-alert decisions. Patient-level CIs remain in each metrics.json.

## Seed-level transfer and withholding

| Seed | A utility | B utility | B utility with abstention | B coverage | B sensitivity without / with abstention |
|---|---:|---:|---:|---:|---:|
| 7 | 0.2353 | 0.0713 | 0.0696 | 96.46% | 54.8% / 54.2% |
| 42 | 0.2294 | 0.0608 | 0.0601 | 96.46% | 55.3% / 54.8% |
| 2026 | 0.2734 | 0.0947 | 0.0926 | 96.46% | 48.7% / 48.1% |

## Interpretation

The original utility values are now verified against the actual official NumPy scorer. Every revised run also passed patient-level observed, ideal, and no-action utility and cohort normalization checks.

Across all three seeds, logistic utility is lower on B than on the held-out A patients. Mean utility is 0.2460 on A and 0.0756 on B. The pooled random experiment averages 0.2094. These results are consistent with poorer cross-hospital performance, but hospital case mix, prevalence, calibration-set composition, and measurement practice remain alternative explanations; the comparison does not isolate a causal effect of evaluation design.

Logistic still improves over the partial SIRS comparator on B in every seed. The paired 95% utility-improvement intervals versus SIRS are [0.0618, 0.1129], [0.0470, 0.1050], and [0.0822, 0.1386] for seeds 7,42,2026. They condition on the fitted model rather than quantify all training uncertainty.

The recent-vitals gate is active, withholding 3.54% of B hours. It slightly reduces utility in all three seeds. The B gate-minus-unselective 95% intervals each include zero: there is no demonstrated utility gain, and the data do not establish a definitive adverse effect on B either. Sensitivity decreases mechanically when some positive model alerts are withheld. On A in seed7 and on the pooled test in seeds7/42, the gate's utility-change intervals exclude zero on the negative side; retain these as failures of this candidate gate. Do not tune a new cutoff using B results to obtain a favorable conclusion.

For the original ungated B classifier, the largest adequately represented subgroup deficit is the unit-2 indicator group: 7.96, 13.71, and 16.19 percentage points below overall hourly sensitivity across the three seeds. Two fits therefore exceed the proposal's ten-point point-estimate limit. Subgroup confidence intervals and a power analysis remain unresolved; three fits cannot certify fairness. The gate does not remove this pattern.

Overall ten-bin ECE remains small, but the original calibration plot shows overconfident higher-risk bins with relatively few observations. The low-risk bin dominates ECE. Do not treat small aggregate ECE or a conditional warning-time median as proof of clinically useful calibration or prospective benefit.

Current conclusion: the baseline reproduces a hospital-transfer performance gap and improves on the SIRS proxy, but evidence for limited reliance is not established. The revised gate solves the implementation failure of never abstaining; it does not demonstrate a utility benefit or repair subgroup disparities. Future work should investigate unit-related measurement differences and time-window/alert-policy definitions, strengthen calibration diagnostics, and obtain clinical review. New B-informed revisions remain exploratory and require new independent validation before stronger claims.

## Artifacts and scope

`original_utility_verification.json` verifies the preserved original run. Each seed contains fitted models, split/file hashes, per-hour predictions, calibration bins, subgroup counts, 1,000-patient-bootstrap summaries, and complete official-utility verification. `abstention_vs_unselective_ci.json` adds the paired gate-versus-ungated comparison. `seed_comparison.csv` and `aggregate.json` provide reusable tables. The two PNGs show cross-seed utility and original calibration/bin counts.

Eighteen software tests passed. Seeds change split, training sample reservoir, and SGD order; a 50,000-hour cap is retained for each model fit. All 20,000 B patients are evaluated on every run. Original result files were hash-checked after analysis and remain unchanged.

The updated source and these results were produced in the writable working copy, rather than overwriting the original project. The supplied `install_followup.py` can copy reviewed updates and new results to the original project with source backups while preserving `results/real_seed42`.
