**Table A1. Effect of decision-time context in the benchmark: without → with context features (test period, mean over five seeds).**

| Line, model | AUC(> 8 h) | B = 6 | B = 12 | B = 24 | B = 48 |
|---|---|---|---|---|---|
| A, LightGBM landmark | 0.749 → 0.769 | 65.2 → 64.4 | 88.2 → 89.6 | 119.9 → 122.3 | 142.5 → 143.0 |
| A, MLP survival | 0.746 → 0.783 | 65.2 → 69.7 | 86.4 → 94.0 | 120.3 → 123.8 | 143.1 → 143.1 |
| B, LightGBM landmark | 0.727 → 0.753 | 451 → 453 | 771 → 777 | 1117 → 1159 | 1422 → 1507 |
| B, MLP survival | 0.751 → 0.759 | 463 → 452 | 776 → 754 | 1127 → 1131 | 1468 → 1483 |

Note: columns B = 6 to 48 give hold hours recovered per calendar day, as in Table 5.
