# Gold / Few-shot + Few-shot 逐条对照
辅助严格数值匹配不替代官方字符串包含匹配。所有变化按论文 ID 和原始记录序号关联。

## 2020.findings-emnlp.378.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 90.32} | [{"index": 1, "raw": {"Task": "Named Entity Recognition", "Dataset": "ON5E", "Metric": "F1", "Result": "90.32"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "90.32"}}] | normalization_null |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 55.14} | [{"index": 2, "raw": {"Task": "Named Entity Recognition", "Dataset": "WN16", "Metric": "F1", "Result": "55.14"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "55.14"}}] | normalization_null |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 50.68} | [{"index": 3, "raw": {"Task": "Named Entity Recognition", "Dataset": "WN17", "Metric": "F1", "Result": "50.68"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "50.68"}}] | normalization_null |
| 4 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v4 - Chinese", "Metric": "F1", "Result": 81.18} | [{"index": 4, "raw": {"Task": "Named Entity Recognition", "Dataset": "ON4C", "Metric": "F1", "Result": "81.18"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "81.18"}}] | normalization_null |
| 5 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Resume - Chinese", "Metric": "F1", "Result": 96.62} | [{"index": 5, "raw": {"Task": "Named Entity Recognition", "Dataset": "RE", "Metric": "F1", "Result": "96.62"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "96.62"}}] | normalization_null |
| 6 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Weibo - Chinese", "Metric": "F1", "Result": 69.78} | [{"index": 6, "raw": {"Task": "Named Entity Recognition", "Dataset": "WE", "Metric": "F1", "Result": "69.78"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "69.78"}}] | normalization_null |
## 1709.04109.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.85} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 96.13} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.59} | [] | numeric_result_missing_or_changed |
## D18-1279.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.64} | [{"index": 3, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2003 English", "Metric": "F1", "Result": "91.64"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": "91.64"}}] | correct |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - German", "Metric": "F1", "Result": 79.43} | [{"index": 4, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2003 German", "Metric": "F1", "Result": "79.43"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - German", "Metric": "F1", "Result": "79.43"}}] | correct |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002 - Spanish", "Metric": "F1", "Result": 86.68} | [{"index": 1, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2002 Spanish", "Metric": "F1", "Result": "86.68"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002 - Spanish", "Metric": "F1", "Result": "86.68"}}] | correct |
| 4 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002- Dutch", "Metric": "F1", "Result": 87.81} | [{"index": 2, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2002 Dutch", "Metric": "F1", "Result": "87.81"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002- Dutch", "Metric": "F1", "Result": "87.81"}}] | correct |
| 5 | {"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 95.29} | [{"index": 5, "raw": {"Task": "Syntactic Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": "95.29"}, "normalized": {"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": "95.29"}}] | correct |
| 6 | {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "F1", "Result": 97.58} | [{"index": 6, "raw": {"Task": "Part-of-Speech Tagging", "Dataset": "Penn Treebank WSJ", "Metric": "F1", "Result": "97.58"}, "normalized": {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "F1", "Result": "97.58"}}] | correct |
## 2020.emnlp-main.523.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "Precision", "Result": 79.9} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "Recall", "Result": 76.6} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "F1", "Result": 78.2} | [{"index": 1, "raw": {"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "F1", "Result": "78.2"}, "normalized": {"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "F1", "Result": "78.2"}}] | correct |
| 4 | {"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "Precision", "Result": 70.4} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "Recall", "Result": 75.1} | [] | numeric_result_missing_or_changed |
| 6 | {"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "F1", "Result": 72.7} | [{"index": 2, "raw": {"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "F1", "Result": "72.7"}, "normalized": {"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "F1", "Result": "72.7"}}] | correct |
| 7 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 94.3} | [{"index": 3, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2003", "Metric": "F1", "Result": "94.3"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "94.3"}}] | normalization_null |
| 8 | {"Task": "Question Answering", "Dataset": "ReCoRD", "Metric": "Exact Match (EM)", "Result": 90.6} | [] | numeric_result_missing_or_changed |
| 9 | {"Task": "Question Answering", "Dataset": "ReCoRD", "Metric": "F1", "Result": 91.2} | [] | numeric_result_missing_or_changed |
| 10 | {"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "Exact Match (EM)", "Result": 90.2} | [] | numeric_result_missing_or_changed |
| 11 | {"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "F1", "Result": 95.4} | [] | numeric_result_missing_or_changed |
## 1905.03197.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 43.33} | [{"index": 1, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-1", "Result": "43.33"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": "43.33"}}] | correct |
| 2 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 20.21} | [{"index": 2, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-2", "Result": "20.21"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": "20.21"}}] | correct |
| 3 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 40.51} | [{"index": 3, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-L", "Result": "40.51"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": "40.51"}}] | correct |
| 4 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 38.45} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 19.45} | [] | numeric_result_missing_or_changed |
| 6 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 35.75} | [{"index": 4, "raw": {"Task": "Abstractive Summarization", "Dataset": "Gigaword", "Metric": "ROUGE-L", "Result": "35.75"}, "normalized": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": "35.75"}}] | correct |
| 7 | {"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "Exact Match (EM)", "Result": 84.7} | [] | numeric_result_missing_or_changed |
| 8 | {"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "F1", "Result": 87.6} | [] | numeric_result_missing_or_changed |
| 9 | {"Task": "Question Answering", "Dataset": "CoQA", "Metric": "F1", "Result": 84.9} | [{"index": 8, "raw": {"Task": "Extractive Question Answering", "Dataset": "CoQA", "Metric": "F1", "Result": "84.9"}, "normalized": {"Task": "Question Answering", "Dataset": "CoQA", "Metric": "F1", "Result": "84.9"}}] | correct |
| 10 | {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "BLEU-4", "Result": 23.75} | [] | numeric_result_missing_or_changed |
| 11 | {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "METEOR", "Result": 25.61} | [{"index": 10, "raw": {"Task": "Question Generation", "Dataset": "SQuAD", "Metric": "BLEU-4", "Result": "25.61"}, "normalized": {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "BLEU-4", "Result": "25.61"}}] | numeric_match_but_binding_or_label_mismatch |
| 12 | {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "ROGUE-L", "Result": 52.04} | [{"index": 12, "raw": {"Task": "Question Generation", "Dataset": "SQuAD", "Metric": "ROUGE-L", "Result": "52.04"}, "normalized": {"Task": "Question Generation", "Dataset": null, "Metric": "ROGUE-L", "Result": "52.04"}}] | normalization_null |
| 13 | {"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "NIST-4", "Result": 2.67} | [] | numeric_result_missing_or_changed |
| 14 | {"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "BLEU-4", "Result": 4.39} | [{"index": 13, "raw": {"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "BLEU-4", "Result": "4.39"}, "normalized": {"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "BLEU-4", "Result": "4.39"}}] | correct |
| 15 | {"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "METEOR", "Result": 8.27} | [] | numeric_result_missing_or_changed |
| 16 | {"Task": "Linguistic Acceptability", "Dataset": "CoLA", "Metric": "Matthew's Correlation Coefficient (MCC)", "Result": 61.1} | [] | numeric_result_missing_or_changed |
| 17 | {"Task": "Sentiment Analysis", "Dataset": "SST-2", "Metric": "Accuracy", "Result": 94.5} | [{"index": 19, "raw": {"Task": "Language Understanding", "Dataset": "GLUE (MRPC)", "Metric": "F1", "Result": "94.5"}, "normalized": {"Task": null, "Dataset": "MRPC", "Metric": "F1", "Result": "94.5"}}] | normalization_null |
| 18 | {"Task": "Paraphrase Detection", "Dataset": "MRPC", "Metric": "F1", "Result": 90.0} | [{"index": 21, "raw": {"Task": "Language Understanding", "Dataset": "GLUE (QQP)", "Metric": "F1", "Result": "90.0"}, "normalized": {"Task": null, "Dataset": "QQP", "Metric": "F1", "Result": "90.0"}}] | normalization_null |
| 19 | {"Task": "Text Similarity", "Dataset": "STS-B", "Metric": "Spearman Correlation", "Result": 87.7} | [] | numeric_result_missing_or_changed |
| 20 | {"Task": "Paraphrase Detection", "Dataset": "QQP", "Metric": "F1", "Result": 71.7} | [] | numeric_result_missing_or_changed |
| 21 | {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": 87.0} | [] | numeric_result_missing_or_changed |
| 22 | {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": 85.9} | [{"index": 23, "raw": {"Task": "Language Understanding", "Dataset": "GLUE (MNLI-mm)", "Metric": "Accuracy", "Result": "85.9"}, "normalized": {"Task": null, "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": "85.9"}}] | normalization_null |
| 23 | {"Task": "Natural Language Inference (NLI)", "Dataset": "QNLI", "Metric": "Accuracy", "Result": 92.7} | [{"index": 24, "raw": {"Task": "Language Understanding", "Dataset": "GLUE (QNLI)", "Metric": "Accuracy", "Result": "92.7"}, "normalized": {"Task": null, "Dataset": "QNLI", "Metric": "Accuracy", "Result": "92.7"}}] | normalization_null |
| 24 | {"Task": "Natural Language Inference (NLI)", "Dataset": "RTE", "Metric": "Accuracy", "Result": 70.9} | [] | numeric_result_missing_or_changed |
| 25 | {"Task": "Natural Language Inference (NLI)", "Dataset": "WNLI", "Metric": "Accuracy", "Result": 65.1} | [] | numeric_result_missing_or_changed |
| 26 | {"Task": "Natural Language Inference (NLI)", "Dataset": "AX", "Metric": "Accuracy", "Result": 38.4} | [] | numeric_result_missing_or_changed |
## 1702.02098.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 90.65} | [{"index": 1, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2003", "Metric": "F1", "Result": "90.65"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "90.65"}}] | normalization_null |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 86.99} | [] | numeric_result_missing_or_changed |
## 2020.emnlp-main.152.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 96.24} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 97.74} | [{"index": 8, "raw": {"Task": "Intent Detection", "Dataset": "ATIS", "Metric": "Accuracy", "Result": "97.74"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": "97.74"}}] | correct |
| 3 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Sent-Accuracy", "Result": 88.64} | [{"index": 9, "raw": {"Task": "Joint Slot Filling and Intent Detection", "Dataset": "ATIS", "Metric": "Sentence Accuracy", "Result": "88.64"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Sent-Accuracy", "Result": "88.64"}}] | correct |
| 4 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 97.05} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 99.04} | [{"index": 11, "raw": {"Task": "Intent Detection", "Dataset": "Snips", "Metric": "Accuracy", "Result": "99.04"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": "99.04"}}] | correct |
| 6 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Sent-Accuracy", "Result": 92.96} | [{"index": 12, "raw": {"Task": "Joint Slot Filling and Intent Detection", "Dataset": "Snips", "Metric": "Sentence Accuracy", "Result": "92.96"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Sent-Accuracy", "Result": "92.96"}}] | correct |
## 2105.03654.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 58.98} | [{"index": 1, "raw": {"Task": "Named Entity Recognition", "Dataset": "WNUT-16", "Metric": "Accuracy", "Result": "58.98"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "Accuracy", "Result": "58.98"}}] | numeric_match_but_binding_or_label_mismatch |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 60.45} | [{"index": 2, "raw": {"Task": "Named Entity Recognition", "Dataset": "WNUT-17", "Metric": "Accuracy", "Result": "60.45"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "Accuracy", "Result": "60.45"}}] | numeric_match_but_binding_or_label_mismatch |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.56} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL++", "Metric": "F1", "Result": 94.81} | [{"index": 4, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL++", "Metric": "Accuracy", "Result": "94.81"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL++", "Metric": "Accuracy", "Result": "94.81"}}] | numeric_match_but_binding_or_label_mismatch |
| 5 | {"Task": "Named Entity Recognition (NER)", "Dataset": "BC5CDR", "Metric": "F1", "Result": 90.99} | [{"index": 5, "raw": {"Task": "Named Entity Recognition", "Dataset": "BC5CDR", "Metric": "Accuracy", "Result": "90.99"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "BC5CDR", "Metric": "Accuracy", "Result": "90.99"}}] | numeric_match_but_binding_or_label_mismatch |
| 6 | {"Task": "Named Entity Recognition (NER)", "Dataset": "NCBI", "Metric": "F1", "Result": 89.24} | [] | numeric_result_missing_or_changed |
| 7 | {"Task": "Named Entity Recognition (NER)", "Dataset": "E-commerce", "Metric": "F1", "Result": 83.99} | [] | numeric_result_missing_or_changed |
## 1910.13461.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "Exact Match (EM)", "Result": 88.8} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "F1", "Result": 94.6} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "Exact Match (EM)", "Result": 86.1} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "F1", "Result": 89.2} | [{"index": 11, "raw": {"Task": "Natural Language Inference", "Dataset": "MNLI", "Metric": "Accuracy", "Result": "89.2"}, "normalized": {"Task": "Natural Language Inference (NLI)", "Dataset": null, "Metric": "Accuracy", "Result": "89.2"}}] | normalization_null |
| 5 | {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": 89.9} | [] | numeric_result_missing_or_changed |
| 6 | {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": 90.1} | [] | numeric_result_missing_or_changed |
| 7 | {"Task": "Sentiment Analysis", "Dataset": "SST-2", "Metric": "Accuracy", "Result": 96.6} | [] | numeric_result_missing_or_changed |
| 8 | {"Task": "Paraphrase Detection", "Dataset": "QQP", "Metric": "Accuracy", "Result": 92.5} | [] | numeric_result_missing_or_changed |
| 9 | {"Task": "Natural Language Inference (NLI)", "Dataset": "QNLI", "Metric": "Accuracy", "Result": 94.9} | [] | numeric_result_missing_or_changed |
| 10 | {"Task": "Text Similarity", "Dataset": "STS-B", "Metric": "Accuracy", "Result": 91.2} | [] | numeric_result_missing_or_changed |
| 11 | {"Task": "Natural Language Inference (NLI)", "Dataset": "RTE", "Metric": "Accuracy", "Result": 87.0} | [] | numeric_result_missing_or_changed |
| 12 | {"Task": "Paraphrase Detection", "Dataset": "MRPC", "Metric": "Accuracy", "Result": 90.4} | [] | numeric_result_missing_or_changed |
| 13 | {"Task": "Linguistic Acceptability", "Dataset": "CoLA", "Metric": "Matthew's Correlation Coefficient (MCC)", "Result": 62.8} | [] | numeric_result_missing_or_changed |
| 14 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 44.16} | [{"index": 1, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-1", "Result": "44.16"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": "44.16"}}] | correct |
| 15 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 21.28} | [{"index": 2, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-2", "Result": "21.28"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": "21.28"}}] | correct |
| 16 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 40.9} | [{"index": 3, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-L", "Result": "40.90"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": "40.90"}}] | correct |
| 17 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 45.14} | [{"index": 4, "raw": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-1", "Result": "45.14"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": "45.14"}}] | correct |
| 18 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 22.27} | [{"index": 5, "raw": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-2", "Result": "22.27"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": null, "Result": "22.27"}}] | normalization_null |
| 19 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 37.25} | [{"index": 6, "raw": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-L", "Result": "37.25"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": "37.25"}}] | correct |
| 20 | {"Task": "Dialogue Generation", "Dataset": "ConvAI2", "Metric": "F1", "Result": 20.72} | [{"index": 13, "raw": {"Task": "Dialogue Response Generation", "Dataset": "ConvAI2", "Metric": "Valid F1", "Result": "20.72"}, "normalized": {"Task": "Response Generation", "Dataset": "ConvAI2", "Metric": "F1", "Result": "20.72"}}] | numeric_match_but_binding_or_label_mismatch |
| 21 | {"Task": "Dialogue Generation", "Dataset": "ConvAI2", "Metric": "Perplexity", "Result": 11.85} | [{"index": 12, "raw": {"Task": "Dialogue Response Generation", "Dataset": "ConvAI2", "Metric": "Perplexity", "Result": "11.85"}, "normalized": {"Task": "Response Generation", "Dataset": "ConvAI2", "Metric": "Perplexity", "Result": "11.85"}}] | numeric_match_but_binding_or_label_mismatch |
| 22 | {"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-1", "Result": 30.6} | [{"index": 14, "raw": {"Task": "Abstractive Question Answering", "Dataset": "ELI5", "Metric": "ROUGE-1", "Result": "30.6"}, "normalized": {"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-1", "Result": "30.6"}}] | correct |
| 23 | {"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-2", "Result": 6.2} | [{"index": 15, "raw": {"Task": "Abstractive Question Answering", "Dataset": "ELI5", "Metric": "ROUGE-2", "Result": "6.2"}, "normalized": {"Task": "Question Answering", "Dataset": "ELI5", "Metric": null, "Result": "6.2"}}] | normalization_null |
| 24 | {"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-L", "Result": 24.3} | [{"index": 16, "raw": {"Task": "Abstractive Question Answering", "Dataset": "ELI5", "Metric": "ROUGE-L", "Result": "24.3"}, "normalized": {"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-L", "Result": "24.3"}}] | correct |
| 25 | {"Task": "Machine Translation", "Dataset": "WMT’16 RO-EN", "Metric": "BLEU", "Result": 37.96} | [{"index": 17, "raw": {"Task": "Machine Translation", "Dataset": "WMT'16 RO-EN", "Metric": "BLEU", "Result": "37.96"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’16 RO-EN", "Metric": "BLEU", "Result": "37.96"}}] | correct |
## D18-1105.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 83.1} | [{"index": 1, "raw": {"Task": "Dialog Act Classification", "Dataset": "SwDA", "Metric": "Accuracy", "Result": "83.1"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": "83.1"}}] | correct |
| 2 | {"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 86.7} | [{"index": 2, "raw": {"Task": "Dialog Act Classification", "Dataset": "MRDA", "Metric": "Accuracy", "Result": "86.7"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": "86.7"}}] | correct |
## 1703.06345.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.26} | [{"index": 2, "raw": {"Task": "Chunking", "Dataset": "CoNLL 2000", "Metric": "F1", "Result": "91.26"}, "normalized": {"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": "91.26"}}] | numeric_match_but_binding_or_label_mismatch |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002 - Spanish", "Metric": "F1", "Result": 85.77} | [{"index": 4, "raw": {"Task": "NER", "Dataset": "CoNLL 2002 Spanish", "Metric": "F1", "Result": "85.77"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002 - Spanish", "Metric": "F1", "Result": "85.77"}}] | correct |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002- Dutch", "Metric": "F1", "Result": 85.19} | [{"index": 5, "raw": {"Task": "NER", "Dataset": "CoNLL 2002 Dutch", "Metric": "F1", "Result": "85.19"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002- Dutch", "Metric": "F1", "Result": "85.19"}}] | correct |
| 4 | {"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 95.41} | [{"index": 1, "raw": {"Task": "POS Tagging", "Dataset": "PTB", "Metric": "Accuracy", "Result": "95.41"}, "normalized": {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": "95.41"}}] | numeric_match_but_binding_or_label_mismatch |
| 5 | {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.55} | [] | numeric_result_missing_or_changed |
## 1903.07785.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Linguistic Acceptability", "Dataset": "CoLA", "Metric": "Matthew's Correlation Coefficient (MCC)", "Result": 53.1} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Sentiment Analysis", "Dataset": "SST-2", "Metric": "Accuracy", "Result": 94.6} | [{"index": 9, "raw": {"Task": "Single Sentence Classification", "Dataset": "SST-2", "Metric": "Accuracy", "Result": "94.6"}, "normalized": {"Task": null, "Dataset": "SST-2", "Metric": "Accuracy", "Result": "94.6"}}] | normalization_null |
| 3 | {"Task": "Paraphrase Detection", "Dataset": "MRPC", "Metric": "F1", "Result": 83.7} | [{"index": 1, "raw": {"Task": "Sentence Similarity", "Dataset": "MRPC", "Metric": "F1", "Result": "83.7"}, "normalized": {"Task": "Text Similarity", "Dataset": "MRPC", "Metric": "F1", "Result": "83.7"}}] | numeric_match_but_binding_or_label_mismatch |
| 4 | {"Task": "Text Similarity", "Dataset": "STS-B", "Metric": "Spearman Correlation", "Result": 84.2} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Paraphrase Detection", "Dataset": "QQP", "Metric": "F1", "Result": 71.7} | [{"index": 2, "raw": {"Task": "Sentence Similarity", "Dataset": "QQP", "Metric": "F1", "Result": "71.7"}, "normalized": {"Task": "Text Similarity", "Dataset": "QQP", "Metric": "F1", "Result": "71.7"}}] | numeric_match_but_binding_or_label_mismatch |
| 6 | {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": 84.3} | [{"index": 4, "raw": {"Task": "Natural Language Inference", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": "84.3"}, "normalized": {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": "84.3"}}] | correct |
| 7 | {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": 83.8} | [{"index": 5, "raw": {"Task": "Natural Language Inference", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": "83.8"}, "normalized": {"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": "83.8"}}] | correct |
| 8 | {"Task": "Natural Language Inference (NLI)", "Dataset": "QNLI", "Metric": "Accuracy", "Result": 89.8} | [{"index": 6, "raw": {"Task": "Natural Language Inference", "Dataset": "QNLI", "Metric": "Accuracy", "Result": "89.8"}, "normalized": {"Task": "Natural Language Inference (NLI)", "Dataset": "QNLI", "Metric": "Accuracy", "Result": "89.8"}}] | correct |
| 9 | {"Task": "Natural Language Inference (NLI)", "Dataset": "RTE", "Metric": "Accuracy", "Result": 63.7} | [{"index": 7, "raw": {"Task": "Natural Language Inference", "Dataset": "RTE", "Metric": "Accuracy", "Result": "63.7"}, "normalized": {"Task": "Natural Language Inference (NLI)", "Dataset": "RTE", "Metric": "Accuracy", "Result": "63.7"}}] | correct |
| 10 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.5} | [] | numeric_result_missing_or_changed |
| 11 | {"Task": "Constituency Parsing", "Dataset": "Penn Treebank (PTB)", "Metric": "F1", "Result": 95.6} | [{"index": 10, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2003", "Metric": "F1", "Result": "95.6"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": "95.6"}}] | numeric_match_but_binding_or_label_mismatch |
## 1912.08777.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 47.21} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 24.56} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 39.25} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 44.17} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 21.47} | [] | numeric_result_missing_or_changed |
| 6 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 41.11} | [] | numeric_result_missing_or_changed |
| 7 | {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-1", "Result": 45.15} | [] | numeric_result_missing_or_changed |
| 8 | {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-2", "Result": 33.51} | [] | numeric_result_missing_or_changed |
| 9 | {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-L", "Result": 41.33} | [] | numeric_result_missing_or_changed |
| 10 | {"Task": "Summarization", "Dataset": "Multi-News", "Metric": "ROGUE-1", "Result": 47.52} | [] | numeric_result_missing_or_changed |
| 11 | {"Task": "Summarization", "Dataset": "Multi-News", "Metric": "ROGUE-2", "Result": 18.72} | [] | numeric_result_missing_or_changed |
| 12 | {"Task": "Summarization", "Dataset": "Multi-News", "Metric": "ROGUE-L", "Result": 24.91} | [] | numeric_result_missing_or_changed |
| 13 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 39.12} | [] | numeric_result_missing_or_changed |
| 14 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 19.86} | [] | numeric_result_missing_or_changed |
| 15 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 36.24} | [] | numeric_result_missing_or_changed |
| 16 | {"Task": "Summarization", "Dataset": "WikiHow", "Metric": "ROGUE-1", "Result": 43.06} | [] | numeric_result_missing_or_changed |
| 17 | {"Task": "Summarization", "Dataset": "WikiHow", "Metric": "ROGUE-2", "Result": 19.71} | [] | numeric_result_missing_or_changed |
| 18 | {"Task": "Summarization", "Dataset": "WikiHow", "Metric": "ROGUE-L", "Result": 34.8} | [] | numeric_result_missing_or_changed |
| 19 | {"Task": "Summarization", "Dataset": "Reddit TIFU", "Metric": "ROGUE-1", "Result": 26.63} | [] | numeric_result_missing_or_changed |
| 20 | {"Task": "Summarization", "Dataset": "Reddit TIFU", "Metric": "ROGUE-2", "Result": 9.01} | [] | numeric_result_missing_or_changed |
| 21 | {"Task": "Summarization", "Dataset": "Reddit TIFU", "Metric": "ROGUE-L", "Result": 21.64} | [] | numeric_result_missing_or_changed |
| 22 | {"Task": "Summarization", "Dataset": "BIGPATENT", "Metric": "ROGUE-1", "Result": 53.63} | [] | numeric_result_missing_or_changed |
| 23 | {"Task": "Summarization", "Dataset": "BIGPATENT", "Metric": "ROGUE-2", "Result": 33.16} | [] | numeric_result_missing_or_changed |
| 24 | {"Task": "Summarization", "Dataset": "BIGPATENT", "Metric": "ROGUE-L", "Result": 42.25} | [] | numeric_result_missing_or_changed |
| 25 | {"Task": "Summarization", "Dataset": "arXiv", "Metric": "ROGUE-1", "Result": 44.7} | [] | numeric_result_missing_or_changed |
| 26 | {"Task": "Summarization", "Dataset": "arXiv", "Metric": "ROGUE-2", "Result": 17.27} | [] | numeric_result_missing_or_changed |
| 27 | {"Task": "Summarization", "Dataset": "arXiv", "Metric": "ROGUE-L", "Result": 25.8} | [] | numeric_result_missing_or_changed |
| 28 | {"Task": "Summarization", "Dataset": "PubMed", "Metric": "ROGUE-1", "Result": 45.49} | [] | numeric_result_missing_or_changed |
| 29 | {"Task": "Summarization", "Dataset": "PubMed", "Metric": "ROGUE-2", "Result": 19.9} | [] | numeric_result_missing_or_changed |
| 30 | {"Task": "Summarization", "Dataset": "PubMed", "Metric": "ROGUE-L", "Result": 27.69} | [] | numeric_result_missing_or_changed |
| 31 | {"Task": "Summarization", "Dataset": "AESLC", "Metric": "ROGUE-1", "Result": 37.69} | [] | numeric_result_missing_or_changed |
| 32 | {"Task": "Summarization", "Dataset": "AESLC", "Metric": "ROGUE-2", "Result": 21.85} | [] | numeric_result_missing_or_changed |
| 33 | {"Task": "Summarization", "Dataset": "AESLC", "Metric": "ROGUE-L", "Result": 36.84} | [] | numeric_result_missing_or_changed |
| 34 | {"Task": "Summarization", "Dataset": "BillSum", "Metric": "ROGUE-1", "Result": 57.31} | [] | numeric_result_missing_or_changed |
| 35 | {"Task": "Summarization", "Dataset": "BillSum", "Metric": "ROGUE-2", "Result": 40.19} | [] | numeric_result_missing_or_changed |
| 36 | {"Task": "Summarization", "Dataset": "BillSum", "Metric": "ROGUE-L", "Result": 45.82} | [] | numeric_result_missing_or_changed |
## 1711.05568.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 81.3} | [{"index": 1, "raw": {"Task": "Dialogue Act Recognition", "Dataset": "SwDA", "Metric": "Accuracy", "Result": "81.3"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": "81.3"}}] | correct |
| 2 | {"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 91.7} | [{"index": 2, "raw": {"Task": "Dialogue Act Recognition", "Dataset": "MRDA", "Metric": "Accuracy", "Result": "91.7"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": "91.7"}}] | correct |
## wang19f.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Language Modeling", "Dataset": "WikiText-103", "Metric": "Perplexity", "Result": 28.0} | [{"index": 3, "raw": {"Task": "Neural Language Modeling", "Dataset": "Wikitext-103 (WT103)", "Metric": "Test Perplexity", "Result": "28.0"}, "normalized": {"Task": "Language Modeling", "Dataset": "WikiText-103", "Metric": "Perplexity", "Result": "28.0"}}] | correct |
| 2 | {"Task": "Language Modeling", "Dataset": "Penn Treebank (PTB)", "Metric": "Perplexity", "Result": 46.01} | [{"index": 1, "raw": {"Task": "Neural Language Modeling", "Dataset": "Penn Treebank (PTB)", "Metric": "Test Perplexity", "Result": "46.01"}, "normalized": {"Task": "Language Modeling", "Dataset": "Penn Treebank (PTB)", "Metric": "Perplexity", "Result": "46.01"}}] | correct |
| 3 | {"Task": "Language Modeling", "Dataset": "Wikitext-2", "Metric": "Perplexity", "Result": 38.65} | [{"index": 2, "raw": {"Task": "Neural Language Modeling", "Dataset": "Wikitext-2 (WT2)", "Metric": "Test Perplexity", "Result": "38.65"}, "normalized": {"Task": "Language Modeling", "Dataset": "Wikitext-2", "Metric": "Perplexity", "Result": "38.65"}}] | correct |
| 4 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.52} | [{"index": 4, "raw": {"Task": "Neural Machine Translation", "Dataset": "WMT2014 En→De", "Metric": "BLEU", "Result": "29.52"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": "29.52"}}] | correct |
| 5 | {"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 35.18} | [{"index": 5, "raw": {"Task": "Neural Machine Translation", "Dataset": "IWSLT2014 De→En", "Metric": "BLEU", "Result": "35.18"}, "normalized": {"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": "35.18"}}] | correct |
## 128538.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 53.48} | [{"index": 1, "raw": {"Task": "Named Entity Recognition", "Dataset": "WNUT 2016", "Metric": "F1", "Result": "53.48"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": "53.48"}}] | correct |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 50.52} | [{"index": 2, "raw": {"Task": "Named Entity Recognition", "Dataset": "WNUT 2017", "Metric": "F1", "Result": "50.52"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": "50.52"}}] | correct |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.76} | [{"index": 3, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL 2003 (English)", "Metric": "F1", "Result": "93.76"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": "93.76"}}] | correct |
| 4 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Multimodal", "Metric": "F1", "Result": 74.17} | [{"index": 4, "raw": {"Task": "Named Entity Recognition (Multimodal)", "Dataset": "Multimodal", "Metric": "F1", "Result": "74.17"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "Multimodal", "Metric": "F1", "Result": "74.17"}}] | correct |
## 1511.08308.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.62} | [{"index": 1, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL-2003", "Metric": "F1", "Result": "91.62"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": "91.62"}}] | correct |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 86.28} | [{"index": 2, "raw": {"Task": "Named Entity Recognition", "Dataset": "OntoNotes 5.0", "Metric": "F1", "Result": "86.28"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": "86.28"}}] | correct |
## 1603.01354.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "Precision", "Result": 91.35} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "Recall", "Result": 91.06} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.21} | [{"index": 2, "raw": {"Task": "Named Entity Recognition", "Dataset": "CoNLL 2003", "Metric": "F1", "Result": "91.21"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": "91.21"}}] | correct |
| 4 | {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.55} | [{"index": 1, "raw": {"Task": "POS Tagging", "Dataset": "WSJ portion of Penn Treebank (PTB)", "Metric": "Accuracy", "Result": "97.55"}, "normalized": {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": "97.55"}}] | correct |
## 1804.09849.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 41.0} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 28.49} | [] | numeric_result_missing_or_changed |
## 1806.03489.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.73} | [{"index": 1, "raw": {"Task": "Named Entity Recognition", "Dataset": "CONLL-2003", "Metric": "F1", "Result": "91.73"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": "91.73"}}] | correct |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 87.95} | [{"index": 2, "raw": {"Task": "Named Entity Recognition", "Dataset": "ONTONOTES 5.0", "Metric": "F1", "Result": "87.95"}, "normalized": {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": "87.95"}}] | correct |
## 1808.08745.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 31.89} | [{"index": 1, "raw": {"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "ROUGE-1", "Result": "31.89"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": "31.89"}}] | correct |
| 2 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 11.54} | [{"index": 2, "raw": {"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "ROUGE-2", "Result": "11.54"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": "11.54"}}] | correct |
| 3 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 25.75} | [{"index": 3, "raw": {"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "ROUGE-L", "Result": "25.75"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": "25.75"}}] | correct |
## 1809.08370.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Combinatory Categorial Grammar (CCG) Supertagging", "Dataset": "CCGBank", "Metric": "Accuracy", "Result": 96.1} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 97.0} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 92.6} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 88.8} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.74} | [{"index": 5, "raw": {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank WSJ", "Metric": "Accuracy", "Result": "97.74"}, "normalized": {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": "97.74"}}] | correct |
| 6 | {"Task": "Dependency Parsing", "Dataset": "Penn Treebank (PTB)", "Metric": "Unlabeled Attachment Score", "Result": 96.6} | [] | numeric_result_missing_or_changed |
| 7 | {"Task": "Dependency Parsing", "Dataset": "Penn Treebank (PTB)", "Metric": "Labeled Attachment Score", "Result": 95.0} | [] | numeric_result_missing_or_changed |
| 8 | {"Task": "Machine Translation", "Dataset": "IWSLT’15 EN-VI", "Metric": "BLEU", "Result": 29.6} | [] | numeric_result_missing_or_changed |
## 1811.05021.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 81.5} | [{"index": 1, "raw": {"Task": "Dialogue Act Classification", "Dataset": "SwDA", "Metric": "Accuracy", "Result": "81.5"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": "81.5"}}] | correct |
| 2 | {"Task": "Dialogue Act Classification", "Dataset": "MapTask", "Metric": "Accuracy", "Result": 68.5} | [{"index": 2, "raw": {"Task": "Dialogue Act Classification", "Dataset": "MapTask", "Metric": "Accuracy", "Result": "68.5"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "MapTask", "Metric": "Accuracy", "Result": "68.5"}}] | correct |
## 1811.09242.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy normalized mutual information (FNMI)", "Result": 9.55} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy B-Cubed (FBC)", "Result": 62.2} | [{"index": 3, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "F-BC", "Result": "62.2"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": null, "Result": "62.2"}}] | normalization_null |
| 3 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": 24.37} | [{"index": 4, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": "24.37"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": "24.37"}}] | correct |
| 4 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-Score (F-S)", "Result": 62.9} | [{"index": 1, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-S", "Result": "62.9"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-Score (F-S)", "Result": "62.9"}}] | correct |
| 5 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-Measure (V-M)", "Result": 10.1} | [] | numeric_result_missing_or_changed |
| 6 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "AVG", "Result": 25.2} | [{"index": 2, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-M AVG", "Result": "25.20"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": null, "Result": "25.20"}}] | normalization_null |
## 1812.09471.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 0.952} | [{"index": 3, "raw": {"Task": "Overall Joint Slot/Intent Accuracy", "Dataset": "SNIPS-NLU", "Metric": "Accuracy", "Result": "0.952"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": null, "Metric": "Accuracy", "Result": "0.952"}}] | normalization_null |
| 2 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 0.95} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Overall-Accuracy", "Result": 0.834} | [{"index": 6, "raw": {"Task": "Overall Joint Slot/Intent Accuracy", "Dataset": "ATIS", "Metric": "Accuracy", "Result": "0.834"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": "0.834"}}] | numeric_match_but_binding_or_label_mismatch |
| 4 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 0.918} | [{"index": 1, "raw": {"Task": "Slot Filling", "Dataset": "SNIPS-NLU", "Metric": "F1", "Result": "0.918"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": null, "Metric": "F1", "Result": "0.918"}}] | normalization_null |
| 5 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 0.977} | [{"index": 2, "raw": {"Task": "Intent Detection", "Dataset": "SNIPS-NLU", "Metric": "Accuracy", "Result": "0.977"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": null, "Metric": "Accuracy", "Result": "0.977"}}] | normalization_null |
| 6 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Overall-Accuracy", "Result": 0.809} | [{"index": 4, "raw": {"Task": "Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": "0.809"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": "0.809"}}] | numeric_match_but_binding_or_label_mismatch |
## 1812.10235.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 96.89} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 98.99} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Movie", "Metric": "F1", "Result": 93.8} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Movie", "Metric": "Accuracy", "Result": 95.91} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Home", "Metric": "F1", "Result": 95.8} | [] | numeric_result_missing_or_changed |
| 6 | {"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Home", "Metric": "Accuracy", "Result": 99.49} | [] | numeric_result_missing_or_changed |
| 7 | {"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Food", "Metric": "F1", "Result": 98.2} | [] | numeric_result_missing_or_changed |
| 8 | {"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Food", "Metric": "Accuracy", "Result": 99.27} | [] | numeric_result_missing_or_changed |
## 1901.10430.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.2} | [{"index": 2, "raw": {"Task": "Machine Translation", "Dataset": "WMT English-French (newstest2014)", "Metric": "BLEU", "Result": "43.2"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": "43.2"}}] | correct |
| 2 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.7} | [{"index": 1, "raw": {"Task": "Machine Translation", "Dataset": "WMT English-German (newstest2014)", "Metric": "BLEU", "Result": "29.7"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": "29.7"}}] | correct |
| 3 | {"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 35.2} | [{"index": 3, "raw": {"Task": "Machine Translation", "Dataset": "IWSLT'14 German-English", "Metric": "BLEU", "Result": "35.2"}, "normalized": {"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": "35.2"}}] | correct |
| 4 | {"Task": "Machine Translation", "Dataset": "WMT’17 EN-ZH", "Metric": "BLEU", "Result": 24.4} | [{"index": 4, "raw": {"Task": "Machine Translation", "Dataset": "WMT Chinese-English (newstest2017)", "Metric": "BLEU", "Result": "24.4"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’17 EN-ZH", "Metric": "BLEU", "Result": "24.4"}}] | correct |
| 5 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 39.84} | [{"index": 6, "raw": {"Task": "Summarization", "Dataset": "CNN-DailyMail", "Metric": "ROUGE-1", "Result": "39.84"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": null, "Result": "39.84"}}] | normalization_null |
| 6 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 16.25} | [{"index": 7, "raw": {"Task": "Summarization", "Dataset": "CNN-DailyMail", "Metric": "ROUGE-2", "Result": "16.25"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": "16.25"}}] | correct |
| 7 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 36.73} | [{"index": 8, "raw": {"Task": "Summarization", "Dataset": "CNN-DailyMail", "Metric": "ROUGE-L", "Result": "36.73"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": "36.73"}}] | correct |
| 8 | {"Task": "Language Modeling", "Dataset": "Google Billion Word", "Metric": "Perplexity", "Result": 26.67} | [{"index": 5, "raw": {"Task": "Language Modeling", "Dataset": "Google Billion Word", "Metric": "Perplexity (Test)", "Result": "26.67"}, "normalized": {"Task": "Language Modeling", "Dataset": "Google Billion Word", "Metric": "Perplexity", "Result": "26.67"}}] | correct |
## 1905.12598.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy normalized mutual information (FNMI)", "Result": 21.4} | [{"index": 1, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "FNMI", "Result": "21.4"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy normalized mutual information (FNMI)", "Result": "21.4"}}] | correct |
| 2 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy B-Cubed (FBC)", "Result": 64.0} | [{"index": 2, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "FBC", "Result": "64.0"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy B-Cubed (FBC)", "Result": "64.0"}}] | correct |
| 3 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": 37.0} | [{"index": 3, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": "37.0"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": "37.0"}}] | correct |
| 4 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-Score (F-S)", "Result": 71.3} | [{"index": 4, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-S", "Result": "71.3"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-Score (F-S)", "Result": "71.3"}}] | correct |
| 5 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-Measure (V-M)", "Result": 40.4} | [{"index": 5, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-M", "Result": "40.4"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-Measure (V-M)", "Result": "40.4"}}] | correct |
| 6 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "AVG", "Result": 53.6} | [{"index": 6, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "AVG", "Result": "53.6"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "AVG", "Result": "53.6"}}] | correct |
## 1906.05012.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 39.11} | [{"index": 1, "raw": {"Task": "Abstractive Sentence Summarization", "Dataset": "Annotated English Gigaword", "Metric": "ROUGE-1", "Result": "39.11"}, "normalized": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": "39.11"}}] | correct |
| 2 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 19.78} | [{"index": 2, "raw": {"Task": "Abstractive Sentence Summarization", "Dataset": "Annotated English Gigaword", "Metric": "ROUGE-2", "Result": "19.78"}, "normalized": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": "19.78"}}] | correct |
| 3 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 36.87} | [{"index": 3, "raw": {"Task": "Abstractive Sentence Summarization", "Dataset": "Annotated English Gigaword", "Metric": "ROUGE-L", "Result": "36.87"}, "normalized": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": "36.87"}}] | correct |
## 1907.00390.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 95.8} | [{"index": 1, "raw": {"Task": "Slot Filling", "Dataset": "ATIS", "Metric": "F1-score", "Result": "95.80"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": "95.80"}}] | correct |
| 2 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 97.76} | [{"index": 2, "raw": {"Task": "Intent Detection", "Dataset": "ATIS", "Metric": "Accuracy", "Result": "97.76"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": "97.76"}}] | correct |
| 3 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Sent-Accuracy", "Result": 86.9} | [{"index": 3, "raw": {"Task": "Sentence-level Semantic Frame Accuracy", "Dataset": "ATIS", "Metric": "Accuracy", "Result": "86.90"}, "normalized": {"Task": null, "Dataset": "ATIS", "Metric": "Accuracy", "Result": "86.90"}}] | normalization_null |
| 4 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 92.23} | [{"index": 4, "raw": {"Task": "Slot Filling", "Dataset": "Snips", "Metric": "F1-score", "Result": "92.23"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": "92.23"}}] | correct |
| 5 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 97.43} | [{"index": 5, "raw": {"Task": "Intent Detection", "Dataset": "Snips", "Metric": "Accuracy", "Result": "97.43"}, "normalized": {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": "97.43"}}] | correct |
| 6 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Sent-Accuracy", "Result": 80.57} | [{"index": 6, "raw": {"Task": "Sentence-level Semantic Frame Accuracy", "Dataset": "Snips", "Metric": "Accuracy", "Result": "80.57"}, "normalized": {"Task": null, "Dataset": "SNIPS", "Metric": "Accuracy", "Result": "80.57"}}] | normalization_null |
## 1908.08345.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 43.85} | [{"index": 1, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-1", "Result": "43.85"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": "43.85"}}] | correct |
| 2 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 20.34} | [{"index": 2, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-2", "Result": "20.34"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": null, "Result": "20.34"}}] | normalization_null |
| 3 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 39.9} | [{"index": 3, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-L", "Result": "39.90"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": "39.90"}}] | correct |
| 4 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 38.81} | [{"index": 7, "raw": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-1", "Result": "38.81"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": "38.81"}}] | correct |
| 5 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 16.5} | [{"index": 8, "raw": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-2", "Result": "16.50"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": null, "Result": "16.50"}}] | normalization_null |
| 6 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 31.27} | [{"index": 9, "raw": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-L", "Result": "31.27"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": "31.27"}}] | correct |
| 7 | {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-1", "Result": 49.02} | [{"index": 4, "raw": {"Task": "Summarization", "Dataset": "NYT", "Metric": "ROUGE-1", "Result": "49.02"}, "normalized": {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": null, "Result": "49.02"}}] | normalization_null |
| 8 | {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-2", "Result": 31.02} | [{"index": 5, "raw": {"Task": "Summarization", "Dataset": "NYT", "Metric": "ROUGE-2", "Result": "31.02"}, "normalized": {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-2", "Result": "31.02"}}] | correct |
| 9 | {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-L", "Result": 45.55} | [{"index": 6, "raw": {"Task": "Summarization", "Dataset": "NYT", "Metric": "ROUGE-L", "Result": "45.55"}, "normalized": {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-L", "Result": "45.55"}}] | correct |
## 1909.02188.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 95.9} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 96.9} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Overall-Accuracy", "Result": 86.5} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 94.2} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 98.0} | [] | numeric_result_missing_or_changed |
| 6 | {"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Overall-Accuracy", "Result": 86.9} | [] | numeric_result_missing_or_changed |
## 1911.09483.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.5} | [{"index": 1, "raw": {"Task": "Machine Translation", "Dataset": "WMT14 En-Fr", "Metric": "BLEU", "Result": "43.5"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": "43.5"}}] | correct |
| 2 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.9} | [{"index": 2, "raw": {"Task": "Machine Translation", "Dataset": "WMT14 En-De", "Metric": "BLEU", "Result": "29.9"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": "29.9"}}] | correct |
| 3 | {"Task": "Machine Translation", "Dataset": "IWSLT’15 EN-VI", "Metric": "BLEU", "Result": 31.3} | [{"index": 4, "raw": {"Task": "Machine Translation", "Dataset": "IWSLT 2015 En-Vi", "Metric": "BLEU", "Result": "31.3"}, "normalized": {"Task": "Machine Translation", "Dataset": "IWSLT’15 EN-VI", "Metric": "BLEU", "Result": "31.3"}}] | correct |
| 4 | {"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 36.3} | [{"index": 3, "raw": {"Task": "Machine Translation", "Dataset": "IWSLT 2014 De-En", "Metric": "BLEU", "Result": "36.3"}, "normalized": {"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": "36.3"}}] | correct |
## 1911.10390.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 39.19} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 20.47} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 36.69} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "BERTScore", "Result": 61.51} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-1", "Result": 45.93} | [{"index": 1, "raw": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROUGE-1", "Result": "45.93"}, "normalized": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": null, "Result": "45.93"}}] | normalization_null |
| 6 | {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-2", "Result": 24.14} | [{"index": 2, "raw": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROUGE-2", "Result": "24.14"}, "normalized": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": null, "Result": "24.14"}}] | normalization_null |
| 7 | {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-L", "Result": 42.51} | [{"index": 3, "raw": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROUGE-L", "Result": "42.51"}, "normalized": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-L", "Result": "42.51"}}] | correct |
| 8 | {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "BERTScore", "Result": 66.2} | [{"index": 4, "raw": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "BERT-S", "Result": "66.20"}, "normalized": {"Task": "Summarization", "Dataset": "Newsroom", "Metric": "BERTScore", "Result": "66.20"}}] | correct |
## 2001.04063.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 44.2} | [{"index": 1, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-1", "Result": "44.20"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": "44.20"}}] | correct |
| 2 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 21.17} | [{"index": 2, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-2", "Result": "21.17"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": null, "Result": "21.17"}}] | normalization_null |
| 3 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 41.3} | [{"index": 3, "raw": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-L", "Result": "41.30"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": "41.30"}}] | correct |
| 4 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 39.51} | [{"index": 4, "raw": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROUGE-1", "Result": "39.51"}, "normalized": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": null, "Result": "39.51"}}] | normalization_null |
| 5 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 20.42} | [{"index": 5, "raw": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROUGE-2", "Result": "20.42"}, "normalized": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": "20.42"}}] | correct |
| 6 | {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 36.69} | [{"index": 6, "raw": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROUGE-L", "Result": "36.69"}, "normalized": {"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": "36.69"}}] | correct |
| 7 | {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "BLEU-4", "Result": 25.8} | [{"index": 7, "raw": {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "BLEU-4", "Result": "25.80"}, "normalized": {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "BLEU-4", "Result": "25.80"}}] | correct |
| 8 | {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "METEOR", "Result": 27.54} | [{"index": 8, "raw": {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "METEOR", "Result": "27.54"}, "normalized": {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "METEOR", "Result": "27.54"}}] | correct |
| 9 | {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "ROGUE-L", "Result": 53.65} | [{"index": 9, "raw": {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "ROUGE-L", "Result": "53.65"}, "normalized": {"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "ROGUE-L", "Result": "53.65"}}] | correct |
## 2002.03184.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.2} | [{"index": 2, "raw": {"Task": "Machine Translation", "Dataset": "WMT En-Fr", "Metric": "BLEU", "Result": "43.2"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": "43.2"}}] | correct |
| 2 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.6} | [{"index": 1, "raw": {"Task": "Machine Translation", "Dataset": "WMT En-De", "Metric": "BLEU", "Result": "29.6"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": "29.6"}}] | correct |
| 3 | {"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 35.5} | [{"index": 3, "raw": {"Task": "Machine Translation", "Dataset": "IWSLT De-En", "Metric": "BLEU", "Result": "35.5"}, "normalized": {"Task": "Machine Translation", "Dataset": null, "Metric": "BLEU", "Result": "35.5"}}] | normalization_null |
| 4 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 40.59} | [{"index": 4, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNN-DailyMail", "Metric": "ROUGE-1", "Result": "40.59"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": "40.59"}}] | correct |
| 5 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 18.97} | [{"index": 5, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNN-DailyMail", "Metric": "ROUGE-2", "Result": "18.97"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": null, "Result": "18.97"}}] | normalization_null |
| 6 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 36.81} | [{"index": 6, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNN-DailyMail", "Metric": "ROUGE-L", "Result": "36.81"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": "36.81"}}] | correct |
| 7 | {"Task": "Language Modeling", "Dataset": "WikiText-103", "Metric": "Perplexity", "Result": 23.3} | [{"index": 7, "raw": {"Task": "Language Modeling", "Dataset": "WikiText-103", "Metric": "Test Perplexity", "Result": "23.3"}, "normalized": {"Task": "Language Modeling", "Dataset": "WikiText-103", "Metric": "Perplexity", "Result": "23.3"}}] | correct |
## 2008.07772.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "TER", "Result": 40.3} | [{"index": 3, "raw": {"Task": "Machine Translation", "Dataset": "WMT'14 English-French", "Metric": "TER", "Result": "40.3"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "TER", "Result": "40.3"}}] | correct |
| 2 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "METEOR", "Result": 62.4} | [{"index": 4, "raw": {"Task": "Machine Translation", "Dataset": "WMT'14 English-French", "Metric": "METEOR", "Result": "62.4"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "METEOR", "Result": "62.4"}}] | correct |
| 3 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.8} | [{"index": 1, "raw": {"Task": "Machine Translation", "Dataset": "WMT'14 English-French", "Metric": "BLEU (multi-bleu.perl)", "Result": "43.8"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": "43.8"}}] | correct |
| 4 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "TER", "Result": 51.8} | [] | numeric_result_missing_or_changed |
| 5 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "METEOR", "Result": 48.3} | [{"index": 8, "raw": {"Task": "Machine Translation", "Dataset": "WMT'14 English-German", "Metric": "METEOR", "Result": "48.3"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "METEOR", "Result": "48.3"}}] | correct |
| 6 | {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 30.1} | [{"index": 5, "raw": {"Task": "Machine Translation", "Dataset": "WMT'14 English-German", "Metric": "BLEU (multi-bleu.perl)", "Result": "30.1"}, "normalized": {"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": "30.1"}}] | correct |
## 2203.16804.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 47.78} | [{"index": 1, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNNDM", "Metric": "ROUGE-1", "Result": "47.78"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": null, "Result": "47.78"}}] | normalization_null |
| 2 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 23.55} | [{"index": 2, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNNDM", "Metric": "ROUGE-2", "Result": "23.55"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": "23.55"}}] | correct |
| 3 | {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 44.57} | [{"index": 3, "raw": {"Task": "Abstractive Summarization", "Dataset": "CNNDM", "Metric": "ROUGE-L", "Result": "44.57"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": "44.57"}}] | correct |
| 4 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 49.07} | [{"index": 4, "raw": {"Task": "Abstractive Summarization", "Dataset": "XSum", "Metric": "ROUGE-1", "Result": "49.07"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": null, "Result": "49.07"}}] | normalization_null |
| 5 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 25.59} | [{"index": 5, "raw": {"Task": "Abstractive Summarization", "Dataset": "XSum", "Metric": "ROUGE-2", "Result": "25.59"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": null, "Result": "25.59"}}] | normalization_null |
| 6 | {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 40.4} | [{"index": 6, "raw": {"Task": "Abstractive Summarization", "Dataset": "XSum", "Metric": "ROUGE-L", "Result": "40.40"}, "normalized": {"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": "40.40"}}] | correct |
| 7 | {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-1", "Result": 57.75} | [{"index": 7, "raw": {"Task": "Abstractive Summarization", "Dataset": "NYT", "Metric": "ROUGE-1", "Result": "57.75"}, "normalized": {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": null, "Result": "57.75"}}] | normalization_null |
| 8 | {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-2", "Result": 38.64} | [{"index": 8, "raw": {"Task": "Abstractive Summarization", "Dataset": "NYT", "Metric": "ROUGE-2", "Result": "38.64"}, "normalized": {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": null, "Result": "38.64"}}] | normalization_null |
| 9 | {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-L", "Result": 54.54} | [{"index": 9, "raw": {"Task": "Abstractive Summarization", "Dataset": "NYT", "Metric": "ROUGE-L", "Result": "54.54"}, "normalized": {"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-L", "Result": "54.54"}}] | correct |
## C18-1139.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.09} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - German", "Metric": "F1", "Result": 88.32} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 96.72} | [] | numeric_result_missing_or_changed |
| 4 | {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.85} | [] | numeric_result_missing_or_changed |
## D18-1523.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy normalized mutual information (FNMI)", "Result": 11.26} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy B-Cubed (FBC)", "Result": 57.49} | [] | numeric_result_missing_or_changed |
| 3 | {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": 25.43} | [{"index": 1, "raw": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": "25.43"}, "normalized": {"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": "25.43"}}] | correct |
## D19-1367.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Language Modeling", "Dataset": "Penn Treebank (PTB)", "Metric": "Perplexity", "Result": 56.0} | [{"index": 1, "raw": {"Task": "Language Modeling", "Dataset": "PTB", "Metric": "Perplexity", "Result": "56.0"}, "normalized": {"Task": "Language Modeling", "Dataset": "Penn Treebank (PTB)", "Metric": "Perplexity", "Result": "56.0"}}] | correct |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.47} | [] | numeric_result_missing_or_changed |
## K19-1036.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 82.3} | [{"index": 1, "raw": {"Task": "Dialogue Act Classification", "Dataset": "SWDA", "Metric": "Accuracy", "Result": "82.3"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": "82.3"}}] | correct |
| 2 | {"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 92.2} | [{"index": 2, "raw": {"Task": "Dialogue Act Classification", "Dataset": "MRDA", "Metric": "Accuracy", "Result": "92.2"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": "92.2"}}] | correct |
| 3 | {"Task": "Dialogue Act Classification", "Dataset": "Dailydialog (DyDA)", "Metric": "Accuracy", "Result": 88.1} | [{"index": 3, "raw": {"Task": "Dialogue Act Classification", "Dataset": "DyDA", "Metric": "Accuracy", "Result": "88.1"}, "normalized": {"Task": "Dialogue Act Classification", "Dataset": "Dailydialog (DyDA)", "Metric": "Accuracy", "Result": "88.1"}}] | correct |
## N19-1373.pdf

| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |
| --- | --- | --- | --- |
| 1 | {"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 82.9} | [] | numeric_result_missing_or_changed |
| 2 | {"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 91.1} | [] | numeric_result_missing_or_changed |