# Follow-up verification record

The user's original `results/real_seed42` was read but not modified. Result hashes are recorded in `original_run_hashes.json` so this can be checked later.

## Official scorer

Retrieved the unmodified upstream Python scorer and BSD license via the GitHub connector. Provenance includes the Git blob IDs and local SHA-256 hashes. Loaded the actual scorer with NumPy 2.0.2 under the user's existing Python 3.9 environment; no NumPy substitute or rewritten scorer was used.

`verify_saved.py` checked all patient trajectories in the original A-test (3,051), B-transfer (20,000), and pooled random test (6,052), for SIRS, logistic, and logistic-with-abstention. Observed, ideal-window, and no-action utilities agree within floating-point error (<1e-13 per patient); cohort normalization matches the original saved metrics. This removes the previous utility-verification caveat for those saved results. It does not validate labels or establish clinical utility prospectively.

## Revised missingness rule

Eighteen tests passed, including offset ICU hours, no future or backward filling, patient split separation, utility examples, threshold ties, six-hour vital expiration, an all-missing hard stop when the legacy cutoff is 1.0, and acceptance of fresh vital signs. A synthetic end-to-end recent-vitals run also completed.

The seed42 A-only training, preprocessing, probability calibration, and threshold were reproduced to <1e-12 absolute numerical difference from the original fit. The difference in the revised system is the explicit missingness gate, rather than retraining to a different model specification.

## Interpretation and artifact details

Revised raw and abstaining models are both evaluated. The same A-derived threshold is retained for B. Covered-only calibration is separated from whole-cohort latent-risk calibration. AUROC of an abstaining row refers to the unchanged latent probabilities, not a changed selective ranking. Withheld hours remain in the utility and sensitivity denominators as no alerts.

Within-run intervals against SIRS use the original paired-patient bootstrap implementation. The added gate-versus-unselective comparison uses a separate NumPy paired-patient bootstrap with linear percentile quantiles; its RNG and method are recorded. Across three seeds, SD/range combine changed splits, sample reservoirs, and SGD order. They are descriptive, not a confidence interval or three independent external datasets.

The original calibration figure includes bin-count data. Sparse high-risk bins should not be interpreted without their small sample counts. Overall low ECE does not resolve that uncertainty.

## Completed repeated runs

All three seeds (7,42,2026) completed A-only and pooled experiments, with 15 model epochs, the original 50,000-hour cap, recent-vitals abstention, and 1,000 bootstrap replicates. Complete utility verification passed for every evaluated trajectory/model and cohort normalization in every run. All original result hashes and the core fitting-source fingerprints were checked after completion. Across-seed tables, a paired gate comparison, and two inspected PNG figures are included.
