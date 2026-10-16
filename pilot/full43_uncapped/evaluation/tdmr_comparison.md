# 逐条 Gold 与原始 / 标准化输出对照

候选索引按数值命中列出，不强行假设一对一关系；`±`、单位等非纯数值文本不满足 Decimal 严格相等。官方字符串包含匹配单独列出。

## 2020.findings-emnlp.378.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 90.32 | #1: Named Entity Recognition / ON5E / F1 / 90.32 → Named Entity Recognition (NER) / None / F1 / 90.32 | [1] | [] | normalization_null |
| 2: Named Entity Recognition (NER) / WNUT-16 - English / F1 / 55.14 | #2: Named Entity Recognition / WN16 / F1 / 55.14 → Named Entity Recognition (NER) / None / F1 / 55.14 | [2] | [] | normalization_null |
| 3: Named Entity Recognition (NER) / WNUT-17 - English / F1 / 50.68 | #3: Named Entity Recognition / WN17 / F1 / 50.68 → Named Entity Recognition (NER) / None / F1 / 50.68 | [3] | [] | normalization_null |
| 4: Named Entity Recognition (NER) / Ontonotes v4 - Chinese / F1 / 81.18 | #4: Named Entity Recognition / ON4C / F1 / 81.18 → Named Entity Recognition (NER) / None / F1 / 81.18 | [4] | [] | normalization_null |
| 5: Named Entity Recognition (NER) / Resume - Chinese / F1 / 96.62 | #5: Named Entity Recognition / RE / F1 / 96.62 → Named Entity Recognition (NER) / None / F1 / 96.62 | [5] | [] | normalization_null |
| 6: Named Entity Recognition (NER) / Weibo - Chinese / F1 / 69.78 | #6: Named Entity Recognition / WE / F1 / 69.78 → Named Entity Recognition (NER) / None / F1 / 69.78 | [6] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / ON5E / F1 / 90.32 | Named Entity Recognition (NER) / None / F1 / 90.32 |
| 2 | Named Entity Recognition / WN16 / F1 / 55.14 | Named Entity Recognition (NER) / None / F1 / 55.14 |
| 3 | Named Entity Recognition / WN17 / F1 / 50.68 | Named Entity Recognition (NER) / None / F1 / 50.68 |
| 4 | Named Entity Recognition / ON4C / F1 / 81.18 | Named Entity Recognition (NER) / None / F1 / 81.18 |
| 5 | Named Entity Recognition / RE / F1 / 96.62 | Named Entity Recognition (NER) / None / F1 / 96.62 |
| 6 | Named Entity Recognition / WE / F1 / 69.78 | Named Entity Recognition (NER) / None / F1 / 69.78 |

## 1709.04109.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.85 | #1: Named Entity Recognition / CoNLL03 NER / F1 score / 91.85 → Named Entity Recognition (NER) / None / F1 / 91.85 | [1] | [] | normalization_null |
| 2: Text Chunking / CoNLL-2000 / F1 / 96.13 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.59 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / CoNLL03 NER / F1 score / 91.85 | Named Entity Recognition (NER) / None / F1 / 91.85 |
| 2 | Part-of-Speech Tagging / WSJ / Accuracy / 97.55 | Part-of-Speech (POS) Tagging / None / Accuracy / 97.55 |
| 3 | Chunking / CoNLL00 chunking / F1 score / 95.96 | Text Chunking / CoNLL-2000 / F1 / 95.96 |

## D18-1279.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.64 | #3: Named Entity Recognition / CoNLL-2003 English / F1 / 91.64 → Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.64 | [3] | [3] | correct |
| 2: Named Entity Recognition (NER) / CoNLL-2003 - German / F1 / 79.43 | #4: Named Entity Recognition / CoNLL-2003 German / F1 / 79.43 → Named Entity Recognition (NER) / CoNLL-2003 - German / F1 / 79.43 | [4] | [4] | correct |
| 3: Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 86.68 | #1: Named Entity Recognition / CoNLL-2002 Spanish / F1 / 86.68 → Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 86.68 | [1] | [1] | correct |
| 4: Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 87.81 | #2: Named Entity Recognition / CoNLL-2002 Dutch / F1 / 87.81 → Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 87.81 | [2] | [2] | correct |
| 5: Text Chunking / CoNLL-2000 / F1 / 95.29 | #5: Syntactic Chunking / CoNLL-2000 / F1 / 95.29 → Text Chunking / CoNLL-2000 / F1 / 95.29 | [5] | [5] | correct |
| 6: Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / F1 / 97.58 | #6: Part-of-Speech Tagging / Penn Treebank WSJ / F1 / 97.58 → Part-of-Speech (POS) Tagging / None / F1 / 97.58 | [6] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / CoNLL-2002 Spanish / F1 / 86.68 | Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 86.68 |
| 2 | Named Entity Recognition / CoNLL-2002 Dutch / F1 / 87.81 | Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 87.81 |
| 3 | Named Entity Recognition / CoNLL-2003 English / F1 / 91.64 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.64 |
| 4 | Named Entity Recognition / CoNLL-2003 German / F1 / 79.43 | Named Entity Recognition (NER) / CoNLL-2003 - German / F1 / 79.43 |
| 5 | Syntactic Chunking / CoNLL-2000 / F1 / 95.29 | Text Chunking / CoNLL-2000 / F1 / 95.29 |
| 6 | Part-of-Speech Tagging / Penn Treebank WSJ / F1 / 97.58 | Part-of-Speech (POS) Tagging / None / F1 / 97.58 |

## 2020.emnlp-main.523.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Entity Typing / Open Entity / Precision / 79.9 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Entity Typing / Open Entity / Recall / 76.6 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Entity Typing / Open Entity / F1 / 78.2 | #1: Entity Typing / Open Entity / F1 / 78.2 → Entity Typing / Open Entity / F1 / 78.2 | [1] | [1] | correct |
| 4: Relation Classification / TACRED / Precision / 70.4 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Relation Classification / TACRED / Recall / 75.1 | — | [] | [] | numeric_result_missing_or_changed |
| 6: Relation Classification / TACRED / F1 / 72.7 | #2: Relation Classification / TACRED / F1 / 72.7 → Relation Classification / TACRED / F1 / 72.7 | [2] | [2] | correct |
| 7: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 94.3 | #3: Named Entity Recognition / CoNLL-2003 / F1 / 94.3 → Named Entity Recognition (NER) / None / F1 / 94.3 | [3] | [] | normalization_null |
| 8: Question Answering / ReCoRD / Exact Match (EM) / 90.6 | — | [] | [] | numeric_result_missing_or_changed |
| 9: Question Answering / ReCoRD / F1 / 91.2 | — | [] | [] | numeric_result_missing_or_changed |
| 10: Question Answering / SQuAD 1.1 / Exact Match (EM) / 90.2 | — | [] | [] | numeric_result_missing_or_changed |
| 11: Question Answering / SQuAD 1.1 / F1 / 95.4 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Entity Typing / Open Entity / F1 / 78.2 | Entity Typing / Open Entity / F1 / 78.2 |
| 2 | Relation Classification / TACRED / F1 / 72.7 | Relation Classification / TACRED / F1 / 72.7 |
| 3 | Named Entity Recognition / CoNLL-2003 / F1 / 94.3 | Named Entity Recognition (NER) / None / F1 / 94.3 |
| 4 | Cloze-style Question Answering / ReCoRD / EM / 90.8 | Question Answering / ReCoRD / Exact Match (EM) / 90.8 |
| 5 | Cloze-style Question Answering / ReCoRD / F1 / 91.4 | Question Answering / ReCoRD / F1 / 91.4 |
| 6 | Extractive Question Answering / SQuAD 1.1 / EM / 89.8 | Question Answering / SQuAD 1.1 / Exact Match (EM) / 89.8 |
| 7 | Extractive Question Answering / SQuAD 1.1 / F1 / 95.0 | Question Answering / SQuAD 1.1 / F1 / 95.0 |

## 1905.03197.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / CNN/DailyMail / ROGUE-1 / 43.33 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Summarization / CNN/DailyMail / ROGUE-2 / 20.21 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Summarization / CNN/DailyMail / ROGUE-L / 40.51 | #1: Abstractive Summarization / CNN/DailyMail / ROUGE-L / 40.51 → Summarization / CNN/DailyMail / None / 40.51 | [1] | [] | normalization_null |
| 4: Summarization / Gigaword / ROGUE-1 / 38.45 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Summarization / Gigaword / ROGUE-2 / 19.45 | — | [] | [] | numeric_result_missing_or_changed |
| 6: Summarization / Gigaword / ROGUE-L / 35.75 | #2: Abstractive Summarization / Gigaword (Full Training Set) / ROUGE-L / 35.75 → Summarization / Gigaword / None / 35.75 | [2] | [] | normalization_null |
| 7: Question Answering / SQuAD 2.0 / Exact Match (EM) / 84.7 | — | [] | [] | numeric_result_missing_or_changed |
| 8: Question Answering / SQuAD 2.0 / F1 / 87.6 | — | [] | [] | numeric_result_missing_or_changed |
| 9: Question Answering / CoQA / F1 / 84.9 | #5: Extractive Question Answering / CoQA / F1 / 84.9 → Question Answering / CoQA / F1 / 84.9 | [5] | [5] | correct |
| 10: Question Generation / SQuAD 1.1 / BLEU-4 / 23.75 | — | [] | [] | numeric_result_missing_or_changed |
| 11: Question Generation / SQuAD 1.1 / METEOR / 25.61 | #7: Question Generation / SQuAD / BLEU-4 / 25.61 → Question Generation / None / BLEU-4 / 25.61 | [7] | [] | normalization_null |
| 12: Question Generation / SQuAD 1.1 / ROGUE-L / 52.04 | #9: Question Generation / SQuAD / ROUGE-L / 52.04 → Question Generation / None / None / 52.04 | [9] | [] | normalization_null |
| 13: Response Generation / DSTC7 / NIST-4 / 2.67 | — | [] | [] | numeric_result_missing_or_changed |
| 14: Response Generation / DSTC7 / BLEU-4 / 4.39 | #10: Response Generation / DSTC7 / BLEU-4 / 4.39 → Response Generation / DSTC7 / BLEU-4 / 4.39 | [10] | [10] | correct |
| 15: Response Generation / DSTC7 / METEOR / 8.27 | — | [] | [] | numeric_result_missing_or_changed |
| 16: Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 61.1 | — | [] | [] | numeric_result_missing_or_changed |
| 17: Sentiment Analysis / SST-2 / Accuracy / 94.5 | — | [] | [] | numeric_result_missing_or_changed |
| 18: Paraphrase Detection / MRPC / F1 / 90.0 | #4: Extractive Question Answering / SQuAD / F1 / 90.0 → Question Answering / None / F1 / 90.0 | [4] | [] | normalization_null |
| 19: Text Similarity / STS-B / Spearman Correlation / 87.7 | — | [] | [] | numeric_result_missing_or_changed |
| 20: Paraphrase Detection / QQP / F1 / 71.7 | — | [] | [] | numeric_result_missing_or_changed |
| 21: Natural Language Inference (NLI) / MNLI-m / Accuracy / 87.0 | #14: Language Understanding (GLUE Benchmark) / GLUE / MNLI-m Accuracy / 87.0 → Natural Language Inference (NLI) / None / None / 87.0 | [14] | [] | normalization_null |
| 22: Natural Language Inference (NLI) / MNLI-mm / Accuracy / 85.9 | #15: Language Understanding (GLUE Benchmark) / GLUE / MNLI-mm Accuracy / 85.9 → Natural Language Inference (NLI) / None / Accuracy / 85.9 | [15] | [] | normalization_null |
| 23: Natural Language Inference (NLI) / QNLI / Accuracy / 92.7 | #16: Language Understanding (GLUE Benchmark) / GLUE / QNLI Accuracy / 92.7 → Natural Language Inference (NLI) / None / Accuracy / 92.7 | [16] | [] | normalization_null |
| 24: Natural Language Inference (NLI) / RTE / Accuracy / 70.9 | — | [] | [] | numeric_result_missing_or_changed |
| 25: Natural Language Inference (NLI) / WNLI / Accuracy / 65.1 | — | [] | [] | numeric_result_missing_or_changed |
| 26: Natural Language Inference (NLI) / AX / Accuracy / 38.4 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Abstractive Summarization / CNN/DailyMail / ROUGE-L / 40.51 | Summarization / CNN/DailyMail / None / 40.51 |
| 2 | Abstractive Summarization / Gigaword (Full Training Set) / ROUGE-L / 35.75 | Summarization / Gigaword / None / 35.75 |
| 3 | Abstractive Summarization / Gigaword (10K Training Examples) / ROUGE-L / 30.56 | Summarization / Gigaword / None / 30.56 |
| 4 | Extractive Question Answering / SQuAD / F1 / 90.0 | Question Answering / None / F1 / 90.0 |
| 5 | Extractive Question Answering / CoQA / F1 / 84.9 | Question Answering / CoQA / F1 / 84.9 |
| 6 | Generative Question Answering / CoQA / F1 / 82.5 | Question Answering / CoQA / F1 / 82.5 |
| 7 | Question Generation / SQuAD / BLEU-4 / 25.61 | Question Generation / None / BLEU-4 / 25.61 |
| 8 | Question Generation / SQuAD / METEOR / 25.06 | Question Generation / None / METEOR / 25.06 |
| 9 | Question Generation / SQuAD / ROUGE-L / 52.04 | Question Generation / None / None / 52.04 |
| 10 | Response Generation / DSTC7 / BLEU-4 / 4.39 | Response Generation / DSTC7 / BLEU-4 / 4.39 |
| 11 | Response Generation / DSTC7 / Div-1 / 0.109 | Response Generation / DSTC7 / None / 0.109 |
| 12 | Response Generation / DSTC7 / Div-2 / 0.325 | Response Generation / DSTC7 / None / 0.325 |
| 13 | Language Understanding (GLUE Benchmark) / GLUE / SST-2 Accuracy / 94.9 | Natural Language Inference (NLI) / None / Accuracy / 94.9 |
| 14 | Language Understanding (GLUE Benchmark) / GLUE / MNLI-m Accuracy / 87.0 | Natural Language Inference (NLI) / None / None / 87.0 |
| 15 | Language Understanding (GLUE Benchmark) / GLUE / MNLI-mm Accuracy / 85.9 | Natural Language Inference (NLI) / None / Accuracy / 85.9 |
| 16 | Language Understanding (GLUE Benchmark) / GLUE / QNLI Accuracy / 92.7 | Natural Language Inference (NLI) / None / Accuracy / 92.7 |
| 17 | Language Understanding (GLUE Benchmark) / GLUE / CoLA MCC / 60.5 | Natural Language Inference (NLI) / None / Matthew's Correlation Coefficient (MCC) / 60.5 |
| 18 | Language Understanding (GLUE Benchmark) / GLUE / STS-B Spearman Corr. / 89.3 | Natural Language Inference (NLI) / None / Spearman Correlation / 89.3 |

