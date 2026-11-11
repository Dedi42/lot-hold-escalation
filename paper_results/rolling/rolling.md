# Rolling-origin hypotheses (aggregated, no dates)


## pred_pooled_point

| line   | model          | version                              |      C |   AUC8 |
|:-------|:---------------|:-------------------------------------|-------:|-------:|
| A      | LightGBM onset | pooled scores (Table 4 as published) | 0.6728 | 0.8246 |
| A      | Landmark GBM   | pooled scores (Table 4 as published) | 0.6761 | 0.8353 |
| A      | Kaplan–Meier   | pooled scores (Table 4 as published) | 0.6082 | 0.7102 |
| A      | Static p90     | pooled scores (Table 4 as published) | 0.5412 | 0.5948 |
| A      | Ensemble       | pooled scores (Table 4 as published) | 0.6926 | 0.8564 |
| B      | LightGBM onset | pooled scores (Table 4 as published) | 0.6866 | 0.793  |
| B      | Landmark GBM   | pooled scores (Table 4 as published) | 0.6934 | 0.8264 |
| B      | Kaplan–Meier   | pooled scores (Table 4 as published) | 0.652  | 0.7561 |
| B      | Static p90     | pooled scores (Table 4 as published) | 0.4895 | 0.4859 |
| B      | Ensemble       | pooled scores (Table 4 as published) | 0.712  | 0.8388 |

## pred_within_landmark

| line   | model          |      C |   C_lo |   C_hi |    AUC |   AUC_lo |   AUC_hi |
|:-------|:---------------|-------:|-------:|-------:|-------:|---------:|---------:|
| A      | Ensemble       | 0.6475 | 0.6375 | 0.6574 | 0.7708 |   0.7486 |   0.791  |
| A      | LightGBM onset | 0.6228 | 0.6106 | 0.6352 | 0.7274 |   0.6995 |   0.7561 |
| A      | Landmark GBM   | 0.6326 | 0.6249 | 0.6411 | 0.7519 |   0.7355 |   0.7687 |
| A      | Kaplan–Meier   | 0.5295 | 0.5203 | 0.5387 | 0.5558 |   0.5346 |   0.5766 |
| A      | Static p90     | 0.4514 | 0.4412 | 0.4608 | 0.4208 |   0.396  |   0.4428 |
| B      | Ensemble       | 0.6629 | 0.6572 | 0.669  | 0.7571 |   0.747  |   0.7675 |
| B      | LightGBM onset | 0.6318 | 0.6255 | 0.6384 | 0.6989 |   0.6875 |   0.7107 |
| B      | Landmark GBM   | 0.6468 | 0.6413 | 0.6524 | 0.7503 |   0.7409 |   0.7603 |
| B      | Kaplan–Meier   | 0.5906 | 0.5845 | 0.5969 | 0.652  |   0.6406 |   0.6635 |
| B      | Static p90     | 0.4071 | 0.4011 | 0.4136 | 0.3436 |   0.3325 |   0.3552 |

## pred_within_landmark_tests

| line   | hypothesis   | metric   | model_a      | model_b        |   diff |     lo |     hi |   p_one_sided |   p_holm |
|:-------|:-------------|:---------|:-------------|:---------------|-------:|-------:|-------:|--------------:|---------:|
| A      | H3a          | AUC      | Ensemble     | LightGBM onset | 0.0433 | 0.0298 | 0.0566 |         0.001 |    0.003 |
| A      | H3a          | C        | Ensemble     | LightGBM onset | 0.0247 | 0.0179 | 0.0315 |         0.001 |    0.003 |
| A      | H3b          | AUC      | Ensemble     | Landmark GBM   | 0.0188 | 0.0042 | 0.033  |         0.011 |    0.011 |
| A      | H3b          | C        | Ensemble     | Landmark GBM   | 0.0148 | 0.0081 | 0.0215 |         0.001 |    0.003 |
| A      | H3c          | AUC      | Ensemble     | Kaplan–Meier   | 0.2153 | 0.1849 | 0.2446 |         0.001 |    0.003 |
| A      | H3c          | C        | Ensemble     | Kaplan–Meier   | 0.1179 | 0.1054 | 0.1305 |         0.001 |    0.003 |
| A      | H3d          | AUC      | Landmark GBM | Static p90     | 0.3317 | 0.3004 | 0.3647 |         0.001 |    0.001 |
| A      | H3d          | C        | Landmark GBM | Static p90     | 0.1816 | 0.1672 | 0.1962 |         0.001 |    0.001 |
| B      | H3a          | AUC      | Ensemble     | LightGBM onset | 0.0581 | 0.0523 | 0.0641 |         0.001 |    0.003 |
| B      | H3a          | C        | Ensemble     | LightGBM onset | 0.031  | 0.0277 | 0.0346 |         0.001 |    0.003 |
| B      | H3b          | AUC      | Ensemble     | Landmark GBM   | 0.0067 | 0.0007 | 0.0121 |         0.008 |    0.008 |
| B      | H3b          | C        | Ensemble     | Landmark GBM   | 0.0161 | 0.0128 | 0.0193 |         0.001 |    0.003 |
| B      | H3c          | AUC      | Ensemble     | Kaplan–Meier   | 0.1052 | 0.0945 | 0.1152 |         0.001 |    0.003 |
| B      | H3c          | C        | Ensemble     | Kaplan–Meier   | 0.0724 | 0.0671 | 0.0779 |         0.001 |    0.003 |
| B      | H3d          | AUC      | Landmark GBM | Static p90     | 0.407  | 0.3888 | 0.4244 |         0.001 |    0.001 |
| B      | H3d          | C        | Landmark GBM | Static p90     | 0.2399 | 0.2293 | 0.2502 |         0.001 |    0.001 |

## pred_by_landmark

| line   |    e |     n | model          |      C |   AUC8 |
|:-------|-----:|------:|:---------------|-------:|-------:|
| A      |  0   |  7515 | LightGBM onset | 0.6987 | 0.8529 |
| A      |  0   |  7515 | Landmark GBM   | 0.5722 | 0.851  |
| A      |  0   |  7515 | Kaplan–Meier   | 0.5276 | 0.636  |
| A      |  0   |  7515 | Static p90     | 0.5    | 0.5    |
| A      |  0   |  7515 | Ensemble       | 0.6597 | 0.8878 |
| A      |  0.5 |  4543 | LightGBM onset | 0.6393 | 0.8126 |
| A      |  0.5 |  4543 | Landmark GBM   | 0.6305 | 0.8478 |
| A      |  0.5 |  4543 | Kaplan–Meier   | 0.5456 | 0.6198 |
| A      |  0.5 |  4543 | Static p90     | 0.4355 | 0.3434 |
| A      |  0.5 |  4543 | Ensemble       | 0.656  | 0.8633 |
| A      |  1   |  3427 | LightGBM onset | 0.6314 | 0.797  |
| A      |  1   |  3427 | Landmark GBM   | 0.6493 | 0.841  |
| A      |  1   |  3427 | Kaplan–Meier   | 0.5477 | 0.6092 |
| A      |  1   |  3427 | Static p90     | 0.4308 | 0.3548 |
| A      |  1   |  3427 | Ensemble       | 0.6597 | 0.8516 |
| A      |  2   |  2140 | LightGBM onset | 0.6335 | 0.766  |
| A      |  2   |  2140 | Landmark GBM   | 0.6713 | 0.8117 |
| A      |  2   |  2140 | Kaplan–Meier   | 0.5364 | 0.5727 |
| A      |  2   |  2140 | Static p90     | 0.4268 | 0.3831 |
| A      |  2   |  2140 | Ensemble       | 0.6733 | 0.8211 |
| A      |  4   |  1115 | LightGBM onset | 0.6379 | 0.7282 |
| A      |  4   |  1115 | Landmark GBM   | 0.6471 | 0.7201 |
| A      |  4   |  1115 | Kaplan–Meier   | 0.528  | 0.5357 |
| A      |  4   |  1115 | Static p90     | 0.4523 | 0.4367 |
| A      |  4   |  1115 | Ensemble       | 0.6691 | 0.7655 |
| A      |  8   |   600 | LightGBM onset | 0.5809 | 0.5972 |
| A      |  8   |   600 | Landmark GBM   | 0.5732 | 0.5715 |
| A      |  8   |   600 | Kaplan–Meier   | 0.533  | 0.5324 |
| A      |  8   |   600 | Static p90     | 0.4997 | 0.509  |
| A      |  8   |   600 | Ensemble       | 0.6033 | 0.6236 |
| A      | 16   |   311 | LightGBM onset | 0.5619 | 0.6577 |
| A      | 16   |   311 | Landmark GBM   | 0.5659 | 0.5082 |
| A      | 16   |   311 | Kaplan–Meier   | 0.5385 | 0.5105 |
| A      | 16   |   311 | Static p90     | 0.4741 | 0.4533 |
| A      | 16   |   311 | Ensemble       | 0.6001 | 0.6318 |
| A      | 24   |   190 | LightGBM onset | 0.4684 | 0.4412 |
| A      | 24   |   190 | Landmark GBM   | 0.6397 | 0.6763 |
| A      | 24   |   190 | Kaplan–Meier   | 0.5899 | 0.6112 |
| A      | 24   |   190 | Static p90     | 0.5002 | 0.518  |
| A      | 24   |   190 | Ensemble       | 0.5747 | 0.5752 |
| A      | 48   |    53 | LightGBM onset | 0.5358 | 0.4939 |
| A      | 48   |    53 | Landmark GBM   | 0.6181 | 0.7419 |
| A      | 48   |    53 | Kaplan–Meier   | 0.6338 | 0.8354 |
| A      | 48   |    53 | Static p90     | 0.4698 | 0.4766 |
| A      | 48   |    53 | Ensemble       | 0.5958 | 0.6585 |
| B      |  0   | 27137 | LightGBM onset | 0.7613 | 0.8331 |
| B      |  0   | 27137 | Landmark GBM   | 0.5618 | 0.7886 |
| B      |  0   | 27137 | Kaplan–Meier   | 0.6231 | 0.7188 |
| B      |  0   | 27137 | Static p90     | 0.5    | 0.5    |
| B      |  0   | 27137 | Ensemble       | 0.6892 | 0.8638 |
| B      |  0.5 | 16904 | LightGBM onset | 0.6563 | 0.7667 |
| B      |  0.5 | 16904 | Landmark GBM   | 0.6405 | 0.8109 |
| B      |  0.5 | 16904 | Kaplan–Meier   | 0.5847 | 0.6851 |
| B      |  0.5 | 16904 | Static p90     | 0.4126 | 0.3106 |
| B      |  0.5 | 16904 | Ensemble       | 0.6762 | 0.8293 |
| B      |  1   | 13921 | LightGBM onset | 0.648  | 0.7495 |
| B      |  1   | 13921 | Landmark GBM   | 0.6571 | 0.8091 |
| B      |  1   | 13921 | Kaplan–Meier   | 0.5962 | 0.6861 |
| B      |  1   | 13921 | Static p90     | 0.4006 | 0.3082 |
| B      |  1   | 13921 | Ensemble       | 0.6801 | 0.818  |
| B      |  2   | 10114 | LightGBM onset | 0.6412 | 0.7281 |
| B      |  2   | 10114 | Landmark GBM   | 0.6673 | 0.7928 |
| B      |  2   | 10114 | Kaplan–Meier   | 0.6049 | 0.6777 |
| B      |  2   | 10114 | Static p90     | 0.3894 | 0.3148 |
| B      |  2   | 10114 | Ensemble       | 0.682  | 0.7991 |
| B      |  4   |  6394 | LightGBM onset | 0.6222 | 0.6904 |
| B      |  4   |  6394 | Landmark GBM   | 0.6816 | 0.7686 |
| B      |  4   |  6394 | Kaplan–Meier   | 0.6016 | 0.649  |
| B      |  4   |  6394 | Static p90     | 0.3945 | 0.342  |
| B      |  4   |  6394 | Ensemble       | 0.6764 | 0.7681 |
| B      |  8   |  3555 | LightGBM onset | 0.6222 | 0.6653 |
| B      |  8   |  3555 | Landmark GBM   | 0.6546 | 0.6892 |
| B      |  8   |  3555 | Kaplan–Meier   | 0.6222 | 0.6468 |
| B      |  8   |  3555 | Static p90     | 0.37   | 0.339  |
| B      |  8   |  3555 | Ensemble       | 0.6555 | 0.7056 |
| B      | 16   |  1928 | LightGBM onset | 0.6091 | 0.6094 |
| B      | 16   |  1928 | Landmark GBM   | 0.687  | 0.693  |
| B      | 16   |  1928 | Kaplan–Meier   | 0.6573 | 0.6566 |
| B      | 16   |  1928 | Static p90     | 0.3498 | 0.3422 |
| B      | 16   |  1928 | Ensemble       | 0.6583 | 0.6653 |
| B      | 24   |  1329 | LightGBM onset | 0.6258 | 0.6168 |
| B      | 24   |  1329 | Landmark GBM   | 0.7186 | 0.7103 |
| B      | 24   |  1329 | Kaplan–Meier   | 0.6969 | 0.7076 |
| B      | 24   |  1329 | Static p90     | 0.3158 | 0.2991 |
| B      | 24   |  1329 | Ensemble       | 0.6837 | 0.6831 |
| B      | 48   |   735 | LightGBM onset | 0.6953 | 0.6611 |
| B      | 48   |   735 | Landmark GBM   | 0.7379 | 0.7294 |
| B      | 48   |   735 | Kaplan–Meier   | 0.7159 | 0.7303 |
| B      | 48   |   735 | Static p90     | 0.3391 | 0.2738 |
| B      | 48   |   735 | Ensemble       | 0.7228 | 0.7007 |

