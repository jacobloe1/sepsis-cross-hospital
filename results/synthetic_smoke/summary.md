# SYNTHETIC SOFTWARE CHECK — NOT PROJECT EVIDENCE

| Regime | Cohort | Model | AUROC | Utility* | Hour sensitivity | PPV | ECE | Coverage |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A_only | A_test | sirs | 0.9639 | 0.9229 | 1.0000 | 0.6824 | NA | 1.0000 |
| A_only | A_test | logistic | 0.9979 | 0.9048 | 1.0000 | 0.5577 | 0.0174 | 1.0000 |
| A_only | A_test | logistic_abstain | 0.9979 | 0.9048 | 0.9655 | 0.5490 | 0.0174 | 0.9907 |
| A_only | B_transfer | sirs | 0.9604 | 0.9108 | 0.9923 | 0.6855 | NA | 1.0000 |
| A_only | B_transfer | logistic | 0.9978 | 0.9044 | 1.0000 | 0.5836 | 0.0216 | 1.0000 |
| A_only | B_transfer | logistic_abstain | 0.9978 | 0.5495 | 0.6266 | 0.5819 | 0.0216 | 0.6503 |
| pooled | pooled_random_test | sirs | 0.9654 | 0.9175 | 1.0000 | 0.6829 | NA | 1.0000 |
| pooled | pooled_random_test | logistic | 0.9987 | 0.9110 | 1.0000 | 0.5864 | 0.0075 | 1.0000 |
| pooled | pooled_random_test | logistic_abstain | 0.9987 | 0.8665 | 0.9732 | 0.5798 | 0.0075 | 0.9873 |

*Utility is an independent implementation. Check utility_verification in metrics.json before citing.
Bootstrap intervals and subgroup counts are in metrics.json. Abstentions remain in the denominator as no alert.
Warning times describe detected cases only. None of these results establishes clinical safety or benefit.
