# 逐条 Gold 与原始 / 标准化输出对照

候选索引按数值命中列出，不强行假设一对一关系；`±`、单位等非纯数值文本不满足 Decimal 严格相等。官方字符串包含匹配单独列出。

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
| 3: Intent Detection and Slot Filling / ATIS / Sent-Accuracy / 88.64 | #3: Sentence-level Joint Accuracy / ATIS / Sentence Accuracy / 88.64 → None / ATIS / Sent-Accuracy / 88.64 | [3] | [] | normalization_null |
| 4: Intent Detection and Slot Filling / SNIPS / F1 / 97.05 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Intent Detection and Slot Filling / SNIPS / Accuracy / 99.04 | #4: Intent Detection / Snips / Accuracy / 99.04 → Intent Detection and Slot Filling / SNIPS / Accuracy / 99.04 | [4] | [4] | correct |
| 6: Intent Detection and Slot Filling / SNIPS / Sent-Accuracy / 92.96 | #6: Sentence-level Joint Accuracy / Snips / Sentence Accuracy / 92.96 → None / SNIPS / Sent-Accuracy / 92.96 | [6] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Intent Detection / ATIS / Accuracy / 97.74 | Intent Detection and Slot Filling / ATIS / Accuracy / 97.74 |
| 2 | Slot Filling / ATIS / F1-score / 96.16 | Intent Detection and Slot Filling / ATIS / F1 / 96.16 |
| 3 | Sentence-level Joint Accuracy / ATIS / Sentence Accuracy / 88.64 | None / ATIS / Sent-Accuracy / 88.64 |
| 4 | Intent Detection / Snips / Accuracy / 99.04 | Intent Detection and Slot Filling / SNIPS / Accuracy / 99.04 |
| 5 | Slot Filling / Snips / F1-score / 99.00 | Intent Detection and Slot Filling / SNIPS / F1 / 99.00 |
| 6 | Sentence-level Joint Accuracy / Snips / Sentence Accuracy / 92.96 | None / SNIPS / Sent-Accuracy / 92.96 |

## 2105.03654.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / WNUT-16 - English / F1 / 58.98 | #1: Named Entity Recognition / WNUT-16 / Accuracy / 58.98 → Named Entity Recognition (NER) / WNUT-16 - English / Accuracy / 58.98 | [1] | [] | numeric_match_but_binding_or_label_mismatch |
| 2: Named Entity Recognition (NER) / WNUT-17 - English / F1 / 60.45 | #2: Named Entity Recognition / WNUT-17 / Accuracy / 60.45 → Named Entity Recognition (NER) / WNUT-17 - English / Accuracy / 60.45 | [2] | [] | numeric_match_but_binding_or_label_mismatch |
| 3: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.56 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Named Entity Recognition (NER) / CoNLL++ / F1 / 94.81 | #3: Named Entity Recognition / CoNLL-03 / Accuracy / 94.81 → Named Entity Recognition (NER) / None / Accuracy / 94.81 | [3] | [] | normalization_null |
| 5: Named Entity Recognition (NER) / BC5CDR / F1 / 90.99 | #5: Named Entity Recognition / BC5CDR / Accuracy / 90.99 → Named Entity Recognition (NER) / BC5CDR / Accuracy / 90.99 | [5] | [] | numeric_match_but_binding_or_label_mismatch |
| 6: Named Entity Recognition (NER) / NCBI / F1 / 89.24 | — | [] | [] | numeric_result_missing_or_changed |
| 7: Named Entity Recognition (NER) / E-commerce / F1 / 83.99 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Named Entity Recognition / WNUT-16 / Accuracy / 58.98 | Named Entity Recognition (NER) / WNUT-16 - English / Accuracy / 58.98 |
| 2 | Named Entity Recognition / WNUT-17 / Accuracy / 60.45 | Named Entity Recognition (NER) / WNUT-17 - English / Accuracy / 60.45 |
| 3 | Named Entity Recognition / CoNLL-03 / Accuracy / 94.81 | Named Entity Recognition (NER) / None / Accuracy / 94.81 |
| 4 | Named Entity Recognition / CoNLL++ / Accuracy / 94.62 | Named Entity Recognition (NER) / CoNLL++ / Accuracy / 94.62 |
| 5 | Named Entity Recognition / BC5CDR / Accuracy / 90.99 | Named Entity Recognition (NER) / BC5CDR / Accuracy / 90.99 |
| 6 | Named Entity Recognition / NCBI / Accuracy / 89.22 | Named Entity Recognition (NER) / NCBI / Accuracy / 89.22 |
| 7 | Named Entity Recognition / E-commerce / Accuracy / 84.10 | Named Entity Recognition (NER) / E-commerce / Accuracy / 84.10 |
| 8 | Cross-domain NER Transfer / CBS SciTech News (trained on CoNLL-03) / Accuracy / 76.38 | Named Entity Recognition (NER) / CoNLL-2003 - English / Accuracy / 76.38 |
| 9 | Named Entity Recognition / WNUT-17 / F1 Score / 62.29 | Named Entity Recognition (NER) / WNUT-17 - English / F1 / 62.29 |

