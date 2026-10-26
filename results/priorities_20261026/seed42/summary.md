# Preliminary evaluation

| Regime | Cohort | Model | AUROC | Utility* | Hour sensitivity | PPV | ECE | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A_only | A_test | sirs | 0.5869 | 0.0721 | 0.5129 | 0.0326 | NA | 1.0000 |
| A_only | A_test | logistic | 0.7196 | 0.2294 | 0.6725 | 0.0414 | 0.0038 | 1.0000 |
| A_only | A_test | logistic_abstain | 0.7196 | 0.2205 | 0.6565 | 0.0410 | 0.0038 | 0.9682 |
| A_only | B_transfer | sirs | 0.6223 | -0.0159 | 0.4963 | 0.0275 | NA | 1.0000 |
| A_only | B_transfer | logistic | 0.6966 | 0.0608 | 0.5531 | 0.0313 | 0.0010 | 1.0000 |
| A_only | B_transfer | logistic_abstain | 0.6966 | 0.0601 | 0.5482 | 0.0312 | 0.0010 | 0.9646 |
| pooled | pooled_random_test | sirs | 0.6064 | 0.0406 | 0.5077 | 0.0307 | NA | 1.0000 |
| pooled | pooled_random_test | logistic | 0.7443 | 0.2071 | 0.6767 | 0.0396 | 0.0016 | 1.0000 |
| pooled | pooled_random_test | logistic_abstain | 0.7443 | 0.1982 | 0.6633 | 0.0392 | 0.0016 | 0.9670 |

*Utility is an independent implementation. Check utility_verification in metrics.json before citing.
Bootstrap intervals and subgroup counts are in metrics.json. Abstentions remain in the denominator as no alert.
Warning times describe detected cases only. None of these results establishes clinical safety or benefit.
