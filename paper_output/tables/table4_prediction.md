**Table 4. Discrimination among open holds on the test period (landmarks 0.5–48 h).**

| Model | C-index A | AUC(> 8 h) A | C-index B | AUC(> 8 h) B |
|---|---|---|---|---|
| Static p90 rule | 0.541 [0.533, 0.548] | 0.595 [0.579, 0.609] | 0.490 [0.484, 0.494] | 0.486 [0.476, 0.495] |
| Kaplan–Meier (department × reason) | 0.608 [0.601, 0.616] | 0.710 [0.694, 0.725] | 0.652 [0.646, 0.658] | 0.756 [0.747, 0.767] |
| LightGBM onset | 0.673 [0.663, 0.682] | 0.825 [0.805, 0.845] | 0.687 [0.681, 0.692] | 0.793 [0.783, 0.803] |
| Landmark GBM | 0.676 [0.667, 0.684] | 0.835 [0.820, 0.851] | 0.693 [0.687, 0.699] | 0.826 [0.819, 0.836] |
| Ensemble (Equation 4) | 0.693 [0.684, 0.701] | 0.856 [0.841, 0.872] | 0.712 [0.707, 0.717] | 0.839 [0.830, 0.848] |

Note: 95% lot cluster bootstrap intervals in brackets.
