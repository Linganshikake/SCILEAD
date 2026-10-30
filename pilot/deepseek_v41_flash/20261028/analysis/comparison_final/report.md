# Offline experiment comparison

Status: **COMPLETE**. Completion covers ten 43-paper/295-Gold evaluations and their all27 boards. Masked10 is optional and separately labeled. Evaluation report only; not an audit of API generation, replay, usage, or normalization semantics.

Partially **stage2 is the primary result**; stage1 is retained as a diagnostic. Both stages and source files remain in comparison.json and CSV. This supersedes the 24-Oct report convention.

Original repository HEAD: `8bf74b0a830feb7035c6166dce3394dc344ae532`. Frozen outer/archive commit: `b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25`. These are distinct provenance fields.

Local scores below are percentages. Tuple cells show P / R / F1; macro F1 uses macro P/R. Partial rows use only the displayed observed-paper denominator. No full-scope improvement claim is made for partial rows.

## Local tuple metrics

| Model / case | Status; papers; Gold; predictions | Task IIM | Dataset IIM | Metric IIM | Result IIM | TDM Exact Match | TDMR Exact Match | Strict Result |
|---|---|---|---|---|---|---|---|---|
| GPT-4.1 / fully (primary) | COMPLETE; 43/43; 295/295; 284 | 96.05 / 97.34 / 96.69 | 82.01 / 78.22 / 80.07 | 87.11 / 83.61 / 85.32 | 69.02 / 71.81 / 70.38 | 63.96 / 58.70 / 61.22 | 41.18 / 43.18 / 42.16 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / fully_cs (primary) | COMPLETE; 43/43; 295/295; 284 | 97.21 / 97.34 / 97.28 | 89.22 / 86.41 / 87.80 | 87.32 / 84.52 / 85.90 | 69.02 / 71.81 / 70.38 | 73.21 / 69.51 / 71.31 | 53.26 / 55.30 / 54.26 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / partially_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 284 | 26.82 / 31.36 / 28.91 | 47.97 / 48.51 / 48.24 | 86.68 / 82.06 / 84.31 | 69.02 / 71.81 / 70.38 | 11.40 / 10.79 / 11.09 | 8.60 / 9.22 / 8.90 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / partially_stage2 (primary) | COMPLETE; 43/43; 295/295; 284 | 35.23 / 48.61 / 40.85 | 57.62 / 58.35 / 57.98 | 86.68 / 82.06 / 84.31 | 69.02 / 71.81 / 70.38 | 22.10 / 21.80 / 21.95 | 16.28 / 17.65 / 16.94 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / cold_default_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 284 | 22.10 / 25.06 / 23.49 | 32.60 / 32.16 / 32.38 | 49.36 / 49.08 / 49.22 | 69.02 / 71.81 / 70.38 | 3.68 / 3.45 / 3.56 | 2.76 / 2.48 / 2.62 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / cold_default_stage2 (primary) | COMPLETE; 43/43; 295/295; 284 | 26.17 / 32.04 / 28.81 | 39.26 / 39.02 / 39.14 | 50.68 / 50.79 / 50.74 | 69.02 / 71.81 / 70.38 | 11.12 / 10.68 / 10.89 | 9.04 / 8.54 / 8.79 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / cold_0_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 284 | 22.69 / 27.39 / 24.82 | 33.52 / 33.40 / 33.46 | 50.29 / 49.08 / 49.68 | 69.02 / 71.81 / 70.38 | 3.68 / 3.45 / 3.56 | 2.76 / 2.48 / 2.62 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / cold_0_stage2 (primary) | COMPLETE; 43/43; 295/295; 284 | 26.06 / 32.62 / 28.97 | 39.04 / 38.79 / 38.91 | 50.58 / 49.60 / 50.08 | 69.02 / 71.81 / 70.38 | 9.30 / 8.77 / 9.03 | 7.22 / 6.64 / 6.92 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / cold_42_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 284 | 21.77 / 24.68 / 23.13 | 31.79 / 31.38 / 31.59 | 48.98 / 49.08 / 49.03 | 69.02 / 71.81 / 70.38 | 3.10 / 2.77 / 2.93 | 2.76 / 2.48 / 2.62 | 57.97 / 59.40 / 58.68 |
| GPT-4.1 / cold_42_stage2 (primary) | COMPLETE; 43/43; 295/295; 284 | 26.50 / 33.79 / 29.70 | 40.78 / 40.18 / 40.48 | 51.92 / 53.58 / 52.74 | 69.02 / 71.81 / 70.38 | 13.69 / 12.75 / 13.20 | 12.07 / 11.29 / 11.67 | 57.97 / 59.40 / 58.68 |
| Sol / fully (primary) | COMPLETE; 43/43; 295/295; 335 | 98.19 / 98.58 / 98.38 | 97.42 / 97.71 / 97.57 | 96.63 / 97.67 / 97.15 | 77.75 / 83.67 / 80.60 | 95.53 / 96.23 / 95.88 | 75.11 / 81.06 / 77.97 | 45.19 / 51.69 / 48.22 |
| Sol / fully_cs (primary) | COMPLETE; 43/43; 295/295; 335 | 96.22 / 98.84 / 97.51 | 91.28 / 90.90 / 91.09 | 88.34 / 88.41 / 88.37 | 77.75 / 83.67 / 80.60 | 81.38 / 79.84 / 80.60 | 62.88 / 67.42 / 65.07 | 45.19 / 51.69 / 48.22 |
| Sol / partially_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 335 | 47.36 / 52.45 / 49.78 | 59.99 / 60.85 / 60.41 | 96.63 / 97.67 / 97.15 | 77.75 / 83.67 / 80.60 | 30.93 / 31.04 / 30.99 | 24.83 / 28.46 / 26.52 | 45.19 / 51.69 / 48.22 |
| Sol / partially_stage2 (primary) | COMPLETE; 43/43; 295/295; 335 | 61.70 / 79.20 / 69.36 | 74.87 / 79.45 / 77.09 | 96.63 / 97.67 / 97.15 | 77.75 / 83.67 / 80.60 | 46.50 / 47.06 / 46.78 | 38.07 / 42.02 / 39.95 | 45.19 / 51.69 / 48.22 |
| Sol / cold_default_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 335 | 16.88 / 17.64 / 17.25 | 34.87 / 36.55 / 35.69 | 31.28 / 33.11 / 32.17 | 77.75 / 83.67 / 80.60 | 0.78 / 0.78 / 0.78 | 0.78 / 0.78 / 0.78 | 45.19 / 51.69 / 48.22 |
| Sol / cold_default_stage2 (primary) | COMPLETE; 43/43; 295/295; 335 | 49.97 / 77.20 / 60.67 | 63.17 / 69.50 / 66.18 | 51.55 / 66.90 / 58.23 | 77.75 / 83.67 / 80.60 | 35.26 / 36.97 / 36.10 | 27.64 / 29.16 / 28.38 | 45.19 / 51.69 / 48.22 |
| Sol / cold_0_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 335 | 23.27 / 22.74 / 23.00 | 33.91 / 36.84 / 35.31 | 30.74 / 31.87 / 31.29 | 77.75 / 83.67 / 80.60 | 1.16 / 1.16 / 1.16 | 1.16 / 1.16 / 1.16 | 45.19 / 51.69 / 48.22 |
| Sol / cold_0_stage2 (primary) | COMPLETE; 43/43; 295/295; 335 | 46.66 / 71.06 / 56.33 | 59.87 / 66.77 / 63.13 | 50.59 / 66.57 / 57.49 | 77.75 / 83.67 / 80.60 | 33.31 / 34.60 / 33.94 | 24.86 / 26.17 / 25.50 | 45.19 / 51.69 / 48.22 |
| Sol / cold_42_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 335 | 11.24 / 11.63 / 11.43 | 43.09 / 43.99 / 43.54 | 34.02 / 36.23 / 35.09 | 77.75 / 83.67 / 80.60 | 2.07 / 2.33 / 2.19 | 2.07 / 2.33 / 2.19 | 45.19 / 51.69 / 48.22 |
| Sol / cold_42_stage2 (primary) | COMPLETE; 43/43; 295/295; 335 | 49.35 / 70.48 / 58.05 | 75.05 / 79.17 / 77.06 | 57.94 / 72.16 / 64.27 | 77.75 / 83.67 / 80.60 | 42.23 / 43.55 / 42.88 | 35.49 / 36.89 / 36.18 | 45.19 / 51.69 / 48.22 |
| DeepSeek / fully (primary) | COMPLETE; 43/43; 295/295; 295 | 97.97 / 97.60 / 97.78 | 96.23 / 96.35 / 96.29 | 95.21 / 95.14 / 95.18 | 81.63 / 80.89 / 81.26 | 93.63 / 90.68 / 92.13 | 76.38 / 75.13 / 75.75 | 72.33 / 73.13 / 72.73 |
| DeepSeek / fully_cs (primary) | COMPLETE; 43/43; 295/295; 295 | 97.92 / 98.38 / 98.15 | 88.15 / 87.74 / 87.95 | 89.46 / 86.33 / 87.87 | 81.63 / 80.89 / 81.26 | 78.43 / 74.16 / 76.23 | 60.72 / 58.94 / 59.82 | 72.33 / 73.13 / 72.73 |
| DeepSeek / partially_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 295 | 37.15 / 39.38 / 38.23 | 45.95 / 48.16 / 47.03 | 94.98 / 95.14 / 95.06 | 81.63 / 80.89 / 81.26 | 19.38 / 18.06 / 18.70 | 15.16 / 13.75 / 14.42 | 72.33 / 73.13 / 72.73 |
| DeepSeek / partially_stage2 (primary) | COMPLETE; 43/43; 295/295; 295 | 41.02 / 47.13 / 43.87 | 51.84 / 54.83 / 53.29 | 94.98 / 95.14 / 95.06 | 81.63 / 80.89 / 81.26 | 25.25 / 23.82 / 24.51 | 20.92 / 19.51 / 20.19 | 72.33 / 73.13 / 72.73 |
| DeepSeek / cold_default_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 295 | 29.59 / 30.84 / 30.21 | 33.39 / 35.64 / 34.48 | 42.53 / 41.22 / 41.86 | 81.63 / 80.89 / 81.26 | 6.14 / 4.81 / 5.40 | 5.56 / 4.13 / 4.74 | 72.33 / 73.13 / 72.73 |
| DeepSeek / cold_default_stage2 (primary) | COMPLETE; 43/43; 295/295; 295 | 35.60 / 41.69 / 38.41 | 41.71 / 45.60 / 43.57 | 45.63 / 48.20 / 46.88 | 81.63 / 80.89 / 81.26 | 14.10 / 12.99 / 13.52 | 12.06 / 10.76 / 11.38 | 72.33 / 73.13 / 72.73 |
| DeepSeek / cold_0_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 295 | 30.22 / 33.72 / 31.88 | 35.03 / 36.62 / 35.81 | 42.44 / 41.22 / 41.82 | 81.63 / 80.89 / 81.26 | 5.65 / 4.30 / 4.88 | 5.07 / 3.62 / 4.22 | 72.33 / 73.13 / 72.73 |
| DeepSeek / cold_0_stage2 (primary) | COMPLETE; 43/43; 295/295; 295 | 33.13 / 39.15 / 35.89 | 41.81 / 43.40 / 42.59 | 45.74 / 47.11 / 46.41 | 81.63 / 80.89 / 81.26 | 13.11 / 11.85 / 12.45 | 11.85 / 10.40 / 11.08 | 72.33 / 73.13 / 72.73 |
| DeepSeek / cold_42_stage1 (stage1_diagnostic) | COMPLETE; 43/43; 295/295; 295 | 30.63 / 33.17 / 31.85 | 34.62 / 35.36 / 34.98 | 42.53 / 41.22 / 41.86 | 81.63 / 80.89 / 81.26 | 6.04 / 4.72 / 5.30 | 5.46 / 4.04 / 4.64 | 72.33 / 73.13 / 72.73 |
| DeepSeek / cold_42_stage2 (primary) | COMPLETE; 43/43; 295/295; 295 | 33.95 / 38.01 / 35.86 | 41.23 / 43.34 / 42.26 | 42.53 / 41.22 / 41.86 | 81.63 / 80.89 / 81.26 | 11.66 / 10.48 / 11.04 | 10.50 / 9.12 / 9.76 | 72.33 / 73.13 / 72.73 |

