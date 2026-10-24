# 逐条 Gold 对照（离线诊断）

预测索引从0开始。数值存在但名称或绑定不同，并不单凭该检查认定 Baseline 混入。

|论文|Gold索引|Gold TDMR|严格数值对应预测|严格TDMR对应预测|分类|
|---|---:|---|---|---|---|
|2020.findings-emnlp.378.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 90.32}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2020.findings-emnlp.378.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 55.14}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2020.findings-emnlp.378.pdf|2|{"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 50.68}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2020.findings-emnlp.378.pdf|3|{"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v4 - Chinese", "Metric": "F1", "Result": 81.18}|[3]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2020.findings-emnlp.378.pdf|4|{"Task": "Named Entity Recognition (NER)", "Dataset": "Resume - Chinese", "Metric": "F1", "Result": 96.62}|[4]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2020.findings-emnlp.378.pdf|5|{"Task": "Named Entity Recognition (NER)", "Dataset": "Weibo - Chinese", "Metric": "F1", "Result": 69.78}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1709.04109.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.85}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1709.04109.pdf|1|{"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 96.13}|[]|[]|VALUE_NOT_PRESENT|
|1709.04109.pdf|2|{"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.59}|[]|[]|VALUE_NOT_PRESENT|
|D18-1279.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.64}|[2]|[2]|STRICT_TDMR_MATCH|
|D18-1279.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - German", "Metric": "F1", "Result": 79.43}|[3]|[3]|STRICT_TDMR_MATCH|
|D18-1279.pdf|2|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002 - Spanish", "Metric": "F1", "Result": 86.68}|[0]|[0]|STRICT_TDMR_MATCH|
|D18-1279.pdf|3|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002- Dutch", "Metric": "F1", "Result": 87.81}|[1]|[1]|STRICT_TDMR_MATCH|
|D18-1279.pdf|4|{"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 95.29}|[4]|[4]|STRICT_TDMR_MATCH|
|D18-1279.pdf|5|{"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "F1", "Result": 97.58}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2020.emnlp-main.523.pdf|0|{"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "Precision", "Result": 79.9}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.523.pdf|1|{"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "Recall", "Result": 76.6}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.523.pdf|2|{"Task": "Entity Typing", "Dataset": "Open Entity", "Metric": "F1", "Result": 78.2}|[0]|[0]|STRICT_TDMR_MATCH|
|2020.emnlp-main.523.pdf|3|{"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "Precision", "Result": 70.4}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.523.pdf|4|{"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "Recall", "Result": 75.1}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.523.pdf|5|{"Task": "Relation Classification", "Dataset": "TACRED", "Metric": "F1", "Result": 72.7}|[1]|[1]|STRICT_TDMR_MATCH|
|2020.emnlp-main.523.pdf|6|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 94.3}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2020.emnlp-main.523.pdf|7|{"Task": "Question Answering", "Dataset": "ReCoRD", "Metric": "Exact Match (EM)", "Result": 90.6}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.523.pdf|8|{"Task": "Question Answering", "Dataset": "ReCoRD", "Metric": "F1", "Result": 91.2}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.523.pdf|9|{"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "Exact Match (EM)", "Result": 90.2}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.523.pdf|10|{"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "F1", "Result": 95.4}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|0|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 43.33}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|1|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 20.21}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|2|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 40.51}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|3|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 38.45}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|4|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 19.45}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|5|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 35.75}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|6|{"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "Exact Match (EM)", "Result": 84.7}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|7|{"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "F1", "Result": 87.6}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|8|{"Task": "Question Answering", "Dataset": "CoQA", "Metric": "F1", "Result": 84.9}|[4]|[4]|STRICT_TDMR_MATCH|
|1905.03197.pdf|9|{"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "BLEU-4", "Result": 23.75}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|10|{"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "METEOR", "Result": 25.61}|[6]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|11|{"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "ROGUE-L", "Result": 52.04}|[8]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|12|{"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "NIST-4", "Result": 2.67}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|13|{"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "BLEU-4", "Result": 4.39}|[9]|[9]|STRICT_TDMR_MATCH|
|1905.03197.pdf|14|{"Task": "Response Generation", "Dataset": "DSTC7", "Metric": "METEOR", "Result": 8.27}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|15|{"Task": "Linguistic Acceptability", "Dataset": "CoLA", "Metric": "Matthew's Correlation Coefficient (MCC)", "Result": 61.1}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|16|{"Task": "Sentiment Analysis", "Dataset": "SST-2", "Metric": "Accuracy", "Result": 94.5}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|17|{"Task": "Paraphrase Detection", "Dataset": "MRPC", "Metric": "F1", "Result": 90.0}|[3]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|18|{"Task": "Text Similarity", "Dataset": "STS-B", "Metric": "Spearman Correlation", "Result": 87.7}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|19|{"Task": "Paraphrase Detection", "Dataset": "QQP", "Metric": "F1", "Result": 71.7}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|20|{"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": 87.0}|[13]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|21|{"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": 85.9}|[14]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|22|{"Task": "Natural Language Inference (NLI)", "Dataset": "QNLI", "Metric": "Accuracy", "Result": 92.7}|[15]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1905.03197.pdf|23|{"Task": "Natural Language Inference (NLI)", "Dataset": "RTE", "Metric": "Accuracy", "Result": 70.9}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|24|{"Task": "Natural Language Inference (NLI)", "Dataset": "WNLI", "Metric": "Accuracy", "Result": 65.1}|[]|[]|VALUE_NOT_PRESENT|
|1905.03197.pdf|25|{"Task": "Natural Language Inference (NLI)", "Dataset": "AX", "Metric": "Accuracy", "Result": 38.4}|[]|[]|VALUE_NOT_PRESENT|
|1702.02098.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 90.65}|[]|[]|VALUE_NOT_PRESENT|
|1702.02098.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 86.99}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.152.pdf|0|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 96.24}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.152.pdf|1|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 97.74}|[0]|[0]|STRICT_TDMR_MATCH|
|2020.emnlp-main.152.pdf|2|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Sent-Accuracy", "Result": 88.64}|[2]|[2]|STRICT_TDMR_MATCH|
|2020.emnlp-main.152.pdf|3|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 97.05}|[]|[]|VALUE_NOT_PRESENT|
|2020.emnlp-main.152.pdf|4|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 99.04}|[3]|[3]|STRICT_TDMR_MATCH|
|2020.emnlp-main.152.pdf|5|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Sent-Accuracy", "Result": 92.96}|[5]|[5]|STRICT_TDMR_MATCH|
|2105.03654.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 58.98}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2105.03654.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 60.45}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2105.03654.pdf|2|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.56}|[]|[]|VALUE_NOT_PRESENT|
|2105.03654.pdf|3|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL++", "Metric": "F1", "Result": 94.81}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2105.03654.pdf|4|{"Task": "Named Entity Recognition (NER)", "Dataset": "BC5CDR", "Metric": "F1", "Result": 90.99}|[4]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2105.03654.pdf|5|{"Task": "Named Entity Recognition (NER)", "Dataset": "NCBI", "Metric": "F1", "Result": 89.24}|[]|[]|VALUE_NOT_PRESENT|
|2105.03654.pdf|6|{"Task": "Named Entity Recognition (NER)", "Dataset": "E-commerce", "Metric": "F1", "Result": 83.99}|[6]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|0|{"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "Exact Match (EM)", "Result": 88.8}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|1|{"Task": "Question Answering", "Dataset": "SQuAD 1.1", "Metric": "F1", "Result": 94.6}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|2|{"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "Exact Match (EM)", "Result": 86.1}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|3|{"Task": "Question Answering", "Dataset": "SQuAD 2.0", "Metric": "F1", "Result": 89.2}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|4|{"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": 89.9}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|5|{"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": 90.1}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|6|{"Task": "Sentiment Analysis", "Dataset": "SST-2", "Metric": "Accuracy", "Result": 96.6}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|7|{"Task": "Paraphrase Detection", "Dataset": "QQP", "Metric": "Accuracy", "Result": 92.5}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|8|{"Task": "Natural Language Inference (NLI)", "Dataset": "QNLI", "Metric": "Accuracy", "Result": 94.9}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|9|{"Task": "Text Similarity", "Dataset": "STS-B", "Metric": "Accuracy", "Result": 91.2}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|10|{"Task": "Natural Language Inference (NLI)", "Dataset": "RTE", "Metric": "Accuracy", "Result": 87.0}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|11|{"Task": "Paraphrase Detection", "Dataset": "MRPC", "Metric": "Accuracy", "Result": 90.4}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|12|{"Task": "Linguistic Acceptability", "Dataset": "CoLA", "Metric": "Matthew's Correlation Coefficient (MCC)", "Result": 62.8}|[]|[]|VALUE_NOT_PRESENT|
|1910.13461.pdf|13|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 44.16}|[3]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|14|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 21.28}|[4]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|15|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 40.9}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|16|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 45.14}|[6]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|17|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 22.27}|[7]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|18|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 37.25}|[8]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|19|{"Task": "Dialogue Generation", "Dataset": "ConvAI2", "Metric": "F1", "Result": 20.72}|[9]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|20|{"Task": "Dialogue Generation", "Dataset": "ConvAI2", "Metric": "Perplexity", "Result": 11.85}|[10]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|21|{"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-1", "Result": 30.6}|[11]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|22|{"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-2", "Result": 6.2}|[12]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|23|{"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-L", "Result": 24.3}|[13]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1910.13461.pdf|24|{"Task": "Machine Translation", "Dataset": "WMT’16 RO-EN", "Metric": "BLEU", "Result": 37.96}|[14]|[14]|STRICT_TDMR_MATCH|
|D18-1105.pdf|0|{"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 83.1}|[0]|[0]|STRICT_TDMR_MATCH|
|D18-1105.pdf|1|{"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 86.7}|[1]|[1]|STRICT_TDMR_MATCH|
|1703.06345.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.26}|[2]|[2]|STRICT_TDMR_MATCH|
|1703.06345.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002 - Spanish", "Metric": "F1", "Result": 85.77}|[3]|[3]|STRICT_TDMR_MATCH|
|1703.06345.pdf|2|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2002- Dutch", "Metric": "F1", "Result": 85.19}|[4]|[4]|STRICT_TDMR_MATCH|
|1703.06345.pdf|3|{"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 95.41}|[1]|[1]|STRICT_TDMR_MATCH|
|1703.06345.pdf|4|{"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.55}|[]|[]|VALUE_NOT_PRESENT|
|1903.07785.pdf|0|{"Task": "Linguistic Acceptability", "Dataset": "CoLA", "Metric": "Matthew's Correlation Coefficient (MCC)", "Result": 53.1}|[]|[]|VALUE_NOT_PRESENT|
|1903.07785.pdf|1|{"Task": "Sentiment Analysis", "Dataset": "SST-2", "Metric": "Accuracy", "Result": 94.6}|[1]|[1]|STRICT_TDMR_MATCH|
|1903.07785.pdf|2|{"Task": "Paraphrase Detection", "Dataset": "MRPC", "Metric": "F1", "Result": 83.7}|[2]|[2]|STRICT_TDMR_MATCH|
|1903.07785.pdf|3|{"Task": "Text Similarity", "Dataset": "STS-B", "Metric": "Spearman Correlation", "Result": 84.2}|[3]|[3]|STRICT_TDMR_MATCH|
|1903.07785.pdf|4|{"Task": "Paraphrase Detection", "Dataset": "QQP", "Metric": "F1", "Result": 71.7}|[4]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1903.07785.pdf|5|{"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-m", "Metric": "Accuracy", "Result": 84.3}|[5]|[5]|STRICT_TDMR_MATCH|
|1903.07785.pdf|6|{"Task": "Natural Language Inference (NLI)", "Dataset": "MNLI-mm", "Metric": "Accuracy", "Result": 83.8}|[6]|[6]|STRICT_TDMR_MATCH|
|1903.07785.pdf|7|{"Task": "Natural Language Inference (NLI)", "Dataset": "QNLI", "Metric": "Accuracy", "Result": 89.8}|[7]|[7]|STRICT_TDMR_MATCH|
|1903.07785.pdf|8|{"Task": "Natural Language Inference (NLI)", "Dataset": "RTE", "Metric": "Accuracy", "Result": 63.7}|[]|[]|VALUE_NOT_PRESENT|
|1903.07785.pdf|9|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.5}|[]|[]|VALUE_NOT_PRESENT|
|1903.07785.pdf|10|{"Task": "Constituency Parsing", "Dataset": "Penn Treebank (PTB)", "Metric": "F1", "Result": 95.6}|[9]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1711.05568.pdf|0|{"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 81.3}|[0]|[0]|STRICT_TDMR_MATCH|
|1711.05568.pdf|1|{"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 91.7}|[1]|[1]|STRICT_TDMR_MATCH|
|wang19f.pdf|0|{"Task": "Language Modeling", "Dataset": "WikiText-103", "Metric": "Perplexity", "Result": 28.0}|[2]|[2]|STRICT_TDMR_MATCH|
|wang19f.pdf|1|{"Task": "Language Modeling", "Dataset": "Penn Treebank (PTB)", "Metric": "Perplexity", "Result": 46.01}|[0]|[0]|STRICT_TDMR_MATCH|
|wang19f.pdf|2|{"Task": "Language Modeling", "Dataset": "Wikitext-2", "Metric": "Perplexity", "Result": 38.65}|[1]|[1]|STRICT_TDMR_MATCH|
|wang19f.pdf|3|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.52}|[3]|[3]|STRICT_TDMR_MATCH|
|wang19f.pdf|4|{"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 35.18}|[4]|[4]|STRICT_TDMR_MATCH|
|128538.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 53.48}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|128538.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 50.52}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|128538.pdf|2|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.76}|[2]|[2]|STRICT_TDMR_MATCH|
|128538.pdf|3|{"Task": "Named Entity Recognition (NER)", "Dataset": "Multimodal", "Metric": "F1", "Result": 74.17}|[3]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1511.08308.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.62}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1511.08308.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 86.28}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1603.01354.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "Precision", "Result": 91.35}|[]|[]|VALUE_NOT_PRESENT|
|1603.01354.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "Recall", "Result": 91.06}|[]|[]|VALUE_NOT_PRESENT|
|1603.01354.pdf|2|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.21}|[1]|[1]|STRICT_TDMR_MATCH|
|1603.01354.pdf|3|{"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.55}|[0]|[0]|STRICT_TDMR_MATCH|
|1804.09849.pdf|0|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 41.0}|[]|[]|VALUE_NOT_PRESENT|
|1804.09849.pdf|1|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 28.49}|[]|[]|VALUE_NOT_PRESENT|
|1806.03489.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 91.73}|[]|[]|VALUE_NOT_PRESENT|
|1806.03489.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 87.95}|[]|[]|VALUE_NOT_PRESENT|
|1808.08745.pdf|0|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 31.89}|[0]|[0]|STRICT_TDMR_MATCH|
|1808.08745.pdf|1|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 11.54}|[1]|[1]|STRICT_TDMR_MATCH|
|1808.08745.pdf|2|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 25.75}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1809.08370.pdf|0|{"Task": "Combinatory Categorial Grammar (CCG) Supertagging", "Dataset": "CCGBank", "Metric": "Accuracy", "Result": 96.1}|[]|[]|VALUE_NOT_PRESENT|
|1809.08370.pdf|1|{"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 97.0}|[]|[]|VALUE_NOT_PRESENT|
|1809.08370.pdf|2|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 92.6}|[]|[]|VALUE_NOT_PRESENT|
|1809.08370.pdf|3|{"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 88.8}|[]|[]|VALUE_NOT_PRESENT|
|1809.08370.pdf|4|{"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.74}|[4]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1809.08370.pdf|5|{"Task": "Dependency Parsing", "Dataset": "Penn Treebank (PTB)", "Metric": "Unlabeled Attachment Score", "Result": 96.6}|[]|[]|VALUE_NOT_PRESENT|
|1809.08370.pdf|6|{"Task": "Dependency Parsing", "Dataset": "Penn Treebank (PTB)", "Metric": "Labeled Attachment Score", "Result": 95.0}|[]|[]|VALUE_NOT_PRESENT|
|1809.08370.pdf|7|{"Task": "Machine Translation", "Dataset": "IWSLT’15 EN-VI", "Metric": "BLEU", "Result": 29.6}|[]|[]|VALUE_NOT_PRESENT|
|1811.05021.pdf|0|{"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 81.5}|[0]|[0]|STRICT_TDMR_MATCH|
|1811.05021.pdf|1|{"Task": "Dialogue Act Classification", "Dataset": "MapTask", "Metric": "Accuracy", "Result": 68.5}|[1]|[1]|STRICT_TDMR_MATCH|
|1811.09242.pdf|0|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy normalized mutual information (FNMI)", "Result": 9.55}|[]|[]|VALUE_NOT_PRESENT|
|1811.09242.pdf|1|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy B-Cubed (FBC)", "Result": 62.2}|[]|[]|VALUE_NOT_PRESENT|
|1811.09242.pdf|2|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": 24.37}|[]|[]|VALUE_NOT_PRESENT|
|1811.09242.pdf|3|{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-Score (F-S)", "Result": 62.9}|[0]|[0]|STRICT_TDMR_MATCH|
|1811.09242.pdf|4|{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-Measure (V-M)", "Result": 10.1}|[]|[]|VALUE_NOT_PRESENT|
|1811.09242.pdf|5|{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "AVG", "Result": 25.2}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1812.09471.pdf|0|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 0.952}|[3]|[3]|STRICT_TDMR_MATCH|
|1812.09471.pdf|1|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 0.95}|[]|[]|VALUE_NOT_PRESENT|
|1812.09471.pdf|2|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Overall-Accuracy", "Result": 0.834}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1812.09471.pdf|3|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 0.918}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1812.09471.pdf|4|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 0.977}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1812.09471.pdf|5|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Overall-Accuracy", "Result": 0.809}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1812.10235.pdf|0|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 96.89}|[]|[]|VALUE_NOT_PRESENT|
|1812.10235.pdf|1|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 98.99}|[]|[]|VALUE_NOT_PRESENT|
|1812.10235.pdf|2|{"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Movie", "Metric": "F1", "Result": 93.8}|[]|[]|VALUE_NOT_PRESENT|
|1812.10235.pdf|3|{"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Movie", "Metric": "Accuracy", "Result": 95.91}|[]|[]|VALUE_NOT_PRESENT|
|1812.10235.pdf|4|{"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Home", "Metric": "F1", "Result": 95.8}|[]|[]|VALUE_NOT_PRESENT|
|1812.10235.pdf|5|{"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Home", "Metric": "Accuracy", "Result": 99.49}|[]|[]|VALUE_NOT_PRESENT|
|1812.10235.pdf|6|{"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Food", "Metric": "F1", "Result": 98.2}|[]|[]|VALUE_NOT_PRESENT|
|1812.10235.pdf|7|{"Task": "Intent Detection and Slot Filling", "Dataset": "Multi-domain Food", "Metric": "Accuracy", "Result": 99.27}|[]|[]|VALUE_NOT_PRESENT|
|1901.10430.pdf|0|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.2}|[1]|[1]|STRICT_TDMR_MATCH|
|1901.10430.pdf|1|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.7}|[0]|[0]|STRICT_TDMR_MATCH|
|1901.10430.pdf|2|{"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 35.2}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1901.10430.pdf|3|{"Task": "Machine Translation", "Dataset": "WMT’17 EN-ZH", "Metric": "BLEU", "Result": 24.4}|[3]|[3]|STRICT_TDMR_MATCH|
|1901.10430.pdf|4|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 39.84}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1901.10430.pdf|5|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 16.25}|[6]|[6]|STRICT_TDMR_MATCH|
|1901.10430.pdf|6|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 36.73}|[7]|[7]|STRICT_TDMR_MATCH|
|1901.10430.pdf|7|{"Task": "Language Modeling", "Dataset": "Google Billion Word", "Metric": "Perplexity", "Result": 26.67}|[4]|[4]|STRICT_TDMR_MATCH|
|1905.12598.pdf|0|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy normalized mutual information (FNMI)", "Result": 21.4}|[]|[]|VALUE_NOT_PRESENT|
|1905.12598.pdf|1|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy B-Cubed (FBC)", "Result": 64.0}|[]|[]|VALUE_NOT_PRESENT|
|1905.12598.pdf|2|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": 37.0}|[]|[]|VALUE_NOT_PRESENT|
|1905.12598.pdf|3|{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-Score (F-S)", "Result": 71.3}|[]|[]|VALUE_NOT_PRESENT|
|1905.12598.pdf|4|{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-Measure (V-M)", "Result": 40.4}|[]|[]|VALUE_NOT_PRESENT|
|1905.12598.pdf|5|{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "AVG", "Result": 53.6}|[]|[]|VALUE_NOT_PRESENT|
|1906.05012.pdf|0|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 39.11}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1906.05012.pdf|1|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 19.78}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1906.05012.pdf|2|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 36.87}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1907.00390.pdf|0|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 95.8}|[0]|[0]|STRICT_TDMR_MATCH|
|1907.00390.pdf|1|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 97.76}|[1]|[1]|STRICT_TDMR_MATCH|
|1907.00390.pdf|2|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Sent-Accuracy", "Result": 86.9}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1907.00390.pdf|3|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 92.23}|[3]|[3]|STRICT_TDMR_MATCH|
|1907.00390.pdf|4|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 97.43}|[4]|[4]|STRICT_TDMR_MATCH|
|1907.00390.pdf|5|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Sent-Accuracy", "Result": 80.57}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1908.08345.pdf|0|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 43.85}|[0]|[0]|STRICT_TDMR_MATCH|
|1908.08345.pdf|1|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 20.34}|[1]|[1]|STRICT_TDMR_MATCH|
|1908.08345.pdf|2|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 39.9}|[2]|[2]|STRICT_TDMR_MATCH|
|1908.08345.pdf|3|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 38.81}|[12]|[12]|STRICT_TDMR_MATCH|
|1908.08345.pdf|4|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 16.5}|[13]|[13]|STRICT_TDMR_MATCH|
|1908.08345.pdf|5|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 31.27}|[14]|[14]|STRICT_TDMR_MATCH|
|1908.08345.pdf|6|{"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-1", "Result": 49.02}|[]|[]|VALUE_NOT_PRESENT|
|1908.08345.pdf|7|{"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-2", "Result": 31.02}|[]|[]|VALUE_NOT_PRESENT|
|1908.08345.pdf|8|{"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-L", "Result": 45.55}|[]|[]|VALUE_NOT_PRESENT|
|1909.02188.pdf|0|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "F1", "Result": 95.9}|[]|[]|VALUE_NOT_PRESENT|
|1909.02188.pdf|1|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Accuracy", "Result": 96.9}|[]|[]|VALUE_NOT_PRESENT|
|1909.02188.pdf|2|{"Task": "Intent Detection and Slot Filling", "Dataset": "ATIS", "Metric": "Overall-Accuracy", "Result": 86.5}|[]|[]|VALUE_NOT_PRESENT|
|1909.02188.pdf|3|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "F1", "Result": 94.2}|[]|[]|VALUE_NOT_PRESENT|
|1909.02188.pdf|4|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Accuracy", "Result": 98.0}|[]|[]|VALUE_NOT_PRESENT|
|1909.02188.pdf|5|{"Task": "Intent Detection and Slot Filling", "Dataset": "SNIPS", "Metric": "Overall-Accuracy", "Result": 86.9}|[]|[]|VALUE_NOT_PRESENT|
|1911.09483.pdf|0|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.5}|[1]|[1]|STRICT_TDMR_MATCH|
|1911.09483.pdf|1|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.9}|[0]|[0]|STRICT_TDMR_MATCH|
|1911.09483.pdf|2|{"Task": "Machine Translation", "Dataset": "IWSLT’15 EN-VI", "Metric": "BLEU", "Result": 31.3}|[3]|[3]|STRICT_TDMR_MATCH|
|1911.09483.pdf|3|{"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 36.3}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1911.10390.pdf|0|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 39.19}|[]|[]|VALUE_NOT_PRESENT|
|1911.10390.pdf|1|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 20.47}|[]|[]|VALUE_NOT_PRESENT|
|1911.10390.pdf|2|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 36.69}|[]|[]|VALUE_NOT_PRESENT|
|1911.10390.pdf|3|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "BERTScore", "Result": 61.51}|[]|[]|VALUE_NOT_PRESENT|
|1911.10390.pdf|4|{"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-1", "Result": 45.93}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1911.10390.pdf|5|{"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-2", "Result": 24.14}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1911.10390.pdf|6|{"Task": "Summarization", "Dataset": "Newsroom", "Metric": "ROGUE-L", "Result": 42.51}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|1911.10390.pdf|7|{"Task": "Summarization", "Dataset": "Newsroom", "Metric": "BERTScore", "Result": 66.2}|[3]|[3]|STRICT_TDMR_MATCH|
|2001.04063.pdf|0|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 44.2}|[0]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2001.04063.pdf|1|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 21.17}|[1]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2001.04063.pdf|2|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 41.3}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2001.04063.pdf|3|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-1", "Result": 39.51}|[3]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2001.04063.pdf|4|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-2", "Result": 20.42}|[4]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2001.04063.pdf|5|{"Task": "Summarization", "Dataset": "Gigaword", "Metric": "ROGUE-L", "Result": 36.69}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2001.04063.pdf|6|{"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "BLEU-4", "Result": 25.8}|[6]|[6]|STRICT_TDMR_MATCH|
|2001.04063.pdf|7|{"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "METEOR", "Result": 27.54}|[7]|[7]|STRICT_TDMR_MATCH|
|2001.04063.pdf|8|{"Task": "Question Generation", "Dataset": "SQuAD 1.1", "Metric": "ROGUE-L", "Result": 53.65}|[8]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2002.03184.pdf|0|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.2}|[1]|[1]|STRICT_TDMR_MATCH|
|2002.03184.pdf|1|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 29.6}|[0]|[0]|STRICT_TDMR_MATCH|
|2002.03184.pdf|2|{"Task": "Machine Translation", "Dataset": "IWSLT’14 EN-DE", "Metric": "BLEU", "Result": 35.5}|[2]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2002.03184.pdf|3|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 40.59}|[3]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2002.03184.pdf|4|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 18.97}|[4]|[4]|STRICT_TDMR_MATCH|
|2002.03184.pdf|5|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 36.81}|[5]|[5]|STRICT_TDMR_MATCH|
|2002.03184.pdf|6|{"Task": "Language Modeling", "Dataset": "WikiText-103", "Metric": "Perplexity", "Result": 23.3}|[6]|[6]|STRICT_TDMR_MATCH|
|2008.07772.pdf|0|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "TER", "Result": 40.3}|[1]|[1]|STRICT_TDMR_MATCH|
|2008.07772.pdf|1|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "METEOR", "Result": 62.4}|[2]|[2]|STRICT_TDMR_MATCH|
|2008.07772.pdf|2|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-FR", "Metric": "BLEU", "Result": 43.8}|[0]|[0]|STRICT_TDMR_MATCH|
|2008.07772.pdf|3|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "TER", "Result": 51.8}|[4]|[4]|STRICT_TDMR_MATCH|
|2008.07772.pdf|4|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "METEOR", "Result": 48.3}|[5]|[5]|STRICT_TDMR_MATCH|
|2008.07772.pdf|5|{"Task": "Machine Translation", "Dataset": "WMT’14 EN-DE", "Metric": "BLEU", "Result": 30.1}|[3]|[3]|STRICT_TDMR_MATCH|
|2203.16804.pdf|0|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 47.78}|[]|[]|VALUE_NOT_PRESENT|
|2203.16804.pdf|1|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": 23.55}|[]|[]|VALUE_NOT_PRESENT|
|2203.16804.pdf|2|{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-L", "Result": 44.57}|[]|[]|VALUE_NOT_PRESENT|
|2203.16804.pdf|3|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-1", "Result": 49.07}|[3]|[3]|STRICT_TDMR_MATCH|
|2203.16804.pdf|4|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-2", "Result": 25.59}|[4]|[4]|STRICT_TDMR_MATCH|
|2203.16804.pdf|5|{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROGUE-L", "Result": 40.4}|[5]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2203.16804.pdf|6|{"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-1", "Result": 57.75}|[6]|[]|VALUE_PRESENT_NAMES_OR_BINDING_DIFFER|
|2203.16804.pdf|7|{"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-2", "Result": 38.64}|[7]|[7]|STRICT_TDMR_MATCH|
|2203.16804.pdf|8|{"Task": "Summarization", "Dataset": "New York Times (NYT)", "Metric": "ROGUE-L", "Result": 54.54}|[8]|[8]|STRICT_TDMR_MATCH|
|C18-1139.pdf|0|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.09}|[]|[]|VALUE_NOT_PRESENT|
|C18-1139.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - German", "Metric": "F1", "Result": 88.32}|[]|[]|VALUE_NOT_PRESENT|
|C18-1139.pdf|2|{"Task": "Text Chunking", "Dataset": "CoNLL-2000", "Metric": "F1", "Result": 96.72}|[]|[]|VALUE_NOT_PRESENT|
|C18-1139.pdf|3|{"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.85}|[]|[]|VALUE_NOT_PRESENT|
|D18-1523.pdf|0|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy normalized mutual information (FNMI)", "Result": 11.26}|[]|[]|VALUE_NOT_PRESENT|
|D18-1523.pdf|1|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "Fuzzy B-Cubed (FBC)", "Result": 57.49}|[]|[]|VALUE_NOT_PRESENT|
|D18-1523.pdf|2|{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": 25.43}|[]|[]|VALUE_NOT_PRESENT|
|D19-1367.pdf|0|{"Task": "Language Modeling", "Dataset": "Penn Treebank (PTB)", "Metric": "Perplexity", "Result": 56.0}|[0]|[0]|STRICT_TDMR_MATCH|
|D19-1367.pdf|1|{"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": 93.47}|[]|[]|VALUE_NOT_PRESENT|
|K19-1036.pdf|0|{"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 82.3}|[0]|[0]|STRICT_TDMR_MATCH|
|K19-1036.pdf|1|{"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 92.2}|[1]|[1]|STRICT_TDMR_MATCH|
|K19-1036.pdf|2|{"Task": "Dialogue Act Classification", "Dataset": "Dailydialog (DyDA)", "Metric": "Accuracy", "Result": 88.1}|[2]|[2]|STRICT_TDMR_MATCH|
|N19-1373.pdf|0|{"Task": "Dialogue Act Classification", "Dataset": "Switchboard Dialog Act Corpus (SWDA)", "Metric": "Accuracy", "Result": 82.9}|[]|[]|VALUE_NOT_PRESENT|
|N19-1373.pdf|1|{"Task": "Dialogue Act Classification", "Dataset": "ICSI Meeting Recorder Dialog Act Corpus (MRDA)", "Metric": "Accuracy", "Result": 91.1}|[]|[]|VALUE_NOT_PRESENT|
