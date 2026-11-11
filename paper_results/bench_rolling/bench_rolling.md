# Benchmark over rolling origins (frozen hyperparameters)


## Line A: gain over the paper ensemble (%)

budget                                           6     12    24    48
policy                                                               
Age (oldest first)                             -9.8  -9.3  -9.5  -5.1
FT-Transformer survival (ext.)                  7.3   6.6   1.2   0.8
FT-Transformer survival (ext.) [mean score]     8.2   7.0   1.4   0.8
Hybrid (deep + LightGBM)                        6.8   8.2   1.4   0.8
Kaplan–Meier (D×R)                             -2.8 -10.3 -10.5  -3.5
Landmark GBM                                    0.9  -2.2  -0.6   0.4
LightGBM (log T)                               -4.1  -2.6  -1.2  -1.4
LightGBM LambdaRank (ext.)                      1.2   1.0  -1.4   0.3
LightGBM gain regression (ext.)                -0.9   2.5   0.4   0.6
LightGBM landmark (ext. features)               0.8   1.9  -0.4   0.3
LightGBM landmark (paper features)             -1.3  -2.1  -1.3   0.1
LotSeq decision-focused ranker                  7.2   8.5   2.3   1.1
LotSeq survival (ext. + history)                4.2   5.9   0.6   0.8
LotSeq survival (ext. + history) [mean score]   4.2   6.0   0.4   0.7
MLP survival (ext.)                             7.0   5.2  -0.3   0.7
MLP survival (ext.) [mean score]                7.6   5.2  -0.1   0.7
MLP survival (paper features)                   2.9   2.3  -2.0   0.3
MLP survival (paper features) [mean score]      2.9   2.5  -2.0   0.5
Oracle                                         40.2  31.5  12.6   3.7
Static p90 rule                               -19.0 -26.6 -37.1 -42.6

## Line B: gain over the paper ensemble (%)

budget                                           6     12    24    48
policy                                                               
Age (oldest first)                            -20.2 -13.6 -12.9  -7.7
FT-Transformer survival (ext.)                 -0.5  -1.7  -1.9   0.4
FT-Transformer survival (ext.) [mean score]    -0.5  -1.7  -1.9   0.4
Hybrid (deep + LightGBM)                       -2.6  -1.5  -0.5   0.6
Kaplan–Meier (D×R)                              0.5  -1.7  -1.4  -3.0
Landmark GBM                                   -1.1  -1.6  -0.6  -1.2
LightGBM (log T)                               -1.0  -3.7  -5.4  -3.7
LightGBM LambdaRank (ext.)                    -35.6 -27.6 -17.6  -8.7
LightGBM gain regression (ext.)                -1.7  -1.3  -0.4   0.3
LightGBM landmark (ext. features)              -0.7  -1.2  -0.1   0.0
LightGBM landmark (paper features)             -1.7  -2.8  -3.8  -0.9
LotSeq decision-focused ranker                -10.4  -2.9  -1.3   0.7
LotSeq survival (ext. + history)               -0.6  -4.1  -3.1  -0.6
LotSeq survival (ext. + history) [mean score]  -0.6  -4.1  -3.1  -0.5
MLP survival (ext.)                            -2.4  -4.3  -2.9  -0.9
MLP survival (ext.) [mean score]               -2.4  -4.3  -2.8  -0.9
MLP survival (paper features)                  -2.7  -3.3  -4.1  -1.6
MLP survival (paper features) [mean score]     -2.7  -3.3  -4.1  -1.6
Oracle                                          9.4  15.5  17.0  17.9
Static p90 rule                               -52.6 -55.8 -57.9 -57.6