## 1910.13461.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Question Answering / SQuAD 1.1 / Exact Match (EM) / 88.8 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Question Answering / SQuAD 1.1 / F1 / 94.6 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Question Answering / SQuAD 2.0 / Exact Match (EM) / 86.1 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Question Answering / SQuAD 2.0 / F1 / 89.2 | — | [] | [] | numeric_result_missing_or_changed |
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
| 15: Summarization / CNN/DailyMail / ROGUE-2 / 21.28 | #3: Summarization / CNN/DailyMail / ROUGE-2 / 21.28 → Summarization / CNN/DailyMail / None / 21.28 | [3] | [] | normalization_null |
| 16: Summarization / CNN/DailyMail / ROGUE-L / 40.9 | #5: Summarization / CNN/DailyMail / ROUGE-L / 40.90 → Summarization / CNN/DailyMail / None / 40.90 | [5] | [] | normalization_null |
| 17: Summarization / XSum / ROGUE-1 / 45.14 | #6: Summarization / XSum / ROUGE-1 / 45.14 → Summarization / XSum / None / 45.14 | [6] | [] | normalization_null |
| 18: Summarization / XSum / ROGUE-2 / 22.27 | #7: Summarization / XSum / ROUGE-2 / 22.27 → Summarization / XSum / None / 22.27 | [7] | [] | normalization_null |
| 19: Summarization / XSum / ROGUE-L / 37.25 | #8: Summarization / XSum / ROUGE-L / 37.25 → Summarization / XSum / None / 37.25 | [8] | [] | normalization_null |
| 20: Dialogue Generation / ConvAI2 / F1 / 20.72 | — | [] | [] | numeric_result_missing_or_changed |
| 21: Dialogue Generation / ConvAI2 / Perplexity / 11.85 | #9: Conversational Response Generation / ConvAI2 / Valid PPL / 11.85 → Response Generation / ConvAI2 / Perplexity / 11.85 | [9] | [] | numeric_match_but_binding_or_label_mismatch |
| 22: Question Answering / ELI5 / ROGUE-1 / 30.6 | #10: Abstractive Question Answering / ELI5 / ROUGE-1 / 30.6 → Question Answering / ELI5 / None / 30.6 | [10] | [] | normalization_null |
| 23: Question Answering / ELI5 / ROGUE-2 / 6.2 | #11: Abstractive Question Answering / ELI5 / ROUGE-2 / 6.2 → Question Answering / ELI5 / None / 6.2 | [11] | [] | normalization_null |
| 24: Question Answering / ELI5 / ROGUE-L / 24.3 | #12: Abstractive Question Answering / ELI5 / ROUGE-L / 24.3 → Question Answering / ELI5 / None / 24.3 | [12] | [] | normalization_null |
| 25: Machine Translation / WMT’16 RO-EN / BLEU / 37.96 | #13: Machine Translation / WMT'16 RO-EN / BLEU / 37.96 → Machine Translation / WMT’16 RO-EN / BLEU / 37.96 | [13] | [13] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Extractive Question Answering / SQuAD 1.1 / F1 / 90.9 | Question Answering / SQuAD 1.1 / F1 / 90.9 |
| 2 | Natural Language Inference / MNLI / Accuracy / 86.6 | Natural Language Inference (NLI) / None / Accuracy / 86.6 |
| 3 | Summarization / CNN/DailyMail / ROUGE-2 / 21.28 | Summarization / CNN/DailyMail / None / 21.28 |
| 4 | Summarization / CNN/DailyMail / ROUGE-1 / 44.16 | Summarization / CNN/DailyMail / None / 44.16 |
| 5 | Summarization / CNN/DailyMail / ROUGE-L / 40.90 | Summarization / CNN/DailyMail / None / 40.90 |
| 6 | Summarization / XSum / ROUGE-1 / 45.14 | Summarization / XSum / None / 45.14 |
| 7 | Summarization / XSum / ROUGE-2 / 22.27 | Summarization / XSum / None / 22.27 |
| 8 | Summarization / XSum / ROUGE-L / 37.25 | Summarization / XSum / None / 37.25 |
| 9 | Conversational Response Generation / ConvAI2 / Valid PPL / 11.85 | Response Generation / ConvAI2 / Perplexity / 11.85 |
| 10 | Abstractive Question Answering / ELI5 / ROUGE-1 / 30.6 | Question Answering / ELI5 / None / 30.6 |
| 11 | Abstractive Question Answering / ELI5 / ROUGE-2 / 6.2 | Question Answering / ELI5 / None / 6.2 |
| 12 | Abstractive Question Answering / ELI5 / ROUGE-L / 24.3 | Question Answering / ELI5 / None / 24.3 |
| 13 | Machine Translation / WMT'16 RO-EN / BLEU / 37.96 | Machine Translation / WMT’16 RO-EN / BLEU / 37.96 |

