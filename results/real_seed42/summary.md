# Preliminary evaluation

| Regime | Cohort | Model | AUROC | Utility* | Hour sensitivity | PPV | ECE | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A_only | A_test | sirs | 0.5869 | 0.0721 | 0.5129 | 0.0326 | NA | 1.0000 |
| A_only | A_test | logistic | 0.7196 | 0.2294 | 0.6725 | 0.0414 | 0.0038 | 1.0000 |
| A_only | A_test | logistic_abstain | 0.7196 | 0.2294 | 0.6725 | 0.0414 | 0.0038 | 1.0000 |
| A_only | B_transfer | sirs | 0.6223 | -0.0159 | 0.4963 | 0.0275 | NA | 1.0000 |
| A_only | B_transfer | logistic | 0.6966 | 0.0608 | 0.5531 | 0.0313 | 0.0010 | 1.0000 |
| A_only | B_transfer | logistic_abstain | 0.6966 | 0.0608 | 0.5531 | 0.0313 | 0.0010 | 1.0000 |
| pooled | pooled_random_test | sirs | 0.6064 | 0.0406 | 0.5077 | 0.0307 | NA | 1.0000 |
| pooled | pooled_random_test | logistic | 0.7443 | 0.2071 | 0.6767 | 0.0396 | 0.0016 | 1.0000 |
| pooled | pooled_random_test | logistic_abstain | 0.7443 | 0.2071 | 0.6767 | 0.0396 | 0.0016 | 1.0000 |

*Utility is an independent implementation. Check utility_verification in metrics.json before citing.
Bootstrap intervals and subgroup counts are in metrics.json. Abstentions remain in the denominator as no alert.
Warning times describe detected cases only. None of these results establishes clinical safety or benefit.
