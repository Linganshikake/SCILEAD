# GPT-5.6 Sol Partially / ColdStart evaluation

Status: **COMPLETE**.

Completion refers to all required official stages and hash-checked evaluations. Historical failed attempts remain in the accounting after an authorized recovery; completion does not require failed_or_unknown=0.

Scope: 43 papers, 335 recovered extraction rows, 295 Gold rows; the paper keys are reordered to the legacy order while each paper's records, fields and source documents are preserved.

Official normalization and evaluator algorithms are retained. Requests use gpt-5.6-sol, reasoning_effort=medium, max_completion_tokens=32768, stream=false, and omit seed/temperature. Method masking seed is integer 0; ColdStart order seeds are None, string '0', string '42'; PYTHONHASHSEED=0.

The GPT-4.1 history used 284 extraction rows and uncapped generation with temperature/seed=0. Cross-model differences therefore include extraction and generation-policy differences; they are not an isolated normalization-model comparison. Fully CS belongs to a separate agent and is not included in this report's completion status.

## Branch readiness

| Branch | Evaluation status | Last saved stage 1 | Last saved stage 2 | Issues |
| --- | --- | --- | --- | --- |
| partially | COMPLETE | COMPLETE | COMPLETE |  |
| cold_default | COMPLETE | COMPLETE | COMPLETE |  |
| cold_0 | COMPLETE | COMPLETE | COMPLETE |  |
| cold_42 | COMPLETE | COMPLETE | COMPLETE |  |

Saved stage statuses and usage are snapshots and may lag a resumed worker. Missing or incomplete evaluations receive no score; omitted tuple tables and dashes do not mean zero. Available completed stages are reported independently.

## Both-stage TDM / TDMR metrics

P/R are official per-paper macro means. F1 is 2PR/(P+R) using those means. The separate mean of per-paper F1 remains in the evaluation JSON.

Partially stage 1 is the primary tuple-extraction comparison after dynamic normalization. Stage 2 adds matching to the 27 Gold leaderboard triples and supplies leaderboard evaluation; its tuple scores are supplementary post-alignment diagnostics. Fully normalizes individual fields against the full predefined name sets, so stage-2 Partially scores must not be presented as the same naming scope as Fully. Even the primary stage-1 comparison has intentionally different candidate availability. ColdStart tuple metrics at both stages are diagnostic; its primary results are the three-order leaderboard scores. Both stages are retained without choosing the higher score.

### partially / stage1

Primary Partially tuple-extraction comparison, evaluated after its own dynamic name normalization.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.473603 | 0.524548 | 0.497775 | 0.289100 | 0.208676 | 0.983846 |
| Dataset IIM | 0.599859 | 0.608474 | 0.604136 | 0.482356 | 0.121780 | 0.975682 |
| Metric IIM | 0.966300 | 0.976744 | 0.971494 | 0.843065 | 0.128429 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.309301 | 0.310430 | 0.309864 | 0.110872 | 0.198993 | 0.958770 |
| TDMR Exact Match | 0.248313 | 0.284578 | 0.265212 | 0.089025 | 0.176186 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.4518900757884846, "Recall": 0.516922999481139, "F1": 0.48222382495680755}.

### partially / stage2

Additional matching to the 27 Gold leaderboard triples; tuple metrics are post-alignment diagnostics, not the primary Partially tuple comparison or the same naming scope as Fully.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.617014 | 0.791990 | 0.693637 | 0.408491 | 0.285146 | 0.983846 |
| Dataset IIM | 0.748696 | 0.794521 | 0.770928 | 0.579829 | 0.191099 | 0.975682 |
| Metric IIM | 0.966300 | 0.976744 | 0.971494 | 0.843065 | 0.128429 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.464986 | 0.470636 | 0.467794 | 0.219500 | 0.248293 | 0.958770 |
| TDMR Exact Match | 0.380742 | 0.420237 | 0.399516 | 0.169384 | 0.230132 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.4518900757884846, "Recall": 0.516922999481139, "F1": 0.48222382495680755}.

### cold_default / stage1

Dynamic open-vocabulary naming diagnostics; all three name sets started empty.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.168826 | 0.176357 | 0.172509 | 0.234914 | -0.062405 | 0.983846 |
| Dataset IIM | 0.348748 | 0.365497 | 0.356926 | 0.323767 | 0.033159 | 0.975682 |
| Metric IIM | 0.312755 | 0.331066 | 0.321651 | 0.492232 | -0.170581 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.007752 | 0.007752 | 0.007752 | 0.035610 | -0.027858 | 0.958770 |
| TDMR Exact Match | 0.007752 | 0.007752 | 0.007752 | 0.026157 | -0.018405 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.4518900757884846, "Recall": 0.516922999481139, "F1": 0.48222382495680755}.