## D18-1105.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 83.1 | #1: Dialog Act Classification / SwDA / Accuracy / 83.1 → Dialogue Act Classification / None / Accuracy / 83.1 | [1] | [] | normalization_null |
| 2: Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 86.7 | #2: Dialog Act Classification / MRDA / Accuracy / 86.7 → Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 86.7 | [2] | [2] | correct |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Dialog Act Classification / SwDA / Accuracy / 83.1 | Dialogue Act Classification / None / Accuracy / 83.1 |
| 2 | Dialog Act Classification / MRDA / Accuracy / 86.7 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 86.7 |

## 1703.06345.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.26 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 85.77 | #4: NER / CoNLL 2002 Spanish / F1 / 85.77 → Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 85.77 | [4] | [4] | correct |
| 3: Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 85.19 | #5: NER / CoNLL 2002 Dutch / F1 / 85.19 → Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 85.19 | [5] | [5] | correct |
| 4: Text Chunking / CoNLL-2000 / F1 / 95.41 | #1: POS Tagging / PTB / Accuracy / 95.41 → Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 95.41 | [1] | [] | numeric_match_but_binding_or_label_mismatch |
| 5: Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.55 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | POS Tagging / PTB / Accuracy / 95.41 | Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 95.41 |
| 2 | Chunking / CoNLL 2000 / F1 / 94.66 | Text Chunking / CoNLL-2000 / F1 / 94.66 |
| 3 | NER / CoNLL 2003 English / F1 / 91.21 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.21 |
| 4 | NER / CoNLL 2002 Spanish / F1 / 85.77 | Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 85.77 |
| 5 | NER / CoNLL 2002 Dutch / F1 / 85.19 | Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 85.19 |
| 6 | POS Tagging / Genia / Accuracy / 92.62 | Part-of-Speech (POS) Tagging / None / Accuracy / 92.62 |
| 7 | POS Tagging / Twitter / Accuracy / 83.65 | Part-of-Speech (POS) Tagging / None / Accuracy / 83.65 |

