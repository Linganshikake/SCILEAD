# GPT-5.6 Sol paired semantic-alignment comparison

Status: **INCOMPLETE**. Primary stage2: **INCOMPLETE**. Diagnostic stage1: **INCOMPLETE**.
Generated UTC: 2026-10-28T15:47:43.608303+00:00

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
| partially_stage2 / variant | pending | pending | pending | pending | pending | pending |
| cold_default_stage2 / baseline | 49.9668 / 77.1964 / 60.6662 | 63.1693 / 69.4955 / 66.1816 | 51.5542 / 66.9016 / 58.2337 | 77.7471 / 83.6690 / 80.5995 | 35.2617 / 36.9701 / 36.0957 | 27.6406 / 29.1611 / 28.3805 |
| cold_default_stage2 / variant | pending | pending | pending | pending | pending | pending |
| cold_0_stage2 / baseline | 46.6621 / 71.0594 / 56.3327 | 59.8746 / 66.7702 / 63.1347 | 50.5863 / 66.5739 / 57.4893 | 77.7471 / 83.6690 / 80.5995 | 33.3096 / 34.5966 / 33.9409 | 24.8600 / 26.1664 / 25.4965 |
| cold_0_stage2 / variant | pending | pending | pending | pending | pending | pending |
| cold_42_stage2 / baseline | 49.3522 / 70.4780 / 58.0529 | 75.0492 / 79.1743 / 77.0566 | 57.9396 / 72.1564 / 64.2712 | 77.7471 / 83.6690 / 80.5995 | 42.2263 / 43.5497 / 42.8778 | 35.4919 / 36.8942 / 36.1795 |
| cold_42_stage2 / variant | pending | pending | pending | pending | pending | pending |

| Case / version | LR | finite nonempty | PC | RC | RBO | AO |
|---|---|---|---|---|---|---|
| partially_stage2 / baseline | 70.3704 | 70.3704 | 47.5617 | 41.9444 | 35.3951 | 41.7047 |
| partially_stage2 / variant | pending | pending | pending | pending | pending | pending |
| cold_default_stage2 / baseline | 88.8889 | 88.8889 | 55.4982 | 44.3254 | 51.9990 | 62.3570 |
| cold_default_stage2 / variant | pending | pending | pending | pending | pending | pending |
| cold_0_stage2 / baseline | 88.8889 | 88.8889 | 54.9427 | 41.6711 | 47.9599 | 60.3817 |
| cold_0_stage2 / variant | pending | pending | pending | pending | pending | pending |
| cold_42_stage2 / baseline | 88.8889 | 88.8889 | 61.4594 | 51.6402 | 47.3064 | 56.2086 |
| cold_42_stage2 / variant | pending | pending | pending | pending | pending | pending |

### stage2 three-Cold mean / sample SD

Exactly cold_default, cold_0 and cold_42. SD uses ddof=1; delta SD is computed from the three paired differences. These orders are not independent model replicates.