### cold_default / stage2

Post-leaderboard-alignment tuple diagnostics; ColdStart primary results are the stage-2 leaderboard metrics across the three paper orders.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.499668 | 0.771964 | 0.606662 | 0.288119 | 0.318543 | 0.983846 |
| Dataset IIM | 0.631693 | 0.694955 | 0.661816 | 0.391414 | 0.270402 | 0.975682 |
| Metric IIM | 0.515542 | 0.669016 | 0.582337 | 0.507351 | 0.074986 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.352617 | 0.369701 | 0.360957 | 0.108934 | 0.252024 | 0.958770 |
| TDMR Exact Match | 0.276406 | 0.291611 | 0.283805 | 0.087867 | 0.195937 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.4518900757884846, "Recall": 0.516922999481139, "F1": 0.48222382495680755}.

### cold_0 / stage1

Dynamic open-vocabulary naming diagnostics; all three name sets started empty.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.232734 | 0.227390 | 0.230031 | 0.248168 | -0.018137 | 0.983846 |
| Dataset IIM | 0.339056 | 0.368422 | 0.353130 | 0.334578 | 0.018551 | 0.975682 |
| Metric IIM | 0.307357 | 0.318663 | 0.312908 | 0.496813 | -0.183905 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.011628 | 0.011628 | 0.011628 | 0.035610 | -0.023982 | 0.958770 |
| TDMR Exact Match | 0.011628 | 0.011628 | 0.011628 | 0.026157 | -0.014529 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.4518900757884846, "Recall": 0.516922999481139, "F1": 0.48222382495680755}.

### cold_0 / stage2

Post-leaderboard-alignment tuple diagnostics; ColdStart primary results are the stage-2 leaderboard metrics across the three paper orders.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.466621 | 0.710594 | 0.563327 | 0.289729 | 0.273598 | 0.983846 |
| Dataset IIM | 0.598746 | 0.667702 | 0.631347 | 0.389143 | 0.242204 | 0.975682 |
| Metric IIM | 0.505863 | 0.665739 | 0.574893 | 0.500833 | 0.074060 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.333096 | 0.345966 | 0.339409 | 0.090262 | 0.249147 | 0.958770 |
| TDMR Exact Match | 0.248600 | 0.261664 | 0.254965 | 0.069175 | 0.185790 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.4518900757884846, "Recall": 0.516922999481139, "F1": 0.48222382495680755}.

### cold_42 / stage1

Dynamic open-vocabulary naming diagnostics; all three name sets started empty.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.112403 | 0.116279 | 0.114308 | 0.231336 | -0.117028 | 0.983846 |
| Dataset IIM | 0.430918 | 0.439916 | 0.435371 | 0.315851 | 0.119520 | 0.975682 |
| Metric IIM | 0.340241 | 0.362250 | 0.350901 | 0.490297 | -0.139396 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.020672 | 0.023256 | 0.021888 | 0.029258 | -0.007370 | 0.958770 |
| TDMR Exact Match | 0.020672 | 0.023256 | 0.021888 | 0.026157 | -0.004269 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.45189007578848467, "Recall": 0.516922999481139, "F1": 0.4822238249568076}.

### cold_42 / stage2

Post-leaderboard-alignment tuple diagnostics; ColdStart primary results are the stage-2 leaderboard metrics across the three paper orders.

| Metric | P | R | F1 | GPT-4.1 same variant/stage F1 | Delta F1 | GPT-5.6 Fully reference F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Task IIM | 0.493522 | 0.704780 | 0.580529 | 0.297029 | 0.283500 | 0.983846 |
| Dataset IIM | 0.750492 | 0.791743 | 0.770566 | 0.404795 | 0.365770 | 0.975682 |
| Metric IIM | 0.579396 | 0.721564 | 0.642712 | 0.527376 | 0.115336 | 0.971494 |
| Result IIM | 0.777471 | 0.836690 | 0.805995 | 0.703841 | 0.102154 | 0.805995 |
| TDM Exact Match | 0.422263 | 0.435497 | 0.428778 | 0.132017 | 0.296761 | 0.958770 |
| TDMR Exact Match | 0.354919 | 0.368942 | 0.361795 | 0.116691 | 0.245104 | 0.779715 |

