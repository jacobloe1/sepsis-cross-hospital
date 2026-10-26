# Preliminary evaluation

| Regime | Cohort | Model | AUROC | Utility* | Hour sensitivity | PPV | ECE | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A_only | A_test | sirs | 0.5862 | 0.0794 | 0.4998 | 0.0333 | NA | 1.0000 |
| A_only | A_test | logistic | 0.7377 | 0.2734 | 0.6739 | 0.0457 | 0.0022 | 1.0000 |
| A_only | A_test | logistic_abstain | 0.7377 | 0.2693 | 0.6619 | 0.0456 | 0.0022 | 0.9687 |
| A_only | B_transfer | sirs | 0.6223 | -0.0159 | 0.4963 | 0.0275 | NA | 1.0000 |
| A_only | B_transfer | logistic | 0.6915 | 0.0947 | 0.4874 | 0.0347 | 0.0037 | 1.0000 |
| A_only | B_transfer | logistic_abstain | 0.6915 | 0.0926 | 0.4809 | 0.0346 | 0.0037 | 0.9646 |
| pooled | pooled_random_test | sirs | 0.6036 | 0.0415 | 0.4966 | 0.0308 | NA | 1.0000 |
| pooled | pooled_random_test | logistic | 0.7457 | 0.2267 | 0.6612 | 0.0418 | 0.0012 | 1.0000 |
| pooled | pooled_random_test | logistic_abstain | 0.7457 | 0.2226 | 0.6510 | 0.0417 | 0.0012 | 0.9674 |

*Utility is an independent implementation. Check utility_verification in metrics.json before citing.
Bootstrap intervals and subgroup counts are in metrics.json. Abstentions remain in the denominator as no alert.
Warning times describe detected cases only. None of these results establishes clinical safety or benefit.