## ro_policies

| line   | variant              |   budget | policy               |   h_per_calendar_day |   escalations |
|:-------|:---------------------|---------:|:---------------------|---------------------:|--------------:|
| A      | warm-up              |        6 | Age (oldest first)   |              59.2052 |           308 |
| A      | alpha(e), gamma 0.25 |        6 | Age (oldest first)   |              51.6543 |           308 |
| A      | alpha(e), gamma 0.5  |        6 | Age (oldest first)   |              45.1667 |           308 |
| A      | alpha(e), gamma 1    |        6 | Age (oldest first)   |              34.7531 |           308 |
| A      | warm-up              |        6 | Kaplan–Meier (D×R)   |              63.7601 |           308 |
| A      | alpha(e), gamma 0.25 |        6 | Kaplan–Meier (D×R)   |              58.118  |           308 |
| A      | alpha(e), gamma 0.5  |        6 | Kaplan–Meier (D×R)   |              53.0942 |           308 |
| A      | alpha(e), gamma 1    |        6 | Kaplan–Meier (D×R)   |              44.587  |           308 |
| A      | warm-up              |        6 | Ensemble             |              65.9308 |           308 |
| A      | alpha(e), gamma 0.25 |        6 | Ensemble             |              59.2856 |           308 |
| A      | alpha(e), gamma 0.5  |        6 | Ensemble             |              53.5504 |           308 |
| A      | alpha(e), gamma 1    |        6 | Ensemble             |              44.2499 |           308 |
| A      | warm-up              |        6 | Ensemble (gain)      |              65.4375 |           308 |
| A      | warm-up              |        6 | Transfer             |              58.3848 |           308 |
| A      | warm-up              |        6 | Oracle               |              92.0456 |           308 |
| A      | alpha(e), gamma 0.25 |        6 | Oracle               |              89.1696 |           308 |
| A      | alpha(e), gamma 0.5  |        6 | Oracle               |              86.46   |           308 |
| A      | alpha(e), gamma 1    |        6 | Oracle               |              81.4857 |           308 |
| A      | alpha(e), gamma 0.25 |        6 | Oracle, effect-aware |              89.2037 |           308 |
| A      | alpha(e), gamma 0.5  |        6 | Oracle, effect-aware |              86.5725 |           308 |
| A      | alpha(e), gamma 1    |        6 | Oracle, effect-aware |              81.7902 |           308 |
| A      | warm-up              |       12 | Age (oldest first)   |              82.4159 |           616 |
| A      | alpha(e), gamma 0.25 |       12 | Age (oldest first)   |              74.9437 |           616 |
| A      | alpha(e), gamma 0.5  |       12 | Age (oldest first)   |              68.2582 |           616 |
| A      | alpha(e), gamma 1    |       12 | Age (oldest first)   |              56.8882 |           616 |
| A      | warm-up              |       12 | Kaplan–Meier (D×R)   |              81.0459 |           615 |
| A      | alpha(e), gamma 0.25 |       12 | Kaplan–Meier (D×R)   |              75.5163 |           615 |
| A      | alpha(e), gamma 0.5  |       12 | Kaplan–Meier (D×R)   |              70.4889 |           615 |
| A      | alpha(e), gamma 1    |       12 | Kaplan–Meier (D×R)   |              61.7168 |           615 |
| A      | warm-up              |       12 | Ensemble             |              91.7317 |           615 |
| A      | alpha(e), gamma 0.25 |       12 | Ensemble             |              85.9119 |           615 |
| A      | alpha(e), gamma 0.5  |       12 | Ensemble             |              80.6632 |           615 |
| A      | alpha(e), gamma 1    |       12 | Ensemble             |              71.6167 |           615 |
| A      | warm-up              |       12 | Ensemble (gain)      |              91.853  |           615 |
| A      | warm-up              |       12 | Transfer             |              74.3905 |           615 |
| A      | warm-up              |       12 | Oracle               |             118.972  |           612 |
| A      | alpha(e), gamma 0.25 |       12 | Oracle               |             116.24   |           612 |
| A      | alpha(e), gamma 0.5  |       12 | Oracle               |             113.623  |           612 |
| A      | alpha(e), gamma 1    |       12 | Oracle               |             108.701  |           612 |
| A      | alpha(e), gamma 0.25 |       12 | Oracle, effect-aware |             116.265  |           612 |
| A      | alpha(e), gamma 0.5  |       12 | Oracle, effect-aware |             113.691  |           612 |
| A      | alpha(e), gamma 1    |       12 | Oracle, effect-aware |             108.901  |           612 |
| A      | warm-up              |       24 | Age (oldest first)   |             116.978  |          1215 |
| A      | alpha(e), gamma 0.25 |       24 | Age (oldest first)   |             110.657  |          1215 |
| A      | alpha(e), gamma 0.5  |       24 | Age (oldest first)   |             104.734  |          1215 |
| A      | alpha(e), gamma 1    |       24 | Age (oldest first)   |              93.9729 |          1215 |
| A      | warm-up              |       24 | Kaplan–Meier (D×R)   |             116.822  |          1213 |
| A      | alpha(e), gamma 0.25 |       24 | Kaplan–Meier (D×R)   |             111.411  |          1213 |
| A      | alpha(e), gamma 0.5  |       24 | Kaplan–Meier (D×R)   |             106.348  |          1213 |
| A      | alpha(e), gamma 1    |       24 | Kaplan–Meier (D×R)   |              97.1592 |          1213 |
| A      | warm-up              |       24 | Ensemble             |             129.772  |          1212 |
| A      | alpha(e), gamma 0.25 |       24 | Ensemble             |             125.665  |          1212 |
| A      | alpha(e), gamma 0.5  |       24 | Ensemble             |             121.783  |          1212 |
| A      | alpha(e), gamma 1    |       24 | Ensemble             |             114.629  |          1212 |
| A      | warm-up              |       24 | Ensemble (gain)      |             128.866  |          1212 |
| A      | warm-up              |       24 | Transfer             |             102.177  |          1219 |
| A      | warm-up              |       24 | Oracle               |             143.619  |          1205 |
| A      | alpha(e), gamma 0.25 |       24 | Oracle               |             140.873  |          1205 |
| A      | alpha(e), gamma 0.5  |       24 | Oracle               |             138.208  |          1205 |
| A      | alpha(e), gamma 1    |       24 | Oracle               |             133.107  |          1205 |
| A      | alpha(e), gamma 0.25 |       24 | Oracle, effect-aware |             140.88   |          1205 |
| A      | alpha(e), gamma 0.5  |       24 | Oracle, effect-aware |             138.228  |          1205 |
| A      | alpha(e), gamma 1    |       24 | Oracle, effect-aware |             133.162  |          1205 |
| A      | warm-up              |       48 | Age (oldest first)   |             141.776  |          2249 |
| A      | alpha(e), gamma 0.25 |       48 | Age (oldest first)   |             137.6    |          2249 |
| A      | alpha(e), gamma 0.5  |       48 | Age (oldest first)   |             133.58   |          2249 |
| A      | alpha(e), gamma 1    |       48 | Age (oldest first)   |             125.983  |          2249 |
| A      | warm-up              |       48 | Kaplan–Meier (D×R)   |             144.583  |          2236 |
| A      | alpha(e), gamma 0.25 |       48 | Kaplan–Meier (D×R)   |             141.144  |          2236 |
| A      | alpha(e), gamma 0.5  |       48 | Kaplan–Meier (D×R)   |             137.815  |          2236 |
| A      | alpha(e), gamma 1    |       48 | Kaplan–Meier (D×R)   |             131.473  |          2236 |
| A      | warm-up              |       48 | Ensemble             |             149.078  |          2220 |
| A      | alpha(e), gamma 0.25 |       48 | Ensemble             |             146.157  |          2220 |
| A      | alpha(e), gamma 0.5  |       48 | Ensemble             |             143.319  |          2220 |
| A      | alpha(e), gamma 1    |       48 | Ensemble             |             137.882  |          2220 |
| A      | warm-up              |       48 | Ensemble (gain)      |             148.902  |          2220 |
| A      | warm-up              |       48 | Transfer             |             139.802  |          2253 |
| A      | warm-up              |       48 | Oracle               |             153.952  |          2206 |
| A      | alpha(e), gamma 0.25 |       48 | Oracle               |             151.278  |          2206 |
| A      | alpha(e), gamma 0.5  |       48 | Oracle               |             148.67   |          2206 |
| A      | alpha(e), gamma 1    |       48 | Oracle               |             143.645  |          2206 |
| A      | alpha(e), gamma 0.25 |       48 | Oracle, effect-aware |             151.278  |          2206 |
| A      | alpha(e), gamma 0.5  |       48 | Oracle, effect-aware |             148.67   |          2206 |
| A      | alpha(e), gamma 1    |       48 | Oracle, effect-aware |             143.646  |          2206 |
| B      | warm-up              |        6 | Age (oldest first)   |             357.609  |           308 |
| B      | alpha(e), gamma 0.25 |        6 | Age (oldest first)   |             188.677  |           308 |
| B      | alpha(e), gamma 0.5  |        6 | Age (oldest first)   |             101.212  |           308 |
| B      | alpha(e), gamma 1    |        6 | Age (oldest first)   |              30.632  |           308 |
| B      | warm-up              |        6 | Kaplan–Meier (D×R)   |             472.729  |           308 |
| B      | alpha(e), gamma 0.25 |        6 | Kaplan–Meier (D×R)   |             341.211  |           308 |
| B      | alpha(e), gamma 0.5  |        6 | Kaplan–Meier (D×R)   |             266.233  |           308 |
| B      | alpha(e), gamma 1    |        6 | Kaplan–Meier (D×R)   |             186.556  |           308 |
| B      | warm-up              |        6 | Ensemble             |             461.261  |           308 |
| B      | alpha(e), gamma 0.25 |        6 | Ensemble             |             335.086  |           308 |
| B      | alpha(e), gamma 0.5  |        6 | Ensemble             |             270.503  |           308 |
| B      | alpha(e), gamma 1    |        6 | Ensemble             |             211.405  |           308 |
| B      | warm-up              |        6 | Ensemble (gain)      |             460.937  |           308 |
| B      | warm-up              |        6 | Transfer             |             374.547  |           308 |
| B      | warm-up              |        6 | Oracle               |             449.27   |           308 |
| B      | alpha(e), gamma 0.25 |        6 | Oracle               |             365.137  |           308 |
| B      | alpha(e), gamma 0.5  |        6 | Oracle               |             316.768  |           308 |
| B      | alpha(e), gamma 1    |        6 | Oracle               |             262.453  |           308 |
| B      | alpha(e), gamma 0.25 |        6 | Oracle, effect-aware |             425.099  |           308 |
| B      | alpha(e), gamma 0.5  |        6 | Oracle, effect-aware |             399.586  |           308 |
| B      | alpha(e), gamma 1    |        6 | Oracle, effect-aware |             373.167  |           308 |
| B      | warm-up              |       12 | Age (oldest first)   |             557.892  |           616 |
| B      | alpha(e), gamma 0.25 |       12 | Age (oldest first)   |             386.451  |           616 |
| B      | alpha(e), gamma 0.5  |       12 | Age (oldest first)   |             272.233  |           616 |
| B      | alpha(e), gamma 1    |       12 | Age (oldest first)   |             141.178  |           616 |
| B      | warm-up              |       12 | Kaplan–Meier (D×R)   |             665.716  |           616 |
| B      | alpha(e), gamma 0.25 |       12 | Kaplan–Meier (D×R)   |             555.905  |           616 |
| B      | alpha(e), gamma 0.5  |       12 | Kaplan–Meier (D×R)   |             490.647  |           616 |
| B      | alpha(e), gamma 1    |       12 | Kaplan–Meier (D×R)   |             415.206  |           616 |
| B      | warm-up              |       12 | Ensemble             |             654.445  |           616 |
| B      | alpha(e), gamma 0.25 |       12 | Ensemble             |             566.939  |           616 |
| B      | alpha(e), gamma 0.5  |       12 | Ensemble             |             510.362  |           616 |
| B      | alpha(e), gamma 1    |       12 | Ensemble             |             440.728  |           616 |
| B      | warm-up              |       12 | Ensemble (gain)      |             643.844  |           616 |
| B      | warm-up              |       12 | Transfer             |             603.915  |           616 |
| B      | warm-up              |       12 | Oracle               |             745.347  |           616 |
| B      | alpha(e), gamma 0.25 |       12 | Oracle               |             703.978  |           616 |
| B      | alpha(e), gamma 0.5  |       12 | Oracle               |             667.825  |           616 |
| B      | alpha(e), gamma 1    |       12 | Oracle               |             607.299  |           616 |
| B      | alpha(e), gamma 0.25 |       12 | Oracle, effect-aware |             717.199  |           616 |
| B      | alpha(e), gamma 0.5  |       12 | Oracle, effect-aware |             688.836  |           616 |
| B      | alpha(e), gamma 1    |       12 | Oracle, effect-aware |             640.736  |           616 |
| B      | warm-up              |       24 | Age (oldest first)   |             830.625  |          1232 |
| B      | alpha(e), gamma 0.25 |       24 | Age (oldest first)   |             649.858  |          1232 |
| B      | alpha(e), gamma 0.5  |       24 | Age (oldest first)   |             511.721  |          1232 |
| B      | alpha(e), gamma 1    |       24 | Age (oldest first)   |             323.324  |          1232 |
| B      | warm-up              |       24 | Kaplan–Meier (D×R)   |             886.759  |          1232 |
| B      | alpha(e), gamma 0.25 |       24 | Kaplan–Meier (D×R)   |             791.607  |          1232 |
| B      | alpha(e), gamma 0.5  |       24 | Kaplan–Meier (D×R)   |             717.228  |          1232 |
| B      | alpha(e), gamma 1    |       24 | Kaplan–Meier (D×R)   |             610.068  |          1232 |
| B      | warm-up              |       24 | Ensemble             |             896.782  |          1232 |
| B      | alpha(e), gamma 0.25 |       24 | Ensemble             |             818.09   |          1232 |
| B      | alpha(e), gamma 0.5  |       24 | Ensemble             |             755.671  |          1232 |
| B      | alpha(e), gamma 1    |       24 | Ensemble             |             662.676  |          1232 |
| B      | warm-up              |       24 | Ensemble (gain)      |             899.948  |          1232 |
| B      | warm-up              |       24 | Transfer             |             802.032  |          1232 |
| B      | warm-up              |       24 | Oracle               |            1055.32   |          1232 |
| B      | alpha(e), gamma 0.25 |       24 | Oracle               |            1014.73   |          1232 |
| B      | alpha(e), gamma 0.5  |       24 | Oracle               |             978.121  |          1232 |
| B      | alpha(e), gamma 1    |       24 | Oracle               |             914.191  |          1232 |
| B      | alpha(e), gamma 0.25 |       24 | Oracle, effect-aware |            1019.28   |          1232 |
| B      | alpha(e), gamma 0.5  |       24 | Oracle, effect-aware |             986.462  |          1232 |
| B      | alpha(e), gamma 1    |       24 | Oracle, effect-aware |             930.8    |          1232 |
| B      | warm-up              |       48 | Age (oldest first)   |            1052.41   |          2464 |
| B      | alpha(e), gamma 0.25 |       48 | Age (oldest first)   |             905.365  |          2464 |
| B      | alpha(e), gamma 0.5  |       48 | Age (oldest first)   |             780.568  |          2464 |
| B      | alpha(e), gamma 1    |       48 | Age (oldest first)   |             584.02   |          2464 |
| B      | warm-up              |       48 | Kaplan–Meier (D×R)   |            1093.03   |          2464 |
| B      | alpha(e), gamma 0.25 |       48 | Kaplan–Meier (D×R)   |            1009.52   |          2464 |
| B      | alpha(e), gamma 0.5  |       48 | Kaplan–Meier (D×R)   |             937.441  |          2464 |
| B      | alpha(e), gamma 1    |       48 | Kaplan–Meier (D×R)   |             820.139  |          2464 |
| B      | warm-up              |       48 | Ensemble             |            1117.25   |          2464 |
| B      | alpha(e), gamma 0.25 |       48 | Ensemble             |            1049.94   |          2464 |
| B      | alpha(e), gamma 0.5  |       48 | Ensemble             |             991.791  |          2464 |
| B      | alpha(e), gamma 1    |       48 | Ensemble             |             896.408  |          2464 |
| B      | warm-up              |       48 | Ensemble (gain)      |            1115.01   |          2464 |
| B      | warm-up              |       48 | Transfer             |             993.866  |          2464 |
| B      | warm-up              |       48 | Oracle               |            1318.09   |          2464 |
| B      | alpha(e), gamma 0.25 |       48 | Oracle               |            1285.1    |          2464 |
| B      | alpha(e), gamma 0.5  |       48 | Oracle               |            1253.49   |          2464 |
| B      | alpha(e), gamma 1    |       48 | Oracle               |            1194.13   |          2464 |
| B      | alpha(e), gamma 0.25 |       48 | Oracle, effect-aware |            1285.54   |          2464 |
| B      | alpha(e), gamma 0.5  |       48 | Oracle, effect-aware |            1254.55   |          2464 |
| B      | alpha(e), gamma 1    |       48 | Oracle, effect-aware |            1197.37   |          2464 |