## Local leaderboards

LR means exact normalized TDM hit. Nonempty additionally requires a finite converted Result. PC/RC/RBO use unchanged official code; AO ranks paper IDs. All target boards, including empty boards, stay in each macro denominator. The copied helper’s old LR_primary prose does not override these labels.

| Model / case | Scope / boards | Papers | LR | Nonempty | PC | RC | RBO (values) | AO (paper IDs) |
|---|---|---|---|---|---|---|---|---|
| GPT-4.1 / fully | all27 / 27 | 43/43 | 81.48 | 74.07 | 48.71 | 31.80 | 24.77 | 46.25 |
| GPT-4.1 / fully_cs | all27 / 27 | 43/43 | 92.59 | 88.89 | 63.16 | 41.19 | 30.34 | 52.22 |
| GPT-4.1 / partially_stage2 | all27 / 27 | 43/43 | 48.15 | 40.74 | 13.33 | 8.61 | 11.05 | 15.58 |
| GPT-4.1 / partially_stage2 | masked10 / 10 | 43/43 | 40.00 | 40.00 | 13.90 | 11.40 | 12.07 | 12.07 |
| GPT-4.1 / cold_default_stage2 | all27 / 27 | 43/43 | 44.44 | 44.44 | 10.90 | 8.00 | 10.19 | 13.89 |
| GPT-4.1 / cold_default_stage2 | masked10 / 10 | 43/43 | 20.00 | 20.00 | 7.86 | 5.36 | 7.50 | 7.50 |
| GPT-4.1 / cold_0_stage2 | all27 / 27 | 43/43 | 29.63 | 29.63 | 7.56 | 4.39 | 8.17 | 11.88 |
| GPT-4.1 / cold_0_stage2 | masked10 / 10 | 43/43 | 20.00 | 20.00 | 8.57 | 5.36 | 12.07 | 12.07 |
| GPT-4.1 / cold_42_stage2 | all27 / 27 | 43/43 | 44.44 | 44.44 | 12.79 | 11.86 | 7.90 | 8.31 |
| GPT-4.1 / cold_42_stage2 | masked10 / 10 | 43/43 | 50.00 | 50.00 | 19.02 | 16.52 | 11.32 | 12.43 |
| Sol / fully | all27 / 27 | 43/43 | 100.00 | 100.00 | 98.73 | 81.97 | 78.31 | 94.78 |
| Sol / fully_cs | all27 / 27 | 43/43 | 88.89 | 88.89 | 78.42 | 62.37 | 55.31 | 71.39 |
| Sol / partially_stage2 | all27 / 27 | 43/43 | 70.37 | 70.37 | 47.56 | 41.94 | 35.40 | 41.70 |
| Sol / partially_stage2 | masked10 / 10 | 43/43 | 40.00 | 40.00 | 34.00 | 29.00 | 33.33 | 36.67 |
| Sol / cold_default_stage2 | all27 / 27 | 43/43 | 88.89 | 88.89 | 55.50 | 44.33 | 52.00 | 62.36 |
| Sol / cold_default_stage2 | masked10 / 10 | 43/43 | 90.00 | 90.00 | 60.93 | 49.43 | 51.67 | 58.89 |
| Sol / cold_0_stage2 | all27 / 27 | 43/43 | 88.89 | 88.89 | 54.94 | 41.67 | 47.96 | 60.38 |
| Sol / cold_0_stage2 | masked10 / 10 | 43/43 | 100.00 | 100.00 | 70.93 | 55.43 | 64.58 | 73.96 |
| Sol / cold_42_stage2 | all27 / 27 | 43/43 | 88.89 | 88.89 | 61.46 | 51.64 | 47.31 | 56.21 |
| Sol / cold_42_stage2 | masked10 / 10 | 43/43 | 80.00 | 80.00 | 64.86 | 59.43 | 62.30 | 67.53 |
| DeepSeek / fully | all27 / 27 | 43/43 | 100.00 | 100.00 | 94.12 | 77.26 | 73.26 | 93.89 |
| DeepSeek / fully_cs | all27 / 27 | 43/43 | 88.89 | 88.89 | 75.20 | 55.16 | 53.23 | 71.15 |
| DeepSeek / partially_stage1 | all27 / 27 | 43/43 | 59.26 | 59.26 | 24.23 | 17.35 | 19.44 | 23.56 |
| DeepSeek / partially_stage2 | all27 / 27 | 43/43 | 77.78 | 77.78 | 30.05 | 22.55 | 31.07 | 36.11 |
| DeepSeek / cold_default_stage1 | all27 / 27 | 43/43 | 3.70 | 3.70 | 3.70 | 3.70 | 3.70 | 3.70 |
| DeepSeek / cold_default_stage2 | all27 / 27 | 43/43 | 29.63 | 29.63 | 12.07 | 10.59 | 8.02 | 9.95 |
| DeepSeek / cold_0_stage1 | all27 / 27 | 43/43 | 3.70 | 3.70 | 3.70 | 3.70 | 3.70 | 3.70 |
| DeepSeek / cold_0_stage2 | all27 / 27 | 43/43 | 29.63 | 29.63 | 11.68 | 9.52 | 6.87 | 6.87 |
| DeepSeek / cold_42_stage1 | all27 / 27 | 43/43 | 3.70 | 3.70 | 3.70 | 3.70 | 3.70 | 3.70 |
| DeepSeek / cold_42_stage2 | all27 / 27 | 43/43 | 25.93 | 25.93 | 11.93 | 10.45 | 20.78 | 24.49 |

