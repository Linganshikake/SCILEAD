# GPT-5.6 Sol paired semantic-alignment comparison

Status: **COMPLETE**. Primary stage2: **COMPLETE**. Diagnostic stage1: **COMPLETE**.
Generated UTC: 2026-10-28T16:32:48.330871+00:00

Baseline: 20261024. Variant directory identifier: 20261028_semantic_alignment_v1 (not a claim about execution dates).
Each scored stage has 43 papers, 335 predictions, 295 Gold annotations and all 27 Gold boards. Extraction bytes match the Sol baseline.
Main-agent handoff: the same semantic-alignment Prompt additions as DeepSeek; Sol medium / 32768 generation settings unchanged. Runtime and Prompt audit remain with the main agent.

Tuple P/R are official per-paper macros; F1 is their harmonic mean. LR is exact TDM hit; finite nonempty is separate. Official RBO ranks deduplicated numeric values. AO ranks paper IDs with deterministic ties; empty boards count as zero in all27.
Tables show percentages; deltas are percentage points (variant minus baseline). Pending values are missing, never zero.

## Primary: stage2

Tuple cells: P / R / F1.

| Case / version | Task IIM | Dataset IIM | Metric IIM | Result IIM | TDM Exact Match | TDMR Exact Match |
|---|---|---|---|---|---|---|
| partially_stage2 / baseline | 61.7014 / 79.1990 / 69.3637 | 74.8696 / 79.4521 / 77.0928 | 96.6300 / 97.6744 / 97.1494 | 77.7471 / 83.6690 / 80.5995 | 46.4986 / 47.0636 / 46.7794 | 38.0742 / 42.0237 / 39.9516 |
| partially_stage2 / variant | 88.9329 / 96.7700 / 92.6861 | 89.6039 / 92.8125 / 91.1800 | 96.6300 / 94.5736 / 95.5908 | 77.7471 / 83.6690 / 80.5995 | 83.9635 / 82.0882 / 83.0153 | 63.9368 / 69.0692 / 66.4040 |
| partially_stage2 / delta | +27.2316 / +17.5711 / +23.3224 | +14.7343 / +13.3604 / +14.0872 | +0.0000 / -3.1008 / -1.5586 | +0.0000 / +0.0000 / +0.0000 | +37.4650 / +35.0246 / +36.2359 | +25.8626 / +27.0455 / +26.4524 |
| cold_default_stage2 / baseline | 49.9668 / 77.1964 / 60.6662 | 63.1693 / 69.4955 / 66.1816 | 51.5542 / 66.9016 / 58.2337 | 77.7471 / 83.6690 / 80.5995 | 35.2617 / 36.9701 / 36.0957 | 27.6406 / 29.1611 / 28.3805 |
| cold_default_stage2 / variant | 63.7791 / 83.9886 / 72.5018 | 77.2317 / 80.9573 / 79.0506 | 71.1693 / 83.7409 / 76.9450 | 77.7471 / 83.6690 / 80.5995 | 61.3038 / 60.0642 / 60.6776 | 48.6367 / 50.8172 / 49.7030 |
| cold_default_stage2 / delta | +13.8123 / +6.7922 / +11.8356 | +14.0623 / +11.4618 / +12.8690 | +19.6150 / +16.8393 / +18.7113 | +0.0000 / +0.0000 / +0.0000 | +26.0421 / +23.0940 / +24.5819 | +20.9961 / +21.6561 / +21.3226 |
| cold_0_stage2 / baseline | 46.6621 / 71.0594 / 56.3327 | 59.8746 / 66.7702 / 63.1347 | 50.5863 / 66.5739 / 57.4893 | 77.7471 / 83.6690 / 80.5995 | 33.3096 / 34.5966 / 33.9409 | 24.8600 / 26.1664 / 25.4965 |
| cold_0_stage2 / variant | 72.1512 / 88.1229 / 79.3412 | 77.5805 / 82.4689 / 79.9500 | 71.5153 / 83.7409 / 77.1468 | 77.7471 / 83.6690 / 80.5995 | 63.0572 / 61.8499 / 62.4477 | 50.3901 / 52.6029 / 51.4727 |
| cold_0_stage2 / delta | +25.4890 / +17.0635 / +23.0086 | +17.7059 / +15.6987 / +16.8154 | +20.9290 / +17.1670 / +19.6575 | +0.0000 / +0.0000 / +0.0000 | +29.7476 / +27.2532 / +28.5068 | +25.5301 / +26.4365 / +25.9762 |
| cold_42_stage2 / baseline | 49.3522 / 70.4780 / 58.0529 | 75.0492 / 79.1743 / 77.0566 | 57.9396 / 72.1564 / 64.2712 | 77.7471 / 83.6690 / 80.5995 | 42.2263 / 43.5497 / 42.8778 | 35.4919 / 36.8942 / 36.1795 |
| cold_42_stage2 / variant | 67.8488 / 87.8645 / 76.5703 | 77.4431 / 81.1687 / 79.2621 | 71.1296 / 83.5342 / 76.8344 | 77.7471 / 83.6690 / 80.5995 | 61.8391 / 60.8394 / 61.3351 | 49.2827 / 51.5924 / 50.4111 |
| cold_42_stage2 / delta | +18.4967 / +17.3865 / +18.5174 | +2.3939 / +1.9944 / +2.2055 | +13.1900 / +11.3777 / +12.5632 | +0.0000 / +0.0000 / +0.0000 | +19.6128 / +17.2896 / +18.4573 | +13.7907 / +14.6982 / +14.2316 |