Strict Decimal Result diagnostic (auxiliary): {"Precision": 0.45189007578848467, "Recall": 0.516922999481139, "F1": 0.4822238249568076}.

## Leaderboards

LR is exact TDM hit before numeric conversion; finite nonempty rate is separate. PC/RC/RBO use unchanged official formulas. Official RBO compares deduplicated numeric scores. AO compares paper IDs, sorts ties by paper ID, and averages prefix overlap through min(rank-list lengths). Empty predictions remain zero in the full 27/10-board denominator; RC is not clipped. All 43 papers participate in both scopes.

### all27

| Run | LR | Finite nonempty | PC | RC | RBO (values) | AO (paper IDs) |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-4.1 partially | 0.481481 | 0.407407 | 0.133289 | 0.086067 | 0.110535 | 0.155802 |
| GPT-5.6 partially | 0.703704 | 0.703704 | 0.475617 | 0.419444 | 0.353951 | 0.417047 |
| GPT-4.1 cold_default | 0.444444 | 0.444444 | 0.109039 | 0.080026 | 0.101852 | 0.138889 |
| GPT-5.6 cold_default | 0.888889 | 0.888889 | 0.554982 | 0.443254 | 0.519990 | 0.623570 |
| GPT-4.1 cold_0 | 0.296296 | 0.296296 | 0.075573 | 0.043915 | 0.081728 | 0.118765 |
| GPT-5.6 cold_0 | 0.888889 | 0.888889 | 0.549427 | 0.416711 | 0.479599 | 0.603817 |
| GPT-4.1 cold_42 | 0.444444 | 0.444444 | 0.127866 | 0.118607 | 0.078961 | 0.083076 |
| GPT-5.6 cold_42 | 0.888889 | 0.888889 | 0.614594 | 0.516402 | 0.473064 | 0.562086 |
| GPT-5.6 Fully | 1.000000 | 1.000000 | 0.987302 | 0.819665 | 0.783107 | 0.947806 |

### masked10

| Run | LR | Finite nonempty | PC | RC | RBO (values) | AO (paper IDs) |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-4.1 partially | 0.400000 | 0.400000 | 0.139048 | 0.114048 | 0.120667 | 0.120667 |
| GPT-5.6 partially | 0.400000 | 0.400000 | 0.340000 | 0.290000 | 0.333333 | 0.366667 |
| GPT-4.1 cold_default | 0.200000 | 0.200000 | 0.078571 | 0.053571 | 0.075000 | 0.075000 |
| GPT-5.6 cold_default | 0.900000 | 0.900000 | 0.609286 | 0.494286 | 0.516667 | 0.588889 |
| GPT-4.1 cold_0 | 0.200000 | 0.200000 | 0.085714 | 0.053571 | 0.120667 | 0.120667 |
| GPT-5.6 cold_0 | 1.000000 | 1.000000 | 0.709286 | 0.554286 | 0.645833 | 0.739583 |
| GPT-4.1 cold_42 | 0.500000 | 0.500000 | 0.190238 | 0.165238 | 0.113194 | 0.124306 |
| GPT-5.6 cold_42 | 0.800000 | 0.800000 | 0.648571 | 0.594286 | 0.622996 | 0.675327 |
| GPT-5.6 Fully | 1.000000 | 1.000000 | 0.965714 | 0.796429 | 0.840329 | 0.977549 |

## ColdStart three-order aggregation

Each run is macro-averaged first. Main SD uses ddof=1; population SD uses ddof=0. The author's ddof is unconfirmed. Complete P/R/F1 statistics are saved in summary/cold_statistics.json.

### all27

| Metric | Mean | Sample SD | Population SD | GPT-4.1 mean | GPT-4.1 sample SD |
| --- | --- | --- | --- | --- | --- |
| LR | 0.888889 | 0.000000 | 0.000000 | 0.395062 | 0.085533 |
| Finite nonempty | 0.888889 | 0.000000 | 0.000000 | 0.395062 | 0.085533 |
| PC | 0.573001 | 0.036128 | 0.029498 | 0.104159 | 0.026486 |
| RC | 0.458789 | 0.051629 | 0.042155 | 0.080850 | 0.037352 |
| RBO (values) | 0.490884 | 0.025417 | 0.020753 | 0.087514 | 0.012494 |
| AO (paper IDs) | 0.596491 | 0.031390 | 0.025630 | 0.113577 | 0.028266 |

### masked10

