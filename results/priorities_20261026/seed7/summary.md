# Preliminary evaluation

| Regime | Cohort | Model | AUROC | Utility* | Hour sensitivity | PPV | ECE | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A_only | A_test | sirs | 0.5958 | 0.0868 | 0.5319 | 0.0335 | NA | 1.0000 |
| A_only | A_test | logistic | 0.7196 | 0.2353 | 0.6729 | 0.0418 | 0.0028 | 1.0000 |
| A_only | A_test | logistic_abstain | 0.7196 | 0.2250 | 0.6570 | 0.0414 | 0.0028 | 0.9705 |
| A_only | B_transfer | sirs | 0.6223 | -0.0159 | 0.4963 | 0.0275 | NA | 1.0000 |
| A_only | B_transfer | logistic | 0.6971 | 0.0713 | 0.5476 | 0.0321 | 0.0018 | 1.0000 |
| A_only | B_transfer | logistic_abstain | 0.6971 | 0.0696 | 0.5424 | 0.0320 | 0.0018 | 0.9646 |
| pooled | pooled_random_test | sirs | 0.6082 | 0.0407 | 0.5137 | 0.0307 | NA | 1.0000 |
| pooled | pooled_random_test | logistic | 0.7373 | 0.1946 | 0.6557 | 0.0388 | 0.0018 | 1.0000 |
| pooled | pooled_random_test | logistic_abstain | 0.7373 | 0.1887 | 0.6442 | 0.0386 | 0.0018 | 0.9671 |

*Utility is an independent implementation. Check utility_verification in metrics.json before citing.
Bootstrap intervals and subgroup counts are in metrics.json. Abstentions remain in the denominator as no alert.
Warning times describe detected cases only. None of these results establishes clinical safety or benefit.
