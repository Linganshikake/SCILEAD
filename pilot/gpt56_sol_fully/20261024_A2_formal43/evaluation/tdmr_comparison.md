# Gold逐条诊断（独立辅助，不改官方指标）


## 2020.findings-emnlp.378.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 90.32|[0]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / WNUT-16 - English / F1 / 55.14|[1]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / WNUT-17 - English / F1 / 50.68|[2]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / Ontonotes v4 - Chinese / F1 / 81.18|[3]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / Resume - Chinese / F1 / 96.62|[4]|RESULT_PRESENT_TDM_MISMATCH|
|Named Entity Recognition (NER) / Weibo - Chinese / F1 / 69.78|[5]|RESULT_PRESENT_WITH_NULL|

## 1709.04109.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.85|[0]|STRICT_TDMR_MATCH|
|Text Chunking / CoNLL-2000 / F1 / 96.13|[2]|STRICT_TDMR_MATCH|
|Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.59|[]|RESULT_NOT_STRICTLY_FOUND|

## D18-1279.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.64|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2003 - German / F1 / 79.43|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 86.68|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 87.81|[]|RESULT_NOT_STRICTLY_FOUND|
|Text Chunking / CoNLL-2000 / F1 / 95.29|[]|RESULT_NOT_STRICTLY_FOUND|
|Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / F1 / 97.58|[]|RESULT_NOT_STRICTLY_FOUND|

## 2020.emnlp-main.523.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Entity Typing / Open Entity / Precision / 79.9|[0]|STRICT_TDMR_MATCH|
|Entity Typing / Open Entity / Recall / 76.6|[1]|STRICT_TDMR_MATCH|
|Entity Typing / Open Entity / F1 / 78.2|[2]|STRICT_TDMR_MATCH|
|Relation Classification / TACRED / Precision / 70.4|[3]|STRICT_TDMR_MATCH|
|Relation Classification / TACRED / Recall / 75.1|[4]|STRICT_TDMR_MATCH|
|Relation Classification / TACRED / F1 / 72.7|[5]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 94.3|[6]|STRICT_TDMR_MATCH|
|Question Answering / ReCoRD / Exact Match (EM) / 90.6|[9]|STRICT_TDMR_MATCH|
|Question Answering / ReCoRD / F1 / 91.2|[10]|STRICT_TDMR_MATCH|
|Question Answering / SQuAD 1.1 / Exact Match (EM) / 90.2|[13]|STRICT_TDMR_MATCH|
|Question Answering / SQuAD 1.1 / F1 / 95.4|[14]|STRICT_TDMR_MATCH|

## 1905.03197.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / CNN/DailyMail / ROGUE-1 / 43.33|[0]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-2 / 20.21|[1]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-L / 40.51|[2]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-1 / 38.45|[6]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-2 / 19.45|[7]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-L / 35.75|[8]|STRICT_TDMR_MATCH|
|Question Answering / SQuAD 2.0 / Exact Match (EM) / 84.7|[]|RESULT_NOT_STRICTLY_FOUND|
|Question Answering / SQuAD 2.0 / F1 / 87.6|[]|RESULT_NOT_STRICTLY_FOUND|
|Question Answering / CoQA / F1 / 84.9|[11]|STRICT_TDMR_MATCH|
|Question Generation / SQuAD 1.1 / BLEU-4 / 23.75|[17]|RESULT_PRESENT_TDM_MISMATCH|
|Question Generation / SQuAD 1.1 / METEOR / 25.61|[16]|RESULT_PRESENT_TDM_MISMATCH|
|Question Generation / SQuAD 1.1 / ROGUE-L / 52.04|[18]|STRICT_TDMR_MATCH|
|Response Generation / DSTC7 / NIST-4 / 2.67|[]|RESULT_NOT_STRICTLY_FOUND|
|Response Generation / DSTC7 / BLEU-4 / 4.39|[20]|STRICT_TDMR_MATCH|
|Response Generation / DSTC7 / METEOR / 8.27|[21]|STRICT_TDMR_MATCH|
|Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 61.1|[26]|STRICT_TDMR_MATCH|
|Sentiment Analysis / SST-2 / Accuracy / 94.5|[27]|STRICT_TDMR_MATCH|
|Paraphrase Detection / MRPC / F1 / 90.0|[28]|STRICT_TDMR_MATCH|
|Text Similarity / STS-B / Spearman Correlation / 87.7|[29]|STRICT_TDMR_MATCH|
|Paraphrase Detection / QQP / F1 / 71.7|[30]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / MNLI-m / Accuracy / 87.0|[31]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / MNLI-mm / Accuracy / 85.9|[32]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / QNLI / Accuracy / 92.7|[33]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / RTE / Accuracy / 70.9|[34]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / WNLI / Accuracy / 65.1|[35]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / AX / Accuracy / 38.4|[36]|STRICT_TDMR_MATCH|