| Metric | Mean | Sample SD | Population SD | GPT-4.1 mean | GPT-4.1 sample SD |
| --- | --- | --- | --- | --- | --- |
| LR | 0.900000 | 0.100000 | 0.081650 | 0.300000 | 0.173205 |
| Finite nonempty | 0.900000 | 0.100000 | 0.081650 | 0.300000 | 0.173205 |
| PC | 0.655714 | 0.050381 | 0.041136 | 0.118175 | 0.062511 |
| RC | 0.547619 | 0.050332 | 0.041096 | 0.090794 | 0.064471 |
| RBO (values) | 0.595165 | 0.068934 | 0.056285 | 0.102954 | 0.024495 |
| AO (paper IDs) | 0.667933 | 0.075619 | 0.061743 | 0.106657 | 0.027476 |

### stage1 F1 diagnostics

| Metric | Mean F1 | Sample SD | Population SD |
| --- | --- | --- | --- |
| Task IIM | 0.172283 | 0.057862 | 0.047244 |
| Dataset IIM | 0.381809 | 0.046425 | 0.037906 |
| Metric IIM | 0.328486 | 0.019898 | 0.016246 |
| Result IIM | 0.805995 | 0.000000 | 0.000000 |
| TDM Exact Match | 0.013756 | 0.007304 | 0.005964 |
| TDMR Exact Match | 0.013756 | 0.007304 | 0.005964 |

### stage2 F1 diagnostics

| Metric | Mean F1 | Sample SD | Population SD |
| --- | --- | --- | --- |
| Task IIM | 0.583506 | 0.021821 | 0.017816 |
| Dataset IIM | 0.687909 | 0.073186 | 0.059756 |
| Metric IIM | 0.599981 | 0.037193 | 0.030368 |
| Result IIM | 0.805995 | 0.000000 | 0.000000 |
| TDM Exact Match | 0.376382 | 0.046638 | 0.038080 |
| TDMR Exact Match | 0.300188 | 0.055267 | 0.045126 |

## Recorded API usage

| Branch | Stage | Physical attempts | Accepted responses | Historical failed/unknown | Unknown usage | Logical completed | Authorized extra attempts | Prompt | Completion | Total tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| partially | stage1 | 533 | 532 | 1 | 1 | 532 | 1 | 176854 | 9371 | 186225 |
| partially | stage2 | 286 | 286 | 0 | 0 | 286 | 0 | 151823 | 7557 | 159380 |
| cold_default | stage1 | 378 | 378 | 0 | 0 | 378 | — | 130026 | 7424 | 137450 |
| cold_default | stage2 | 334 | 334 | 0 | 0 | 334 | — | 177440 | 11134 | 188574 |
| cold_0 | stage1 | 407 | 406 | 1 | 1 | 406 | 1 | 128782 | 6953 | 135735 |
| cold_0 | stage2 | 335 | 335 | 0 | 0 | 335 | 0 | 177878 | 11140 | 189018 |
| cold_42 | stage1 | 445 | 445 | 0 | 0 | 445 | — | 144071 | 8917 | 152988 |
| cold_42 | stage2 | 334 | 332 | 2 | 2 | 332 | 2 | 176200 | 11120 | 187320 |

Physical attempts include original HTTP 524 failures or HTTP 403 quota refusals and their explicitly authorized retries. Each successful one-retry recovery contributes two physical attempts, one accepted response, and one completed logical request; the original failed attempt remains recorded after recovery or refill. Its missing token usage remains unknown, rather than being inferred as zero. Accepted parent pointers and saved-response replays are not additional network attempts. An absent counter is shown as missing; for older completed workers only, logical count may come from the completed-stage request cursor. These accounting fields do not change metric aggregation or require historical failures to be zero for completion.

These counters describe normalization calls already recorded by the parent runner. Evaluation/reporting makes zero API requests. Missing usage stays missing; charges are not inferred from tokens. Historical requests: Partially 340+204; ColdStart default 279+282, string-0 293+282, string-42 283+281 (2244 total).

## Reproducibility and limitations

Source paths and hashes, all branch metrics, comparisons and status are in summary/variant_comparison.json. Per-paper values and strict Result diagnostics are in each branch's evaluation directory. Leaderboard helper scripts are copied byte-for-byte; generated common.py binds the new predictions and the experiment's 335-row merged raw input. Helper LR_primary prose is a legacy label; this report explicitly uses LR_exact_tdm_hit.

The supplied 27 boards and the exact historical masked 10 are retained. New scores never alter prompts, candidate sets, parsing, Gold, or ranking formulas. A report marked complete refers only to completed and hash-checked evaluations, not an independent API replay validation.
