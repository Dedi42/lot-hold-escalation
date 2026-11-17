**Table 2. Hypotheses and tests.**

| | Hypothesis | Statistic | Test |
|:---|:---|:---|:---|
| H1 | Hold hours are concentrated | Share of hold hours in the longest 10% of holds > 0.5 | Lot cluster bootstrap |
| H2a | Hazard of release decreases | Weibull shape < 1 | Wald interval (Kaplan–Meier hazard as check) |
| H2b | Remaining time grows with age | Median remaining after 8 h / median at onset > 1 | Lot cluster bootstrap |
| H3 | Ensemble ranks open holds best; landmark beats p90 (d) | ΔAUC(remaining > 8 h) vs LightGBM onset, landmark, Kaplan–Meier (a–c), and of landmark vs p90 (d) | Lot bootstrap, Holm |
| H4 | Ensemble beats oldest-first | Relative gain in recovered hold hours, test period and rolling origins (H4-RO) | Weekly block bootstrap, Holm |
| H5 | Static p90 rule is worse than oldest-first | Relative difference in recovered hold hours | Weekly block bootstrap, Holm |
| H6 | H4 holds with heterogeneous effects | Gain over oldest-first, 200 draws of α(c) ~ U(0.2, 0.8), δ(c) ~ U(1, 8) h | 5th percentile > 0 |
| H7 | Gain-based and mean-based indices are equivalent | Relative difference | TOST, margin ±3% |
| H8 | Models transfer across lines | (a) gain over oldest-first > 0; (b) not more than 3% (relative) below the in-line model | Block bootstrap; margin 3% |
| H9 | Gain is consistent across lines | Pooled log ratio over rolling origins; Cochran's Q, I² | Inverse-variance meta-analysis |
| H10 | Urgency weighting reduces lateness (Line A) | Relative gain in lateness removed, vs oldest-first and vs plain ensemble | Bootstrap over late lots, Holm |