## 1702.02098.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 90.65|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 86.99|[]|RESULT_NOT_STRICTLY_FOUND|

## 2020.emnlp-main.152.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Intent Detection and Slot Filling / ATIS / F1 / 96.24|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / ATIS / Accuracy / 97.74|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / ATIS / Sent-Accuracy / 88.64|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / SNIPS / F1 / 97.05|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / SNIPS / Accuracy / 99.04|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / SNIPS / Sent-Accuracy / 92.96|[]|RESULT_NOT_STRICTLY_FOUND|

## 2105.03654.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / WNUT-16 - English / F1 / 58.98|[0]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / WNUT-17 - English / F1 / 60.45|[1]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.56|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL++ / F1 / 94.81|[3]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / BC5CDR / F1 / 90.99|[4]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / NCBI / F1 / 89.24|[5]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / E-commerce / F1 / 83.99|[]|RESULT_NOT_STRICTLY_FOUND|

## 1910.13461.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Question Answering / SQuAD 1.1 / Exact Match (EM) / 88.8|[0]|STRICT_TDMR_MATCH|
|Question Answering / SQuAD 1.1 / F1 / 94.6|[1]|STRICT_TDMR_MATCH|
|Question Answering / SQuAD 2.0 / Exact Match (EM) / 86.1|[2]|STRICT_TDMR_MATCH|
|Question Answering / SQuAD 2.0 / F1 / 89.2|[3]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / MNLI-m / Accuracy / 89.9|[4]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / MNLI-mm / Accuracy / 90.1|[5]|STRICT_TDMR_MATCH|
|Sentiment Analysis / SST-2 / Accuracy / 96.6|[6]|STRICT_TDMR_MATCH|
|Paraphrase Detection / QQP / Accuracy / 92.5|[7]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / QNLI / Accuracy / 94.9|[8]|STRICT_TDMR_MATCH|
|Text Similarity / STS-B / Accuracy / 91.2|[9]|RESULT_PRESENT_TDM_MISMATCH|
|Natural Language Inference (NLI) / RTE / Accuracy / 87.0|[10]|STRICT_TDMR_MATCH|
|Paraphrase Detection / MRPC / Accuracy / 90.4|[11]|STRICT_TDMR_MATCH|
|Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 62.8|[12]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-1 / 44.16|[13]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-2 / 21.28|[14]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-L / 40.9|[15]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-1 / 45.14|[16]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-2 / 22.27|[17]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-L / 37.25|[18]|STRICT_TDMR_MATCH|
|Dialogue Generation / ConvAI2 / F1 / 20.72|[19]|RESULT_PRESENT_TDM_MISMATCH|
|Dialogue Generation / ConvAI2 / Perplexity / 11.85|[20]|RESULT_PRESENT_TDM_MISMATCH|
|Question Answering / ELI5 / ROGUE-1 / 30.6|[21]|STRICT_TDMR_MATCH|
|Question Answering / ELI5 / ROGUE-2 / 6.2|[22]|STRICT_TDMR_MATCH|
|Question Answering / ELI5 / ROGUE-L / 24.3|[23]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’16 RO-EN / BLEU / 37.96|[24]|STRICT_TDMR_MATCH|