## 1702.02098.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 90.65 | — | [1] | [] | numeric_result_missing_or_changed |
| 2: Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 86.99 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / CoNLL-2003 / F1 / 90.65 ± 0.15 | Named Entity Recognition (NER) / None / F1 / 90.65 ± 0.15 |
| 2 | Named Entity Recognition / OntoNotes / F1 / 86.84 ± 0.19 | Named Entity Recognition (NER) / None / F1 / 86.84 ± 0.19 |

## 2020.emnlp-main.152.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Intent Detection and Slot Filling / ATIS / F1 / 96.24 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Intent Detection and Slot Filling / ATIS / Accuracy / 97.74 | #1: Intent Detection / ATIS / Accuracy / 97.74 → Intent Detection and Slot Filling / ATIS / Accuracy / 97.74 | [1] | [1] | correct |
| 3: Intent Detection and Slot Filling / ATIS / Sent-Accuracy / 88.64 | #3: Sentence Accuracy (Intent + Slot) / ATIS / Sentence Accuracy / 88.64 → Intent Detection and Slot Filling / ATIS / Sent-Accuracy / 88.64 | [3] | [3] | correct |
| 4: Intent Detection and Slot Filling / SNIPS / F1 / 97.05 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Intent Detection and Slot Filling / SNIPS / Accuracy / 99.04 | #4: Intent Detection / Snips / Accuracy / 99.04 → Intent Detection and Slot Filling / SNIPS / Accuracy / 99.04 | [4] | [4] | correct |
| 6: Intent Detection and Slot Filling / SNIPS / Sent-Accuracy / 92.96 | #6: Sentence Accuracy (Intent + Slot) / Snips / Sentence Accuracy / 92.96 → Intent Detection and Slot Filling / SNIPS / Sent-Accuracy / 92.96 | [6] | [6] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Intent Detection / ATIS / Accuracy / 97.74 | Intent Detection and Slot Filling / ATIS / Accuracy / 97.74 |
| 2 | Slot Filling / ATIS / F1-score / 96.16 | Intent Detection and Slot Filling / ATIS / F1 / 96.16 |
| 3 | Sentence Accuracy (Intent + Slot) / ATIS / Sentence Accuracy / 88.64 | Intent Detection and Slot Filling / ATIS / Sent-Accuracy / 88.64 |
| 4 | Intent Detection / Snips / Accuracy / 99.04 | Intent Detection and Slot Filling / SNIPS / Accuracy / 99.04 |
| 5 | Slot Filling / Snips / F1-score / 99.00 | Intent Detection and Slot Filling / SNIPS / F1 / 99.00 |
| 6 | Sentence Accuracy (Intent + Slot) / Snips / Sentence Accuracy / 92.96 | Intent Detection and Slot Filling / SNIPS / Sent-Accuracy / 92.96 |

## 2105.03654.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / WNUT-16 - English / F1 / 58.98 | #1: Named Entity Recognition (NER) / WNUT-16 / Accuracy / 58.98 → Named Entity Recognition (NER) / WNUT-16 - English / Accuracy / 58.98 | [1] | [] | numeric_match_but_binding_or_label_mismatch |
| 2: Named Entity Recognition (NER) / WNUT-17 - English / F1 / 60.45 | #2: Named Entity Recognition (NER) / WNUT-17 / Accuracy / 60.45 → Named Entity Recognition (NER) / WNUT-17 - English / Accuracy / 60.45 | [2] | [] | numeric_match_but_binding_or_label_mismatch |
| 3: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.56 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Named Entity Recognition (NER) / CoNLL++ / F1 / 94.81 | #3: Named Entity Recognition (NER) / CoNLL-03 / Accuracy / 94.81 → Named Entity Recognition (NER) / None / Accuracy / 94.81 | [3] | [] | normalization_null |
| 5: Named Entity Recognition (NER) / BC5CDR / F1 / 90.99 | #5: Named Entity Recognition (NER) / BC5CDR / Accuracy / 90.99 → Named Entity Recognition (NER) / BC5CDR / Accuracy / 90.99 | [5] | [] | numeric_match_but_binding_or_label_mismatch |
| 6: Named Entity Recognition (NER) / NCBI / F1 / 89.24 | — | [] | [] | numeric_result_missing_or_changed |
| 7: Named Entity Recognition (NER) / E-commerce / F1 / 83.99 | #7: Named Entity Recognition (NER) / E-commerce / Accuracy / 83.99 → Named Entity Recognition (NER) / E-commerce / Accuracy / 83.99 | [7] | [] | numeric_match_but_binding_or_label_mismatch |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition (NER) / WNUT-16 / Accuracy / 58.98 | Named Entity Recognition (NER) / WNUT-16 - English / Accuracy / 58.98 |
| 2 | Named Entity Recognition (NER) / WNUT-17 / Accuracy / 60.45 | Named Entity Recognition (NER) / WNUT-17 - English / Accuracy / 60.45 |
| 3 | Named Entity Recognition (NER) / CoNLL-03 / Accuracy / 94.81 | Named Entity Recognition (NER) / None / Accuracy / 94.81 |
| 4 | Named Entity Recognition (NER) / CoNLL++ / Accuracy / 94.62 | Named Entity Recognition (NER) / CoNLL++ / Accuracy / 94.62 |
| 5 | Named Entity Recognition (NER) / BC5CDR / Accuracy / 90.99 | Named Entity Recognition (NER) / BC5CDR / Accuracy / 90.99 |
| 6 | Named Entity Recognition (NER) / NCBI / Accuracy / 89.22 | Named Entity Recognition (NER) / NCBI / Accuracy / 89.22 |
| 7 | Named Entity Recognition (NER) / E-commerce / Accuracy / 83.99 | Named Entity Recognition (NER) / E-commerce / Accuracy / 83.99 |
| 8 | Cross-domain NER Transfer / CoNLL-03 (train) → CBS SciTech News (test) / Accuracy / 76.38 | Named Entity Recognition (NER) / None / Accuracy / 76.38 |
| 9 | Semi-supervised NER / E-commerce / Accuracy / 84.10 | Named Entity Recognition (NER) / E-commerce / Accuracy / 84.10 |
| 10 | NER with Context Retrieval / WNUT-17 / F1 / 62.29 | Named Entity Recognition (NER) / None / F1 / 62.29 |
| 11 | NER with Document-level Contexts / CoNLL-03 / Accuracy / 93.85 | Named Entity Recognition (NER) / None / Accuracy / 93.85 |

## 1910.13461.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Question Answering / SQuAD 1.1 / Exact Match (EM) / 88.8 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Question Answering / SQuAD 1.1 / F1 / 94.6 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Question Answering / SQuAD 2.0 / Exact Match (EM) / 86.1 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Question Answering / SQuAD 2.0 / F1 / 89.2 | #3: Natural Language Inference / MNLI / Accuracy / 89.2 → Natural Language Inference (NLI) / None / Accuracy / 89.2 | [3] | [] | normalization_null |
| 5: Natural Language Inference (NLI) / MNLI-m / Accuracy / 89.9 | — | [] | [] | numeric_result_missing_or_changed |
| 6: Natural Language Inference (NLI) / MNLI-mm / Accuracy / 90.1 | — | [] | [] | numeric_result_missing_or_changed |
| 7: Sentiment Analysis / SST-2 / Accuracy / 96.6 | — | [] | [] | numeric_result_missing_or_changed |
| 8: Paraphrase Detection / QQP / Accuracy / 92.5 | — | [] | [] | numeric_result_missing_or_changed |
| 9: Natural Language Inference (NLI) / QNLI / Accuracy / 94.9 | — | [] | [] | numeric_result_missing_or_changed |
| 10: Text Similarity / STS-B / Accuracy / 91.2 | — | [] | [] | numeric_result_missing_or_changed |
| 11: Natural Language Inference (NLI) / RTE / Accuracy / 87.0 | — | [] | [] | numeric_result_missing_or_changed |
| 12: Paraphrase Detection / MRPC / Accuracy / 90.4 | — | [] | [] | numeric_result_missing_or_changed |
| 13: Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 62.8 | — | [] | [] | numeric_result_missing_or_changed |
| 14: Summarization / CNN/DailyMail / ROGUE-1 / 44.16 | #4: Summarization / CNN/DailyMail / ROUGE-1 / 44.16 → Summarization / CNN/DailyMail / None / 44.16 | [4] | [] | normalization_null |
| 15: Summarization / CNN/DailyMail / ROGUE-2 / 21.28 | #5: Summarization / CNN/DailyMail / ROUGE-2 / 21.28 → Summarization / CNN/DailyMail / None / 21.28 | [5] | [] | normalization_null |
| 16: Summarization / CNN/DailyMail / ROGUE-L / 40.9 | #6: Summarization / CNN/DailyMail / ROUGE-L / 40.90 → Summarization / CNN/DailyMail / None / 40.90 | [6] | [] | normalization_null |
| 17: Summarization / XSum / ROGUE-1 / 45.14 | #7: Summarization / XSum / ROUGE-1 / 45.14 → Summarization / XSum / None / 45.14 | [7] | [] | normalization_null |
| 18: Summarization / XSum / ROGUE-2 / 22.27 | #8: Summarization / XSum / ROUGE-2 / 22.27 → Summarization / XSum / None / 22.27 | [8] | [] | normalization_null |
| 19: Summarization / XSum / ROGUE-L / 37.25 | #9: Summarization / XSum / ROUGE-L / 37.25 → Summarization / XSum / None / 37.25 | [9] | [] | normalization_null |
| 20: Dialogue Generation / ConvAI2 / F1 / 20.72 | #10: Conversational Response Generation / ConvAI2 / Valid F1 / 20.72 → Response Generation / ConvAI2 / F1 / 20.72 | [10] | [] | numeric_match_but_binding_or_label_mismatch |
| 21: Dialogue Generation / ConvAI2 / Perplexity / 11.85 | #11: Conversational Response Generation / ConvAI2 / Valid PPL / 11.85 → Response Generation / ConvAI2 / Perplexity / 11.85 | [11] | [] | numeric_match_but_binding_or_label_mismatch |
| 22: Question Answering / ELI5 / ROGUE-1 / 30.6 | #12: Abstractive Question Answering / ELI5 / ROUGE-1 / 30.6 → Question Answering / ELI5 / None / 30.6 | [12] | [] | normalization_null |
| 23: Question Answering / ELI5 / ROGUE-2 / 6.2 | #13: Abstractive Question Answering / ELI5 / ROUGE-2 / 6.2 → Question Answering / ELI5 / None / 6.2 | [13] | [] | normalization_null |
| 24: Question Answering / ELI5 / ROGUE-L / 24.3 | #14: Abstractive Question Answering / ELI5 / ROUGE-L / 24.3 → Question Answering / ELI5 / None / 24.3 | [14] | [] | normalization_null |
| 25: Machine Translation / WMT’16 RO-EN / BLEU / 37.96 | #15: Machine Translation / WMT'16 RO-EN / BLEU / 37.96 → Machine Translation / WMT’16 RO-EN / BLEU / 37.96 | [15] | [15] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Extractive Question Answering / SQuAD 1.1 / F1 / 90.9 | Question Answering / SQuAD 1.1 / F1 / 90.9 |
| 2 | Extractive Question Answering / SQuAD 1.1 / EM / 84.1 | Question Answering / SQuAD 1.1 / Exact Match (EM) / 84.1 |
| 3 | Natural Language Inference / MNLI / Accuracy / 89.2 | Natural Language Inference (NLI) / None / Accuracy / 89.2 |
| 4 | Summarization / CNN/DailyMail / ROUGE-1 / 44.16 | Summarization / CNN/DailyMail / None / 44.16 |
| 5 | Summarization / CNN/DailyMail / ROUGE-2 / 21.28 | Summarization / CNN/DailyMail / None / 21.28 |
| 6 | Summarization / CNN/DailyMail / ROUGE-L / 40.90 | Summarization / CNN/DailyMail / None / 40.90 |
| 7 | Summarization / XSum / ROUGE-1 / 45.14 | Summarization / XSum / None / 45.14 |
| 8 | Summarization / XSum / ROUGE-2 / 22.27 | Summarization / XSum / None / 22.27 |
| 9 | Summarization / XSum / ROUGE-L / 37.25 | Summarization / XSum / None / 37.25 |
| 10 | Conversational Response Generation / ConvAI2 / Valid F1 / 20.72 | Response Generation / ConvAI2 / F1 / 20.72 |
| 11 | Conversational Response Generation / ConvAI2 / Valid PPL / 11.85 | Response Generation / ConvAI2 / Perplexity / 11.85 |
| 12 | Abstractive Question Answering / ELI5 / ROUGE-1 / 30.6 | Question Answering / ELI5 / None / 30.6 |
| 13 | Abstractive Question Answering / ELI5 / ROUGE-2 / 6.2 | Question Answering / ELI5 / None / 6.2 |
| 14 | Abstractive Question Answering / ELI5 / ROUGE-L / 24.3 | Question Answering / ELI5 / None / 24.3 |
| 15 | Machine Translation / WMT'16 RO-EN / BLEU / 37.96 | Machine Translation / WMT’16 RO-EN / BLEU / 37.96 |