## ro_comparisons

| tag                                      | line   | variant              |   budget |     rel |   rel_lo |   rel_hi |   p_greater |   p_less |   p_signflip_greater |   p_signflip_less |    t_lo |    t_hi |   a_h_per_day |   b_h_per_day |   log_ratio |   log_ratio_se |   weeks |   p_holm |   p_signflip_holm |
|:-----------------------------------------|:-------|:---------------------|---------:|--------:|---------:|---------:|------------:|---------:|---------------------:|------------------:|--------:|--------:|--------------:|--------------:|------------:|---------------:|--------:|---------:|------------------:|
| Ensemble vs Age (oldest first)           | A      | warm-up              |        6 |  0.1136 |   0.0001 |   0.2847 |      0.0255 |   0.975  |               0.0586 |            0.9453 | -0.0276 |  0.3764 |       65.9308 |       59.2052 |      0.1076 |         0.0652 |       8 |   0.0255 |            0.0586 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | warm-up              |        6 |  0.0769 |  -0.0269 |   0.2195 |      0.0905 |   0.91   |               0.1406 |            0.8633 | -0.0338 |  0.213  |       63.7601 |       59.2052 |      0.0741 |         0.0588 |       8 |   0.2714 |            0.4219 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | warm-up              |        6 |  0.034  |  -0.0416 |   0.1586 |      0.2219 |   0.7786 |               0.2891 |            0.7148 | -0.1211 |  0.2993 |       65.9308 |       63.7601 |      0.0335 |         0.0485 |       8 |   0.2219 |            0.2891 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.25 |        6 |  0.1477 |   0.0417 |   0.3129 |      0.001  |   0.9995 |               0.0195 |            0.9844 |  0.0037 |  0.4131 |       59.2856 |       51.6543 |      0.1378 |         0.0602 |       8 |   0.002  |            0.0195 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.25 |        6 |  0.1251 |   0.0134 |   0.2972 |      0.013  |   0.9875 |               0.0469 |            0.957  | -0.0145 |  0.2895 |       58.118  |       51.6543 |      0.1179 |         0.0641 |       8 |   0.039  |            0.1406 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.25 |        6 |  0.0201 |  -0.0736 |   0.1569 |      0.3513 |   0.6492 |               0.3672 |            0.6367 | -0.1462 |  0.3072 |       59.2856 |       58.118  |      0.0199 |         0.0557 |       8 |   0.3513 |            0.3672 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.5  |        6 |  0.1856 |   0.0853 |   0.3441 |      0.0005 |   1      |               0.0039 |            1      |  0.037  |  0.4549 |       53.5504 |       45.1667 |      0.1703 |         0.056  |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.5  |        6 |  0.1755 |   0.0513 |   0.3818 |      0.0005 |   1      |               0.0312 |            0.9727 |  0.0042 |  0.3729 |       53.0942 |       45.1667 |      0.1617 |         0.0702 |       8 |   0.002  |            0.0938 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.5  |        6 |  0.0086 |  -0.1064 |   0.1614 |      0.4363 |   0.5642 |               0.4492 |            0.5547 | -0.1718 |  0.3215 |       53.5504 |       53.0942 |      0.0086 |         0.0648 |       8 |   0.4363 |            0.4492 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 1    |        6 |  0.2733 |   0.1806 |   0.4362 |      0.0005 |   1      |               0.0039 |            1      |  0.1106 |  0.5547 |       44.2499 |       34.7531 |      0.2416 |         0.0499 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 1    |        6 |  0.283  |   0.1277 |   0.5578 |      0.0005 |   1      |               0.0039 |            1      |  0.0421 |  0.5591 |       44.587  |       34.7531 |      0.2492 |         0.0835 |       8 |   0.002  |            0.0156 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 1    |        6 | -0.0076 |  -0.1661 |   0.1821 |      0.5147 |   0.4858 |               0.543  |            0.4609 | -0.2207 |  0.3638 |       44.2499 |       44.587  |     -0.0076 |         0.0849 |       8 |   0.4858 |            0.4609 |
| H7 Ensemble (gain) vs Ensemble           | A      | warm-up              |        6 | -0.0075 |  -0.0366 |   0.0333 |      0.6752 |   0.3253 |               0.6602 |            0.3438 | -0.0613 |  0.0896 |       65.4375 |       65.9308 |     -0.0075 |         0.0179 |       8 |   0.6507 |            0.7617 |
| H8a Transfer vs Age (oldest first)       | A      | warm-up              |        6 | -0.0139 |  -0.1127 |   0.1412 |      0.5992 |   0.4013 |               0.582  |            0.4219 | -0.1755 |  0.1383 |       58.3848 |       59.2052 |     -0.014  |         0.0661 |       8 |   0.4013 |            0.4219 |
| H8b Transfer vs Ensemble                 | A      | warm-up              |        6 | -0.1145 |  -0.2329 |  -0.0136 |      0.985  |   0.0155 |               0.9648 |            0.0391 | -0.3224 |  0.0349 |       58.3848 |       65.9308 |     -0.1216 |         0.063  |       8 |   0.0155 |            0.0391 |
| Ensemble vs Age (oldest first)           | A      | warm-up              |       12 |  0.113  |   0.0425 |   0.2089 |      0.0015 |   0.999  |               0.0234 |            0.9805 |  0.0219 |  0.2781 |       91.7317 |       82.4159 |      0.1071 |         0.0379 |       8 |   0.003  |            0.0469 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | warm-up              |       12 | -0.0166 |  -0.0681 |   0.0189 |      0.7781 |   0.2224 |               0.7422 |            0.2617 | -0.087  |  0.046  |       81.0459 |       82.4159 |     -0.0168 |         0.0232 |       8 |   0.4448 |            0.5234 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | warm-up              |       12 |  0.1318 |   0.0611 |   0.2522 |      0.0005 |   1      |               0.0039 |            1      |  0.0356 |  0.3206 |       91.7317 |       81.0459 |      0.1239 |         0.0435 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.25 |       12 |  0.1464 |   0.0689 |   0.2519 |      0.001  |   0.9995 |               0.0078 |            0.9961 |  0.0482 |  0.3243 |       85.9119 |       74.9437 |      0.1366 |         0.0407 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.25 |       12 |  0.0076 |  -0.0515 |   0.0539 |      0.3793 |   0.6212 |               0.4023 |            0.6016 | -0.0762 |  0.079  |       75.5163 |       74.9437 |      0.0076 |         0.0272 |       8 |   0.5037 |            0.625  |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.25 |       12 |  0.1377 |   0.0654 |   0.2604 |      0.0005 |   1      |               0.0039 |            1      |  0.0335 |  0.3473 |       85.9119 |       75.5163 |      0.129  |         0.0457 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.5  |       12 |  0.1817 |   0.0971 |   0.297  |      0.0005 |   1      |               0.0078 |            0.9961 |  0.0756 |  0.3743 |       80.6632 |       68.2582 |      0.167  |         0.0435 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.5  |       12 |  0.0327 |  -0.0358 |   0.0936 |      0.1704 |   0.8301 |               0.1914 |            0.8125 | -0.0671 |  0.1164 |       70.4889 |       68.2582 |      0.0322 |         0.0319 |       8 |   0.2349 |            0.3125 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.5  |       12 |  0.1443 |   0.071  |   0.286  |      0.0005 |   1      |               0.0039 |            1      |  0.0302 |  0.3775 |       80.6632 |       70.4889 |      0.1348 |         0.0485 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 1    |       12 |  0.2589 |   0.1599 |   0.3985 |      0.0005 |   1      |               0.0039 |            1      |  0.1345 |  0.4853 |       71.6167 |       56.8882 |      0.2302 |         0.0489 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 1    |       12 |  0.0849 |  -0.0023 |   0.177  |      0.028  |   0.9725 |               0.0586 |            0.9453 | -0.0511 |  0.2011 |       61.7168 |       56.8882 |      0.0815 |         0.0419 |       8 |   0.043  |            0.1016 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 1    |       12 |  0.1604 |   0.0767 |   0.3301 |      0.0005 |   1      |               0.0039 |            1      |  0.0229 |  0.4453 |       71.6167 |       61.7168 |      0.1488 |         0.0551 |       8 |   0.002  |            0.0156 |
| H7 Ensemble (gain) vs Ensemble           | A      | warm-up              |       12 |  0.0013 |  -0.0112 |   0.015  |      0.4533 |   0.5472 |               0.4766 |            0.5273 | -0.0154 |  0.0134 |       91.853  |       91.7317 |      0.0013 |         0.007  |       8 |   0.6507 |            0.7617 |
| H8a Transfer vs Age (oldest first)       | A      | warm-up              |       12 | -0.0974 |  -0.1782 |  -0.0428 |      1      |   0.0005 |               0.9961 |            0.0078 | -0.2164 |  0.0101 |       74.3905 |       82.4159 |     -0.1025 |         0.0401 |       8 |   0.002  |            0.0312 |
| H8b Transfer vs Ensemble                 | A      | warm-up              |       12 | -0.189  |  -0.2969 |  -0.1195 |      1      |   0.0005 |               1      |            0.0039 | -0.345  | -0.0748 |       74.3905 |       91.7317 |     -0.2095 |         0.059  |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | warm-up              |       24 |  0.1094 |   0.0724 |   0.1483 |      0.0005 |   1      |               0.0039 |            1      |  0.0704 |  0.1635 |      129.772  |      116.978  |      0.1038 |         0.0181 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | warm-up              |       24 | -0.0013 |  -0.0235 |   0.0183 |      0.5102 |   0.4903 |               0.5273 |            0.4766 | -0.0312 |  0.0399 |      116.822  |      116.978  |     -0.0013 |         0.0107 |       8 |   0.4903 |            0.5234 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | warm-up              |       24 |  0.1109 |   0.0677 |   0.1602 |      0.0005 |   1      |               0.0039 |            1      |  0.0532 |  0.1737 |      129.772  |      116.822  |      0.1051 |         0.0218 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.25 |       24 |  0.1356 |   0.0941 |   0.18   |      0.0005 |   1      |               0.0039 |            1      |  0.0918 |  0.1947 |      125.665  |      110.657  |      0.1272 |         0.02   |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.25 |       24 |  0.0068 |  -0.0176 |   0.0283 |      0.2519 |   0.7486 |               0.3125 |            0.6914 | -0.0256 |  0.0511 |      111.411  |      110.657  |      0.0068 |         0.0117 |       8 |   0.5037 |            0.625  |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.25 |       24 |  0.1279 |   0.0814 |   0.1799 |      0.0005 |   1      |               0.0039 |            1      |  0.0672 |  0.1934 |      125.665  |      111.411  |      0.1204 |         0.0226 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.5  |       24 |  0.1628 |   0.1155 |   0.2126 |      0.0005 |   1      |               0.0039 |            1      |  0.1134 |  0.2279 |      121.783  |      104.734  |      0.1508 |         0.0221 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.5  |       24 |  0.0154 |  -0.0109 |   0.0402 |      0.1174 |   0.8831 |               0.1562 |            0.8477 | -0.02   |  0.063  |      106.348  |      104.734  |      0.0153 |         0.013  |       8 |   0.2349 |            0.3125 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.5  |       24 |  0.1451 |   0.0962 |   0.199  |      0.0005 |   1      |               0.0039 |            1      |  0.0808 |  0.2142 |      121.783  |      106.348  |      0.1355 |         0.0235 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 1    |       24 |  0.2198 |   0.1617 |   0.2839 |      0.0005 |   1      |               0.0039 |            1      |  0.1573 |  0.2997 |      114.629  |       93.9729 |      0.1987 |         0.0265 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 1    |       24 |  0.0339 |   0.0026 |   0.0663 |      0.0215 |   0.979  |               0.0508 |            0.9531 | -0.0084 |  0.089  |       97.1592 |       93.9729 |      0.0333 |         0.0159 |       8 |   0.043  |            0.1016 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 1    |       24 |  0.1798 |   0.1231 |   0.2403 |      0.0005 |   1      |               0.0039 |            1      |  0.1066 |  0.2587 |      114.629  |       97.1592 |      0.1653 |         0.0258 |       8 |   0.002  |            0.0156 |
| H7 Ensemble (gain) vs Ensemble           | A      | warm-up              |       24 | -0.007  |  -0.0147 |   0.0003 |      0.971  |   0.0295 |               0.9297 |            0.0742 | -0.0167 |  0.003  |      128.866  |      129.772  |     -0.007  |         0.0038 |       8 |   0.1179 |            0.2969 |
| H8a Transfer vs Age (oldest first)       | A      | warm-up              |       24 | -0.1265 |  -0.1876 |  -0.0662 |      1      |   0.0005 |               0.9961 |            0.0078 | -0.2059 | -0.044  |      102.177  |      116.978  |     -0.1353 |         0.0348 |       8 |   0.002  |            0.0312 |
| H8b Transfer vs Ensemble                 | A      | warm-up              |       24 | -0.2126 |  -0.2842 |  -0.1413 |      1      |   0.0005 |               1      |            0.0039 | -0.3081 | -0.119  |      102.177  |      129.772  |     -0.2391 |         0.048  |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | warm-up              |       48 |  0.0515 |   0.0351 |   0.0715 |      0.0005 |   1      |               0.0039 |            1      |  0.0299 |  0.0789 |      149.078  |      141.776  |      0.0502 |         0.0089 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | warm-up              |       48 |  0.0198 |   0.0048 |   0.0311 |      0.007  |   0.9935 |               0.0391 |            0.9648 | -0.0113 |  0.0385 |      144.583  |      141.776  |      0.0196 |         0.0066 |       8 |   0.028  |            0.1562 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | warm-up              |       48 |  0.0311 |   0.0162 |   0.0527 |      0.0005 |   1      |               0.0039 |            1      |  0.0071 |  0.0746 |      149.078  |      144.583  |      0.0306 |         0.0087 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.25 |       48 |  0.0622 |   0.0427 |   0.0836 |      0.0005 |   1      |               0.0039 |            1      |  0.0371 |  0.0917 |      146.157  |      137.6    |      0.0603 |         0.0098 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.25 |       48 |  0.0258 |   0.009  |   0.0383 |      0.005  |   0.9955 |               0.0195 |            0.9844 | -0.0097 |  0.0465 |      141.144  |      137.6    |      0.0254 |         0.0074 |       8 |   0.02   |            0.0781 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.25 |       48 |  0.0355 |   0.0185 |   0.0596 |      0.0005 |   1      |               0.0039 |            1      |  0.0095 |  0.0823 |      146.157  |      141.144  |      0.0349 |         0.0099 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 0.5  |       48 |  0.0729 |   0.0504 |   0.0968 |      0.0005 |   1      |               0.0039 |            1      |  0.0437 |  0.1054 |      143.319  |      133.58   |      0.0704 |         0.011  |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 0.5  |       48 |  0.0317 |   0.0129 |   0.0454 |      0.003  |   0.9975 |               0.0195 |            0.9844 | -0.0082 |  0.0546 |      137.815  |      133.58   |      0.0312 |         0.0082 |       8 |   0.009  |            0.0781 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 0.5  |       48 |  0.0399 |   0.0206 |   0.0665 |      0.0005 |   1      |               0.0039 |            1      |  0.0116 |  0.0903 |      143.319  |      137.815  |      0.0392 |         0.0112 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | A      | alpha(e), gamma 1    |       48 |  0.0944 |   0.0653 |   0.1234 |      0.0005 |   1      |               0.0039 |            1      |  0.0555 |  0.1344 |      137.882  |      125.983  |      0.0903 |         0.0138 |       8 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | A      | alpha(e), gamma 1    |       48 |  0.0436 |   0.0199 |   0.0601 |      0.0015 |   0.999  |               0.0195 |            0.9844 | -0.0053 |  0.0711 |      131.473  |      125.983  |      0.0427 |         0.0101 |       8 |   0.0045 |            0.0586 |
| Ensemble vs Kaplan–Meier (D×R)           | A      | alpha(e), gamma 1    |       48 |  0.0487 |   0.0247 |   0.0814 |      0.0005 |   1      |               0.0039 |            1      |  0.0152 |  0.107  |      137.882  |      131.473  |      0.0476 |         0.0139 |       8 |   0.002  |            0.0156 |
| H7 Ensemble (gain) vs Ensemble           | A      | warm-up              |       48 | -0.0012 |  -0.0045 |   0.001  |      0.8026 |   0.1979 |               0.75   |            0.2539 | -0.0053 |  0.0021 |      148.902  |      149.078  |     -0.0012 |         0.0014 |       8 |   0.5937 |            0.7617 |
| H8a Transfer vs Age (oldest first)       | A      | warm-up              |       48 | -0.0139 |  -0.0264 |  -0.0023 |      0.991  |   0.0095 |               0.9688 |            0.0352 | -0.0388 |  0.0033 |      139.802  |      141.776  |     -0.014  |         0.0064 |       8 |   0.019  |            0.0703 |
| H8b Transfer vs Ensemble                 | A      | warm-up              |       48 | -0.0622 |  -0.0877 |  -0.039  |      1      |   0.0005 |               1      |            0.0039 | -0.105  | -0.0303 |      139.802  |      149.078  |     -0.0642 |         0.0134 |       8 |   0.002  |            0.0156 |
| Ensemble vs Age (oldest first)           | B      | warm-up              |        6 |  0.2898 |   0.1377 |   0.5012 |      0.0005 |   1      |               0.0039 |            0.998  |  0.0967 |  0.7072 |      461.261  |      357.609  |      0.2545 |         0.0713 |       9 |   0.002  |            0.0156 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | warm-up              |        6 |  0.3219 |   0.1629 |   0.5529 |      0.0005 |   1      |               0.002  |            1      |  0.1192 |  0.7509 |      472.729  |      357.609  |      0.2791 |         0.0748 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | warm-up              |        6 | -0.0243 |  -0.0445 |  -0.0077 |      1      |   0.0005 |               1      |            0.0078 | -0.0432 | -0.0014 |      461.261  |      472.729  |     -0.0246 |         0.0097 |       9 |   0.002  |            0.0312 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.25 |        6 |  0.776  |   0.425  |   1.1582 |      0.0005 |   1      |               0.0039 |            0.998  |  0.3434 |  1.6396 |      335.086  |      188.677  |      0.5743 |         0.1106 |       9 |   0.002  |            0.0117 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.25 |        6 |  0.8084 |   0.3688 |   1.2711 |      0.0005 |   1      |               0.0078 |            0.9941 |  0.3197 |  1.7192 |      341.211  |      188.677  |      0.5925 |         0.1288 |       9 |   0.002  |            0.0234 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.25 |        6 | -0.018  |  -0.1068 |   0.0673 |      0.6327 |   0.3678 |               0.6035 |            0.3984 | -0.1068 |  0.1063 |      335.086  |      341.211  |     -0.0181 |         0.0469 |       9 |   0.3678 |            0.3984 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.5  |        6 |  1.6726 |   0.847  |   2.5874 |      0.0005 |   1      |               0.0039 |            0.998  |  0.6685 |  3.5765 |      270.503  |      101.212  |      0.9831 |         0.1734 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.5  |        6 |  1.6305 |   0.6599 |   2.7459 |      0.0005 |   1      |               0.0098 |            0.9922 |  0.4994 |  3.6699 |      266.233  |      101.212  |      0.9672 |         0.2045 |       9 |   0.002  |            0.0098 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.5  |        6 |  0.016  |  -0.1291 |   0.1686 |      0.4023 |   0.5982 |               0.418  |            0.584  | -0.122  |  0.2421 |      270.503  |      266.233  |      0.0159 |         0.0776 |       9 |   0.4023 |            0.418  |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 1    |        6 |  5.9015 |   2.6398 |  10.1574 |      0.0005 |   1      |               0.0039 |            0.998  |  1.789  | 14.8305 |      211.405  |       30.632  |      1.9317 |         0.2886 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 1    |        6 |  5.0903 |   1.9978 |   9.7511 |      0.0005 |   1      |               0.0078 |            0.9941 |  1.0309 | 13.9698 |      186.556  |       30.632  |      1.8067 |         0.3304 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 1    |        6 |  0.1332 |  -0.0929 |   0.4063 |      0.1409 |   0.8596 |               0.1934 |            0.8086 | -0.0702 |  0.5619 |      211.405  |      186.556  |      0.125  |         0.1134 |       9 |   0.1409 |            0.1934 |
| H7 Ensemble (gain) vs Ensemble           | B      | warm-up              |        6 | -0.0007 |  -0.0051 |   0.0036 |      0.6327 |   0.3678 |               0.6406 |            0.375  | -0.0058 |  0.0042 |      460.937  |      461.261  |     -0.0007 |         0.0022 |       9 |   0.3678 |            0.4648 |
| H8a Transfer vs Age (oldest first)       | B      | warm-up              |        6 |  0.0474 |  -0.0559 |   0.1806 |      0.2049 |   0.7956 |               0.2246 |            0.7773 | -0.0886 |  0.3346 |      374.547  |      357.609  |      0.0463 |         0.057  |       9 |   0.2049 |            0.2578 |
| H8b Transfer vs Ensemble                 | B      | warm-up              |        6 | -0.188  |  -0.249  |  -0.13   |      1      |   0.0005 |               1      |            0.002  | -0.2586 | -0.1238 |      374.547  |      461.261  |     -0.2082 |         0.0374 |       9 |   0.002  |            0.0078 |
| Ensemble vs Age (oldest first)           | B      | warm-up              |       12 |  0.1731 |   0.0174 |   0.3413 |      0.0165 |   0.984  |               0.0371 |            0.9648 | -0.0272 |  0.5421 |      654.445  |      557.892  |      0.1596 |         0.0707 |       9 |   0.023  |            0.0664 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | warm-up              |       12 |  0.1933 |   0.0367 |   0.3753 |      0.0095 |   0.991  |               0.0254 |            0.9766 | -0.0072 |  0.5251 |      665.716  |      557.892  |      0.1767 |         0.0733 |       9 |   0.0285 |            0.0762 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | warm-up              |       12 | -0.0169 |  -0.0553 |   0.0223 |      0.7906 |   0.2099 |               0.7754 |            0.2266 | -0.0604 |  0.0545 |      654.445  |      665.716  |     -0.0171 |         0.0204 |       9 |   0.4198 |            0.4531 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.25 |       12 |  0.467  |   0.2295 |   0.7193 |      0.0005 |   1      |               0.0059 |            0.9961 |  0.1408 |  1.1399 |      566.939  |      386.451  |      0.3832 |         0.0864 |       9 |   0.002  |            0.0117 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.25 |       12 |  0.4385 |   0.2103 |   0.68   |      0.0005 |   1      |               0.0078 |            0.9941 |  0.1191 |  1.0622 |      555.905  |      386.451  |      0.3636 |         0.0848 |       9 |   0.002  |            0.0234 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.25 |       12 |  0.0198 |  -0.0176 |   0.0582 |      0.1314 |   0.8691 |               0.1602 |            0.8418 | -0.02   |  0.0793 |      566.939  |      555.905  |      0.0197 |         0.0186 |       9 |   0.2629 |            0.3203 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.5  |       12 |  0.8747 |   0.4985 |   1.312  |      0.0005 |   1      |               0.002  |            1      |  0.3532 |  2.1067 |      510.362  |      272.233  |      0.6285 |         0.1124 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.5  |       12 |  0.8023 |   0.4261 |   1.221  |      0.0005 |   1      |               0.002  |            1      |  0.2793 |  1.9715 |      490.647  |      272.233  |      0.5891 |         0.1142 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.5  |       12 |  0.0402 |   0.0037 |   0.0849 |      0.013  |   0.9875 |               0.0371 |            0.9648 | -0.0007 |  0.1066 |      510.362  |      490.647  |      0.0394 |         0.0194 |       9 |   0.026  |            0.0742 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 1    |       12 |  2.1218 |   1.24   |   3.4099 |      0.0005 |   1      |               0.002  |            1      |  0.9473 |  6.0464 |      440.728  |      141.178  |      1.1384 |         0.1755 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 1    |       12 |  1.941  |   1.0449 |   3.2427 |      0.0005 |   1      |               0.002  |            1      |  0.7203 |  5.7612 |      415.206  |      141.178  |      1.0788 |         0.1892 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 1    |       12 |  0.0615 |   0.0186 |   0.1264 |      0.0015 |   0.999  |               0.0137 |            0.9883 |  0.004  |  0.175  |      440.728  |      415.206  |      0.0597 |         0.0258 |       9 |   0.003  |            0.0273 |
| H7 Ensemble (gain) vs Ensemble           | B      | warm-up              |       12 | -0.0162 |  -0.025  |  -0.0065 |      1      |   0.0005 |               0.9883 |            0.0156 | -0.0236 | -0.0022 |      643.844  |      654.445  |     -0.0163 |         0.005  |       9 |   0.002  |            0.0625 |
| H8a Transfer vs Age (oldest first)       | B      | warm-up              |       12 |  0.0825 |  -0.0047 |   0.1882 |      0.0335 |   0.967  |               0.0684 |            0.9336 | -0.0315 |  0.2339 |      603.915  |      557.892  |      0.0793 |         0.0452 |       9 |   0.08   |            0.2578 |
| H8b Transfer vs Ensemble                 | B      | warm-up              |       12 | -0.0772 |  -0.1503 |   0.0207 |      0.9485 |   0.052  |               0.9258 |            0.0762 | -0.2525 |  0.0657 |      603.915  |      654.445  |     -0.0804 |         0.0472 |       9 |   0.052  |            0.0762 |
| Ensemble vs Age (oldest first)           | B      | warm-up              |       24 |  0.0796 |   0.0131 |   0.1758 |      0.0115 |   0.989  |               0.0332 |            0.9688 |  0.0054 |  0.2739 |      896.782  |      830.625  |      0.0766 |         0.0384 |       9 |   0.023  |            0.0664 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | warm-up              |       24 |  0.0676 |   0.01   |   0.134  |      0.0105 |   0.99   |               0.0273 |            0.9746 | -0.0205 |  0.241  |      886.759  |      830.625  |      0.0654 |         0.0298 |       9 |   0.0285 |            0.0762 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | warm-up              |       24 |  0.0113 |  -0.0192 |   0.0563 |      0.2409 |   0.7596 |               0.2734 |            0.7285 | -0.0189 |  0.0739 |      896.782  |      886.759  |      0.0112 |         0.0188 |       9 |   0.4198 |            0.4531 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.25 |       24 |  0.2589 |   0.1874 |   0.3474 |      0.0005 |   1      |               0.002  |            1      |  0.1538 |  0.4586 |      818.09   |      649.858  |      0.2302 |         0.0328 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.25 |       24 |  0.2181 |   0.131  |   0.3078 |      0.0005 |   1      |               0.0039 |            0.998  |  0.0793 |  0.425  |      791.607  |      649.858  |      0.1973 |         0.0379 |       9 |   0.002  |            0.0156 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.25 |       24 |  0.0335 |   0.006  |   0.0754 |      0.0065 |   0.994  |               0.0215 |            0.9805 | -0.0015 |  0.096  |      818.09   |      791.607  |      0.0329 |         0.0171 |       9 |   0.0195 |            0.0645 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.5  |       24 |  0.4767 |   0.3706 |   0.5922 |      0.0005 |   1      |               0.002  |            1      |  0.3097 |  0.7281 |      755.671  |      511.721  |      0.3898 |         0.0396 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.5  |       24 |  0.4016 |   0.2563 |   0.547  |      0.0005 |   1      |               0.002  |            1      |  0.1843 |  0.6833 |      717.228  |      511.721  |      0.3376 |         0.0528 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.5  |       24 |  0.0536 |   0.0191 |   0.0986 |      0.0015 |   0.999  |               0.0117 |            0.9902 |  0.0114 |  0.1225 |      755.671  |      717.228  |      0.0522 |         0.0193 |       9 |   0.0045 |            0.0352 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 1    |       24 |  1.0496 |   0.7684 |   1.3593 |      0.0005 |   1      |               0.002  |            1      |  0.6497 |  1.6144 |      662.676  |      323.324  |      0.7176 |         0.0747 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 1    |       24 |  0.8869 |   0.5657 |   1.2449 |      0.0005 |   1      |               0.002  |            1      |  0.4213 |  1.5029 |      610.068  |      323.324  |      0.6349 |         0.0927 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 1    |       24 |  0.0862 |   0.0375 |   0.1508 |      0.0005 |   1      |               0.0078 |            0.9941 |  0.0294 |  0.1778 |      662.676  |      610.068  |      0.0827 |         0.0267 |       9 |   0.002  |            0.0234 |
| H7 Ensemble (gain) vs Ensemble           | B      | warm-up              |       24 |  0.0035 |  -0.0021 |   0.0096 |      0.1154 |   0.8851 |               0.127  |            0.875  | -0.0051 |  0.0154 |      899.948  |      896.782  |      0.0035 |         0.003  |       9 |   0.3463 |            0.3809 |
| H8a Transfer vs Age (oldest first)       | B      | warm-up              |       24 | -0.0344 |  -0.0616 |  -0.0022 |      0.9765 |   0.024  |               0.9375 |            0.0645 | -0.093  |  0.0801 |      802.032  |      830.625  |     -0.035  |         0.0161 |       9 |   0.08   |            0.2578 |
| H8b Transfer vs Ensemble                 | B      | warm-up              |       24 | -0.1057 |  -0.1747 |  -0.047  |      1      |   0.0005 |               0.9961 |            0.0059 | -0.2006 | -0.0433 |      802.032  |      896.782  |     -0.1117 |         0.0356 |       9 |   0.002  |            0.0176 |
| Ensemble vs Age (oldest first)           | B      | warm-up              |       48 |  0.0616 |   0.0163 |   0.1252 |      0.0015 |   0.999  |               0.0176 |            0.9844 | -0.0638 |  0.1707 |     1117.25   |     1052.41   |      0.0598 |         0.0253 |       9 |   0.0045 |            0.0527 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | warm-up              |       48 |  0.0386 |  -0.0107 |   0.0805 |      0.0645 |   0.936  |               0.0918 |            0.9102 | -0.1124 |  0.1289 |     1093.03   |     1052.41   |      0.0379 |         0.0224 |       9 |   0.0645 |            0.0918 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | warm-up              |       48 |  0.0222 |  -0.0032 |   0.0636 |      0.052  |   0.9485 |               0.0801 |            0.9219 |  0.0056 |  0.0877 |     1117.25   |     1093.03   |      0.0219 |         0.0166 |       9 |   0.1559 |            0.2402 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.25 |       48 |  0.1597 |   0.1129 |   0.2204 |      0.0005 |   1      |               0.0039 |            0.998  |  0.04   |  0.2498 |     1049.94   |      905.365  |      0.1482 |         0.0233 |       9 |   0.002  |            0.0117 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.25 |       48 |  0.115  |   0.0583 |   0.1588 |      0.001  |   0.9995 |               0.0137 |            0.9883 | -0.029  |  0.186  |     1009.52   |      905.365  |      0.1089 |         0.0235 |       9 |   0.002  |            0.0234 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.25 |       48 |  0.04   |   0.0148 |   0.0815 |      0.0005 |   1      |               0.0078 |            0.9941 |  0.0235 |  0.1029 |     1049.94   |     1009.52   |      0.0393 |         0.0162 |       9 |   0.002  |            0.0312 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 0.5  |       48 |  0.2706 |   0.2131 |   0.331  |      0.0005 |   1      |               0.002  |            1      |  0.1538 |  0.3447 |      991.791  |      780.568  |      0.2395 |         0.024  |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 0.5  |       48 |  0.201  |   0.1256 |   0.2571 |      0.0005 |   1      |               0.0039 |            0.998  |  0.0571 |  0.2606 |      937.441  |      780.568  |      0.1831 |         0.0285 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 0.5  |       48 |  0.058  |   0.0334 |   0.0988 |      0.0005 |   1      |               0.002  |            1      |  0.041  |  0.1184 |      991.791  |      937.441  |      0.0564 |         0.0156 |       9 |   0.002  |            0.0078 |
| Ensemble vs Age (oldest first)           | B      | alpha(e), gamma 1    |       48 |  0.5349 |   0.4266 |   0.6294 |      0.0005 |   1      |               0.002  |            1      |  0.3861 |  0.62   |      896.408  |      584.02   |      0.4285 |         0.0341 |       9 |   0.002  |            0.0078 |
| Kaplan–Meier (D×R) vs Age (oldest first) | B      | alpha(e), gamma 1    |       48 |  0.4043 |   0.2674 |   0.5153 |      0.0005 |   1      |               0.002  |            1      |  0.2157 |  0.4952 |      820.139  |      584.02   |      0.3395 |         0.0455 |       9 |   0.002  |            0.0078 |
| Ensemble vs Kaplan–Meier (D×R)           | B      | alpha(e), gamma 1    |       48 |  0.093  |   0.0698 |   0.1326 |      0.0005 |   1      |               0.002  |            1      |  0.073  |  0.1513 |      896.408  |      820.139  |      0.0889 |         0.0148 |       9 |   0.002  |            0.0078 |
| H7 Ensemble (gain) vs Ensemble           | B      | warm-up              |       48 | -0.002  |  -0.0061 |   0.002  |      0.8211 |   0.1794 |               0.7695 |            0.2324 | -0.0081 |  0.0032 |     1115.01   |     1117.25   |     -0.002  |         0.0021 |       9 |   0.3588 |            0.4648 |
| H8a Transfer vs Age (oldest first)       | B      | warm-up              |       48 | -0.0556 |  -0.0953 |  -0.0031 |      0.9805 |   0.02   |               0.9355 |            0.0664 | -0.0932 |  0.0447 |      993.866  |     1052.41   |     -0.0572 |         0.025  |       9 |   0.08   |            0.2578 |
| H8b Transfer vs Ensemble                 | B      | warm-up              |       48 | -0.1104 |  -0.1606 |  -0.0396 |      0.9985 |   0.002  |               0.9824 |            0.0195 | -0.2113 |  0.096  |      993.866  |     1117.25   |     -0.117  |         0.034  |       9 |   0.004  |            0.0391 |

