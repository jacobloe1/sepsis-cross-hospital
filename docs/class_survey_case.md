# Draft class-survey case summary and comparison-matrix entry

## One-sentence thesis

A sepsis classifier may beat a simple rule yet lose utility across hospitals, so clinician-review reliance requires evidence on transfer, subgroups, calibration, and the consequences of abstention.

## Case summary

This case evaluates ICU sepsis warnings for clinician review using PhysioNet 2019 hourly data. A-only development and held-out A evaluation are compared with a fixed transfer to B; a separate pooled random-split experiment provides context. A regularized logistic model, used as the proposal's planned fallback, improves over a partial SIRS rule but loses utility on B across three seeds. Fitting is capped at 50,000 sampled training hours; evaluation is uncapped. An initial missingness gate never activated. Its revised recent-vitals version activates without demonstrating a utility benefit and is exploratory because B was already inspected. Unit-related sensitivity gaps and higher-risk calibration failures remain. The case illustrates the need to examine utility, alert burden, subgroup evidence, and selective coverage together, with clinicians retaining diagnosis and treatment authority.

## Matrix entry

| Domain/task | Intended user/action | Evidence and split | Comparator/models | Shift/failure | Measures and uncertainty | Lifecycle/human role | Supported conclusion |
|---|---|---|---|---|---|---|---|
| Clinical ML: ICU early sepsis warnings | Clinician prioritizes further evaluation | PhysioNet 2019; patient-level A train/calibrate/tune/test; fixed B transfer; separate pooled A+B random split | Partial SIRS; regularized logistic; boosted trees pending | Hospital/measurement shift; inactive original gate; no demonstrated utility gain from exploratory revision; unit-2 deficits | Utility, sensitivity/PPV, burden, calibration, warning timing, coverage; 1,000 paired patient bootstrap draws; three-seed SD reported separately | Clinician retains diagnosis/treatment; withheld prediction is not reassurance; no validated fallback workflow | Transfer-performance concern and advantage over partial SIRS; full limited reliance is not established |

Three-seed SD is descriptive, not a confidence interval. Bootstrap intervals condition on one fitted model. Differences in case mix and development exposure remain unresolved. Further B-informed changes require an exploratory label and new independent evidence before stronger reliance claims.