## D18-1105.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 83.1 | #1: Dialog Act Classification / SwDA / Accuracy / 83.1 → Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 83.1 | [1] | [1] | correct |
| 2: Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 86.7 | #2: Dialog Act Classification / MRDA / Accuracy / 86.7 → Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 86.7 | [2] | [2] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Dialog Act Classification / SwDA / Accuracy / 83.1 | Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 83.1 |
| 2 | Dialog Act Classification / MRDA / Accuracy / 86.7 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 86.7 |

## 1703.06345.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.26 | #3: NER / CoNLL 2003 English / F1 / 91.26 → Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.26 | [3] | [3] | correct |
| 2: Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 85.77 | #4: NER / CoNLL 2002 Spanish / F1 / 85.77 → Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 85.77 | [4] | [4] | correct |
| 3: Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 85.19 | #5: NER / CoNLL 2002 Dutch / F1 / 85.19 → Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 85.19 | [5] | [5] | correct |
| 4: Text Chunking / CoNLL-2000 / F1 / 95.41 | #2: Chunking / CoNLL 2000 / F1 / 95.41 → Text Chunking / CoNLL-2000 / F1 / 95.41 | [2] | [2] | correct |
| 5: Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.55 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | POS Tagging / PTB / Accuracy / 97.78 | Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.78 |
| 2 | Chunking / CoNLL 2000 / F1 / 95.41 | Text Chunking / CoNLL-2000 / F1 / 95.41 |
| 3 | NER / CoNLL 2003 English / F1 / 91.26 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.26 |
| 4 | NER / CoNLL 2002 Spanish / F1 / 85.77 | Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 85.77 |
| 5 | NER / CoNLL 2002 Dutch / F1 / 85.19 | Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 85.19 |

## 1903.07785.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 53.1 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Sentiment Analysis / SST-2 / Accuracy / 94.6 | #2: SST-2 (Stanford Sentiment Treebank) classification / SST-2 / Accuracy / 94.6 → Sentiment Analysis / SST-2 / Accuracy / 94.6 | [2] | [2] | correct |
| 3: Paraphrase Detection / MRPC / F1 / 83.7 | #3: MRPC (Microsoft Research Paraphrase Corpus) sentence similarity / MRPC / F1 / 83.7 → Paraphrase Detection / MRPC / F1 / 83.7 | [3] | [3] | correct |
| 4: Text Similarity / STS-B / Spearman Correlation / 84.2 | #4: STS-B (Semantic Textual Similarity Benchmark) / STS-B / Spearman correlation coefficient (scc) / 84.2 → Text Similarity / STS-B / Spearman Correlation / 84.2 | [4] | [4] | correct |
| 5: Paraphrase Detection / QQP / F1 / 71.7 | #5: QQP (Quora Question Pairs) sentence similarity / QQP / F1 / 71.7 → Text Similarity / QQP / F1 / 71.7 | [5] | [] | numeric_match_but_binding_or_label_mismatch |
| 6: Natural Language Inference (NLI) / MNLI-m / Accuracy / 84.3 | #6: MNLI-m (Multi-Genre Natural Language Inference - matched) / MNLI-m / Accuracy / 84.3 → Natural Language Inference (NLI) / MNLI-m / Accuracy / 84.3 | [6] | [6] | correct |
| 7: Natural Language Inference (NLI) / MNLI-mm / Accuracy / 83.8 | #7: MNLI-mm (Multi-Genre Natural Language Inference - mismatched) / MNLI-mm / Accuracy / 83.8 → Natural Language Inference (NLI) / MNLI-mm / Accuracy / 83.8 | [7] | [7] | correct |
| 8: Natural Language Inference (NLI) / QNLI / Accuracy / 89.8 | #8: QNLI (Question Natural Language Inference) / QNLI / Accuracy / 89.8 → Natural Language Inference (NLI) / QNLI / Accuracy / 89.8 | [8] | [8] | correct |
| 9: Natural Language Inference (NLI) / RTE / Accuracy / 63.7 | — | [] | [] | numeric_result_missing_or_changed |
| 10: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.5 | — | [] | [] | numeric_result_missing_or_changed |
| 11: Constituency Parsing / Penn Treebank (PTB) / F1 / 95.6 | #10: Named Entity Recognition / CoNLL-2003 / Test F1 / 95.6 → Named Entity Recognition (NER) / None / F1 / 95.6 | [10] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | CoLA (Corpus of Linguistic Acceptability) classification / CoLA / Matthews correlation coefficient (mcc) / 56.6 | Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 56.6 |
| 2 | SST-2 (Stanford Sentiment Treebank) classification / SST-2 / Accuracy / 94.6 | Sentiment Analysis / SST-2 / Accuracy / 94.6 |
| 3 | MRPC (Microsoft Research Paraphrase Corpus) sentence similarity / MRPC / F1 / 83.7 | Paraphrase Detection / MRPC / F1 / 83.7 |
| 4 | STS-B (Semantic Textual Similarity Benchmark) / STS-B / Spearman correlation coefficient (scc) / 84.2 | Text Similarity / STS-B / Spearman Correlation / 84.2 |
| 5 | QQP (Quora Question Pairs) sentence similarity / QQP / F1 / 71.7 | Text Similarity / QQP / F1 / 71.7 |
| 6 | MNLI-m (Multi-Genre Natural Language Inference - matched) / MNLI-m / Accuracy / 84.3 | Natural Language Inference (NLI) / MNLI-m / Accuracy / 84.3 |
| 7 | MNLI-mm (Multi-Genre Natural Language Inference - mismatched) / MNLI-mm / Accuracy / 83.8 | Natural Language Inference (NLI) / MNLI-mm / Accuracy / 83.8 |
| 8 | QNLI (Question Natural Language Inference) / QNLI / Accuracy / 89.8 | Natural Language Inference (NLI) / QNLI / Accuracy / 89.8 |
| 9 | RTE (Recognizing Textual Entailment) / RTE / Accuracy / 65.1 | Natural Language Inference (NLI) / RTE / Accuracy / 65.1 |
| 10 | Named Entity Recognition / CoNLL-2003 / Test F1 / 95.6 | Named Entity Recognition (NER) / None / F1 / 95.6 |