## ro_h7

| line   |   budget |     rel |   ci90_lo |   ci90_hi |   p_tost |   p_holm |
|:-------|---------:|--------:|----------:|----------:|---------:|---------:|
| A      |        6 | -0.0075 |   -0.0328 |    0.0242 |   0.0765 |   0.0765 |
| A      |       12 |  0.0013 |   -0.0098 |    0.0128 |   0.0005 |   0.002  |
| A      |       24 | -0.007  |   -0.0133 |   -0.0008 |   0.0005 |   0.002  |
| A      |       48 | -0.0012 |   -0.0039 |    0.0009 |   0.0005 |   0.002  |
| B      |        6 | -0.0007 |   -0.0044 |    0.0029 |   0.0005 |   0.002  |
| B      |       12 | -0.0162 |   -0.0236 |   -0.0078 |   0.002  |   0.002  |
| B      |       24 |  0.0035 |   -0.0012 |    0.0084 |   0.0005 |   0.002  |
| B      |       48 | -0.002  |   -0.0055 |    0.0015 |   0.0005 |   0.002  |

## ro_h8

| line   |   budget | test   |     rel |      lo |      hi |      p |   p_holm |
|:-------|---------:|:-------|--------:|--------:|--------:|-------:|---------:|
| A      |        6 | H8a    | -0.0139 | -0.1127 |  0.1412 | 0.5992 |   1      |
| A      |        6 | H8b    | -0.1145 | -0.2329 | -0.0136 | 0.95   |   1      |
| A      |       12 | H8a    | -0.0974 | -0.1782 | -0.0428 | 1      |   1      |
| A      |       12 | H8b    | -0.189  | -0.2969 | -0.1195 | 1      |   1      |
| A      |       24 | H8a    | -0.1265 | -0.1876 | -0.0662 | 1      |   1      |
| A      |       24 | H8b    | -0.2126 | -0.2842 | -0.1413 | 1      |   1      |
| A      |       48 | H8a    | -0.0139 | -0.0264 | -0.0023 | 0.991  |   1      |
| A      |       48 | H8b    | -0.0622 | -0.0877 | -0.039  | 0.997  |   1      |
| B      |        6 | H8a    |  0.0474 | -0.0559 |  0.1806 | 0.2049 |   0.6147 |
| B      |        6 | H8b    | -0.188  | -0.249  | -0.13   | 1      |   1      |
| B      |       12 | H8a    |  0.0825 | -0.0047 |  0.1882 | 0.0335 |   0.1339 |
| B      |       12 | H8b    | -0.0772 | -0.1503 |  0.0207 | 0.8516 |   1      |
| B      |       24 | H8a    | -0.0344 | -0.0616 | -0.0022 | 0.9765 |   1      |
| B      |       24 | H8b    | -0.1057 | -0.1747 | -0.047  | 0.995  |   1      |
| B      |       48 | H8a    | -0.0556 | -0.0953 | -0.0031 | 0.9805 |   1      |
| B      |       48 | H8b    | -0.1104 | -0.1606 | -0.0396 | 0.985  |   1      |