## D18-1105.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 83.1|[]|RESULT_NOT_STRICTLY_FOUND|
|Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 86.7|[]|RESULT_NOT_STRICTLY_FOUND|

## 1703.06345.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.26|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2002 - Spanish / F1 / 85.77|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2002- Dutch / F1 / 85.19|[]|RESULT_NOT_STRICTLY_FOUND|
|Text Chunking / CoNLL-2000 / F1 / 95.41|[]|RESULT_NOT_STRICTLY_FOUND|
|Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.55|[]|RESULT_NOT_STRICTLY_FOUND|

## 1903.07785.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Linguistic Acceptability / CoLA / Matthew's Correlation Coefficient (MCC) / 53.1|[]|RESULT_NOT_STRICTLY_FOUND|
|Sentiment Analysis / SST-2 / Accuracy / 94.6|[1]|STRICT_TDMR_MATCH|
|Paraphrase Detection / MRPC / F1 / 83.7|[]|RESULT_NOT_STRICTLY_FOUND|
|Text Similarity / STS-B / Spearman Correlation / 84.2|[]|RESULT_NOT_STRICTLY_FOUND|
|Paraphrase Detection / QQP / F1 / 71.7|[]|RESULT_NOT_STRICTLY_FOUND|
|Natural Language Inference (NLI) / MNLI-m / Accuracy / 84.3|[5]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / MNLI-mm / Accuracy / 83.8|[6]|RESULT_PRESENT_WITH_NULL|
|Natural Language Inference (NLI) / QNLI / Accuracy / 89.8|[7]|STRICT_TDMR_MATCH|
|Natural Language Inference (NLI) / RTE / Accuracy / 63.7|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.5|[10]|STRICT_TDMR_MATCH|
|Constituency Parsing / Penn Treebank (PTB) / F1 / 95.6|[11]|STRICT_TDMR_MATCH|

## 1912.08777.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / XSum / ROGUE-1 / 47.21|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / XSum / ROGUE-2 / 24.56|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / XSum / ROGUE-L / 39.25|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / CNN/DailyMail / ROGUE-1 / 44.17|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / CNN/DailyMail / ROGUE-2 / 21.47|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / CNN/DailyMail / ROGUE-L / 41.11|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Newsroom / ROGUE-1 / 45.15|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Newsroom / ROGUE-2 / 33.51|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Newsroom / ROGUE-L / 41.33|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Multi-News / ROGUE-1 / 47.52|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Multi-News / ROGUE-2 / 18.72|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Multi-News / ROGUE-L / 24.91|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Gigaword / ROGUE-1 / 39.12|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Gigaword / ROGUE-2 / 19.86|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Gigaword / ROGUE-L / 36.24|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / WikiHow / ROGUE-1 / 43.06|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / WikiHow / ROGUE-2 / 19.71|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / WikiHow / ROGUE-L / 34.8|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Reddit TIFU / ROGUE-1 / 26.63|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Reddit TIFU / ROGUE-2 / 9.01|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / Reddit TIFU / ROGUE-L / 21.64|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / BIGPATENT / ROGUE-1 / 53.63|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / BIGPATENT / ROGUE-2 / 33.16|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / BIGPATENT / ROGUE-L / 42.25|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / arXiv / ROGUE-1 / 44.7|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / arXiv / ROGUE-2 / 17.27|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / arXiv / ROGUE-L / 25.8|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / PubMed / ROGUE-1 / 45.49|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / PubMed / ROGUE-2 / 19.9|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / PubMed / ROGUE-L / 27.69|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / AESLC / ROGUE-1 / 37.69|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / AESLC / ROGUE-2 / 21.85|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / AESLC / ROGUE-L / 36.84|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / BillSum / ROGUE-1 / 57.31|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / BillSum / ROGUE-2 / 40.19|[]|RESULT_NOT_STRICTLY_FOUND|
|Summarization / BillSum / ROGUE-L / 45.82|[]|RESULT_NOT_STRICTLY_FOUND|