## 1912.08777.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / XSum / ROGUE-1 / 47.21 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Summarization / XSum / ROGUE-2 / 24.56 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Summarization / XSum / ROGUE-L / 39.25 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Summarization / CNN/DailyMail / ROGUE-1 / 44.17 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Summarization / CNN/DailyMail / ROGUE-2 / 21.47 | — | [] | [] | numeric_result_missing_or_changed |
| 6: Summarization / CNN/DailyMail / ROGUE-L / 41.11 | — | [] | [] | numeric_result_missing_or_changed |
| 7: Summarization / Newsroom / ROGUE-1 / 45.15 | — | [] | [] | numeric_result_missing_or_changed |
| 8: Summarization / Newsroom / ROGUE-2 / 33.51 | — | [] | [] | numeric_result_missing_or_changed |
| 9: Summarization / Newsroom / ROGUE-L / 41.33 | — | [] | [] | numeric_result_missing_or_changed |
| 10: Summarization / Multi-News / ROGUE-1 / 47.52 | — | [] | [] | numeric_result_missing_or_changed |
| 11: Summarization / Multi-News / ROGUE-2 / 18.72 | — | [] | [] | numeric_result_missing_or_changed |
| 12: Summarization / Multi-News / ROGUE-L / 24.91 | — | [] | [] | numeric_result_missing_or_changed |
| 13: Summarization / Gigaword / ROGUE-1 / 39.12 | — | [] | [] | numeric_result_missing_or_changed |
| 14: Summarization / Gigaword / ROGUE-2 / 19.86 | — | [] | [] | numeric_result_missing_or_changed |
| 15: Summarization / Gigaword / ROGUE-L / 36.24 | — | [] | [] | numeric_result_missing_or_changed |
| 16: Summarization / WikiHow / ROGUE-1 / 43.06 | — | [] | [] | numeric_result_missing_or_changed |
| 17: Summarization / WikiHow / ROGUE-2 / 19.71 | — | [] | [] | numeric_result_missing_or_changed |
| 18: Summarization / WikiHow / ROGUE-L / 34.8 | — | [] | [] | numeric_result_missing_or_changed |
| 19: Summarization / Reddit TIFU / ROGUE-1 / 26.63 | — | [] | [] | numeric_result_missing_or_changed |
| 20: Summarization / Reddit TIFU / ROGUE-2 / 9.01 | — | [] | [] | numeric_result_missing_or_changed |
| 21: Summarization / Reddit TIFU / ROGUE-L / 21.64 | — | [] | [] | numeric_result_missing_or_changed |
| 22: Summarization / BIGPATENT / ROGUE-1 / 53.63 | — | [] | [] | numeric_result_missing_or_changed |
| 23: Summarization / BIGPATENT / ROGUE-2 / 33.16 | — | [] | [] | numeric_result_missing_or_changed |
| 24: Summarization / BIGPATENT / ROGUE-L / 42.25 | — | [] | [] | numeric_result_missing_or_changed |
| 25: Summarization / arXiv / ROGUE-1 / 44.7 | — | [] | [] | numeric_result_missing_or_changed |
| 26: Summarization / arXiv / ROGUE-2 / 17.27 | — | [] | [] | numeric_result_missing_or_changed |
| 27: Summarization / arXiv / ROGUE-L / 25.8 | — | [] | [] | numeric_result_missing_or_changed |
| 28: Summarization / PubMed / ROGUE-1 / 45.49 | — | [] | [] | numeric_result_missing_or_changed |
| 29: Summarization / PubMed / ROGUE-2 / 19.9 | — | [] | [] | numeric_result_missing_or_changed |
| 30: Summarization / PubMed / ROGUE-L / 27.69 | — | [] | [] | numeric_result_missing_or_changed |
| 31: Summarization / AESLC / ROGUE-1 / 37.69 | — | [] | [] | numeric_result_missing_or_changed |
| 32: Summarization / AESLC / ROGUE-2 / 21.85 | — | [] | [] | numeric_result_missing_or_changed |
| 33: Summarization / AESLC / ROGUE-L / 36.84 | — | [] | [] | numeric_result_missing_or_changed |
| 34: Summarization / BillSum / ROGUE-1 / 57.31 | — | [] | [] | numeric_result_missing_or_changed |
| 35: Summarization / BillSum / ROGUE-2 / 40.19 | — | [] | [] | numeric_result_missing_or_changed |
| 36: Summarization / BillSum / ROGUE-L / 45.82 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Abstractive Summarization / XSum / ROUGE-1/ROUGE-2/ROUGE-L F1 / 47.60/24.83/39.64 | Summarization / XSum / None / 47.60/24.83/39.64 |
| 2 | Abstractive Summarization / CNN/DailyMail / ROUGE-1/ROUGE-2/ROUGE-L F1 / 44.16/21.56/41.30 | Summarization / CNN/DailyMail / ROGUE-1 / 44.16/21.56/41.30 |
| 3 | Abstractive Summarization / NEWSROOM / ROUGE-1/ROUGE-2/ROUGE-L F1 / 45.98/34.20/42.18 | Summarization / Newsroom / None / 45.98/34.20/42.18 |
| 4 | Abstractive Summarization / Multi-News / ROUGE-1/ROUGE-2/ROUGE-L F1 / 47.65/18.75/24.95 | Summarization / Multi-News / None / 47.65/18.75/24.95 |
| 5 | Abstractive Summarization / Gigaword / ROUGE-1/ROUGE-2/ROUGE-L F1 / 39.65/20.47/36.76 | Summarization / Gigaword / None / 39.65/20.47/36.76 |
| 6 | Abstractive Summarization / WikiHow / ROUGE-1/ROUGE-2/ROUGE-L F1 / 46.39/22.12/38.41 | Summarization / WikiHow / ROGUE-1 / 46.39/22.12/38.41 |
| 7 | Abstractive Summarization / Reddit TIFU / ROUGE-1/ROUGE-2/ROUGE-L F1 / 27.99/9.81/22.94 | Summarization / Reddit TIFU / None / 27.99/9.81/22.94 |
| 8 | Abstractive Summarization / BIGPATENT / ROUGE-1/ROUGE-2/ROUGE-L F1 / 52.29/33.08/41.66 | Summarization / BIGPATENT / ROGUE-1 / 52.29/33.08/41.66 |
| 9 | Abstractive Summarization / arXiv / ROUGE-1/ROUGE-2/ROUGE-L F1 / 44.21/16.95/25.67 | Summarization / arXiv / ROGUE-1 / 44.21/16.95/25.67 |
| 10 | Abstractive Summarization / PubMed / ROUGE-1/ROUGE-2/ROUGE-L F1 / 45.97/20.15/28.25 | Summarization / PubMed / ROGUE-1 / 45.97/20.15/28.25 |
| 11 | Abstractive Summarization / AESLC / ROUGE-1/ROUGE-2/ROUGE-L F1 / 37.68/21.25/36.51 | Summarization / AESLC / ROGUE-1 / 37.68/21.25/36.51 |
| 12 | Abstractive Summarization / BillSum / ROUGE-1/ROUGE-2/ROUGE-L F1 / 59.67/41.58/47.59 | Summarization / BillSum / ROGUE-1 / 59.67/41.58/47.59 |
| 13 | Abstractive Summarization (Human Evaluation) / XSum / Likert Scale (1-5) / 3.2 | Summarization / XSum / None / 3.2 |
| 14 | Abstractive Summarization (Human Evaluation) / CNN/DailyMail / Likert Scale (1-5) / 3.4 | Summarization / CNN/DailyMail / None / 3.4 |
| 15 | Abstractive Summarization (Human Evaluation) / Reddit TIFU / Likert Scale (1-5) / 2.8 | Summarization / Reddit TIFU / None / 2.8 |

## 1711.05568.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.3 | #1: Dialogue Act Recognition / Switchboard Dialogue Act Corpus (SwDA) / Accuracy / 81.3 → Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.3 | [1] | [1] | correct |
| 2: Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 91.7 | #2: Dialogue Act Recognition / ICSI Meeting Recorder Dialogue Act Corpus (MRDA) / Accuracy / 91.7 → Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 91.7 | [2] | [2] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Dialogue Act Recognition / Switchboard Dialogue Act Corpus (SwDA) / Accuracy / 81.3 | Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.3 |
| 2 | Dialogue Act Recognition / ICSI Meeting Recorder Dialogue Act Corpus (MRDA) / Accuracy / 91.7 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 91.7 |

## wang19f.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Language Modeling / WikiText-103 / Perplexity / 28.0 | #3: Neural Language Modeling / Wikitext-103 (WT103) / Test Perplexity / 28.0 → Language Modeling / WikiText-103 / Perplexity / 28.0 | [3] | [3] | correct |
| 2: Language Modeling / Penn Treebank (PTB) / Perplexity / 46.01 | #1: Neural Language Modeling / Penn Treebank (PTB) / Test Perplexity / 46.01 → Language Modeling / Penn Treebank (PTB) / Perplexity / 46.01 | [1] | [1] | correct |
| 3: Language Modeling / Wikitext-2 / Perplexity / 38.65 | #2: Neural Language Modeling / Wikitext-2 (WT2) / Test Perplexity / 38.65 → Language Modeling / Wikitext-2 / Perplexity / 38.65 | [2] | [2] | correct |
| 4: Machine Translation / WMT’14 EN-DE / BLEU / 29.52 | #4: Neural Machine Translation / WMT2014 English→German / BLEU / 29.52 → Machine Translation / WMT’14 EN-DE / BLEU / 29.52 | [4] | [4] | correct |
| 5: Machine Translation / IWSLT’14 EN-DE / BLEU / 35.18 | #5: Neural Machine Translation / IWSLT2014 German→English / BLEU / 35.18 → Machine Translation / IWSLT’14 EN-DE / BLEU / 35.18 | [5] | [5] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Neural Language Modeling / Penn Treebank (PTB) / Test Perplexity / 46.01 | Language Modeling / Penn Treebank (PTB) / Perplexity / 46.01 |
| 2 | Neural Language Modeling / Wikitext-2 (WT2) / Test Perplexity / 38.65 | Language Modeling / Wikitext-2 / Perplexity / 38.65 |
| 3 | Neural Language Modeling / Wikitext-103 (WT103) / Test Perplexity / 28.0 | Language Modeling / WikiText-103 / Perplexity / 28.0 |
| 4 | Neural Machine Translation / WMT2014 English→German / BLEU / 29.52 | Machine Translation / WMT’14 EN-DE / BLEU / 29.52 |
| 5 | Neural Machine Translation / IWSLT2014 German→English / BLEU / 35.18 | Machine Translation / IWSLT’14 EN-DE / BLEU / 35.18 |

## 128538.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / WNUT-16 - English / F1 / 53.48 | #1: Named Entity Recognition / WNUT 2016 / F1 score / 53.48 → Named Entity Recognition (NER) / None / F1 / 53.48 | [1] | [] | normalization_null |
| 2: Named Entity Recognition (NER) / WNUT-17 - English / F1 / 50.52 | #2: Named Entity Recognition / WNUT 2017 / F1 score / 50.52 → Named Entity Recognition (NER) / None / F1 / 50.52 | [2] | [] | normalization_null |
| 3: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.76 | #3: Named Entity Recognition / CoNLL 2003 (English) / F1 score / 93.76 → Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.76 | [3] | [3] | correct |
| 4: Named Entity Recognition (NER) / Multimodal / F1 / 74.17 | #4: Named Entity Recognition (Multimodal) / Multimodal / F1 score / 74.17 → None / Multimodal / F1 / 74.17 | [4] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / WNUT 2016 / F1 score / 53.48 | Named Entity Recognition (NER) / None / F1 / 53.48 |
| 2 | Named Entity Recognition / WNUT 2017 / F1 score / 50.52 | Named Entity Recognition (NER) / None / F1 / 50.52 |
| 3 | Named Entity Recognition / CoNLL 2003 (English) / F1 score / 93.76 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.76 |
| 4 | Named Entity Recognition (Multimodal) / Multimodal / F1 score / 74.17 | None / Multimodal / F1 / 74.17 |

## 1511.08308.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.62 | #1: Named Entity Recognition / CoNLL-2003 / F1 / 91.62 → Named Entity Recognition (NER) / None / F1 / 91.62 | [1] | [] | normalization_null |
| 2: Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 86.28 | #2: Named Entity Recognition / OntoNotes 5.0 / F1 / 86.28 → Named Entity Recognition (NER) / None / F1 / 86.28 | [2] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / CoNLL-2003 / F1 / 91.62 | Named Entity Recognition (NER) / None / F1 / 91.62 |
| 2 | Named Entity Recognition / OntoNotes 5.0 / F1 / 86.28 | Named Entity Recognition (NER) / None / F1 / 86.28 |

## 1603.01354.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / Precision / 91.35 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Named Entity Recognition (NER) / CoNLL-2003 - English / Recall / 91.06 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.21 | #2: Named Entity Recognition (NER) / CoNLL 2003 English / F1 / 91.21 → Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.21 | [2] | [2] | correct |
| 4: Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.55 | #1: POS Tagging / Wall Street Journal (WSJ) portion of Penn Treebank (PTB) / Accuracy / 97.55 → Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.55 | [1] | [1] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | POS Tagging / Wall Street Journal (WSJ) portion of Penn Treebank (PTB) / Accuracy / 97.55 | Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.55 |
| 2 | Named Entity Recognition (NER) / CoNLL 2003 English / F1 / 91.21 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.21 |

## 1804.09849.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Machine Translation / WMT’14 EN-FR / BLEU / 41.0 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Machine Translation / WMT’14 EN-DE / BLEU / 28.49 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Neural Machine Translation (English to French) / WMT'14 En→Fr / Test BLEU / 41.67 ± 0.11 | Machine Translation / WMT’14 EN-FR / BLEU / 41.67 ± 0.11 |
| 2 | Neural Machine Translation (English to German) / WMT'14 En→De / Test BLEU / 28.84 ± 0.06 | Machine Translation / WMT’14 EN-DE / BLEU / 28.84 ± 0.06 |

## 1806.03489.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.73 | — | [1] | [] | numeric_result_missing_or_changed |
| 2: Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 87.95 | — | [2] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / CONLL-2003 / Mention-level F1 score / 91.73 (± 0.10) | Named Entity Recognition (NER) / None / F1 / 91.73 (± 0.10) |
| 2 | Named Entity Recognition / ONTONOTES 5.0 / Mention-level F1 score / 87.95 (± 0.13) | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 87.95 (± 0.13) |
| 3 | Named Entity Recognition / ONTONOTES 5.0 (Broadcast Conversation genre) / Mention-level F1 score / 86.33 | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 86.33 |
| 4 | Named Entity Recognition / ONTONOTES 5.0 (Broadcast News genre) / Mention-level F1 score / 90.46 | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 90.46 |
| 5 | Named Entity Recognition / ONTONOTES 5.0 (Magazine genre) / Mention-level F1 score / 85.91 | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 85.91 |
| 6 | Named Entity Recognition / ONTONOTES 5.0 (Newswire genre) / Mention-level F1 score / 89.75 | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 89.75 |
| 7 | Named Entity Recognition / ONTONOTES 5.0 (Telephone Conversation genre) / Mention-level F1 score / 76.17 | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 76.17 |
| 8 | Named Entity Recognition / ONTONOTES 5.0 (Blogs and Newsgroups genre) / Mention-level F1 score / 80.39 | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 80.39 |