Sol Fully CS all27 LR is read from its own source: 24/27 = 88.89%. GPT-4.1 Fully CS has 25/27 exact TDM hits; its 24/27 nonempty rate is a different column.

## Cold-order means

| Model | Scope | LR | Nonempty | PC | RC | RBO | AO |
|---|---|---|---|---|---|---|---|
| GPT-4.1 | all27 | 39.51 ± 8.55 | 39.51 ± 8.55 | 10.42 ± 2.65 | 8.08 ± 3.74 | 8.75 ± 1.25 | 11.36 ± 2.83 |
| GPT-4.1 | masked10 | 30.00 ± 17.32 | 30.00 ± 17.32 | 11.82 ± 6.25 | 9.08 ± 6.45 | 10.30 ± 2.45 | 10.67 ± 2.75 |
| Sol | all27 | 88.89 ± 0.00 | 88.89 ± 0.00 | 57.30 ± 3.61 | 45.88 ± 5.16 | 49.09 ± 2.54 | 59.65 ± 3.14 |
| Sol | masked10 | 90.00 ± 10.00 | 90.00 ± 10.00 | 65.57 ± 5.04 | 54.76 ± 5.03 | 59.52 ± 6.89 | 66.79 ± 7.56 |
| DeepSeek | all27 | 28.40 ± 2.14 | 28.40 ± 2.14 | 11.90 ± 0.20 | 10.19 ± 0.58 | 11.89 ± 7.72 | 13.77 ± 9.41 |