| Metric | Baseline mean / SD | Variant mean / SD | Paired delta mean / SD |
|---|---|---|---|
| Task IIM/Precision | 48.6604 / 1.7576 | pending (requires all three) | pending (requires all three) |
| Task IIM/Recall | 72.9113 / 3.7224 | pending (requires all three) | pending (requires all three) |
| Task IIM/F1 | 58.3506 / 2.1821 | pending (requires all three) | pending (requires all three) |
| Dataset IIM/Precision | 66.0310 / 7.9818 | pending (requires all three) | pending (requires all three) |
| Dataset IIM/Recall | 71.8133 / 6.5188 | pending (requires all three) | pending (requires all three) |
| Dataset IIM/F1 | 68.7909 / 7.3186 | pending (requires all three) | pending (requires all three) |
| Metric IIM/Precision | 53.3601 / 3.9954 | pending (requires all three) | pending (requires all three) |
| Metric IIM/Recall | 68.5440 / 3.1328 | pending (requires all three) | pending (requires all three) |
| Metric IIM/F1 | 59.9981 / 3.7193 | pending (requires all three) | pending (requires all three) |
| Result IIM/Precision | 77.7471 / 0.0000 | pending (requires all three) | pending (requires all three) |
| Result IIM/Recall | 83.6690 / 0.0000 | pending (requires all three) | pending (requires all three) |
| Result IIM/F1 | 80.5995 / 0.0000 | pending (requires all three) | pending (requires all three) |
| TDM Exact Match/Precision | 36.9325 / 4.6872 | pending (requires all three) | pending (requires all three) |
| TDM Exact Match/Recall | 38.3722 / 4.6383 | pending (requires all three) | pending (requires all three) |
| TDM Exact Match/F1 | 37.6382 / 4.6638 | pending (requires all three) | pending (requires all three) |
| TDMR Exact Match/Precision | 29.3308 / 5.5138 | pending (requires all three) | pending (requires all three) |
| TDMR Exact Match/Recall | 30.7406 / 5.5356 | pending (requires all three) | pending (requires all three) |
| TDMR Exact Match/F1 | 30.0188 / 5.5267 | pending (requires all three) | pending (requires all three) |
| LR_exact_tdm_hit | 88.8889 / 0.0000 | pending (requires all three) | pending (requires all three) |
| LR_nonempty_finite_result | 88.8889 / 0.0000 | pending (requires all three) | pending (requires all three) |
| PC_official | 57.3001 / 3.6128 | pending (requires all three) | pending (requires all three) |
| RC_official | 45.8789 / 5.1629 | pending (requires all three) | pending (requires all three) |
| RBO_official_value_rankings | 49.0884 / 2.5417 | pending (requires all three) | pending (requires all three) |
| AO_paper_id_macro_all_gold_boards | 59.6491 / 3.1390 | pending (requires all three) | pending (requires all three) |

## Diagnostic: stage1

Tuple cells: P / R / F1.

| Case / version | Task IIM | Dataset IIM | Metric IIM | Result IIM | TDM Exact Match | TDMR Exact Match |
|---|---|---|---|---|---|---|
| partially_stage1 / baseline | 47.3603 / 52.4548 / 49.7775 | 59.9859 / 60.8474 / 60.4136 | 96.6300 / 97.6744 / 97.1494 | 77.7471 / 83.6690 / 80.5995 | 30.9301 / 31.0430 / 30.9864 | 24.8313 / 28.4578 / 26.5212 |
| partially_stage1 / variant | pending | pending | pending | pending | pending | pending |
| cold_default_stage1 / baseline | 16.8826 / 17.6357 / 17.2509 | 34.8748 / 36.5497 / 35.6926 | 31.2755 / 33.1066 / 32.1651 | 77.7471 / 83.6690 / 80.5995 | 0.7752 / 0.7752 / 0.7752 | 0.7752 / 0.7752 / 0.7752 |
| cold_default_stage1 / variant | pending | pending | pending | pending | pending | pending |
| cold_0_stage1 / baseline | 23.2734 / 22.7390 / 23.0031 | 33.9056 / 36.8422 / 35.3130 | 30.7357 / 31.8663 / 31.2908 | 77.7471 / 83.6690 / 80.5995 | 1.1628 / 1.1628 / 1.1628 | 1.1628 / 1.1628 / 1.1628 |
| cold_0_stage1 / variant | pending | pending | pending | pending | pending | pending |
| cold_42_stage1 / baseline | 11.2403 / 11.6279 / 11.4308 | 43.0918 / 43.9916 / 43.5371 | 34.0241 / 36.2250 / 35.0901 | 77.7471 / 83.6690 / 80.5995 | 2.0672 / 2.3256 / 2.1888 | 2.0672 / 2.3256 / 2.1888 |
| cold_42_stage1 / variant | pending | pending | pending | pending | pending | pending |

| Case / version | LR | finite nonempty | PC | RC | RBO | AO |
|---|---|---|---|---|---|---|
| partially_stage1 / baseline | 55.5556 | 55.5556 | 30.7099 | 27.8704 | 16.5700 | 22.1965 |
| partially_stage1 / variant | pending | pending | pending | pending | pending | pending |
| cold_default_stage1 / baseline | 3.7037 | 3.7037 | 1.2346 | 1.2346 | 0.0000 | 0.0000 |
| cold_default_stage1 / variant | pending | pending | pending | pending | pending | pending |
| cold_0_stage1 / baseline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| cold_0_stage1 / variant | pending | pending | pending | pending | pending | pending |
| cold_42_stage1 / baseline | 3.7037 | 3.7037 | 3.7037 | 3.7037 | 3.7037 | 3.7037 |
| cold_42_stage1 / variant | pending | pending | pending | pending | pending | pending |