## 1711.05568.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.3|[]|RESULT_NOT_STRICTLY_FOUND|
|Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 91.7|[]|RESULT_NOT_STRICTLY_FOUND|

## wang19f.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Language Modeling / WikiText-103 / Perplexity / 28.0|[5]|STRICT_TDMR_MATCH|
|Language Modeling / Penn Treebank (PTB) / Perplexity / 46.01|[1]|STRICT_TDMR_MATCH|
|Language Modeling / Wikitext-2 / Perplexity / 38.65|[3]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’14 EN-DE / BLEU / 29.52|[6]|STRICT_TDMR_MATCH|
|Machine Translation / IWSLT’14 EN-DE / BLEU / 35.18|[7]|STRICT_TDMR_MATCH|

## 128538.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / WNUT-16 - English / F1 / 53.48|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / WNUT-17 - English / F1 / 50.52|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.76|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / Multimodal / F1 / 74.17|[]|RESULT_NOT_STRICTLY_FOUND|

## 1511.08308.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.62|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 86.28|[]|RESULT_NOT_STRICTLY_FOUND|

## 1603.01354.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / Precision / 91.35|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2003 - English / Recall / 91.06|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.21|[1]|STRICT_TDMR_MATCH|
|Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.55|[]|RESULT_NOT_STRICTLY_FOUND|

## 1804.09849.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Machine Translation / WMT’14 EN-FR / BLEU / 41.0|[]|RESULT_NOT_STRICTLY_FOUND|
|Machine Translation / WMT’14 EN-DE / BLEU / 28.49|[]|RESULT_NOT_STRICTLY_FOUND|

## 1806.03489.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.73|[0]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 87.95|[1]|STRICT_TDMR_MATCH|

## 1808.08745.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / XSum / ROGUE-1 / 31.89|[0]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-2 / 11.54|[1]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-L / 25.75|[2]|STRICT_TDMR_MATCH|

## 1809.08370.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Combinatory Categorial Grammar (CCG) Supertagging / CCGBank / Accuracy / 96.1|[]|RESULT_NOT_STRICTLY_FOUND|
|Text Chunking / CoNLL-2000 / F1 / 97.0|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 92.6|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / Ontonotes v5 - English / F1 / 88.8|[]|RESULT_NOT_STRICTLY_FOUND|
|Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.74|[]|RESULT_NOT_STRICTLY_FOUND|
|Dependency Parsing / Penn Treebank (PTB) / Unlabeled Attachment Score / 96.6|[]|RESULT_NOT_STRICTLY_FOUND|
|Dependency Parsing / Penn Treebank (PTB) / Labeled Attachment Score / 95.0|[]|RESULT_NOT_STRICTLY_FOUND|
|Machine Translation / IWSLT’15 EN-VI / BLEU / 29.6|[]|RESULT_NOT_STRICTLY_FOUND|

## 1811.05021.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 81.5|[]|RESULT_NOT_STRICTLY_FOUND|
|Dialogue Act Classification / MapTask / Accuracy / 68.5|[]|RESULT_NOT_STRICTLY_FOUND|

## 1811.09242.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) / 9.55|[5]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) / 62.2|[4]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2013 Task 13 / AVG / 24.37|[6]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2010 Task 14 / F-Score (F-S) / 62.9|[0]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2010 Task 14 / V-Measure (V-M) / 10.1|[1]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2010 Task 14 / AVG / 25.2|[2]|STRICT_TDMR_MATCH|

## 1812.10235.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Intent Detection and Slot Filling / ATIS / F1 / 96.89|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / ATIS / Accuracy / 98.99|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / Multi-domain Movie / F1 / 93.8|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / Multi-domain Movie / Accuracy / 95.91|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / Multi-domain Home / F1 / 95.8|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / Multi-domain Home / Accuracy / 99.49|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / Multi-domain Food / F1 / 98.2|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / Multi-domain Food / Accuracy / 99.27|[]|RESULT_NOT_STRICTLY_FOUND|