## 1808.08745.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / XSum / ROGUE-1 / 31.89 | #1: Extreme summarization / XSum / ROUGE-1 F1 / 31.89 → Summarization / XSum / ROGUE-1 / 31.89 | [1] | [1] | correct |
| 2: Summarization / XSum / ROGUE-2 / 11.54 | #2: Extreme summarization / XSum / ROUGE-2 F1 / 11.54 → Summarization / XSum / ROGUE-2 / 11.54 | [2] | [2] | correct |
| 3: Summarization / XSum / ROGUE-L / 25.75 | #3: Extreme summarization / XSum / ROUGE-L F1 / 25.75 → Summarization / XSum / None / 25.75 | [3] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Extreme summarization / XSum / ROUGE-1 F1 / 31.89 | Summarization / XSum / ROGUE-1 / 31.89 |
| 2 | Extreme summarization / XSum / ROUGE-2 F1 / 11.54 | Summarization / XSum / ROGUE-2 / 11.54 |
| 3 | Extreme summarization / XSum / ROUGE-L F1 / 25.75 | Summarization / XSum / None / 25.75 |
| 4 | Extreme summarization / XSum / Human QA-based evaluation (percentage of questions answered correctly) / 46.05 | Summarization / XSum / Overall-Accuracy / 46.05 |
| 5 | Extreme summarization / XSum / Human ranking score / 0.037 | Summarization / XSum / None / 0.037 |

## 1809.08370.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Combinatory Categorial Grammar (CCG) Supertagging / CCGBank / Accuracy / 96.1 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Text Chunking / CoNLL-2000 / F1 / 97.0 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 92.6 | — | [3] | [] | numeric_result_missing_or_changed |
| 4: Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 88.8 | — | [4] | [] | numeric_result_missing_or_changed |
| 5: Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.74 | #5: Part-of-Speech (POS) Tagging / Penn Treebank (WSJ) / Accuracy / 97.74 → Part-of-Speech (POS) Tagging / None / Accuracy / 97.74 | [5] | [] | normalization_null |
| 6: Dependency Parsing / Penn Treebank (PTB) / Unlabeled Attachment Score / 96.6 | — | [6] | [] | numeric_result_missing_or_changed |
| 7: Dependency Parsing / Penn Treebank (PTB) / Labeled Attachment Score / 95.0 | — | [7] | [] | numeric_result_missing_or_changed |
| 8: Machine Translation / IWSLT’15 EN-VI / BLEU / 29.6 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Combinatory Categorial Grammar (CCG) Supertagging / CCGBank / Accuracy / 96.05 | Combinatory Categorial Grammar (CCG) Supertagging / CCGBank / Accuracy / 96.05 |
| 2 | Text Chunking / CoNLL-2000 / F1 / 96.98 | Text Chunking / CoNLL-2000 / F1 / 96.98 |
| 3 | Named Entity Recognition (NER) / CoNLL-2003 / F1 / 92.61 | Named Entity Recognition (NER) / None / F1 / 92.61 |
| 4 | Fine-Grained NER (FGN) / OntoNotes / F1 / 88.81 | Named Entity Recognition (NER) / None / F1 / 88.81 |
| 5 | Part-of-Speech (POS) Tagging / Penn Treebank (WSJ) / Accuracy / 97.74 | Part-of-Speech (POS) Tagging / None / Accuracy / 97.74 |
| 6 | Dependency Parsing / Penn Treebank (Stanford Dependencies v3.3.0) / UAS / 96.61 | Dependency Parsing / None / Unlabeled Attachment Score / 96.61 |
| 7 | Dependency Parsing / Penn Treebank (Stanford Dependencies v3.3.0) / LAS / 95.02 | Dependency Parsing / None / Labeled Attachment Score / 95.02 |
| 8 | Machine Translation (English-Vietnamese) / IWSLT 2015 (tst2013 test set) / BLEU / 29.58 | Machine Translation / IWSLT’15 EN-VI / BLEU / 29.58 |

## 1811.05021.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.5 | #1: Dialogue Act Classification / SwDA / Accuracy / 81.5 → Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.5 | [1] | [1] | correct |
| 2: Dialogue Act Classification / MapTask / Accuracy / 68.5 | #2: Dialogue Act Classification / MapTask / Accuracy / 68.5 → Dialogue Act Classification / MapTask / Accuracy / 68.5 | [2] | [2] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Dialogue Act Classification / SwDA / Accuracy / 81.5 | Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.5 |
| 2 | Dialogue Act Classification / MapTask / Accuracy / 68.5 | Dialogue Act Classification / MapTask / Accuracy / 68.5 |

## 1811.09242.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) / 9.55 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) / 62.2 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Word Sense Induction / SemEval 2013 Task 13 / AVG / 24.37 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Word Sense Induction / SemEval 2010 Task 14 / F-Score (F-S) / 62.9 | #1: Word Sense Induction / SemEval 2010 Task 14 / F-Score / 62.9 → Word Sense Induction / SemEval 2010 Task 14 / F-Score (F-S) / 62.9 | [1] | [1] | correct |
| 5: Word Sense Induction / SemEval 2010 Task 14 / V-Measure (V-M) / 10.1 | — | [] | [] | numeric_result_missing_or_changed |
| 6: Word Sense Induction / SemEval 2010 Task 14 / AVG / 25.2 | #2: Word Sense Induction / SemEval 2010 Task 14 / V-Measure / 25.20 → Word Sense Induction / SemEval 2010 Task 14 / V-Measure (V-M) / 25.20 | [2] | [] | numeric_match_but_binding_or_label_mismatch |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Word Sense Induction / SemEval 2010 Task 14 / F-Score / 62.9 | Word Sense Induction / SemEval 2010 Task 14 / F-Score (F-S) / 62.9 |
| 2 | Word Sense Induction / SemEval 2010 Task 14 / V-Measure / 25.20 | Word Sense Induction / SemEval 2010 Task 14 / V-Measure (V-M) / 25.20 |
| 3 | Word Sense Induction / SemEval 2013 Task 13 / F-BC / 61.7 | Word Sense Induction / SemEval 2013 Task 13 / None / 61.7 |
| 4 | Word Sense Induction / SemEval 2013 Task 13 / F-NMI / 7.97 | Word Sense Induction / SemEval 2013 Task 13 / None / 7.97 |
| 5 | Word Sense Induction / SemEval 2013 Task 13 / AVG / 22.17 | Word Sense Induction / SemEval 2013 Task 13 / AVG / 22.17 |
| 6 | Word Sense Induction / Arnet / F-Score / 58.8 | Word Sense Induction / None / F-Score (F-S) / 58.8 |
| 7 | Word Sense Induction / PubMed / F-Score / 46.6 | Word Sense Induction / PubMed / F-Score (F-S) / 46.6 |

## 1812.09471.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Intent Detection and Slot Filling / ATIS / F1 / 0.952 | #4: Slot Filling / ATIS / F1 / 0.952 → Intent Detection and Slot Filling / ATIS / F1 / 0.952 | [4] | [4] | correct |
| 2: Intent Detection and Slot Filling / ATIS / Accuracy / 0.95 | — | [4] | [] | numeric_result_missing_or_changed |
| 3: Intent Detection and Slot Filling / ATIS / Overall-Accuracy / 0.834 | #6: Overall Accuracy (Joint Slot Filling and Intent Detection) / ATIS / Accuracy / 0.834 → Intent Detection and Slot Filling / ATIS / Accuracy / 0.834 | [6] | [] | numeric_match_but_binding_or_label_mismatch |
| 4: Intent Detection and Slot Filling / SNIPS / F1 / 0.918 | #1: Slot Filling / SNIPS-NLU / F1 / 0.918 → Intent Detection and Slot Filling / None / F1 / 0.918 | [1] | [] | normalization_null |
| 5: Intent Detection and Slot Filling / SNIPS / Accuracy / 0.977 | #2: Intent Detection / SNIPS-NLU / Accuracy / 0.977 → Intent Detection and Slot Filling / None / Accuracy / 0.977 | [2] | [] | normalization_null |
| 6: Intent Detection and Slot Filling / SNIPS / Overall-Accuracy / 0.809 | #3: Overall Accuracy (Joint Slot Filling and Intent Detection) / SNIPS-NLU / Accuracy / 0.809 → Intent Detection and Slot Filling / None / Accuracy / 0.809 | [3] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Slot Filling / SNIPS-NLU / F1 / 0.918 | Intent Detection and Slot Filling / None / F1 / 0.918 |
| 2 | Intent Detection / SNIPS-NLU / Accuracy / 0.977 | Intent Detection and Slot Filling / None / Accuracy / 0.977 |
| 3 | Overall Accuracy (Joint Slot Filling and Intent Detection) / SNIPS-NLU / Accuracy / 0.809 | Intent Detection and Slot Filling / None / Accuracy / 0.809 |
| 4 | Slot Filling / ATIS / F1 / 0.952 | Intent Detection and Slot Filling / ATIS / F1 / 0.952 |
| 5 | Intent Detection / ATIS / Accuracy / 0.948 | Intent Detection and Slot Filling / ATIS / Accuracy / 0.948 |
| 6 | Overall Accuracy (Joint Slot Filling and Intent Detection) / ATIS / Accuracy / 0.834 | Intent Detection and Slot Filling / ATIS / Accuracy / 0.834 |

## 1812.10235.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Intent Detection and Slot Filling / ATIS / F1 / 96.89 | — | [2] | [] | numeric_result_missing_or_changed |
| 2: Intent Detection and Slot Filling / ATIS / Accuracy / 98.99 | — | [1] | [] | numeric_result_missing_or_changed |
| 3: Intent Detection and Slot Filling / Multi-domain Movie / F1 / 93.8 | — | [4] | [] | numeric_result_missing_or_changed |
| 4: Intent Detection and Slot Filling / Multi-domain Movie / Accuracy / 95.91 | — | [3] | [] | numeric_result_missing_or_changed |
| 5: Intent Detection and Slot Filling / Multi-domain Home / F1 / 95.8 | — | [6] | [] | numeric_result_missing_or_changed |
| 6: Intent Detection and Slot Filling / Multi-domain Home / Accuracy / 99.49 | — | [5] | [] | numeric_result_missing_or_changed |
| 7: Intent Detection and Slot Filling / Multi-domain Food / F1 / 98.2 | — | [8] | [] | numeric_result_missing_or_changed |
| 8: Intent Detection and Slot Filling / Multi-domain Food / Accuracy / 99.27 | — | [7] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Intent Detection / ATIS / Accuracy / 98.99% | Intent Detection and Slot Filling / ATIS / Accuracy / 98.99% |
| 2 | Slot Filling / ATIS / F1 Score / 96.89% | Intent Detection and Slot Filling / ATIS / F1 / 96.89% |
| 3 | Intent Detection / Internal Multi-domain (Movie) / Accuracy / 95.91% | Intent Detection and Slot Filling / Multi-domain Movie / Accuracy / 95.91% |
| 4 | Slot Filling / Internal Multi-domain (Movie) / F1 Score / 93.8% | Intent Detection and Slot Filling / Multi-domain Movie / F1 / 93.8% |
| 5 | Intent Detection / Internal Multi-domain (Food) / Accuracy / 99.49% | Intent Detection and Slot Filling / Multi-domain Food / Accuracy / 99.49% |
| 6 | Slot Filling / Internal Multi-domain (Food) / F1 Score / 95.8% | Intent Detection and Slot Filling / Multi-domain Food / F1 / 95.8% |
| 7 | Intent Detection / Internal Multi-domain (Home) / Accuracy / 99.27% | Intent Detection and Slot Filling / Multi-domain Home / Accuracy / 99.27% |
| 8 | Slot Filling / Internal Multi-domain (Home) / F1 Score / 98.2% | Intent Detection and Slot Filling / Multi-domain Home / F1 / 98.2% |

