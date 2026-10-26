# Milestone working notes — not a submission-ready report

## Current thesis
A classifier developed on one hospital may lose useful early-warning performance on another, so evidence for a clinician-review alert requires retained utility and calibration, controlled alert burden, and transparent coverage under missingness shift.

## Progress and revisions
Implemented a minimum viable logistic baseline and partial SIRS rule instead of starting with boosted trees. This follows the proposal's fallback, reduces computational requirements, and makes the first transfer comparison inspectable. Data processing, disjoint patient splits, separate probability calibration, frozen threshold matching, metrics, subgroup tables, paired patient bootstrap, and two missingness policies are coded. Gradient boosting, clinical review of SIRS, full-scale profiling, and real-data experiments are pending.

The contribution should be described as controlled replication/diagnosis. The Challenge publication already studied cross-hospital generalization; the proposal's claim that cross-hospital work is largely absent requires a literature audit. Do not claim novelty from this implementation alone.

## Completed evidence, failed attempts, and interpretation
Thirteen automated tests passed. A complete run used 160 artificial stays solely to exercise both evaluation regimes and artifact generation. These numbers are NOT sepsis findings. The data-download attempt failed at DNS resolution in this execution environment. No PhysioNet cohort was trained/evaluated, and no primary hypothesis or reliance condition has been established. Independent utility passed analytical cases, but agreement with the official Python scorer still requires data and NumPy.

A useful engineering observation from the fixture is that abstention can suppress warnings when measurement availability decreases. This is a software behavior check, not evidence that the same effect occurs in real hospitals. Whole-cohort metrics therefore retain abstained hours as no-alert decisions.

## Real-results table to populate

| Evaluation | Cohort counts and prevalence | SIRS utility | Logistic utility and paired Δ CI | FPR / burden | Sensitivity / PPV | ECE and coverage |
|---|---|---|---|---|---|---|
| A-held-out | Pending | Pending | Pending | Pending | Pending | Pending |
| A→B | Pending | Pending | Pending | Pending | Pending | Pending |
| Pooled random | Pending | Pending | Pending | Pending | Pending | Pending |

Keep a paired A→B utility-improvement interval, reliability plot with bin counts, and coverage table in the eventual report. Mark the bootstrap as conditional on one fitted model; repeat training seeds separately. Do not paste synthetic metrics into this table.

## Draft class-survey case summary
Case: Cross-hospital generalization of an ICU sepsis early-warning classifier. Intended user/action: clinician decides whether to review a patient further. Evidence: public hourly PhysioNet 2019 A/B records with supplied labels; A-only development and fixed B transfer evaluation. Comparators: partial SIRS and regularized logistic regression; boosted trees planned. Shift: hospital measurement practice, patient mix, and missingness. Outcomes: normalized Challenge utility, alert burden, sensitivity/PPV, calibration, warning time, and selective coverage. Current status: pipeline verified on artificial fixtures; real-data findings and reliance judgment pending. Lifecycle response: withhold unsupported missingness cases for clinician review rather than infer reassurance from silence; no validated deployment workflow yet.

## Draft comparison-matrix entry

| Domain / task | User / decision | Evidence and split | Models | Shift / failure | Measures | Human role / lifecycle | Supported conclusion |
|---|---|---|---|---|---|---|---|
| ICU early sepsis warning | Clinician prioritizes review | PhysioNet 2019; patient-level A development/A holdout/B transfer | Partial SIRS; logistic; boosted trees pending | Hospital and missingness shift; abstention may miss warnings | Utility, FPR/burden, sensitivity, PPV, calibration, coverage | Clinician diagnoses; no autonomous treatment; update requires new validation | Pending real-data evidence |

## Completion plan and obstacles

1. Obtain original A/B archives, verify counts/hashes, inspect field availability and labels; run the official utility equivalence check. Resolve any format mismatches before analysis.
2. Freeze protocol and run A-only plus pooled comparisons. Review convergence; repeat seeds 7,42,2026. Profile memory/runtime and vectorize if full-cohort costs are excessive. Keep sample caps identical across experiments and report them.
3. Examine B calibration, group counts and CIs, coverage, and alert burden. Run strict-pattern and dropout stress tests. Add gradient boosting only after the baseline is sound, selecting parameters entirely within A.
4. Obtain clinical feedback on proxy SIRS and label/alert interpretation. Audit literature before novelty claims. Document failed gates and narrow conclusions when appropriate.
5. Draft an actual NeurIPS-format report capped at three content pages, plus references: ~0.5 page question/revisions; ~0.75 methods/split; ~1.0 results/interpretation; ~0.75 survey entry, plan, and contributions. This Markdown file is not NeurIPS formatted and must not be submitted as-is. Add the real shared code URL or project artifact link after team setup.

## Contributions — confirmation required
The proposal assigns Arshia Nalla ingestion/documentation; Trisha Bajpai preprocessing/clinical baselines; Jacob Loe classifier/calibration; Basmala Metwally evaluation/abstention/reproducibility; interpretation/writing to all four. These are planned responsibilities, not verified completed contributions. This initial implementation was generated with AI assistance in Jacob's session. Each member should review their assigned components, record actual changes/experiments, and replace this section with an accurate final account, following course disclosure rules. The original October16 target precedes this October23 implementation and needs a revised team schedule.