## 1903.07785.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 53.1 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Sentiment Analysis / SST-2 / Accuracy / 94.6 | #2: SST-2 (Stanford Sentiment Treebank) / GLUE/SST-2 / Accuracy / 94.6 → Sentiment Analysis / SST-2 / Accuracy / 94.6 | [2] | [2] | correct |
| 3: Paraphrase Detection / MRPC / F1 / 83.7 | #3: MRPC (Microsoft Research Paraphrase Corpus) / GLUE/MRPC / F1 / 83.7 → Paraphrase Detection / MRPC / F1 / 83.7 | [3] | [3] | correct |
| 4: Text Similarity / STS-B / Spearman Correlation / 84.2 | #4: STS-B (Semantic Textual Similarity Benchmark) / GLUE/STS-B / Spearman correlation coefficient (scc) / 84.2 → Text Similarity / STS-B / Spearman Correlation / 84.2 | [4] | [4] | correct |
| 5: Paraphrase Detection / QQP / F1 / 71.7 | #5: QQP (Quora Question Pairs) / GLUE/QQP / F1 / 71.7 → Paraphrase Detection / QQP / F1 / 71.7 | [5] | [5] | correct |
| 6: Natural Language Inference (NLI) / MNLI-m / Accuracy / 84.3 | #6: MNLI-m (Multi-Genre Natural Language Inference - matched) / GLUE/MNLI-m / Accuracy / 84.3 → Natural Language Inference (NLI) / MNLI-m / Accuracy / 84.3 | [6] | [6] | correct |
| 7: Natural Language Inference (NLI) / MNLI-mm / Accuracy / 83.8 | #7: MNLI-mm (Multi-Genre Natural Language Inference - mismatched) / GLUE/MNLI-mm / Accuracy / 83.8 → Natural Language Inference (NLI) / MNLI-mm / Accuracy / 83.8 | [7] | [7] | correct |
| 8: Natural Language Inference (NLI) / QNLI / Accuracy / 89.8 | #8: QNLI (Question Natural Language Inference) / GLUE/QNLI / Accuracy / 89.8 → Natural Language Inference (NLI) / QNLI / Accuracy / 89.8 | [8] | [8] | correct |
| 9: Natural Language Inference (NLI) / RTE / Accuracy / 63.7 | — | [] | [] | numeric_result_missing_or_changed |
| 10: Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.5 | — | [] | [] | numeric_result_missing_or_changed |
| 11: Constituency Parsing / Penn Treebank (PTB) / F1 / 95.6 | #10: CoNLL-2003 Named Entity Recognition / CoNLL-2003 / Test F1 / 95.6 → Named Entity Recognition (NER) / None / F1 / 95.6 | [10] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | CoLA (Corpus of Linguistic Acceptability) / GLUE/CoLA / Matthews correlation coefficient (mcc) / 56.6 | Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 56.6 |
| 2 | SST-2 (Stanford Sentiment Treebank) / GLUE/SST-2 / Accuracy / 94.6 | Sentiment Analysis / SST-2 / Accuracy / 94.6 |
| 3 | MRPC (Microsoft Research Paraphrase Corpus) / GLUE/MRPC / F1 / 83.7 | Paraphrase Detection / MRPC / F1 / 83.7 |
| 4 | STS-B (Semantic Textual Similarity Benchmark) / GLUE/STS-B / Spearman correlation coefficient (scc) / 84.2 | Text Similarity / STS-B / Spearman Correlation / 84.2 |
| 5 | QQP (Quora Question Pairs) / GLUE/QQP / F1 / 71.7 | Paraphrase Detection / QQP / F1 / 71.7 |
| 6 | MNLI-m (Multi-Genre Natural Language Inference - matched) / GLUE/MNLI-m / Accuracy / 84.3 | Natural Language Inference (NLI) / MNLI-m / Accuracy / 84.3 |
| 7 | MNLI-mm (Multi-Genre Natural Language Inference - mismatched) / GLUE/MNLI-mm / Accuracy / 83.8 | Natural Language Inference (NLI) / MNLI-mm / Accuracy / 83.8 |
| 8 | QNLI (Question Natural Language Inference) / GLUE/QNLI / Accuracy / 89.8 | Natural Language Inference (NLI) / QNLI / Accuracy / 89.8 |
| 9 | RTE (Recognizing Textual Entailment) / GLUE/RTE / Accuracy / 65.1 | Natural Language Inference (NLI) / RTE / Accuracy / 65.1 |
| 10 | CoNLL-2003 Named Entity Recognition / CoNLL-2003 / Test F1 / 95.6 | Named Entity Recognition (NER) / None / F1 / 95.6 |

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
| 4: Machine Translation / WMT’14 EN-DE / BLEU / 29.52 | #4: Neural Machine Translation / WMT2014 English-German (En→De) / BLEU / 29.52 → Machine Translation / WMT’14 EN-DE / BLEU / 29.52 | [4] | [4] | correct |
| 5: Machine Translation / IWSLT’14 EN-DE / BLEU / 35.18 | #5: Neural Machine Translation / IWSLT2014 German-English (De→En) / BLEU / 35.18 → Machine Translation / None / BLEU / 35.18 | [5] | [] | normalization_null |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Neural Language Modeling / Penn Treebank (PTB) / Test Perplexity / 46.01 | Language Modeling / Penn Treebank (PTB) / Perplexity / 46.01 |
| 2 | Neural Language Modeling / Wikitext-2 (WT2) / Test Perplexity / 38.65 | Language Modeling / Wikitext-2 / Perplexity / 38.65 |
| 3 | Neural Language Modeling / Wikitext-103 (WT103) / Test Perplexity / 28.0 | Language Modeling / WikiText-103 / Perplexity / 28.0 |
| 4 | Neural Machine Translation / WMT2014 English-German (En→De) / BLEU / 29.52 | Machine Translation / WMT’14 EN-DE / BLEU / 29.52 |
| 5 | Neural Machine Translation / IWSLT2014 German-English (De→En) / BLEU / 35.18 | Machine Translation / None / BLEU / 35.18 |