## 1901.10430.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Machine Translation / WMT’14 EN-FR / BLEU / 43.2 | #2: Machine Translation / WMT English-French (newstest2014) / BLEU / 43.2 → Machine Translation / WMT’14 EN-FR / BLEU / 43.2 | [2] | [2] | correct |
| 2: Machine Translation / WMT’14 EN-DE / BLEU / 29.7 | #1: Machine Translation / WMT English-German (newstest2014) / BLEU / 29.7 → Machine Translation / WMT’14 EN-DE / BLEU / 29.7 | [1] | [1] | correct |
| 3: Machine Translation / IWSLT’14 EN-DE / BLEU / 35.2 | #3: Machine Translation / IWSLT'14 German-English / BLEU / 35.2 → Machine Translation / None / BLEU / 35.2 | [3] | [] | normalization_null |
| 4: Machine Translation / WMT’17 EN-ZH / BLEU / 24.4 | #4: Machine Translation / WMT English-Chinese (newstest2017) / BLEU / 24.4 → Machine Translation / WMT’17 EN-ZH / BLEU / 24.4 | [4] | [4] | correct |
| 5: Summarization / CNN/DailyMail / ROGUE-1 / 39.84 | #6: Summarization / CNN-DailyMail / Rouge-1 / 39.84 → Summarization / CNN/DailyMail / None / 39.84 | [6] | [] | normalization_null |
| 6: Summarization / CNN/DailyMail / ROGUE-2 / 16.25 | #7: Summarization / CNN-DailyMail / Rouge-2 / 16.25 → Summarization / CNN/DailyMail / ROGUE-2 / 16.25 | [7] | [7] | correct |
| 7: Summarization / CNN/DailyMail / ROGUE-L / 36.73 | #8: Summarization / CNN-DailyMail / Rouge-L / 36.73 → Summarization / CNN/DailyMail / ROGUE-L / 36.73 | [8] | [8] | correct |
| 8: Language Modeling / Google Billion Word / Perplexity / 26.67 | #5: Language Modeling / Google Billion Word / Perplexity / 26.67 → Language Modeling / Google Billion Word / Perplexity / 26.67 | [5] | [5] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Machine Translation / WMT English-German (newstest2014) / BLEU / 29.7 | Machine Translation / WMT’14 EN-DE / BLEU / 29.7 |
| 2 | Machine Translation / WMT English-French (newstest2014) / BLEU / 43.2 | Machine Translation / WMT’14 EN-FR / BLEU / 43.2 |
| 3 | Machine Translation / IWSLT'14 German-English / BLEU / 35.2 | Machine Translation / None / BLEU / 35.2 |
| 4 | Machine Translation / WMT English-Chinese (newstest2017) / BLEU / 24.4 | Machine Translation / WMT’17 EN-ZH / BLEU / 24.4 |
| 5 | Language Modeling / Google Billion Word / Perplexity / 26.67 | Language Modeling / Google Billion Word / Perplexity / 26.67 |
| 6 | Summarization / CNN-DailyMail / Rouge-1 / 39.84 | Summarization / CNN/DailyMail / None / 39.84 |
| 7 | Summarization / CNN-DailyMail / Rouge-2 / 16.25 | Summarization / CNN/DailyMail / ROGUE-2 / 16.25 |
| 8 | Summarization / CNN-DailyMail / Rouge-L / 36.73 | Summarization / CNN/DailyMail / ROGUE-L / 36.73 |

## 1905.12598.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) / 21.4 | — | [1] | [] | numeric_result_missing_or_changed |
| 2: Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) / 64.0 | — | [2] | [] | numeric_result_missing_or_changed |
| 3: Word Sense Induction / SemEval 2013 Task 13 / AVG / 37.0 | — | [3] | [] | numeric_result_missing_or_changed |
| 4: Word Sense Induction / SemEval 2010 Task 14 / F-Score (F-S) / 71.3 | — | [4] | [] | numeric_result_missing_or_changed |
| 5: Word Sense Induction / SemEval 2010 Task 14 / V-Measure (V-M) / 40.4 | — | [5] | [] | numeric_result_missing_or_changed |
| 6: Word Sense Induction / SemEval 2010 Task 14 / AVG / 53.6 | — | [6] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Word Sense Induction (WSI) / SemEval 2013 Task 13 / FNMI / 21.4 (0.5) | Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) / 21.4 (0.5) |
| 2 | Word Sense Induction (WSI) / SemEval 2013 Task 13 / FBC / 64.0 (0.5) | Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) / 64.0 (0.5) |
| 3 | Word Sense Induction (WSI) / SemEval 2013 Task 13 / AVG / 37.0 (0.5) | Word Sense Induction / SemEval 2013 Task 13 / AVG / 37.0 (0.5) |
| 4 | Word Sense Induction (WSI) / SemEval 2010 Task 14 / F-S / 71.3 (0.1) | Word Sense Induction / SemEval 2010 Task 14 / F-Score (F-S) / 71.3 (0.1) |
| 5 | Word Sense Induction (WSI) / SemEval 2010 Task 14 / V-M / 40.4 (1.8) | Word Sense Induction / SemEval 2010 Task 14 / V-Measure (V-M) / 40.4 (1.8) |
| 6 | Word Sense Induction (WSI) / SemEval 2010 Task 14 / AVG / 53.6 (1.2) | Word Sense Induction / SemEval 2010 Task 14 / AVG / 53.6 (1.2) |

## 1906.05012.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / Gigaword / ROGUE-1 / 39.11 | #1: Abstractive sentence summarization / Annotated English Gigaword / ROUGE-1 / 39.11 → Summarization / Gigaword / None / 39.11 | [1] | [] | normalization_null |
| 2: Summarization / Gigaword / ROGUE-2 / 19.78 | #2: Abstractive sentence summarization / Annotated English Gigaword / ROUGE-2 / 19.78 → Summarization / Gigaword / None / 19.78 | [2] | [] | normalization_null |
| 3: Summarization / Gigaword / ROGUE-L / 36.87 | #3: Abstractive sentence summarization / Annotated English Gigaword / ROUGE-L / 36.87 → Summarization / Gigaword / None / 36.87 | [3] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Abstractive sentence summarization / Annotated English Gigaword / ROUGE-1 / 39.11 | Summarization / Gigaword / None / 39.11 |
| 2 | Abstractive sentence summarization / Annotated English Gigaword / ROUGE-2 / 19.78 | Summarization / Gigaword / None / 19.78 |
| 3 | Abstractive sentence summarization / Annotated English Gigaword / ROUGE-L / 36.87 | Summarization / Gigaword / None / 36.87 |

## 1907.00390.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Intent Detection and Slot Filling / ATIS / F1 / 95.8 | #1: Slot Filling / ATIS / F1-score / 95.80 → Intent Detection and Slot Filling / ATIS / F1 / 95.80 | [1] | [1] | correct |
| 2: Intent Detection and Slot Filling / ATIS / Accuracy / 97.76 | #2: Intent Detection / ATIS / Accuracy / 97.76 → Intent Detection and Slot Filling / ATIS / Accuracy / 97.76 | [2] | [2] | correct |
| 3: Intent Detection and Slot Filling / ATIS / Sent-Accuracy / 86.9 | #3: Sentence-level Semantic Frame Accuracy / ATIS / Sentence Accuracy / 86.90 → None / ATIS / Sent-Accuracy / 86.90 | [3] | [] | normalization_null |
| 4: Intent Detection and Slot Filling / SNIPS / F1 / 92.23 | #4: Slot Filling / Snips / F1-score / 92.23 → Intent Detection and Slot Filling / SNIPS / F1 / 92.23 | [4] | [4] | correct |
| 5: Intent Detection and Slot Filling / SNIPS / Accuracy / 97.43 | #5: Intent Detection / Snips / Accuracy / 97.43 → Intent Detection and Slot Filling / SNIPS / Accuracy / 97.43 | [5] | [5] | correct |
| 6: Intent Detection and Slot Filling / SNIPS / Sent-Accuracy / 80.57 | #6: Sentence-level Semantic Frame Accuracy / Snips / Sentence Accuracy / 80.57 → None / SNIPS / Sent-Accuracy / 80.57 | [6] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Slot Filling / ATIS / F1-score / 95.80 | Intent Detection and Slot Filling / ATIS / F1 / 95.80 |
| 2 | Intent Detection / ATIS / Accuracy / 97.76 | Intent Detection and Slot Filling / ATIS / Accuracy / 97.76 |
| 3 | Sentence-level Semantic Frame Accuracy / ATIS / Sentence Accuracy / 86.90 | None / ATIS / Sent-Accuracy / 86.90 |
| 4 | Slot Filling / Snips / F1-score / 92.23 | Intent Detection and Slot Filling / SNIPS / F1 / 92.23 |
| 5 | Intent Detection / Snips / Accuracy / 97.43 | Intent Detection and Slot Filling / SNIPS / Accuracy / 97.43 |
| 6 | Sentence-level Semantic Frame Accuracy / Snips / Sentence Accuracy / 80.57 | None / SNIPS / Sent-Accuracy / 80.57 |

## 1908.08345.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / CNN/DailyMail / ROGUE-1 / 43.85 | #1: Single-document news summarization (extractive) / CNN/DailyMail / ROUGE-1 F1 / 43.85 → Summarization / CNN/DailyMail / ROGUE-1 / 43.85 | [1] | [1] | correct |
| 2: Summarization / CNN/DailyMail / ROGUE-2 / 20.34 | #2: Single-document news summarization (extractive) / CNN/DailyMail / ROUGE-2 F1 / 20.34 → Summarization / CNN/DailyMail / ROGUE-2 / 20.34 | [2] | [2] | correct |
| 3: Summarization / CNN/DailyMail / ROGUE-L / 39.9 | #3: Single-document news summarization (extractive) / CNN/DailyMail / ROUGE-L F1 / 39.90 → Summarization / CNN/DailyMail / ROGUE-L / 39.90 | [3] | [3] | correct |
| 4: Summarization / XSum / ROGUE-1 / 38.81 | #13: Single-document news summarization (abstractive) / XSum / ROUGE-1 F1 / 38.81 → Summarization / XSum / ROGUE-1 / 38.81 | [13] | [13] | correct |
| 5: Summarization / XSum / ROGUE-2 / 16.5 | #14: Single-document news summarization (abstractive) / XSum / ROUGE-2 F1 / 16.50 → Summarization / XSum / ROGUE-2 / 16.50 | [14] | [14] | correct |
| 6: Summarization / XSum / ROGUE-L / 31.27 | #15: Single-document news summarization (abstractive) / XSum / ROUGE-L F1 / 31.27 → Summarization / XSum / ROGUE-L / 31.27 | [15] | [15] | correct |
| 7: Summarization / New York Times (NYT) / ROGUE-1 / 49.02 | — | [] | [] | numeric_result_missing_or_changed |
| 8: Summarization / New York Times (NYT) / ROGUE-2 / 31.02 | — | [] | [] | numeric_result_missing_or_changed |
| 9: Summarization / New York Times (NYT) / ROGUE-L / 45.55 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Single-document news summarization (extractive) / CNN/DailyMail / ROUGE-1 F1 / 43.85 | Summarization / CNN/DailyMail / ROGUE-1 / 43.85 |
| 2 | Single-document news summarization (extractive) / CNN/DailyMail / ROUGE-2 F1 / 20.34 | Summarization / CNN/DailyMail / ROGUE-2 / 20.34 |
| 3 | Single-document news summarization (extractive) / CNN/DailyMail / ROUGE-L F1 / 39.90 | Summarization / CNN/DailyMail / ROGUE-L / 39.90 |
| 4 | Single-document news summarization (abstractive) / CNN/DailyMail / ROUGE-1 F1 / 42.13 | Summarization / CNN/DailyMail / ROGUE-1 / 42.13 |
| 5 | Single-document news summarization (abstractive) / CNN/DailyMail / ROUGE-2 F1 / 19.60 | Summarization / CNN/DailyMail / None / 19.60 |
| 6 | Single-document news summarization (abstractive) / CNN/DailyMail / ROUGE-L F1 / 39.18 | Summarization / CNN/DailyMail / None / 39.18 |
| 7 | Single-document news summarization (extractive) / NYT / ROUGE-1 Recall / 46.66 | Summarization / New York Times (NYT) / None / 46.66 |
| 8 | Single-document news summarization (extractive) / NYT / ROUGE-2 Recall / 26.35 | Summarization / New York Times (NYT) / ROGUE-2 / 26.35 |
| 9 | Single-document news summarization (extractive) / NYT / ROUGE-L Recall / 42.62 | Summarization / New York Times (NYT) / None / 42.62 |
| 10 | Single-document news summarization (abstractive) / NYT / ROUGE-1 Recall / 48.92 | Summarization / New York Times (NYT) / None / 48.92 |
| 11 | Single-document news summarization (abstractive) / NYT / ROUGE-2 Recall / 30.84 | Summarization / New York Times (NYT) / ROGUE-2 / 30.84 |
| 12 | Single-document news summarization (abstractive) / NYT / ROUGE-L Recall / 45.41 | Summarization / New York Times (NYT) / None / 45.41 |
| 13 | Single-document news summarization (abstractive) / XSum / ROUGE-1 F1 / 38.81 | Summarization / XSum / ROGUE-1 / 38.81 |
| 14 | Single-document news summarization (abstractive) / XSum / ROUGE-2 F1 / 16.50 | Summarization / XSum / ROGUE-2 / 16.50 |
| 15 | Single-document news summarization (abstractive) / XSum / ROUGE-L F1 / 31.27 | Summarization / XSum / ROGUE-L / 31.27 |