## 1901.10430.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Machine Translation / WMT’14 EN-FR / BLEU / 43.2|[1]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’14 EN-DE / BLEU / 29.7|[0]|STRICT_TDMR_MATCH|
|Machine Translation / IWSLT’14 EN-DE / BLEU / 35.2|[2]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’17 EN-ZH / BLEU / 24.4|[3]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-1 / 39.84|[6]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-2 / 16.25|[7]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-L / 36.73|[8]|STRICT_TDMR_MATCH|
|Language Modeling / Google Billion Word / Perplexity / 26.67|[5]|STRICT_TDMR_MATCH|

## 1905.12598.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) / 21.4|[0]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) / 64.0|[1]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2013 Task 13 / AVG / 37.0|[2]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2010 Task 14 / F-Score (F-S) / 71.3|[3]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2010 Task 14 / V-Measure (V-M) / 40.4|[4]|STRICT_TDMR_MATCH|
|Word Sense Induction / SemEval 2010 Task 14 / AVG / 53.6|[5]|STRICT_TDMR_MATCH|

## 1906.05012.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / Gigaword / ROGUE-1 / 39.11|[0]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-2 / 19.78|[1]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-L / 36.87|[2]|STRICT_TDMR_MATCH|

## 1907.00390.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Intent Detection and Slot Filling / ATIS / F1 / 95.8|[0]|STRICT_TDMR_MATCH|
|Intent Detection and Slot Filling / ATIS / Accuracy / 97.76|[1]|STRICT_TDMR_MATCH|
|Intent Detection and Slot Filling / ATIS / Sent-Accuracy / 86.9|[2]|STRICT_TDMR_MATCH|
|Intent Detection and Slot Filling / SNIPS / F1 / 92.23|[3]|STRICT_TDMR_MATCH|
|Intent Detection and Slot Filling / SNIPS / Accuracy / 97.43|[4]|STRICT_TDMR_MATCH|
|Intent Detection and Slot Filling / SNIPS / Sent-Accuracy / 80.57|[5]|STRICT_TDMR_MATCH|

## 1908.08345.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / CNN/DailyMail / ROGUE-1 / 43.85|[0]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-2 / 20.34|[1]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-L / 39.9|[2]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-1 / 38.81|[12]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-2 / 16.5|[13]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-L / 31.27|[14]|STRICT_TDMR_MATCH|
|Summarization / New York Times (NYT) / ROGUE-1 / 49.02|[9]|STRICT_TDMR_MATCH|
|Summarization / New York Times (NYT) / ROGUE-2 / 31.02|[10]|STRICT_TDMR_MATCH|
|Summarization / New York Times (NYT) / ROGUE-L / 45.55|[11]|STRICT_TDMR_MATCH|

## 1909.02188.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Intent Detection and Slot Filling / ATIS / F1 / 95.9|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / ATIS / Accuracy / 96.9|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / ATIS / Overall-Accuracy / 86.5|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / SNIPS / F1 / 94.2|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / SNIPS / Accuracy / 98.0|[]|RESULT_NOT_STRICTLY_FOUND|
|Intent Detection and Slot Filling / SNIPS / Overall-Accuracy / 86.9|[]|RESULT_NOT_STRICTLY_FOUND|

## 1911.09483.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Machine Translation / WMT’14 EN-FR / BLEU / 43.5|[1]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’14 EN-DE / BLEU / 29.9|[0]|STRICT_TDMR_MATCH|
|Machine Translation / IWSLT’15 EN-VI / BLEU / 31.3|[3]|STRICT_TDMR_MATCH|
|Machine Translation / IWSLT’14 EN-DE / BLEU / 36.3|[2]|STRICT_TDMR_MATCH|

## 1911.10390.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / Gigaword / ROGUE-1 / 39.19|[0]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-2 / 20.47|[1]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-L / 36.69|[2]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / BERTScore / 61.51|[3]|STRICT_TDMR_MATCH|
|Summarization / Newsroom / ROGUE-1 / 45.93|[4]|STRICT_TDMR_MATCH|
|Summarization / Newsroom / ROGUE-2 / 24.14|[5]|STRICT_TDMR_MATCH|
|Summarization / Newsroom / ROGUE-L / 42.51|[6]|STRICT_TDMR_MATCH|
|Summarization / Newsroom / BERTScore / 66.2|[7]|STRICT_TDMR_MATCH|