### stage1 three-Cold mean / sample SD

Exactly cold_default, cold_0 and cold_42. SD uses ddof=1; delta SD is computed from the three paired differences. These orders are not independent model replicates.

| Metric | Baseline mean / SD | Variant mean / SD | Paired delta mean / SD |
|---|---|---|---|
| Task IIM/Precision | 17.1321 / 6.0204 | pending (requires all three) | pending (requires all three) |
| Task IIM/Recall | 17.3342 / 5.5617 | pending (requires all three) | pending (requires all three) |
| Task IIM/F1 | 17.2283 / 5.7862 | pending (requires all three) | pending (requires all three) |
| Dataset IIM/Precision | 37.2907 / 5.0472 | pending (requires all three) | pending (requires all three) |
| Dataset IIM/Recall | 39.1278 / 4.2147 | pending (requires all three) | pending (requires all three) |
| Dataset IIM/F1 | 38.1809 / 4.6425 | pending (requires all three) | pending (requires all three) |
| Metric IIM/Precision | 32.0118 / 1.7635 | pending (requires all three) | pending (requires all three) |
| Metric IIM/Recall | 33.7327 / 2.2458 | pending (requires all three) | pending (requires all three) |
| Metric IIM/F1 | 32.8486 / 1.9898 | pending (requires all three) | pending (requires all three) |
| Result IIM/Precision | 77.7471 / 0.0000 | pending (requires all three) | pending (requires all three) |
| Result IIM/Recall | 83.6690 / 0.0000 | pending (requires all three) | pending (requires all three) |
| Result IIM/F1 | 80.5995 / 0.0000 | pending (requires all three) | pending (requires all three) |
| TDM Exact Match/Precision | 1.3351 / 0.6630 | pending (requires all three) | pending (requires all three) |
| TDM Exact Match/Recall | 1.4212 / 0.8068 | pending (requires all three) | pending (requires all three) |
| TDM Exact Match/F1 | 1.3756 / 0.7304 | pending (requires all three) | pending (requires all three) |
| TDMR Exact Match/Precision | 1.3351 / 0.6630 | pending (requires all three) | pending (requires all three) |
| TDMR Exact Match/Recall | 1.4212 / 0.8068 | pending (requires all three) | pending (requires all three) |
| TDMR Exact Match/F1 | 1.3756 / 0.7304 | pending (requires all three) | pending (requires all three) |
| LR_exact_tdm_hit | 2.4691 / 2.1383 | pending (requires all three) | pending (requires all three) |
| LR_nonempty_finite_result | 2.4691 / 2.1383 | pending (requires all three) | pending (requires all three) |
| PC_official | 1.6461 / 1.8858 | pending (requires all three) | pending (requires all three) |
| RC_official | 1.6461 / 1.8858 | pending (requires all three) | pending (requires all three) |
| RBO_official_value_rankings | 1.2346 / 2.1383 | pending (requires all three) | pending (requires all three) |
| AO_paper_id_macro_all_gold_boards | 1.2346 / 2.1383 | pending (requires all three) | pending (requires all three) |

## Per-paper changes and pending work

per_paper_differences.csv/JSON contains all six tuple metrics, all P/R/F1 and both stages for each of the 43 papers. comparison.csv and cold_statistics.csv retain full precision.

- prompt_improvement_variant / partially_stage1: PENDING; Stage summary status: 'PAUSED_FAILED_OR_UNCERTAIN'
- prompt_improvement_variant / partially_stage2: PENDING; Missing stage summary
- prompt_improvement_variant / cold_default_stage1: PENDING; Missing stage summary
- prompt_improvement_variant / cold_default_stage2: PENDING; Missing stage summary
- prompt_improvement_variant / cold_0_stage1: PENDING; Missing stage summary
- prompt_improvement_variant / cold_0_stage2: PENDING; Missing stage summary
- prompt_improvement_variant / cold_42_stage1: PENDING; Missing stage summary
- prompt_improvement_variant / cold_42_stage2: PENDING; Missing stage summary

DeepSeek results are excluded from paired Sol statistics (295 vs 335 predictions).