| Case / version | LR | finite nonempty | PC | RC | RBO | AO |
|---|---|---|---|---|---|---|
| partially_stage2 / baseline | 70.3704 | 70.3704 | 47.5617 | 41.9444 | 35.3951 | 41.7047 |
| partially_stage2 / variant | 96.2963 | 96.2963 | 93.7919 | 72.9541 | 69.6821 | 89.8938 |
| partially_stage2 / delta | +25.9259 | +25.9259 | +46.2302 | +31.0097 | +34.2870 | +48.1891 |
| cold_default_stage2 / baseline | 88.8889 | 88.8889 | 55.4982 | 44.3254 | 51.9990 | 62.3570 |
| cold_default_stage2 / variant | 96.2963 | 96.2963 | 93.7919 | 72.9541 | 69.6821 | 89.8938 |
| cold_default_stage2 / delta | +7.4074 | +7.4074 | +38.2937 | +28.6287 | +17.6831 | +27.5368 |
| cold_0_stage2 / baseline | 88.8889 | 88.8889 | 54.9427 | 41.6711 | 47.9599 | 60.3817 |
| cold_0_stage2 / variant | 96.2963 | 96.2963 | 95.0265 | 74.1887 | 70.7674 | 90.7683 |
| cold_0_stage2 / delta | +7.4074 | +7.4074 | +40.0838 | +32.5176 | +22.8076 | +30.3866 |
| cold_42_stage2 / baseline | 88.8889 | 88.8889 | 61.4594 | 51.6402 | 47.3064 | 56.2086 |
| cold_42_stage2 / variant | 96.2963 | 96.2963 | 93.7919 | 73.5714 | 71.6111 | 91.2827 |
| cold_42_stage2 / delta | +7.4074 | +7.4074 | +32.3325 | +21.9312 | +24.3046 | +35.0741 |

### stage2 three-Cold mean / sample SD

Exactly cold_default, cold_0 and cold_42. SD uses ddof=1; delta SD is computed from the three paired differences. These orders are not independent model replicates.