## 2001.04063.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / CNN/DailyMail / ROGUE-1 / 44.2|[0]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-2 / 21.17|[1]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-L / 41.3|[2]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-1 / 39.51|[3]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-2 / 20.42|[4]|STRICT_TDMR_MATCH|
|Summarization / Gigaword / ROGUE-L / 36.69|[5]|STRICT_TDMR_MATCH|
|Question Generation / SQuAD 1.1 / BLEU-4 / 25.8|[9]|STRICT_TDMR_MATCH|
|Question Generation / SQuAD 1.1 / METEOR / 27.54|[10]|STRICT_TDMR_MATCH|
|Question Generation / SQuAD 1.1 / ROGUE-L / 53.65|[11]|STRICT_TDMR_MATCH|

## 2008.07772.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Machine Translation / WMT’14 EN-FR / TER / 40.3|[2]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’14 EN-FR / METEOR / 62.4|[3]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’14 EN-FR / BLEU / 43.8|[]|RESULT_NOT_STRICTLY_FOUND|
|Machine Translation / WMT’14 EN-DE / TER / 51.8|[6]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’14 EN-DE / METEOR / 48.3|[7]|STRICT_TDMR_MATCH|
|Machine Translation / WMT’14 EN-DE / BLEU / 30.1|[4]|STRICT_TDMR_MATCH|

## 2203.16804.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Summarization / CNN/DailyMail / ROGUE-1 / 47.78|[0]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-2 / 23.55|[1]|STRICT_TDMR_MATCH|
|Summarization / CNN/DailyMail / ROGUE-L / 44.57|[2]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-1 / 49.07|[3]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-2 / 25.59|[4]|STRICT_TDMR_MATCH|
|Summarization / XSum / ROGUE-L / 40.4|[5]|STRICT_TDMR_MATCH|
|Summarization / New York Times (NYT) / ROGUE-1 / 57.75|[6]|STRICT_TDMR_MATCH|
|Summarization / New York Times (NYT) / ROGUE-2 / 38.64|[7]|STRICT_TDMR_MATCH|
|Summarization / New York Times (NYT) / ROGUE-L / 54.54|[8]|STRICT_TDMR_MATCH|

## C18-1139.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.09|[]|RESULT_NOT_STRICTLY_FOUND|
|Named Entity Recognition (NER) / CoNLL-2003 - German / F1 / 88.32|[]|RESULT_NOT_STRICTLY_FOUND|
|Text Chunking / CoNLL-2000 / F1 / 96.72|[]|RESULT_NOT_STRICTLY_FOUND|
|Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.85|[]|RESULT_NOT_STRICTLY_FOUND|

## D18-1523.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) / 11.26|[]|RESULT_NOT_STRICTLY_FOUND|
|Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) / 57.49|[]|RESULT_NOT_STRICTLY_FOUND|
|Word Sense Induction / SemEval 2013 Task 13 / AVG / 25.43|[]|RESULT_NOT_STRICTLY_FOUND|

## D19-1367.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Language Modeling / Penn Treebank (PTB) / Perplexity / 56.0|[0]|STRICT_TDMR_MATCH|
|Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 93.47|[]|RESULT_NOT_STRICTLY_FOUND|

## K19-1036.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 82.3|[]|RESULT_NOT_STRICTLY_FOUND|
|Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 92.2|[]|RESULT_NOT_STRICTLY_FOUND|
|Dialogue Act Classification / Dailydialog (DyDA) / Accuracy / 88.1|[]|RESULT_NOT_STRICTLY_FOUND|

## N19-1373.pdf

|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|
|---|---|---|
|Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 82.9|[]|RESULT_NOT_STRICTLY_FOUND|
|Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 91.1|[]|RESULT_NOT_STRICTLY_FOUND|