## 1909.02188.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Intent Detection and Slot Filling / ATIS / F1 / 95.9 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Intent Detection and Slot Filling / ATIS / Accuracy / 96.9 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Intent Detection and Slot Filling / ATIS / Overall-Accuracy / 86.5 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Intent Detection and Slot Filling / SNIPS / F1 / 94.2 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Intent Detection and Slot Filling / SNIPS / Accuracy / 98.0 | — | [] | [] | numeric_result_missing_or_changed |
| 6: Intent Detection and Slot Filling / SNIPS / Overall-Accuracy / 86.9 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Slot Filling / SNIPS / F1 Score / 97.0 | Intent Detection and Slot Filling / SNIPS / F1 / 97.0 |
| 2 | Intent Detection / SNIPS / Accuracy / 98.6 | Intent Detection and Slot Filling / SNIPS / Accuracy / 98.6 |
| 3 | Sentence-level Semantic Frame Parsing / SNIPS / Overall Accuracy / 92.9 | None / SNIPS / Overall-Accuracy / 92.9 |
| 4 | Slot Filling / ATIS / F1 Score / 96.1 | Intent Detection and Slot Filling / ATIS / F1 / 96.1 |
| 5 | Intent Detection / ATIS / Accuracy / 97.5 | Intent Detection and Slot Filling / ATIS / Accuracy / 97.5 |
| 6 | Sentence-level Semantic Frame Parsing / ATIS / Overall Accuracy / 88.6 | None / ATIS / Overall-Accuracy / 88.6 |

## 1911.09483.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Machine Translation / WMT’14 EN-FR / BLEU / 43.5 | #2: Machine Translation (English-French) / WMT14 En-Fr / BLEU / 43.5 → Machine Translation / WMT’14 EN-FR / BLEU / 43.5 | [2] | [2] | correct |
| 2: Machine Translation / WMT’14 EN-DE / BLEU / 29.9 | #1: Machine Translation (English-German) / WMT14 En-De / BLEU / 29.9 → Machine Translation / WMT’14 EN-DE / BLEU / 29.9 | [1] | [1] | correct |
| 3: Machine Translation / IWSLT’15 EN-VI / BLEU / 31.3 | #4: Machine Translation (English-Vietnamese) / IWSLT 2015 En-Vi / BLEU / 31.3 → Machine Translation / IWSLT’15 EN-VI / BLEU / 31.3 | [4] | [4] | correct |
| 4: Machine Translation / IWSLT’14 EN-DE / BLEU / 36.3 | #3: Machine Translation (German-English) / IWSLT 2014 De-En / BLEU / 36.3 → Machine Translation / None / BLEU / 36.3 | [3] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Machine Translation (English-German) / WMT14 En-De / BLEU / 29.9 | Machine Translation / WMT’14 EN-DE / BLEU / 29.9 |
| 2 | Machine Translation (English-French) / WMT14 En-Fr / BLEU / 43.5 | Machine Translation / WMT’14 EN-FR / BLEU / 43.5 |
| 3 | Machine Translation (German-English) / IWSLT 2014 De-En / BLEU / 36.3 | Machine Translation / None / BLEU / 36.3 |
| 4 | Machine Translation (English-Vietnamese) / IWSLT 2015 En-Vi / BLEU / 31.3 | Machine Translation / IWSLT’15 EN-VI / BLEU / 31.3 |

## 1911.10390.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / Gigaword / ROGUE-1 / 39.19 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Summarization / Gigaword / ROGUE-2 / 20.47 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Summarization / Gigaword / ROGUE-L / 36.69 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Summarization / Gigaword / BERTScore / 61.51 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Summarization / Newsroom / ROGUE-1 / 45.93 | #1: Abstractive Summarization / NEWSROOM / ROUGE-1 / 45.93 → Summarization / Newsroom / None / 45.93 | [1] | [] | normalization_null |
| 6: Summarization / Newsroom / ROGUE-2 / 24.14 | #2: Abstractive Summarization / NEWSROOM / ROUGE-2 / 24.14 → Summarization / Newsroom / None / 24.14 | [2] | [] | normalization_null |
| 7: Summarization / Newsroom / ROGUE-L / 42.51 | #3: Abstractive Summarization / NEWSROOM / ROUGE-L / 42.51 → Summarization / Newsroom / None / 42.51 | [3] | [] | normalization_null |
| 8: Summarization / Newsroom / BERTScore / 66.2 | #4: Abstractive Summarization / NEWSROOM / BERTScore / 66.20 → Summarization / Newsroom / BERTScore / 66.20 | [4] | [4] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Abstractive Summarization / NEWSROOM / ROUGE-1 / 45.93 | Summarization / Newsroom / None / 45.93 |
| 2 | Abstractive Summarization / NEWSROOM / ROUGE-2 / 24.14 | Summarization / Newsroom / None / 24.14 |
| 3 | Abstractive Summarization / NEWSROOM / ROUGE-L / 42.51 | Summarization / Newsroom / None / 42.51 |
| 4 | Abstractive Summarization / NEWSROOM / BERTScore / 66.20 | Summarization / Newsroom / BERTScore / 66.20 |
| 5 | Abstractive Summarization / NEWSROOM / Human Informativeness / 2.865 | Summarization / Newsroom / None / 2.865 |
| 6 | Abstractive Summarization / NEWSROOM / Human Grammaticality / 2.855 | Summarization / Newsroom / None / 2.855 |
| 7 | Abstractive Summarization / NEWSROOM / Human Truthfulness / 2.738 | Summarization / Newsroom / None / 2.738 |

## 2001.04063.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / CNN/DailyMail / ROGUE-1 / 44.2 | #1: Abstractive Summarization / CNN/DailyMail / ROUGE-1 / 44.20 → Summarization / CNN/DailyMail / None / 44.20 | [1] | [] | normalization_null |
| 2: Summarization / CNN/DailyMail / ROGUE-2 / 21.17 | #2: Abstractive Summarization / CNN/DailyMail / ROUGE-2 / 21.17 → Summarization / CNN/DailyMail / None / 21.17 | [2] | [] | normalization_null |
| 3: Summarization / CNN/DailyMail / ROGUE-L / 41.3 | #3: Abstractive Summarization / CNN/DailyMail / ROUGE-L / 41.30 → Summarization / CNN/DailyMail / None / 41.30 | [3] | [] | normalization_null |
| 4: Summarization / Gigaword / ROGUE-1 / 39.51 | #4: Abstractive Summarization / Gigaword / ROUGE-1 / 39.51 → Summarization / Gigaword / None / 39.51 | [4] | [] | normalization_null |
| 5: Summarization / Gigaword / ROGUE-2 / 20.42 | #5: Abstractive Summarization / Gigaword / ROUGE-2 / 20.42 → Summarization / Gigaword / None / 20.42 | [5] | [] | normalization_null |
| 6: Summarization / Gigaword / ROGUE-L / 36.69 | #6: Abstractive Summarization / Gigaword / ROUGE-L / 36.69 → Summarization / Gigaword / None / 36.69 | [6] | [] | normalization_null |
| 7: Question Generation / SQuAD 1.1 / BLEU-4 / 25.8 | #7: Question Generation / SQuAD 1.1 / BLEU-4 / 25.80 → Question Generation / SQuAD 1.1 / BLEU-4 / 25.80 | [7] | [7] | correct |
| 8: Question Generation / SQuAD 1.1 / METEOR / 27.54 | #8: Question Generation / SQuAD 1.1 / METEOR / 27.54 → Question Generation / SQuAD 1.1 / METEOR / 27.54 | [8] | [8] | correct |
| 9: Question Generation / SQuAD 1.1 / ROGUE-L / 53.65 | #9: Question Generation / SQuAD 1.1 / ROUGE-L / 53.65 → Question Generation / SQuAD 1.1 / None / 53.65 | [9] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Abstractive Summarization / CNN/DailyMail / ROUGE-1 / 44.20 | Summarization / CNN/DailyMail / None / 44.20 |
| 2 | Abstractive Summarization / CNN/DailyMail / ROUGE-2 / 21.17 | Summarization / CNN/DailyMail / None / 21.17 |
| 3 | Abstractive Summarization / CNN/DailyMail / ROUGE-L / 41.30 | Summarization / CNN/DailyMail / None / 41.30 |
| 4 | Abstractive Summarization / Gigaword / ROUGE-1 / 39.51 | Summarization / Gigaword / None / 39.51 |
| 5 | Abstractive Summarization / Gigaword / ROUGE-2 / 20.42 | Summarization / Gigaword / None / 20.42 |
| 6 | Abstractive Summarization / Gigaword / ROUGE-L / 36.69 | Summarization / Gigaword / None / 36.69 |
| 7 | Question Generation / SQuAD 1.1 / BLEU-4 / 25.80 | Question Generation / SQuAD 1.1 / BLEU-4 / 25.80 |
| 8 | Question Generation / SQuAD 1.1 / METEOR / 27.54 | Question Generation / SQuAD 1.1 / METEOR / 27.54 |
| 9 | Question Generation / SQuAD 1.1 / ROUGE-L / 53.65 | Question Generation / SQuAD 1.1 / None / 53.65 |

## 2002.03184.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Machine Translation / WMT’14 EN-FR / BLEU / 43.2 | #2: Machine Translation / WMT En-Fr / BLEU / 43.2 → Machine Translation / WMT’14 EN-FR / BLEU / 43.2 | [2] | [2] | correct |
| 2: Machine Translation / WMT’14 EN-DE / BLEU / 29.6 | #1: Machine Translation / WMT En-De / BLEU / 29.6 → Machine Translation / WMT’14 EN-DE / BLEU / 29.6 | [1] | [1] | correct |
| 3: Machine Translation / IWSLT’14 EN-DE / BLEU / 35.5 | #3: Machine Translation / IWSLT De-En / BLEU / 35.5 → Machine Translation / None / BLEU / 35.5 | [3] | [] | normalization_null |
| 4: Summarization / CNN/DailyMail / ROGUE-1 / 40.59 | #4: Abstractive Summarization / CNN-DailyMail / Rouge-1 / 40.59 → Summarization / CNN/DailyMail / None / 40.59 | [4] | [] | normalization_null |
| 5: Summarization / CNN/DailyMail / ROGUE-2 / 18.97 | #5: Abstractive Summarization / CNN-DailyMail / Rouge-2 / 18.97 → Summarization / CNN/DailyMail / ROGUE-2 / 18.97 | [5] | [5] | correct |
| 6: Summarization / CNN/DailyMail / ROGUE-L / 36.81 | #6: Abstractive Summarization / CNN-DailyMail / Rouge-L / 36.81 → Summarization / CNN/DailyMail / ROGUE-L / 36.81 | [6] | [6] | correct |
| 7: Language Modeling / WikiText-103 / Perplexity / 23.3 | #7: Language Modeling / WikiText-103 / Test Perplexity / 23.3 → Language Modeling / WikiText-103 / Perplexity / 23.3 | [7] | [7] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Machine Translation / WMT En-De / BLEU / 29.6 | Machine Translation / WMT’14 EN-DE / BLEU / 29.6 |
| 2 | Machine Translation / WMT En-Fr / BLEU / 43.2 | Machine Translation / WMT’14 EN-FR / BLEU / 43.2 |
| 3 | Machine Translation / IWSLT De-En / BLEU / 35.5 | Machine Translation / None / BLEU / 35.5 |
| 4 | Abstractive Summarization / CNN-DailyMail / Rouge-1 / 40.59 | Summarization / CNN/DailyMail / None / 40.59 |
| 5 | Abstractive Summarization / CNN-DailyMail / Rouge-2 / 18.97 | Summarization / CNN/DailyMail / ROGUE-2 / 18.97 |
| 6 | Abstractive Summarization / CNN-DailyMail / Rouge-L / 36.81 | Summarization / CNN/DailyMail / ROGUE-L / 36.81 |
| 7 | Language Modeling / WikiText-103 / Test Perplexity / 23.3 | Language Modeling / WikiText-103 / Perplexity / 23.3 |

