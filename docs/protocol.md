# Protocol v0.1 — freeze before real-data evaluation

Question: Does discrimination, early-warning utility, calibration, or alert burden deteriorate when an A-developed model is applied to B relative to A's held-out patients?

Primary thesis: A patient-level random evaluation within the development hospital may overstate transfer performance; limited support for a clinician-review alert requires retained utility, sensitivity, calibration, and coverage under hospital-specific missingness shift.

Development split: Within A and ever-positive status, shuffle with seed42; boundaries floor(0.60n), floor(0.75n), floor(0.85n). Training fits preprocessing/model; calibration fits probability mapping; tuning fits the alert threshold; test is reserved for A evaluation. All hours of each patient remain together. B contains all available B patients for the transfer diagnostic. File hashes record cohort identity and detect exact duplicates; absence of shared person identifiers prevents ruling out non-identical repeated-person leakage.

Primary model is the proposal's simpler fallback: regularized logistic regression. No hyperparameter search yet. Secondary pooled development follows identical fractions within each hospital/sepsis stratum and is explicitly a separate regime. Inspect outputs only after freezing protocol. Subsequent changes require labeling B as an already-inspected development benchmark rather than an untouched final test.

The initial comparison is observational across hospital cohorts. Differences can reflect case mix, baseline prevalence, length of stay, or measurement practice; they do not identify a unique causal source of shift. Repeat with matched training sample sizes and prevalence-standardized descriptive analyses before stronger interpretation.

Proposed reliance gates (not yet tested on real data):

1. Paired bootstrap lower 95% bound of normalized-utility improvement versus SIRS exceeds 0.
2. Hour sensitivity is no more than 0.05 below SIRS at the A-tuned matched FPR. Report its paired CI and actual B alert burden; do not re-match using B labels.
3. Ten-bin ECE <0.05 overall and in evaluated adequately represented groups, with reliability plots/counts. Also inspect Brier score and coverage; low ECE is not sufficient.
4. No adequately represented subgroup has hour sensitivity >0.10 below the overall result. Definition initially ≥30 septic and ≥30 never-septic patients; collect subgroup CIs before treating this as strong evidence.
5. Missingness abstention must report coverage and whole-cohort missed warnings, not just selective accuracy. Compare the default rate-only rule with the stricter unseen-pattern rule.

If a gate is unmeasured, imprecise, or the utility scorer is unverified, classify the reliance claim as unresolved. If a measured gate fails, narrow the claim to unsupported transfer under this protocol. Retrospective gate success would still not establish clinical deployment safety.

Next stress conditions: strict unseen-mask abstention; increased measurement dropout applied only during prediction; unit-indicator exclusion; hospital reversal B→A; variation over seeds 7,42,2026. Never delete missing rows or backward fill. Preserve patient-level resampling. Add a no-alert baseline as a visible utility reference (normalization already makes it 0 when defined).