| Metric | Baseline mean / SD | Variant mean / SD | Paired delta mean / SD |
|---|---|---|---|
| Task IIM/Precision | 48.6604 / 1.7576 | 67.9264 / 4.1866 | 19.2660 / 5.8763 |
| Task IIM/Recall | 72.9113 / 3.7224 | 86.6587 / 2.3160 | 13.7474 / 6.0256 |
| Task IIM/F1 | 58.3506 / 2.1821 | 76.1378 / 3.4401 | 17.7872 / 5.6222 |
| Dataset IIM/Precision | 66.0310 / 7.9818 | 77.4184 / 0.1757 | 11.3874 / 7.9988 |
| Dataset IIM/Recall | 71.8133 / 6.5188 | 81.5316 / 0.8186 | 9.7183 / 7.0165 |
| Dataset IIM/F1 | 68.7909 / 7.3186 | 79.4209 / 0.4703 | 10.6300 / 7.5579 |
| Metric IIM/Precision | 53.3601 / 3.9954 | 71.2714 / 0.2122 | 17.9113 / 4.1412 |
| Metric IIM/Recall | 68.5440 / 3.1328 | 83.6720 / 0.1193 | 15.1280 / 3.2520 |
| Metric IIM/F1 | 59.9981 / 3.7193 | 76.9754 / 0.1584 | 16.9773 / 3.8519 |
| Result IIM/Precision | 77.7471 / 0.0000 | 77.7471 / 0.0000 | 0.0000 / 0.0000 |
| Result IIM/Recall | 83.6690 / 0.0000 | 83.6690 / 0.0000 | 0.0000 / 0.0000 |
| Result IIM/F1 | 80.5995 / 0.0000 | 80.5995 / 0.0000 | 0.0000 / 0.0000 |
| TDM Exact Match/Precision | 36.9325 / 4.6872 | 62.0667 / 0.8986 | 25.1341 / 5.1280 |
| TDM Exact Match/Recall | 38.3722 / 4.6383 | 60.9178 / 0.8954 | 22.5456 / 5.0044 |
| TDM Exact Match/F1 | 37.6382 / 4.6638 | 61.4868 / 0.8947 | 23.8487 / 5.0647 |
| TDMR Exact Match/Precision | 29.3308 / 5.5138 | 49.4365 / 0.8868 | 20.1056 / 5.9201 |
| TDMR Exact Match/Recall | 30.7406 / 5.5356 | 51.6708 / 0.8954 | 20.9303 / 5.9027 |
| TDMR Exact Match/F1 | 30.0188 / 5.5267 | 50.5289 / 0.8907 | 20.5101 / 5.9143 |
| LR_exact_tdm_hit | 88.8889 / 0.0000 | 96.2963 / 0.0000 | 7.4074 / 0.0000 |
| LR_nonempty_finite_result | 88.8889 / 0.0000 | 96.2963 / 0.0000 | 7.4074 / 0.0000 |
| PC_official | 57.3001 / 3.6128 | 94.2034 / 0.7128 | 36.9033 / 4.0584 |
| RC_official | 45.8789 / 5.1629 | 73.5714 / 0.6173 | 27.6925 / 5.3549 |
| RBO_official_value_rankings | 49.0884 / 2.5417 | 70.6869 / 0.9670 | 21.5984 / 3.4724 |
| AO_paper_id_macro_all_gold_boards | 59.6491 / 3.1390 | 90.6482 / 0.7022 | 30.9991 / 3.8058 |

## Diagnostic: stage1

Tuple cells: P / R / F1.