## ro_h6

| line   |   budget |   draws |   mean |     q05 |    q50 |    q95 |   share_positive |
|:-------|---------:|--------:|-------:|--------:|-------:|-------:|-----------------:|
| A      |        6 |     200 | 0.1127 |  0.0764 | 0.1122 | 0.1488 |            1     |
| A      |       12 |     200 | 0.1132 |  0.0842 | 0.1141 | 0.139  |            1     |
| A      |       24 |     200 | 0.11   |  0.0856 | 0.1101 | 0.1311 |            1     |
| A      |       48 |     200 | 0.0518 |  0.0407 | 0.0529 | 0.0613 |            1     |
| B      |        6 |     200 | 0.3318 | -0.0574 | 0.3315 | 0.7324 |            0.885 |
| B      |       12 |     200 | 0.1764 |  0.0663 | 0.1769 | 0.2566 |            0.995 |
| B      |       24 |     200 | 0.0806 |  0.0475 | 0.0809 | 0.112  |            1     |
| B      |       48 |     200 | 0.0624 |  0.0475 | 0.0617 | 0.0786 |            1     |

## ro_pooled

| tag                                      | variant              |   budget |     rel |   rel_lo |   rel_hi |   p_greater |    Q_p |     I2 |
|:-----------------------------------------|:---------------------|---------:|--------:|---------:|---------:|------------:|-------:|-------:|
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.25 |        6 |  0.2681 |   0.1433 |   0.4067 |      0      | 0.0005 | 0.9167 |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.25 |       12 |  0.1989 |   0.1154 |   0.2885 |      0      | 0.0098 | 0.8502 |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.25 |       24 |  0.1679 |   0.1294 |   0.2077 |      0      | 0.0073 | 0.861  |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.25 |       48 |  0.0764 |   0.0574 |   0.0957 |      0      | 0.0005 | 0.917  |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.5  |        6 |  0.2803 |   0.1532 |   0.4213 |      0      | 0      | 0.9497 |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.5  |       12 |  0.2549 |   0.159  |   0.3587 |      0      | 0.0001 | 0.9317 |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.5  |       24 |  0.2306 |   0.1849 |   0.2781 |      0      | 0      | 0.964  |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 0.5  |       48 |  0.1051 |   0.0836 |   0.127  |      0      | 0      | 0.9757 |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 1    |        6 |  0.3373 |   0.2144 |   0.4727 |      0      | 0      | 0.97   |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 1    |       12 |  0.3441 |   0.2255 |   0.4741 |      0      | 0      | 0.9597 |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 1    |       24 |  0.2926 |   0.2309 |   0.3575 |      0      | 0      | 0.9767 |
| Ensemble vs Age (oldest first)           | alpha(e), gamma 1    |       48 |  0.1477 |   0.1193 |   0.1768 |      0      | 0      | 0.9882 |
| Ensemble vs Age (oldest first)           | warm-up              |        6 |  0.1907 |   0.0835 |   0.3084 |      0.0001 | 0.1282 | 0.5679 |
| Ensemble vs Age (oldest first)           | warm-up              |       12 |  0.1262 |   0.0548 |   0.2023 |      0.0002 | 0.5123 | 0      |
| Ensemble vs Age (oldest first)           | warm-up              |       24 |  0.1039 |   0.069  |   0.1399 |      0      | 0.5219 | 0      |
| Ensemble vs Age (oldest first)           | warm-up              |       48 |  0.0526 |   0.0355 |   0.07   |      0      | 0.7213 | 0      |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.25 |        6 | -0.0024 |  -0.0701 |   0.0703 |      0.5262 | 0.6017 | 0      |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.25 |       12 |  0.0358 |   0.0014 |   0.0713 |      0.0206 | 0.0268 | 0.7961 |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.25 |       24 |  0.0669 |   0.0388 |   0.0959 |      0      | 0.002  | 0.8951 |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.25 |       48 |  0.0367 |   0.0197 |   0.054  |      0      | 0.8182 | 0      |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.5  |        6 |  0.0116 |  -0.0823 |   0.1152 |      0.408  | 0.942  | 0      |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.5  |       12 |  0.0539 |   0.0174 |   0.0918 |      0.0018 | 0.0679 | 0.7    |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.5  |       24 |  0.0895 |   0.0581 |   0.1219 |      0      | 0.0062 | 0.8665 |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 0.5  |       48 |  0.046  |   0.0276 |   0.0648 |      0      | 0.369  | 0      |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 1    |        6 |  0.0409 |  -0.0889 |   0.1891 |      0.2778 | 0.3489 | 0      |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 1    |       12 |  0.0787 |   0.0303 |   0.1293 |      0.0006 | 0.1429 | 0.5341 |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 1    |       24 |  0.1336 |   0.0931 |   0.1757 |      0      | 0.0262 | 0.7976 |
| Ensemble vs Kaplan–Meier (D×R)           | alpha(e), gamma 1    |       48 |  0.0692 |   0.0482 |   0.0907 |      0      | 0.042  | 0.7581 |
| Ensemble vs Kaplan–Meier (D×R)           | warm-up              |        6 | -0.0221 |  -0.0401 |  -0.0037 |      0.9907 | 0.2409 | 0.2729 |
| Ensemble vs Kaplan–Meier (D×R)           | warm-up              |       12 |  0.0083 |  -0.0275 |   0.0455 |      0.3264 | 0.0033 | 0.8839 |
| Ensemble vs Kaplan–Meier (D×R)           | warm-up              |       24 |  0.0524 |   0.0235 |   0.0822 |      0.0002 | 0.0011 | 0.906  |
| Ensemble vs Kaplan–Meier (D×R)           | warm-up              |       48 |  0.0291 |   0.0137 |   0.0449 |      0.0001 | 0.6432 | 0      |
| H7 Ensemble (gain) vs Ensemble           | warm-up              |        6 | -0.0008 |  -0.0051 |   0.0035 |      0.6431 | 0.7062 | 0      |
| H7 Ensemble (gain) vs Ensemble           | warm-up              |       12 | -0.0104 |  -0.0182 |  -0.0025 |      0.9949 | 0.0402 | 0.7624 |
| H7 Ensemble (gain) vs Ensemble           | warm-up              |       24 | -0.0004 |  -0.005  |   0.0042 |      0.5666 | 0.0295 | 0.7889 |
| H7 Ensemble (gain) vs Ensemble           | warm-up              |       48 | -0.0014 |  -0.0038 |   0.0009 |      0.8866 | 0.7471 | 0      |
| H8a Transfer vs Age (oldest first)       | warm-up              |        6 |  0.0208 |  -0.062  |   0.1109 |      0.3169 | 0.49   | 0      |
| H8a Transfer vs Age (oldest first)       | warm-up              |       12 | -0.0223 |  -0.0781 |   0.0369 |      0.7736 | 0.0026 | 0.8893 |
| H8a Transfer vs Age (oldest first)       | warm-up              |       24 | -0.0513 |  -0.078  |  -0.0238 |      0.9998 | 0.0089 | 0.8537 |
| H8a Transfer vs Age (oldest first)       | warm-up              |       48 | -0.0165 |  -0.0283 |  -0.0046 |      0.9966 | 0.0933 | 0.6449 |
| H8b Transfer vs Ensemble                 | warm-up              |        6 | -0.1694 |  -0.2202 |  -0.1153 |      1      | 0.2366 | 0.286  |
| H8b Transfer vs Ensemble                 | warm-up              |       12 | -0.1226 |  -0.1837 |  -0.0568 |      0.9998 | 0.0874 | 0.6576 |
| H8b Transfer vs Ensemble                 | warm-up              |       24 | -0.1452 |  -0.1918 |  -0.0959 |      1      | 0.0331 | 0.7799 |
| H8b Transfer vs Ensemble                 | warm-up              |       48 | -0.0688 |  -0.0913 |  -0.0459 |      1      | 0.1482 | 0.5217 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.25 |        6 |  0.2363 |   0.1048 |   0.3835 |      0.0001 | 0.001  | 0.9081 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.25 |       12 |  0.0416 |  -0.0099 |   0.0959 |      0.0576 | 0.0001 | 0.9374 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.25 |       24 |  0.0238 |   0.0015 |   0.0465 |      0.018  | 0      | 0.9567 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.25 |       48 |  0.0335 |   0.0193 |   0.0478 |      0      | 0.0007 | 0.9128 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.5  |        6 |  0.2798 |   0.1236 |   0.4577 |      0.0001 | 0.0002 | 0.928  |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.5  |       12 |  0.0751 |   0.0123 |   0.1418 |      0.0092 | 0      | 0.9547 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.5  |       24 |  0.0342 |   0.009  |   0.0601 |      0.0038 | 0      | 0.9715 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 0.5  |       48 |  0.0438 |   0.0278 |   0.0601 |      0      | 0      | 0.9618 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 1    |        6 |  0.4086 |   0.202  |   0.6507 |      0      | 0      | 0.9521 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 1    |       12 |  0.1366 |   0.0491 |   0.2314 |      0.0009 | 0      | 0.9623 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 1    |       24 |  0.0519 |   0.02   |   0.0847 |      0.0006 | 0      | 0.9755 |
| Kaplan–Meier (D×R) vs Age (oldest first) | alpha(e), gamma 1    |       48 |  0.0583 |   0.038  |   0.0789 |      0      | 0      | 0.9754 |
| Kaplan–Meier (D×R) vs Age (oldest first) | warm-up              |        6 |  0.1645 |   0.0637 |   0.2749 |      0.0005 | 0.0312 | 0.7847 |
| Kaplan–Meier (D×R) vs Age (oldest first) | warm-up              |       12 |  0.0008 |  -0.0416 |   0.045  |      0.4857 | 0.0118 | 0.8422 |
| Kaplan–Meier (D×R) vs Age (oldest first) | warm-up              |       24 |  0.0064 |  -0.0134 |   0.0265 |      0.2655 | 0.0353 | 0.7742 |
| Kaplan–Meier (D×R) vs Age (oldest first) | warm-up              |       48 |  0.0213 |   0.0087 |   0.034  |      0.0004 | 0.4352 | 0      |
