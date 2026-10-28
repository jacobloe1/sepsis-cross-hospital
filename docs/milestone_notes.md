# Current milestone report record

The compiled report is [reports/milestone/milestone_report.pdf](../reports/milestone/milestone_report.pdf). It uses the unmodified official NeurIPS 2026 style, with three content pages and a fourth page containing only references. Editable LaTeX and build instructions are in the same folder. This record supersedes the initial synthetic-only milestone notes; the original experimental results remain unchanged.

## Current thesis

A sepsis classifier may beat a simple rule yet lose utility across hospitals, so clinician-review reliance requires evidence on transfer, subgroups, calibration, and the consequences of abstention.

## Scope and completed work

The logistic model is the proposal's planned fallback instead of boosted trees. It provides an inspectable baseline within available compute; boosted trees remain unimplemented, and no result compares the model families. Preprocessing and classifier fitting use a seeded reservoir capped at **50,000 training hours**. This is not a full-hour model fit. Calibration and evaluation remain uncapped, including all 20,000 B patients.

Completed artifacts include a causal data pipeline, disjoint patient-level development/evaluation splits, partial SIRS and regularized logistic baselines, probability calibration, threshold matching, official utility verification, 18 passing software tests, three-seed results, paired patient bootstrap summaries, subgroup/calibration diagnostics, and two plots. The repository README gives reproduction commands.

## Evidence and uncertainty

| Logistic evaluation | AUROC mean ± seed SD | Utility mean ± seed SD | Hour sensitivity |
|---|---:|---:|---:|
| A holdout | 0.7257 ± 0.0105 | 0.2460 ± 0.0239 | 67.3% |
| B transfer | 0.6951 ± 0.0031 | 0.0756 ± 0.0174 | 52.9% |
| Pooled random | 0.7424 ± 0.0045 | 0.2094 ± 0.0162 | 66.5% |

Seed SD across 7,42,2026 describes variation from changed patient splits, training samples, and SGD order. It is **not a confidence interval**. The separate 95% intervals use 1,000 paired whole-patient bootstrap draws, conditional on one fitted model/threshold, and do not include retraining uncertainty. B utility-improvement intervals versus SIRS are [0.0618,0.1129], [0.0470,0.1050], and [0.0822,0.1386]. Case mix, prevalence, and development-pool differences prevent interpreting these comparisons as a causal effect of evaluation design.

The first raw-missingness abstention rule never activated because its training 95th-percentile cutoff was 1.0. The revised recent-vitals rule withholds 3.54% of B hours, but does not demonstrate a utility gain. **The revision is exploratory because Hospital B had already been inspected.** Each B gate-minus-ungated utility interval includes zero. Unit-2 sensitivity deficits exceed ten percentage points in two fits; sparse higher-risk calibration bins also remain problematic. These failures prevent claiming the proposal's full limited-reliance conditions are satisfied.

## Survey materials

The current [case summary and matrix entry](class_survey_case.md) also appear on content page 3 of the report. This is a controlled replication/diagnosis, not a claim to the first cross-hospital sepsis study.

## Completion plan

1. Basmala: patient-clustered subgroup intervals and group-size review. Trisha: measurement completeness and missing-unit analysis. Deliver a subgroup/measurement table; keep power limitations explicit.
2. Jacob: calibration near the alert threshold and sparse-bin uncertainty. Trisha/Basmala: define cooldown/single-alert comparisons and controlled vital-dropout stress tests. Seek clinical review of the partial SIRS rule and freshness assumptions; narrow claims if it is unavailable.
3. Jacob: attempt boosted trees only if compute permits, selecting entirely on A development data. Otherwise, retain logistic regression and test cap/convergence sensitivity. Preserve current outputs and avoid best-seed or B-based threshold selection.
4. All three: reconcile the final thesis, matrix, citations, limitations, and contribution record. B-informed revisions remain exploratory; if a new independent hospital evaluation is infeasible, retain a bounded diagnostic conclusion.

## Confirmed current team and contributions

Jacob confirmed the completed roles: **Jacob Loe** handled data acquisition, ingestion/documentation, classifier/calibration work, and original baseline execution; **Trisha Bajpai** handled preprocessing and the SIRS-style baseline; **Basmala Metwally** handled evaluation, abstention, and reproducibility checks. The team now has these three members, with Jacob taking over the reassigned ingestion/documentation work.

Implementation, troubleshooting, follow-up computations, and report drafting used AI assistance. The team remains responsible for review and final submission. See [contributions.md](contributions.md) for the current attribution record.