| Case / version | Task IIM | Dataset IIM | Metric IIM | Result IIM | TDM Exact Match | TDMR Exact Match |
|---|---|---|---|---|---|---|
| partially_stage1 / baseline | 47.3603 / 52.4548 / 49.7775 | 59.9859 / 60.8474 / 60.4136 | 96.6300 / 97.6744 / 97.1494 | 77.7471 / 83.6690 / 80.5995 | 30.9301 / 31.0430 / 30.9864 | 24.8313 / 28.4578 / 26.5212 |
| partially_stage1 / variant | 67.0337 / 70.4134 / 68.6820 | 58.0498 / 60.8292 / 59.4070 | 96.6300 / 97.6744 / 97.1494 | 77.7471 / 83.6690 / 80.5995 | 45.1880 / 47.2579 / 46.1998 | 34.0531 / 39.9975 / 36.7867 |
| partially_stage1 / delta | +19.6734 / +17.9587 / +18.9045 | -1.9361 / -0.0182 / -1.0066 | +0.0000 / +0.0000 / +0.0000 | +0.0000 / +0.0000 / +0.0000 | +14.2579 / +16.2149 / +15.2133 | +9.2218 / +11.5396 / +10.2655 |
| cold_default_stage1 / baseline | 16.8826 / 17.6357 / 17.2509 | 34.8748 / 36.5497 / 35.6926 | 31.2755 / 33.1066 / 32.1651 | 77.7471 / 83.6690 / 80.5995 | 0.7752 / 0.7752 / 0.7752 | 0.7752 / 0.7752 / 0.7752 |
| cold_default_stage1 / variant | 16.4535 / 19.5183 / 17.8553 | 35.5944 / 37.6174 / 36.5780 | 31.1233 / 31.0911 / 31.1072 | 77.7471 / 83.6690 / 80.5995 | 0.0000 / 0.0000 / 0.0000 | 0.0000 / 0.0000 / 0.0000 |
| cold_default_stage1 / delta | -0.4291 / +1.8826 / +0.6044 | +0.7197 / +1.0677 / +0.8854 | -0.1523 / -2.0155 / -1.0579 | +0.0000 / +0.0000 / +0.0000 | -0.7752 / -0.7752 / -0.7752 | -0.7752 / -0.7752 / -0.7752 |
| cold_0_stage1 / baseline | 23.2734 / 22.7390 / 23.0031 | 33.9056 / 36.8422 / 35.3130 | 30.7357 / 31.8663 / 31.2908 | 77.7471 / 83.6690 / 80.5995 | 1.1628 / 1.1628 / 1.1628 | 1.1628 / 1.1628 / 1.1628 |
| cold_0_stage1 / variant | 23.8548 / 24.2894 / 24.0702 | 33.9278 / 36.9197 / 35.3606 | 31.5275 / 31.0911 / 31.3078 | 77.7471 / 83.6690 / 80.5995 | 1.1628 / 1.1628 / 1.1628 | 1.1628 / 1.1628 / 1.1628 |
| cold_0_stage1 / delta | +0.5814 / +1.5504 / +1.0670 | +0.0221 / +0.0775 / +0.0476 | +0.7918 / -0.7752 / +0.0170 | +0.0000 / +0.0000 / +0.0000 | +0.0000 / +0.0000 / +0.0000 | +0.0000 / +0.0000 / +0.0000 |
| cold_42_stage1 / baseline | 11.2403 / 11.6279 / 11.4308 | 43.0918 / 43.9916 / 43.5371 | 34.0241 / 36.2250 / 35.0901 | 77.7471 / 83.6690 / 80.5995 | 2.0672 / 2.3256 / 2.1888 | 2.0672 / 2.3256 / 2.1888 |
| cold_42_stage1 / variant | 10.4651 / 10.8527 / 10.6554 | 39.7261 / 42.0536 / 40.8567 | 31.6614 / 32.5899 / 32.1189 | 77.7471 / 83.6690 / 80.5995 | 2.0672 / 2.3256 / 2.1888 | 2.0672 / 2.3256 / 2.1888 |
| cold_42_stage1 / delta | -0.7752 / -0.7752 / -0.7754 | -3.3657 / -1.9380 / -2.6803 | -2.3627 / -3.6352 / -2.9712 | +0.0000 / +0.0000 / +0.0000 | +0.0000 / +0.0000 / +0.0000 | +0.0000 / +0.0000 / +0.0000 |

| Case / version | LR | finite nonempty | PC | RC | RBO | AO |
|---|---|---|---|---|---|---|
| partially_stage1 / baseline | 55.5556 | 55.5556 | 30.7099 | 27.8704 | 16.5700 | 22.1965 |
| partially_stage1 / variant | 59.2593 | 59.2593 | 53.0864 | 43.2099 | 38.5855 | 50.4321 |
| partially_stage1 / delta | +3.7037 | +3.7037 | +22.3765 | +15.3395 | +22.0156 | +28.2356 |
| cold_default_stage1 / baseline | 3.7037 | 3.7037 | 1.2346 | 1.2346 | 0.0000 | 0.0000 |
| cold_default_stage1 / variant | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| cold_default_stage1 / delta | -3.7037 | -3.7037 | -1.2346 | -1.2346 | +0.0000 | +0.0000 |
| cold_0_stage1 / baseline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| cold_0_stage1 / variant | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| cold_0_stage1 / delta | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| cold_42_stage1 / baseline | 3.7037 | 3.7037 | 3.7037 | 3.7037 | 3.7037 | 3.7037 |
| cold_42_stage1 / variant | 3.7037 | 3.7037 | 3.7037 | 3.7037 | 3.7037 | 3.7037 |
| cold_42_stage1 / delta | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |

### stage1 three-Cold mean / sample SD

Exactly cold_default, cold_0 and cold_42. SD uses ddof=1; delta SD is computed from the three paired differences. These orders are not independent model replicates.

| Metric | Baseline mean / SD | Variant mean / SD | Paired delta mean / SD |
|---|---|---|---|
| Task IIM/Precision | 17.1321 / 6.0204 | 16.9245 / 6.7073 | -0.2076 / 0.7049 |
| Task IIM/Recall | 17.3342 / 5.5617 | 18.2201 / 6.8118 | 0.8859 / 1.4481 |
| Task IIM/F1 | 17.2283 / 5.7862 | 17.5270 / 6.7134 | 0.2987 / 0.9585 |
| Dataset IIM/Precision | 37.2907 / 5.0472 | 36.4161 / 2.9852 | -0.8746 / 2.1853 |
| Dataset IIM/Recall | 39.1278 / 4.2147 | 38.8636 / 2.7846 | -0.2643 / 1.5317 |
| Dataset IIM/F1 | 38.1809 / 4.6425 | 37.5984 / 2.8867 | -0.5824 / 1.8645 |
| Metric IIM/Precision | 32.0118 / 1.7635 | 31.4374 / 0.2801 | -0.5744 / 1.6191 |
| Metric IIM/Recall | 33.7327 / 2.2458 | 31.5907 / 0.8653 | -2.1420 / 1.4342 |
| Metric IIM/F1 | 32.8486 / 1.9898 | 31.5113 / 0.5357 | -1.3373 / 1.5136 |
| Result IIM/Precision | 77.7471 / 0.0000 | 77.7471 / 0.0000 | 0.0000 / 0.0000 |
| Result IIM/Recall | 83.6690 / 0.0000 | 83.6690 / 0.0000 | 0.0000 / 0.0000 |
| Result IIM/F1 | 80.5995 / 0.0000 | 80.5995 / 0.0000 | 0.0000 / 0.0000 |
| TDM Exact Match/Precision | 1.3351 / 0.6630 | 1.0767 / 1.0363 | -0.2584 / 0.4476 |
| TDM Exact Match/Recall | 1.4212 / 0.8068 | 1.1628 / 1.1628 | -0.2584 / 0.4476 |
| TDM Exact Match/F1 | 1.3756 / 0.7304 | 1.1172 / 1.0951 | -0.2584 / 0.4476 |
| TDMR Exact Match/Precision | 1.3351 / 0.6630 | 1.0767 / 1.0363 | -0.2584 / 0.4476 |
| TDMR Exact Match/Recall | 1.4212 / 0.8068 | 1.1628 / 1.1628 | -0.2584 / 0.4476 |
| TDMR Exact Match/F1 | 1.3756 / 0.7304 | 1.1172 / 1.0951 | -0.2584 / 0.4476 |
| LR_exact_tdm_hit | 2.4691 / 2.1383 | 1.2346 / 2.1383 | -1.2346 / 2.1383 |
| LR_nonempty_finite_result | 2.4691 / 2.1383 | 1.2346 / 2.1383 | -1.2346 / 2.1383 |
| PC_official | 1.6461 / 1.8858 | 1.2346 / 2.1383 | -0.4115 / 0.7128 |
| RC_official | 1.6461 / 1.8858 | 1.2346 / 2.1383 | -0.4115 / 0.7128 |
| RBO_official_value_rankings | 1.2346 / 2.1383 | 1.2346 / 2.1383 | 0.0000 / 0.0000 |
| AO_paper_id_macro_all_gold_boards | 1.2346 / 2.1383 | 1.2346 / 2.1383 | 0.0000 / 0.0000 |

## Per-paper changes and pending work

per_paper_differences.csv/JSON contains all six tuple metrics, all P/R/F1 and both stages for each of the 43 papers. comparison.csv and cold_statistics.csv retain full precision.

All eight paired stages verified.

DeepSeek results are excluded from paired Sol statistics (295 vs 335 predictions).