## 2008.07772.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Machine Translation / WMT’14 EN-FR / TER / 40.3 | #2: Machine Translation / WMT'14 English-French / TER / 40.3 → Machine Translation / WMT’14 EN-FR / TER / 40.3 | [2] | [2] | correct |
| 2: Machine Translation / WMT’14 EN-FR / METEOR / 62.4 | #3: Machine Translation / WMT'14 English-French / METEOR / 62.4 → Machine Translation / WMT’14 EN-FR / METEOR / 62.4 | [3] | [3] | correct |
| 3: Machine Translation / WMT’14 EN-FR / BLEU / 43.8 | #1: Machine Translation / WMT'14 English-French / BLEU (multi-bleu.perl) / 43.8 → Machine Translation / WMT’14 EN-FR / BLEU / 43.8 | [1] | [1] | correct |
| 4: Machine Translation / WMT’14 EN-DE / TER / 51.8 | #5: Machine Translation / WMT'14 English-German / TER / 51.8 → Machine Translation / WMT’14 EN-DE / TER / 51.8 | [5] | [5] | correct |
| 5: Machine Translation / WMT’14 EN-DE / METEOR / 48.3 | #6: Machine Translation / WMT'14 English-German / METEOR / 48.3 → Machine Translation / WMT’14 EN-DE / METEOR / 48.3 | [6] | [6] | correct |
| 6: Machine Translation / WMT’14 EN-DE / BLEU / 30.1 | #4: Machine Translation / WMT'14 English-German / BLEU (multi-bleu.perl) / 30.1 → Machine Translation / WMT’14 EN-DE / BLEU / 30.1 | [4] | [4] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Machine Translation / WMT'14 English-French / BLEU (multi-bleu.perl) / 43.8 | Machine Translation / WMT’14 EN-FR / BLEU / 43.8 |
| 2 | Machine Translation / WMT'14 English-French / TER / 40.3 | Machine Translation / WMT’14 EN-FR / TER / 40.3 |
| 3 | Machine Translation / WMT'14 English-French / METEOR / 62.4 | Machine Translation / WMT’14 EN-FR / METEOR / 62.4 |
| 4 | Machine Translation / WMT'14 English-German / BLEU (multi-bleu.perl) / 30.1 | Machine Translation / WMT’14 EN-DE / BLEU / 30.1 |
| 5 | Machine Translation / WMT'14 English-German / TER / 51.8 | Machine Translation / WMT’14 EN-DE / TER / 51.8 |
| 6 | Machine Translation / WMT'14 English-German / METEOR / 48.3 | Machine Translation / WMT’14 EN-DE / METEOR / 48.3 |
| 7 | Machine Translation / WMT'14 English-French / BLEU (sacreBLEU.py) / 41.8 | Machine Translation / WMT’14 EN-FR / BLEU / 41.8 |
| 8 | Machine Translation / WMT'14 English-German / BLEU (sacreBLEU.py) / 29.5 | Machine Translation / WMT’14 EN-DE / BLEU / 29.5 |
| 9 | Machine Translation with Back-Translation / WMT'14 English-French / BLEU (multi-bleu.perl) / 46.4 | Machine Translation / WMT’14 EN-FR / BLEU / 46.4 |
| 10 | Machine Translation with Back-Translation / WMT'14 English-French / BLEU (sacreBLEU.py) / 44.4 | Machine Translation / WMT’14 EN-FR / BLEU / 44.4 |

## 2203.16804.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / CNN/DailyMail / ROGUE-1 / 47.78 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Summarization / CNN/DailyMail / ROGUE-2 / 23.55 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Summarization / CNN/DailyMail / ROGUE-L / 44.57 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Summarization / XSum / ROGUE-1 / 49.07 | #4: Abstractive Summarization / XSum / ROUGE-1 F1 / 49.07 → Summarization / XSum / ROGUE-1 / 49.07 | [4] | [4] | correct |
| 5: Summarization / XSum / ROGUE-2 / 25.59 | #5: Abstractive Summarization / XSum / ROUGE-2 F1 / 25.59 → Summarization / XSum / ROGUE-2 / 25.59 | [5] | [5] | correct |
| 6: Summarization / XSum / ROGUE-L / 40.4 | #6: Abstractive Summarization / XSum / ROUGE-L F1 / 40.40 → Summarization / XSum / None / 40.40 | [6] | [] | normalization_null |
| 7: Summarization / New York Times (NYT) / ROGUE-1 / 57.75 | #7: Abstractive Summarization / NYT / ROUGE-1 F1 / 57.75 → Summarization / New York Times (NYT) / None / 57.75 | [7] | [] | normalization_null |
| 8: Summarization / New York Times (NYT) / ROGUE-2 / 38.64 | #8: Abstractive Summarization / NYT / ROUGE-2 F1 / 38.64 → Summarization / New York Times (NYT) / ROGUE-2 / 38.64 | [8] | [8] | correct |
| 9: Summarization / New York Times (NYT) / ROGUE-L / 54.54 | #9: Abstractive Summarization / NYT / ROUGE-L F1 / 54.54 → Summarization / New York Times (NYT) / ROGUE-L / 54.54 | [9] | [9] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Abstractive Summarization / CNNDM / ROUGE-1 F1 / 48.01 | Summarization / CNN/DailyMail / ROGUE-1 / 48.01 |
| 2 | Abstractive Summarization / CNNDM / ROUGE-2 F1 / 23.80 | Summarization / CNN/DailyMail / ROGUE-2 / 23.80 |
| 3 | Abstractive Summarization / CNNDM / ROUGE-L F1 / 44.67 | Summarization / CNN/DailyMail / ROGUE-L / 44.67 |
| 4 | Abstractive Summarization / XSum / ROUGE-1 F1 / 49.07 | Summarization / XSum / ROGUE-1 / 49.07 |
| 5 | Abstractive Summarization / XSum / ROUGE-2 F1 / 25.59 | Summarization / XSum / ROGUE-2 / 25.59 |
| 6 | Abstractive Summarization / XSum / ROUGE-L F1 / 40.40 | Summarization / XSum / None / 40.40 |
| 7 | Abstractive Summarization / NYT / ROUGE-1 F1 / 57.75 | Summarization / New York Times (NYT) / None / 57.75 |
| 8 | Abstractive Summarization / NYT / ROUGE-2 F1 / 38.64 | Summarization / New York Times (NYT) / ROGUE-2 / 38.64 |
| 9 | Abstractive Summarization / NYT / ROUGE-L F1 / 54.54 | Summarization / New York Times (NYT) / ROGUE-L / 54.54 |
| 10 | Abstractive Summarization / CNNDM / BERTScore / 32.59 | Summarization / CNN/DailyMail / BERTScore / 32.59 |
| 11 | Abstractive Summarization / XSum / Expected Calibration Error (ECE) / 0.1423 | Summarization / XSum / None / 0.1423 |
| 12 | Abstractive Summarization / CNNDM / Expected Calibration Error (ECE) / 0.2719 | Summarization / None / None / 0.2719 |
| 13 | Abstractive Summarization / CNNDM / Accuracy / 0.4271 | Summarization / None / Accuracy / 0.4271 |
| 14 | Abstractive Summarization / XSum / Accuracy / 0.4744 | Summarization / XSum / Accuracy / 0.4744 |
| 15 | Abstractive Summarization / CNNDM / Confidence / 0.7365 | Summarization / CNN/DailyMail / None / 0.7365 |
| 16 | Abstractive Summarization / XSum / Confidence / 0.6990 | Summarization / XSum / None / 0.6990 |
| 17 | Abstractive Summarization (Few-shot) / CNNDM / ROUGE-1 F1 / 45.81 | Summarization / None / None / 45.81 |
| 18 | Abstractive Summarization (Few-shot) / CNNDM / ROUGE-2 F1 / 21.91 | Summarization / CNN/DailyMail / ROGUE-2 / 21.91 |
| 19 | Abstractive Summarization (Few-shot) / CNNDM / ROUGE-L F1 / 42.61 | Summarization / None / None / 42.61 |
| 20 | Abstractive Summarization (Few-shot) / XSum / ROUGE-1 F1 / 47.95 | Summarization / XSum / None / 47.95 |
| 21 | Abstractive Summarization (Few-shot) / XSum / ROUGE-2 F1 / 24.89 | Summarization / XSum / ROGUE-2 / 24.89 |
| 22 | Abstractive Summarization (Few-shot) / XSum / ROUGE-L F1 / 39.71 | Summarization / XSum / None / 39.71 |

## C18-1139.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.09 | — | [1] | [] | numeric_result_missing_or_changed |
| 2: Named Entity Recognition (NER) / CoNLL-2003 - German / F1 / 88.32 | — | [2] | [] | numeric_result_missing_or_changed |
| 3: Text Chunking / CoNLL-2000 / F1 / 96.72 | — | [3] | [] | numeric_result_missing_or_changed |
| 4: Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.85 | — | [4] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition (English) / CONLL03 / F1-score / 93.09±0.12 | Named Entity Recognition (NER) / None / F1 / 93.09±0.12 |
| 2 | Named Entity Recognition (German) / CONLL03 / F1-score / 88.32±0.20 | Named Entity Recognition (NER) / None / F1 / 88.32±0.20 |
| 3 | Chunking / CONLL2000 / F1-score / 96.72±0.05 | Text Chunking / CoNLL-2000 / F1 / 96.72±0.05 |
| 4 | Part-of-Speech Tagging / Penn Treebank / Accuracy / 97.85±0.01 | Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.85±0.01 |

## D18-1523.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) / 11.26 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) / 57.49 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Word Sense Induction / SemEval 2013 Task 13 / AVG / 25.43 | — | [1] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Word Sense Induction (WSI) / SemEval 2013 Task 13 / AVG / 25.43 ± 0.48 | Word Sense Induction / SemEval 2013 Task 13 / AVG / 25.43 ± 0.48 |
| 2 | Word Sense Induction (WSI) / SemEval 2013 Task 13 / NMI / 0.22 ± 0.12 | Word Sense Induction / SemEval 2013 Task 13 / None / 0.22 ± 0.12 |

## D19-1367.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Language Modeling / Penn Treebank (PTB) / Perplexity / 56.0 | #1: Language Modeling / PTB (Penn Treebank) / Test Perplexity / 56.0 → Language Modeling / Penn Treebank (PTB) / Perplexity / 56.0 | [1] | [1] | correct |
| 2: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.47 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Language Modeling / PTB (Penn Treebank) / Test Perplexity / 56.0 | Language Modeling / Penn Treebank (PTB) / Perplexity / 56.0 |
| 2 | Language Modeling / PTB (Penn Treebank) / Validation Perplexity / 58.0 | Language Modeling / Penn Treebank (PTB) / Perplexity / 58.0 |
| 3 | Named Entity Recognition / CoNLL-2003 English / F1 Score / Best result for I-DARTS (n = 1) (exact value not provided in the excerpt) | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / Best result for I-DARTS (n = 1) (exact value not provided in the excerpt) |

## K19-1036.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 82.3 | #1: Dialogue Act Classification / SWDA / Accuracy / 82.3 → Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 82.3 | [1] | [1] | correct |
| 2: Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 92.2 | #2: Dialogue Act Classification / MRDA / Accuracy / 92.2 → Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 92.2 | [2] | [2] | correct |
| 3: Dialogue Act Classification / Dailydialog (DyDA) / Accuracy / 88.1 | #3: Dialogue Act Classification / DyDA / Accuracy / 88.1 → Dialogue Act Classification / Dailydialog (DyDA) / Accuracy / 88.1 | [3] | [3] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Dialogue Act Classification / SWDA / Accuracy / 82.3 | Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 82.3 |
| 2 | Dialogue Act Classification / MRDA / Accuracy / 92.2 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 92.2 |
| 3 | Dialogue Act Classification / DyDA / Accuracy / 88.1 | Dialogue Act Classification / Dailydialog (DyDA) / Accuracy / 88.1 |

## N19-1373.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 82.9 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 91.1 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Dialogue Act Classification / SwDA / Accuracy / 86.7 | Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 86.7 |
| 2 | Dialogue Act Classification / MRDA / Accuracy / 89.2 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 89.2 |