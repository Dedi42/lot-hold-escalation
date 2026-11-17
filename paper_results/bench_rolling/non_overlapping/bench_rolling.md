# Benchmark over rolling origins (frozen hyperparameters)


## Line A: gain over the paper ensemble (%)

budget                                           6     12    24    48
policy                                                               
Age (oldest first)                            -10.3  -9.2  -8.1  -4.4
FT-Transformer survival (ext.)                  5.3   6.5   1.5   0.7
FT-Transformer survival (ext.) [mean score]     6.3   6.8   1.7   0.8
Hybrid (deep + LightGBM)                        5.5   8.3   1.6   0.8
Kaplan–Meier (D×R)                             -5.5  -9.4  -8.6  -3.0
Landmark GBM                                    1.3  -0.3  -0.2   0.2
LightGBM (log T)                               -3.0  -3.0  -1.1  -1.3
LightGBM LambdaRank (ext.)                      0.8   2.1  -1.2   0.4
LightGBM gain regression (ext.)                -1.3   1.9   0.5   0.5
LightGBM landmark (ext. features)               1.4   2.4   0.6   0.3
LightGBM landmark (paper features)             -2.0  -0.6  -0.8   0.0
LotSeq decision-focused ranker                  5.0   8.1   2.1   1.0
LotSeq survival (ext. + history)                2.7   5.3   0.4   0.7
LotSeq survival (ext. + history) [mean score]   2.7   5.4   0.3   0.6
MLP survival (ext.)                             6.5   5.7   0.4   0.6
MLP survival (ext.) [mean score]                6.5   5.7   0.7   0.6
MLP survival (paper features)                   1.2   3.1  -1.0   0.2
MLP survival (paper features) [mean score]      1.1   3.1  -1.0   0.3
Oracle                                         33.6  27.2  12.0   3.6
Static p90 rule                               -18.3 -25.4 -33.3 -38.5

## Line B: gain over the paper ensemble (%)

budget                                           6     12    24    48
policy                                                               
Age (oldest first)                            -25.5 -16.4 -14.0  -7.2
FT-Transformer survival (ext.)                  0.7  -2.3  -2.8   0.4
FT-Transformer survival (ext.) [mean score]     0.7  -2.3  -2.8   0.5
Hybrid (deep + LightGBM)                       -1.2  -3.6  -0.7   0.5
Kaplan–Meier (D×R)                              0.2  -1.4   0.2  -1.5
Landmark GBM                                   -0.5  -2.9   0.0  -0.3
LightGBM (log T)                               -2.4  -2.7  -5.4  -4.2
LightGBM LambdaRank (ext.)                    -42.5 -37.8 -21.8  -7.1
LightGBM gain regression (ext.)                -1.9  -1.6   0.0   0.9
LightGBM landmark (ext. features)               0.0  -1.7   0.2   0.3
LightGBM landmark (paper features)             -0.7  -3.7  -3.3  -0.6
LotSeq decision-focused ranker                -15.9  -4.9  -2.7   0.1
LotSeq survival (ext. + history)                0.4  -6.3  -4.7  -0.6
LotSeq survival (ext. + history) [mean score]   0.4  -6.3  -4.7  -0.6
MLP survival (ext.)                            -0.9  -7.0  -4.7  -1.5
MLP survival (ext.) [mean score]               -0.9  -7.0  -4.7  -1.5
MLP survival (paper features)                  -0.1  -3.4  -5.0  -2.0
MLP survival (paper features) [mean score]      0.0  -3.4  -5.0  -2.0
Oracle                                          4.1  14.3  16.3  18.7
Static p90 rule                               -51.5 -53.5 -57.6 -56.3