Mean ± sample SD across all three completed orders. Individual order rows above are not directly equivalent to the published ColdStart mean.

## Original-paper reference (published percentages)

Published reference, not re-evaluation. AxCell=36 papers; other main rows=43. Table5/17 main boards=27 where stated. ColdStart is a three-order mean. Masked and threshold2/62-board appendix rows are separate; never merged with all27. Published AO is not the official code numeric-value RBO.

| Table | Model / setting / normalization | Papers / boards | Metric | P | R | F1 | LR | PC | RC | AO |
|---|---|---|---|---|---|---|---|---|---|---|
| table_3 | AxCell / Fully / LLM | 36 / n/a | TDMR | 32.59 | 13.67 | 19.26 | — | — | — | — |
| table_3 | Llama-2 / Fully / cosine_similarity | 43 / n/a | TDMR | 10.06 | 21.59 | 13.73 | — | — | — | — |
| table_3 | Llama-2 / Fully / LLM | 43 / n/a | TDMR | 9.63 | 15.25 | 11.81 | — | — | — | — |
| table_3 | Llama-3 / Fully / cosine_similarity | 43 / n/a | TDMR | 23.22 | 29.54 | 26.00 | — | — | — | — |
| table_3 | Llama-3 / Fully / LLM | 43 / n/a | TDMR | 27.11 | 35.60 | 30.78 | — | — | — | — |
| table_3 | GPT-4 / Fully / cosine_similarity | 43 / n/a | TDMR | 49.82 | 48.71 | 49.26 | — | — | — | — |
| table_3 | GPT-4 / Fully / LLM | 43 / n/a | TDMR | 56.02 | 54.53 | 55.27 | — | — | — | — |
| table_3 | Llama-2 / Partially / LLM | 43 / n/a | TDMR | 4.17 | 9.89 | 5.87 | — | — | — | — |
| table_3 | Llama-3 / Partially / LLM | 43 / n/a | TDMR | 15.70 | 18.75 | 17.09 | — | — | — | — |
| table_3 | GPT-4 / Partially / LLM | 43 / n/a | TDMR | 40.60 | 39.56 | 40.07 | — | — | — | — |
| table_4 | AxCell / Fully / LLM | 36 / n/a | Task IIM | 68.98 | 58.52 | 63.32 | — | — | — | — |
| table_4 | AxCell / Fully / LLM | 36 / n/a | Dataset IIM | 63.66 | 33.87 | 44.22 | — | — | — | — |
| table_4 | AxCell / Fully / LLM | 36 / n/a | Metric IIM | 69.35 | 51.36 | 59.01 | — | — | — | — |
| table_4 | AxCell / Fully / LLM | 36 / n/a | Result IIM | 45.32 | 18.41 | 26.18 | — | — | — | — |
| table_4 | Llama-2 / Fully / cosine_similarity | 43 / n/a | Task IIM | 59.83 | 67.20 | 63.30 | — | — | — | — |
| table_4 | Llama-2 / Fully / cosine_similarity | 43 / n/a | Dataset IIM | 68.93 | 58.81 | 63.47 | — | — | — | — |
| table_4 | Llama-2 / Fully / cosine_similarity | 43 / n/a | Metric IIM | 67.36 | 61.41 | 64.25 | — | — | — | — |
| table_4 | Llama-2 / Fully / cosine_similarity | 43 / n/a | Result IIM | 23.75 | 31.61 | 27.12 | — | — | — | — |
| table_4 | Llama-2 / Fully / LLM | 43 / n/a | Task IIM | 55.45 | 60.74 | 57.97 | — | — | — | — |
| table_4 | Llama-2 / Fully / LLM | 43 / n/a | Dataset IIM | 62.60 | 55.03 | 58.57 | — | — | — | — |
| table_4 | Llama-2 / Fully / LLM | 43 / n/a | Metric IIM | 71.51 | 65.49 | 68.37 | — | — | — | — |
| table_4 | Llama-2 / Fully / LLM | 43 / n/a | Result IIM | 23.75 | 31.61 | 27.12 | — | — | — | — |
| table_4 | Llama-3 / Fully / cosine_similarity | 43 / n/a | Task IIM | 85.69 | 90.85 | 88.19 | — | — | — | — |
| table_4 | Llama-3 / Fully / cosine_similarity | 43 / n/a | Dataset IIM | 82.43 | 78.62 | 80.48 | — | — | — | — |
| table_4 | Llama-3 / Fully / cosine_similarity | 43 / n/a | Metric IIM | 87.02 | 81.41 | 84.12 | — | — | — | — |
| table_4 | Llama-3 / Fully / cosine_similarity | 43 / n/a | Result IIM | 39.50 | 49.56 | 43.96 | — | — | — | — |
| table_4 | Llama-3 / Fully / LLM | 43 / n/a | Task IIM | 87.33 | 92.17 | 89.68 | — | — | — | — |
| table_4 | Llama-3 / Fully / LLM | 43 / n/a | Dataset IIM | 92.09 | 87.75 | 89.87 | — | — | — | — |
| table_4 | Llama-3 / Fully / LLM | 43 / n/a | Metric IIM | 94.90 | 89.48 | 92.11 | — | — | — | — |
| table_4 | Llama-3 / Fully / LLM | 43 / n/a | Result IIM | 39.50 | 49.56 | 43.96 | — | — | — | — |
| table_4 | GPT-4 / Fully / cosine_similarity | 43 / n/a | Task IIM | 90.70 | 90.77 | 90.73 | — | — | — | — |
| table_4 | GPT-4 / Fully / cosine_similarity | 43 / n/a | Dataset IIM | 86.36 | 79.93 | 83.02 | — | — | — | — |
| table_4 | GPT-4 / Fully / cosine_similarity | 43 / n/a | Metric IIM | 86.36 | 81.49 | 83.85 | — | — | — | — |
| table_4 | GPT-4 / Fully / cosine_similarity | 43 / n/a | Result IIM | 70.34 | 68.22 | 69.26 | — | — | — | — |
| table_4 | GPT-4 / Fully / LLM | 43 / n/a | Task IIM | 90.62 | 91.10 | 90.86 | — | — | — | — |
| table_4 | GPT-4 / Fully / LLM | 43 / n/a | Dataset IIM | 92.64 | 86.05 | 89.22 | — | — | — | — |
| table_4 | GPT-4 / Fully / LLM | 43 / n/a | Metric IIM | 88.18 | 86.46 | 87.31 | — | — | — | — |
| table_4 | GPT-4 / Fully / LLM | 43 / n/a | Result IIM | 70.34 | 68.22 | 69.26 | — | — | — | — |
| table_4 | Llama-2 / Partially / LLM | 43 / n/a | Task IIM | 39.70 | 42.98 | 41.27 | — | — | — | — |
| table_4 | Llama-2 / Partially / LLM | 43 / n/a | Dataset IIM | 41.05 | 33.14 | 36.67 | — | — | — | — |
| table_4 | Llama-2 / Partially / LLM | 43 / n/a | Metric IIM | 61.24 | 59.34 | 60.28 | — | — | — | — |
| table_4 | Llama-2 / Partially / LLM | 43 / n/a | Result IIM | 23.75 | 31.61 | 27.12 | — | — | — | — |
| table_4 | Llama-3 / Partially / LLM | 43 / n/a | Task IIM | 65.72 | 80.39 | 72.32 | — | — | — | — |
| table_4 | Llama-3 / Partially / LLM | 43 / n/a | Dataset IIM | 66.81 | 62.86 | 64.77 | — | — | — | — |
| table_4 | Llama-3 / Partially / LLM | 43 / n/a | Metric IIM | 94.90 | 88.90 | 91.80 | — | — | — | — |
| table_4 | Llama-3 / Partially / LLM | 43 / n/a | Result IIM | 39.50 | 49.56 | 43.96 | — | — | — | — |
| table_4 | GPT-4 / Partially / LLM | 43 / n/a | Task IIM | 63.82 | 78.30 | 70.32 | — | — | — | — |
| table_4 | GPT-4 / Partially / LLM | 43 / n/a | Dataset IIM | 83.29 | 79.52 | 81.36 | — | — | — | — |
| table_4 | GPT-4 / Partially / LLM | 43 / n/a | Metric IIM | 92.21 | 89.27 | 90.72 | — | — | — | — |
| table_4 | GPT-4 / Partially / LLM | 43 / n/a | Result IIM | 70.34 | 68.22 | 69.26 | — | — | — | — |
| table_12 | AxCell / Fully / LLM | 36 / n/a | TDM | 55.08 | 25.78 | 35.12 | — | — | — | — |
| table_12 | Llama-2 / Fully / cosine_similarity | 43 / n/a | TDM | 40.66 | 39.54 | 40.09 | — | — | — | — |
| table_12 | Llama-2 / Fully / LLM | 43 / n/a | TDM | 35.85 | 34.91 | 35.37 | — | — | — | — |
| table_12 | Llama-3 / Fully / cosine_similarity | 43 / n/a | TDM | 62.02 | 58.07 | 59.98 | — | — | — | — |
| table_12 | Llama-3 / Fully / LLM | 43 / n/a | TDM | 77.13 | 72.56 | 74.77 | — | — | — | — |
| table_12 | GPT-4 / Fully / cosine_similarity | 43 / n/a | TDM | 68.95 | 63.82 | 66.29 | — | — | — | — |
| table_12 | GPT-4 / Fully / LLM | 43 / n/a | TDM | 75.28 | 70.40 | 72.75 | — | — | — | — |
| table_12 | Llama-2 / Partially / LLM | 43 / n/a | TDM | 27.23 | 22.99 | 24.93 | — | — | — | — |
| table_12 | Llama-3 / Partially / LLM | 43 / n/a | TDM | 50.75 | 45.30 | 47.87 | — | — | — | — |
| table_12 | GPT-4 / Partially / LLM | 43 / n/a | TDM | 56.08 | 51.89 | 53.90 | — | — | — | — |
| table_5 | AxCell / Fully / LLM | 36 / n/a | Leaderboard | — | — | — | 40.00 | 25.78 | 15.45 | 11.93 |
| table_5 | Llama-2 / Fully / cosine_similarity | 43 / 27 | Leaderboard | — | — | — | 70.37 | 35.23 | 8.88 | 4.60 |
| table_5 | Llama-2 / Fully / LLM | 43 / 27 | Leaderboard | — | — | — | 70.37 | 34.96 | 8.26 | 4.96 |
| table_5 | Llama-3 / Fully / cosine_similarity | 43 / 27 | Leaderboard | — | — | — | 81.48 | 60.15 | 22.65 | 21.45 |
| table_5 | Llama-3 / Fully / LLM | 43 / 27 | Leaderboard | — | — | — | 96.30 | 79.18 | 29.30 | 25.49 |
| table_5 | GPT-4 / Fully / cosine_similarity | 43 / 27 | Leaderboard | — | — | — | 92.59 | 63.70 | 45.59 | 38.66 |
| table_5 | GPT-4 / Fully / LLM | 43 / 27 | Leaderboard | — | — | — | 100.00 | 70.37 | 51.79 | 53.87 |
| table_5 | Llama-2 / Partially / LLM | 43 / 27 | Leaderboard | — | — | — | 74.07 | 30.75 | 4.02 | 1.18 |
| table_5 | Llama-3 / Partially / LLM | 43 / 27 | Leaderboard | — | — | — | 92.59 | 61.90 | 19.01 | 19.52 |
| table_5 | GPT-4 / Partially / LLM | 43 / 27 | Leaderboard | — | — | — | 88.89 | 55.92 | 40.06 | 43.71 |
| table_5 | Llama-2 / ColdStart / LLM | 43 / 27 | Leaderboard | — | — | — | 16.05 | 5.66 | 0.49 | 0.05 |
| table_5 | Llama-3 / ColdStart / LLM | 43 / 27 | Leaderboard | — | — | — | 79.01 | 58.78 | 17.18 | 17.63 |
| table_5 | GPT-4 / ColdStart / LLM | 43 / 27 | Leaderboard | — | — | — | 81.48 | 58.74 | 46.13 | 48.15 |
| table_17 | Llama-2 / ColdStart / LLM | 43 / 27 | Leaderboard mean ± SD | — | — | — | 16.05 ± 4.28 | 5.66 ± 1.76 | 0.49 ± 0.86 | 0.05 ± 0.09 |
| table_17 | Llama-3 / ColdStart / LLM | 43 / 27 | Leaderboard mean ± SD | — | — | — | 79.01 ± 14.02 | 58.78 ± 15.10 | 17.18 ± 4.72 | 17.63 ± 3.17 |
| table_17 | GPT-4 / ColdStart / LLM | 43 / 27 | Leaderboard mean ± SD | — | — | — | 81.48 ± 14.81 | 58.74 ± 7.42 | 46.13 ± 3.10 | 48.15 ± 4.42 |

Published scores are retained as reported, including F1 and SD. They do not establish equality between paper definitions and code quirks (Result substring matching; numeric-value RBO versus paper-ID AO). Masked/threshold-2 appendix values are retained separately in comparison.json.

## Missing or unfinished inputs

None.

Sources and SHA-256 hashes: source_hashes.json. Exact per-row source paths, coverage IDs, and full precision values: comparison.json.
