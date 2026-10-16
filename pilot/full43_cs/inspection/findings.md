# 映射案例与错误记录

按实际输入字符串筛选所有相关记录；完整原始/LLM/CS 元组见 evaluation/paired_comparison.md。所有相似度来自实际选择调用，精确保留项无伪造分数。

配对统计（按 284 条预测，不按 295 条 Gold）：双方严格完整命中 74；仅 CS 命中 33；仅 LLM 命中 9；双方均未严格完整命中 168。旧 null 119 个字段全部得到候选名称；这只是原版强制 Top-1 的行为。

WN16/WN17 映射到正确的 WNUT 标准名称；ON5E→BC5CDR、RE→RTE、WE→WNUT-16 则是错误强制映射，Result 正确仍不能形成正确 TDMR。CONLL03 不含语言信息时，德语任务字段不会被 CS Dataset 编码看到，因此也映射为 English。

ROUGE-1/2 常映射到 Gold 中拼写为 ROGUE-1/2 的标准名称；ROUGE-L→BLEU、ROUGE-L F1→F1 是实际失败。大小写及输入词组不同可能得到不同结果，例如 Rouge-L→ROGUE-L；未按结果重新选择写法。

GLUE→SNIPS，联合语言理解任务→Language Modeling，是错误强制归属；抽取把具体子任务写在 Metric、Dataset 只写 GLUE 的结构也保持不变。Sentence Accuracy→Accuracy 会丢失 Sent-Accuracy 区别。

IWSLT 的若干 De-En 输入→Gold 标签 IWSLT’14 EN-DE 得到形式上的匹配，但输入与标签的方向文字相反，不能据此宣称翻译方向正确。wang19f 的 German→English 输入甚至被映射到 CoNLL-2003 - German。所有 Gold 命中与语义争议分别保留。

## 缩写 ON5E/WN16/WN17/RE/WE（5 条）

| 论文 / 序号 | 字段 | 原始 → LLM → CS | CS Top-1 | 完整元组分类 |
|---|---|---|---:|---|
| 2020.findings-emnlp.378.pdf / 1 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 1 | Dataset | ON5E → None → BC5CDR | 0.615842 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 1 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 2 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 2 | Dataset | WN16 → None → WNUT-16 - English | 0.764185 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 2 | Metric | F1 → F1 → F1 | 精确保留 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 3 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 3 | Dataset | WN17 → None → WNUT-17 - English | 0.757035 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 3 | Metric | F1 → F1 → F1 | 精确保留 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 5 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 5 | Dataset | RE → None → RTE | 0.528385 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 5 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 6 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 6 | Dataset | WE → None → WNUT-16 - English | 0.423788 | neither_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 6 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |

## CoNLL-2003 语言（18 条）

| 论文 / 序号 | 字段 | 原始 → LLM → CS | CS Top-1 | 完整元组分类 |
|---|---|---|---:|---|
| 1709.04109.pdf / 1 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | cs_only_strict_tdmr_match |
| 1709.04109.pdf / 1 | Dataset | CoNLL03 NER → None → CoNLL-2003 - English | 0.725147 | cs_only_strict_tdmr_match |
| 1709.04109.pdf / 1 | Metric | F1 score → F1 → F1 | 0.816479 | cs_only_strict_tdmr_match |
| D18-1279.pdf / 3 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | both_strict_tdmr_match |
| D18-1279.pdf / 3 | Dataset | CoNLL-2003 English → CoNLL-2003 - English → CoNLL-2003 - English | 0.959627 | both_strict_tdmr_match |
| D18-1279.pdf / 3 | Metric | F1 → F1 → F1 | 精确保留 | both_strict_tdmr_match |
| D18-1279.pdf / 4 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | both_strict_tdmr_match |
| D18-1279.pdf / 4 | Dataset | CoNLL-2003 German → CoNLL-2003 - German → CoNLL-2003 - German | 0.982921 | both_strict_tdmr_match |
| D18-1279.pdf / 4 | Metric | F1 → F1 → F1 | 精确保留 | both_strict_tdmr_match |
| 2020.emnlp-main.523.pdf / 3 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | cs_only_strict_tdmr_match |
| 2020.emnlp-main.523.pdf / 3 | Dataset | CoNLL-2003 → None → CoNLL-2003 - English | 0.917780 | cs_only_strict_tdmr_match |
| 2020.emnlp-main.523.pdf / 3 | Metric | F1 → F1 → F1 | 精确保留 | cs_only_strict_tdmr_match |
| 1702.02098.pdf / 1 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1702.02098.pdf / 1 | Dataset | CoNLL-2003 → None → CoNLL-2003 - English | 0.917780 | neither_strict_tdmr_match |
| 1702.02098.pdf / 1 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |
| 2105.03654.pdf / 3 | Task | Named Entity Recognition (NER) → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 精确保留 | neither_strict_tdmr_match |
| 2105.03654.pdf / 3 | Dataset | CoNLL-03 → None → CoNLL-2003 - English | 0.817598 | neither_strict_tdmr_match |
| 2105.03654.pdf / 3 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 2105.03654.pdf / 8 | Task | Cross-domain NER Transfer → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.460105 | neither_strict_tdmr_match |
| 2105.03654.pdf / 8 | Dataset | CoNLL-03 (train) → CBS SciTech News (test) → None → CoNLL-2003 - English | 0.457829 | neither_strict_tdmr_match |
| 2105.03654.pdf / 8 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 2105.03654.pdf / 11 | Task | NER with Document-level Contexts → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.557527 | neither_strict_tdmr_match |
| 2105.03654.pdf / 11 | Dataset | CoNLL-03 → None → CoNLL-2003 - English | 0.817598 | neither_strict_tdmr_match |
| 2105.03654.pdf / 11 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1703.06345.pdf / 3 | Task | NER → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.632466 | both_strict_tdmr_match |
| 1703.06345.pdf / 3 | Dataset | CoNLL 2003 English → CoNLL-2003 - English → CoNLL-2003 - English | 0.907230 | both_strict_tdmr_match |
| 1703.06345.pdf / 3 | Metric | F1 → F1 → F1 | 精确保留 | both_strict_tdmr_match |
| 1903.07785.pdf / 10 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1903.07785.pdf / 10 | Dataset | CoNLL-2003 → None → CoNLL-2003 - English | 0.917780 | neither_strict_tdmr_match |
| 1903.07785.pdf / 10 | Metric | Test F1 → F1 → F1 | 0.783346 | neither_strict_tdmr_match |
| 128538.pdf / 3 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | both_strict_tdmr_match |
| 128538.pdf / 3 | Dataset | CoNLL 2003 (English) → CoNLL-2003 - English → CoNLL-2003 - English | 0.940761 | both_strict_tdmr_match |
| 128538.pdf / 3 | Metric | F1 score → F1 → F1 | 0.816479 | both_strict_tdmr_match |
| 1511.08308.pdf / 1 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | cs_only_strict_tdmr_match |
| 1511.08308.pdf / 1 | Dataset | CoNLL-2003 → None → CoNLL-2003 - English | 0.917780 | cs_only_strict_tdmr_match |
| 1511.08308.pdf / 1 | Metric | F1 → F1 → F1 | 精确保留 | cs_only_strict_tdmr_match |
| 1603.01354.pdf / 2 | Task | Named Entity Recognition (NER) → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 精确保留 | both_strict_tdmr_match |
| 1603.01354.pdf / 2 | Dataset | CoNLL 2003 English → CoNLL-2003 - English → CoNLL-2003 - English | 0.907230 | both_strict_tdmr_match |
| 1603.01354.pdf / 2 | Metric | F1 → F1 → F1 | 精确保留 | both_strict_tdmr_match |
| 1806.03489.pdf / 1 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 1 | Dataset | CONLL-2003 → None → CoNLL-2003 - English | 0.805878 | neither_strict_tdmr_match |
| 1806.03489.pdf / 1 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1809.08370.pdf / 3 | Task | Named Entity Recognition (NER) → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 精确保留 | neither_strict_tdmr_match |
| 1809.08370.pdf / 3 | Dataset | CoNLL-2003 → None → CoNLL-2003 - English | 0.917780 | neither_strict_tdmr_match |
| 1809.08370.pdf / 3 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |
| C18-1139.pdf / 1 | Task | Named Entity Recognition (English) → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.909481 | neither_strict_tdmr_match |
| C18-1139.pdf / 1 | Dataset | CONLL03 → None → CoNLL-2003 - English | 0.714078 | neither_strict_tdmr_match |
| C18-1139.pdf / 1 | Metric | F1-score → F1 → F1 | 0.813116 | neither_strict_tdmr_match |
| C18-1139.pdf / 2 | Task | Named Entity Recognition (German) → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.712323 | neither_strict_tdmr_match |
| C18-1139.pdf / 2 | Dataset | CONLL03 → None → CoNLL-2003 - English | 0.714078 | neither_strict_tdmr_match |
| C18-1139.pdf / 2 | Metric | F1-score → F1 → F1 | 0.813116 | neither_strict_tdmr_match |
| D19-1367.pdf / 3 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| D19-1367.pdf / 3 | Dataset | CoNLL-2003 English → CoNLL-2003 - English → CoNLL-2003 - English | 0.959627 | neither_strict_tdmr_match |
| D19-1367.pdf / 3 | Metric | F1 Score → F1 → F1 | 0.827506 | neither_strict_tdmr_match |

## OntoNotes 版本（11 条）

| 论文 / 序号 | 字段 | 原始 → LLM → CS | CS Top-1 | 完整元组分类 |
|---|---|---|---:|---|
| 2020.findings-emnlp.378.pdf / 4 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 4 | Dataset | ON4C → None → Ontonotes v4 - Chinese | 0.540914 | cs_only_strict_tdmr_match |
| 2020.findings-emnlp.378.pdf / 4 | Metric | F1 → F1 → F1 | 精确保留 | cs_only_strict_tdmr_match |
| 1702.02098.pdf / 2 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1702.02098.pdf / 2 | Dataset | OntoNotes → None → Ontonotes v5 - English | 0.664551 | neither_strict_tdmr_match |
| 1702.02098.pdf / 2 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |
| 1511.08308.pdf / 2 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | cs_only_strict_tdmr_match |
| 1511.08308.pdf / 2 | Dataset | OntoNotes 5.0 → None → Ontonotes v5 - English | 0.780283 | cs_only_strict_tdmr_match |
| 1511.08308.pdf / 2 | Metric | F1 → F1 → F1 | 精确保留 | cs_only_strict_tdmr_match |
| 1806.03489.pdf / 2 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 2 | Dataset | ONTONOTES 5.0 → Ontonotes v5 - English → Ontonotes v5 - English | 0.761912 | neither_strict_tdmr_match |
| 1806.03489.pdf / 2 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1806.03489.pdf / 3 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 3 | Dataset | ONTONOTES 5.0 (Broadcast Conversation genre) → Ontonotes v5 - English → Ontonotes v5 - English | 0.527887 | neither_strict_tdmr_match |
| 1806.03489.pdf / 3 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1806.03489.pdf / 4 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 4 | Dataset | ONTONOTES 5.0 (Broadcast News genre) → Ontonotes v5 - English → Multi-News | 0.613302 | neither_strict_tdmr_match |
| 1806.03489.pdf / 4 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1806.03489.pdf / 5 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 5 | Dataset | ONTONOTES 5.0 (Magazine genre) → Ontonotes v5 - English → Ontonotes v5 - English | 0.543505 | neither_strict_tdmr_match |
| 1806.03489.pdf / 5 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1806.03489.pdf / 6 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 6 | Dataset | ONTONOTES 5.0 (Newswire genre) → Ontonotes v5 - English → Multi-News | 0.596900 | neither_strict_tdmr_match |
| 1806.03489.pdf / 6 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1806.03489.pdf / 7 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 7 | Dataset | ONTONOTES 5.0 (Telephone Conversation genre) → Ontonotes v5 - English → Ontonotes v5 - English | 0.529606 | neither_strict_tdmr_match |
| 1806.03489.pdf / 7 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1806.03489.pdf / 8 | Task | Named Entity Recognition → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.912100 | neither_strict_tdmr_match |
| 1806.03489.pdf / 8 | Dataset | ONTONOTES 5.0 (Blogs and Newsgroups genre) → Ontonotes v5 - English → Ontonotes v5 - English | 0.590302 | neither_strict_tdmr_match |
| 1806.03489.pdf / 8 | Metric | Mention-level F1 score → F1 → F1 | 0.687958 | neither_strict_tdmr_match |
| 1809.08370.pdf / 4 | Task | Fine-Grained NER (FGN) → Named Entity Recognition (NER) → Named Entity Recognition (NER) | 0.552580 | neither_strict_tdmr_match |
| 1809.08370.pdf / 4 | Dataset | OntoNotes → None → Ontonotes v5 - English | 0.664551 | neither_strict_tdmr_match |
| 1809.08370.pdf / 4 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |

## IWSLT 方向（6 条）

| 论文 / 序号 | 字段 | 原始 → LLM → CS | CS Top-1 | 完整元组分类 |
|---|---|---|---:|---|
| wang19f.pdf / 5 | Task | Neural Machine Translation → Machine Translation → Machine Translation | 0.827296 | llm_only_strict_tdmr_match |
| wang19f.pdf / 5 | Dataset | IWSLT2014 German→English → IWSLT’14 EN-DE → CoNLL-2003 - German | 0.628475 | llm_only_strict_tdmr_match |
| wang19f.pdf / 5 | Metric | BLEU → BLEU → BLEU | 精确保留 | llm_only_strict_tdmr_match |
| 1809.08370.pdf / 8 | Task | Machine Translation (English-Vietnamese) → Machine Translation → Machine Translation | 0.784492 | neither_strict_tdmr_match |
| 1809.08370.pdf / 8 | Dataset | IWSLT 2015 (tst2013 test set) → IWSLT’15 EN-VI → IWSLT’15 EN-VI | 0.662547 | neither_strict_tdmr_match |
| 1809.08370.pdf / 8 | Metric | BLEU → BLEU → BLEU | 精确保留 | neither_strict_tdmr_match |
| 1901.10430.pdf / 3 | Task | Machine Translation → Machine Translation → Machine Translation | 精确保留 | cs_only_strict_tdmr_match |
| 1901.10430.pdf / 3 | Dataset | IWSLT'14 German-English → None → IWSLT’14 EN-DE | 0.683809 | cs_only_strict_tdmr_match |
| 1901.10430.pdf / 3 | Metric | BLEU → BLEU → BLEU | 精确保留 | cs_only_strict_tdmr_match |
| 1911.09483.pdf / 3 | Task | Machine Translation (German-English) → Machine Translation → Machine Translation | 0.799063 | cs_only_strict_tdmr_match |
| 1911.09483.pdf / 3 | Dataset | IWSLT 2014 De-En → None → IWSLT’14 EN-DE | 0.865963 | cs_only_strict_tdmr_match |
| 1911.09483.pdf / 3 | Metric | BLEU → BLEU → BLEU | 精确保留 | cs_only_strict_tdmr_match |
| 1911.09483.pdf / 4 | Task | Machine Translation (English-Vietnamese) → Machine Translation → Machine Translation | 0.784492 | both_strict_tdmr_match |
| 1911.09483.pdf / 4 | Dataset | IWSLT 2015 En-Vi → IWSLT’15 EN-VI → IWSLT’15 EN-VI | 0.869805 | both_strict_tdmr_match |
| 1911.09483.pdf / 4 | Metric | BLEU → BLEU → BLEU | 精确保留 | both_strict_tdmr_match |
| 2002.03184.pdf / 3 | Task | Machine Translation → Machine Translation → Machine Translation | 精确保留 | cs_only_strict_tdmr_match |
| 2002.03184.pdf / 3 | Dataset | IWSLT De-En → None → IWSLT’14 EN-DE | 0.763723 | cs_only_strict_tdmr_match |
| 2002.03184.pdf / 3 | Metric | BLEU → BLEU → BLEU | 精确保留 | cs_only_strict_tdmr_match |

## ROUGE / ROGUE（77 条）

| 论文 / 序号 | 字段 | 原始 → LLM → CS | CS Top-1 | 完整元组分类 |
|---|---|---|---:|---|
| 1905.03197.pdf / 1 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1905.03197.pdf / 1 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | neither_strict_tdmr_match |
| 1905.03197.pdf / 1 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1905.03197.pdf / 2 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1905.03197.pdf / 2 | Dataset | Gigaword (Full Training Set) → Gigaword → Gigaword | 0.703595 | neither_strict_tdmr_match |
| 1905.03197.pdf / 2 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1905.03197.pdf / 3 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1905.03197.pdf / 3 | Dataset | Gigaword (10K Training Examples) → Gigaword → Gigaword | 0.689421 | neither_strict_tdmr_match |
| 1905.03197.pdf / 3 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1905.03197.pdf / 9 | Task | Question Generation → Question Generation → Question Generation | 精确保留 | neither_strict_tdmr_match |
| 1905.03197.pdf / 9 | Dataset | SQuAD → None → SQuAD 2.0 | 0.841867 | neither_strict_tdmr_match |
| 1905.03197.pdf / 9 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1910.13461.pdf / 4 | Task | Summarization → Summarization → Summarization | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 4 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 4 | Metric | ROUGE-1 → None → ROGUE-1 | 0.691963 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 5 | Task | Summarization → Summarization → Summarization | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 5 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 5 | Metric | ROUGE-2 → None → ROGUE-2 | 0.712370 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 6 | Task | Summarization → Summarization → Summarization | 精确保留 | neither_strict_tdmr_match |
| 1910.13461.pdf / 6 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | neither_strict_tdmr_match |
| 1910.13461.pdf / 6 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1910.13461.pdf / 7 | Task | Summarization → Summarization → Summarization | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 7 | Dataset | XSum → XSum → XSum | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 7 | Metric | ROUGE-1 → None → ROGUE-1 | 0.691963 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 8 | Task | Summarization → Summarization → Summarization | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 8 | Dataset | XSum → XSum → XSum | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 8 | Metric | ROUGE-2 → None → ROGUE-2 | 0.712370 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 9 | Task | Summarization → Summarization → Summarization | 精确保留 | neither_strict_tdmr_match |
| 1910.13461.pdf / 9 | Dataset | XSum → XSum → XSum | 精确保留 | neither_strict_tdmr_match |
| 1910.13461.pdf / 9 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1910.13461.pdf / 12 | Task | Abstractive Question Answering → Question Answering → Question Answering | 0.817785 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 12 | Dataset | ELI5 → ELI5 → ELI5 | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 12 | Metric | ROUGE-1 → None → ROGUE-1 | 0.691963 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 13 | Task | Abstractive Question Answering → Question Answering → Question Answering | 0.817785 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 13 | Dataset | ELI5 → ELI5 → ELI5 | 精确保留 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 13 | Metric | ROUGE-2 → None → ROGUE-2 | 0.712370 | cs_only_strict_tdmr_match |
| 1910.13461.pdf / 14 | Task | Abstractive Question Answering → Question Answering → Question Answering | 0.817785 | neither_strict_tdmr_match |
| 1910.13461.pdf / 14 | Dataset | ELI5 → ELI5 → ELI5 | 精确保留 | neither_strict_tdmr_match |
| 1910.13461.pdf / 14 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1912.08777.pdf / 1 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 1 | Dataset | XSum → XSum → XSum | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 1 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → None → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 2 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 2 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 2 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → ROGUE-1 → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 3 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 3 | Dataset | NEWSROOM → Newsroom → Newsroom | 0.801178 | neither_strict_tdmr_match |
| 1912.08777.pdf / 3 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → None → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 4 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 4 | Dataset | Multi-News → Multi-News → Multi-News | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 4 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → None → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 5 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 5 | Dataset | Gigaword → Gigaword → Gigaword | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 5 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → None → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 6 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 6 | Dataset | WikiHow → WikiHow → WikiHow | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 6 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → ROGUE-1 → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 7 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 7 | Dataset | Reddit TIFU → Reddit TIFU → Reddit TIFU | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 7 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → None → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 8 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 8 | Dataset | BIGPATENT → BIGPATENT → BIGPATENT | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 8 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → ROGUE-1 → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 9 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 9 | Dataset | arXiv → arXiv → arXiv | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 9 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → ROGUE-1 → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 10 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 10 | Dataset | PubMed → PubMed → PubMed | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 10 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → ROGUE-1 → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 11 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 11 | Dataset | AESLC → AESLC → AESLC | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 11 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → ROGUE-1 → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1912.08777.pdf / 12 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1912.08777.pdf / 12 | Dataset | BillSum → BillSum → BillSum | 精确保留 | neither_strict_tdmr_match |
| 1912.08777.pdf / 12 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 → ROGUE-1 → BLEU-4 | 0.553869 | neither_strict_tdmr_match |
| 1808.08745.pdf / 1 | Task | Extreme summarization → Summarization → Summarization | 0.796725 | both_strict_tdmr_match |
| 1808.08745.pdf / 1 | Dataset | XSum → XSum → XSum | 精确保留 | both_strict_tdmr_match |
| 1808.08745.pdf / 1 | Metric | ROUGE-1 F1 → ROGUE-1 → ROGUE-1 | 0.653527 | both_strict_tdmr_match |
| 1808.08745.pdf / 2 | Task | Extreme summarization → Summarization → Summarization | 0.796725 | both_strict_tdmr_match |
| 1808.08745.pdf / 2 | Dataset | XSum → XSum → XSum | 精确保留 | both_strict_tdmr_match |
| 1808.08745.pdf / 2 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | both_strict_tdmr_match |
| 1808.08745.pdf / 3 | Task | Extreme summarization → Summarization → Summarization | 0.796725 | neither_strict_tdmr_match |
| 1808.08745.pdf / 3 | Dataset | XSum → XSum → XSum | 精确保留 | neither_strict_tdmr_match |
| 1808.08745.pdf / 3 | Metric | ROUGE-L F1 → None → F1 | 0.655063 | neither_strict_tdmr_match |
| 1901.10430.pdf / 6 | Task | Summarization → Summarization → Summarization | 精确保留 | cs_only_strict_tdmr_match |
| 1901.10430.pdf / 6 | Dataset | CNN-DailyMail → CNN/DailyMail → CNN/DailyMail | 0.941954 | cs_only_strict_tdmr_match |
| 1901.10430.pdf / 6 | Metric | Rouge-1 → None → ROGUE-1 | 0.770036 | cs_only_strict_tdmr_match |
| 1901.10430.pdf / 7 | Task | Summarization → Summarization → Summarization | 精确保留 | both_strict_tdmr_match |
| 1901.10430.pdf / 7 | Dataset | CNN-DailyMail → CNN/DailyMail → CNN/DailyMail | 0.941954 | both_strict_tdmr_match |
| 1901.10430.pdf / 7 | Metric | Rouge-2 → ROGUE-2 → ROGUE-2 | 0.767591 | both_strict_tdmr_match |
| 1901.10430.pdf / 8 | Task | Summarization → Summarization → Summarization | 精确保留 | both_strict_tdmr_match |
| 1901.10430.pdf / 8 | Dataset | CNN-DailyMail → CNN/DailyMail → CNN/DailyMail | 0.941954 | both_strict_tdmr_match |
| 1901.10430.pdf / 8 | Metric | Rouge-L → ROGUE-L → ROGUE-L | 0.689695 | both_strict_tdmr_match |
| 1906.05012.pdf / 1 | Task | Abstractive sentence summarization → Summarization → Summarization | 0.831596 | cs_only_strict_tdmr_match |
| 1906.05012.pdf / 1 | Dataset | Annotated English Gigaword → Gigaword → Gigaword | 0.825567 | cs_only_strict_tdmr_match |
| 1906.05012.pdf / 1 | Metric | ROUGE-1 → None → ROGUE-1 | 0.691963 | cs_only_strict_tdmr_match |
| 1906.05012.pdf / 2 | Task | Abstractive sentence summarization → Summarization → Summarization | 0.831596 | cs_only_strict_tdmr_match |
| 1906.05012.pdf / 2 | Dataset | Annotated English Gigaword → Gigaword → Gigaword | 0.825567 | cs_only_strict_tdmr_match |
| 1906.05012.pdf / 2 | Metric | ROUGE-2 → None → ROGUE-2 | 0.712370 | cs_only_strict_tdmr_match |
| 1906.05012.pdf / 3 | Task | Abstractive sentence summarization → Summarization → Summarization | 0.831596 | neither_strict_tdmr_match |
| 1906.05012.pdf / 3 | Dataset | Annotated English Gigaword → Gigaword → Gigaword | 0.825567 | neither_strict_tdmr_match |
| 1906.05012.pdf / 3 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 1908.08345.pdf / 1 | Task | Single-document news summarization (extractive) → Summarization → Summarization | 0.698162 | both_strict_tdmr_match |
| 1908.08345.pdf / 1 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | both_strict_tdmr_match |
| 1908.08345.pdf / 1 | Metric | ROUGE-1 F1 → ROGUE-1 → ROGUE-1 | 0.653527 | both_strict_tdmr_match |
| 1908.08345.pdf / 2 | Task | Single-document news summarization (extractive) → Summarization → Summarization | 0.698162 | both_strict_tdmr_match |
| 1908.08345.pdf / 2 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | both_strict_tdmr_match |
| 1908.08345.pdf / 2 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | both_strict_tdmr_match |
| 1908.08345.pdf / 3 | Task | Single-document news summarization (extractive) → Summarization → Summarization | 0.698162 | llm_only_strict_tdmr_match |
| 1908.08345.pdf / 3 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | llm_only_strict_tdmr_match |
| 1908.08345.pdf / 3 | Metric | ROUGE-L F1 → ROGUE-L → F1 | 0.655063 | llm_only_strict_tdmr_match |
| 1908.08345.pdf / 4 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | neither_strict_tdmr_match |
| 1908.08345.pdf / 4 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | neither_strict_tdmr_match |
| 1908.08345.pdf / 4 | Metric | ROUGE-1 F1 → ROGUE-1 → ROGUE-1 | 0.653527 | neither_strict_tdmr_match |
| 1908.08345.pdf / 5 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | neither_strict_tdmr_match |
| 1908.08345.pdf / 5 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | neither_strict_tdmr_match |
| 1908.08345.pdf / 5 | Metric | ROUGE-2 F1 → None → ROGUE-2 | 0.650505 | neither_strict_tdmr_match |
| 1908.08345.pdf / 6 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | neither_strict_tdmr_match |
| 1908.08345.pdf / 6 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | neither_strict_tdmr_match |
| 1908.08345.pdf / 6 | Metric | ROUGE-L F1 → None → F1 | 0.655063 | neither_strict_tdmr_match |
| 1908.08345.pdf / 7 | Task | Single-document news summarization (extractive) → Summarization → Summarization | 0.698162 | neither_strict_tdmr_match |
| 1908.08345.pdf / 7 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | neither_strict_tdmr_match |
| 1908.08345.pdf / 7 | Metric | ROUGE-1 Recall → None → ROGUE-1 | 0.618108 | neither_strict_tdmr_match |
| 1908.08345.pdf / 8 | Task | Single-document news summarization (extractive) → Summarization → Summarization | 0.698162 | neither_strict_tdmr_match |
| 1908.08345.pdf / 8 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | neither_strict_tdmr_match |
| 1908.08345.pdf / 8 | Metric | ROUGE-2 Recall → ROGUE-2 → ROGUE-2 | 0.645338 | neither_strict_tdmr_match |
| 1908.08345.pdf / 9 | Task | Single-document news summarization (extractive) → Summarization → Summarization | 0.698162 | neither_strict_tdmr_match |
| 1908.08345.pdf / 9 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | neither_strict_tdmr_match |
| 1908.08345.pdf / 9 | Metric | ROUGE-L Recall → None → Recall | 0.631267 | neither_strict_tdmr_match |
| 1908.08345.pdf / 10 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | neither_strict_tdmr_match |
| 1908.08345.pdf / 10 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | neither_strict_tdmr_match |
| 1908.08345.pdf / 10 | Metric | ROUGE-1 Recall → None → ROGUE-1 | 0.618108 | neither_strict_tdmr_match |
| 1908.08345.pdf / 11 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | neither_strict_tdmr_match |
| 1908.08345.pdf / 11 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | neither_strict_tdmr_match |
| 1908.08345.pdf / 11 | Metric | ROUGE-2 Recall → ROGUE-2 → ROGUE-2 | 0.645338 | neither_strict_tdmr_match |
| 1908.08345.pdf / 12 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | neither_strict_tdmr_match |
| 1908.08345.pdf / 12 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | neither_strict_tdmr_match |
| 1908.08345.pdf / 12 | Metric | ROUGE-L Recall → None → Recall | 0.631267 | neither_strict_tdmr_match |
| 1908.08345.pdf / 13 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | both_strict_tdmr_match |
| 1908.08345.pdf / 13 | Dataset | XSum → XSum → XSum | 精确保留 | both_strict_tdmr_match |
| 1908.08345.pdf / 13 | Metric | ROUGE-1 F1 → ROGUE-1 → ROGUE-1 | 0.653527 | both_strict_tdmr_match |
| 1908.08345.pdf / 14 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | both_strict_tdmr_match |
| 1908.08345.pdf / 14 | Dataset | XSum → XSum → XSum | 精确保留 | both_strict_tdmr_match |
| 1908.08345.pdf / 14 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | both_strict_tdmr_match |
| 1908.08345.pdf / 15 | Task | Single-document news summarization (abstractive) → Summarization → Summarization | 0.732859 | llm_only_strict_tdmr_match |
| 1908.08345.pdf / 15 | Dataset | XSum → XSum → XSum | 精确保留 | llm_only_strict_tdmr_match |
| 1908.08345.pdf / 15 | Metric | ROUGE-L F1 → ROGUE-L → F1 | 0.655063 | llm_only_strict_tdmr_match |
| 1911.10390.pdf / 1 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 1911.10390.pdf / 1 | Dataset | NEWSROOM → Newsroom → Newsroom | 0.801178 | cs_only_strict_tdmr_match |
| 1911.10390.pdf / 1 | Metric | ROUGE-1 → None → ROGUE-1 | 0.691963 | cs_only_strict_tdmr_match |
| 1911.10390.pdf / 2 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 1911.10390.pdf / 2 | Dataset | NEWSROOM → Newsroom → Newsroom | 0.801178 | cs_only_strict_tdmr_match |
| 1911.10390.pdf / 2 | Metric | ROUGE-2 → None → ROGUE-2 | 0.712370 | cs_only_strict_tdmr_match |
| 1911.10390.pdf / 3 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 1911.10390.pdf / 3 | Dataset | NEWSROOM → Newsroom → Newsroom | 0.801178 | neither_strict_tdmr_match |
| 1911.10390.pdf / 3 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 2001.04063.pdf / 1 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 1 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 1 | Metric | ROUGE-1 → None → ROGUE-1 | 0.691963 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 2 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 2 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 2 | Metric | ROUGE-2 → None → ROGUE-2 | 0.712370 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 3 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 2001.04063.pdf / 3 | Dataset | CNN/DailyMail → CNN/DailyMail → CNN/DailyMail | 精确保留 | neither_strict_tdmr_match |
| 2001.04063.pdf / 3 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 2001.04063.pdf / 4 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 4 | Dataset | Gigaword → Gigaword → Gigaword | 精确保留 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 4 | Metric | ROUGE-1 → None → ROGUE-1 | 0.691963 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 5 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 5 | Dataset | Gigaword → Gigaword → Gigaword | 精确保留 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 5 | Metric | ROUGE-2 → None → ROGUE-2 | 0.712370 | cs_only_strict_tdmr_match |
| 2001.04063.pdf / 6 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 2001.04063.pdf / 6 | Dataset | Gigaword → Gigaword → Gigaword | 精确保留 | neither_strict_tdmr_match |
| 2001.04063.pdf / 6 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 2001.04063.pdf / 9 | Task | Question Generation → Question Generation → Question Generation | 精确保留 | neither_strict_tdmr_match |
| 2001.04063.pdf / 9 | Dataset | SQuAD 1.1 → SQuAD 1.1 → SQuAD 1.1 | 精确保留 | neither_strict_tdmr_match |
| 2001.04063.pdf / 9 | Metric | ROUGE-L → None → BLEU | 0.747069 | neither_strict_tdmr_match |
| 2002.03184.pdf / 4 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 2002.03184.pdf / 4 | Dataset | CNN-DailyMail → CNN/DailyMail → CNN/DailyMail | 0.941954 | cs_only_strict_tdmr_match |
| 2002.03184.pdf / 4 | Metric | Rouge-1 → None → ROGUE-1 | 0.770036 | cs_only_strict_tdmr_match |
| 2002.03184.pdf / 5 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | both_strict_tdmr_match |
| 2002.03184.pdf / 5 | Dataset | CNN-DailyMail → CNN/DailyMail → CNN/DailyMail | 0.941954 | both_strict_tdmr_match |
| 2002.03184.pdf / 5 | Metric | Rouge-2 → ROGUE-2 → ROGUE-2 | 0.767591 | both_strict_tdmr_match |
| 2002.03184.pdf / 6 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | both_strict_tdmr_match |
| 2002.03184.pdf / 6 | Dataset | CNN-DailyMail → CNN/DailyMail → CNN/DailyMail | 0.941954 | both_strict_tdmr_match |
| 2002.03184.pdf / 6 | Metric | Rouge-L → ROGUE-L → ROGUE-L | 0.689695 | both_strict_tdmr_match |
| 2203.16804.pdf / 1 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 2203.16804.pdf / 1 | Dataset | CNNDM → CNN/DailyMail → QNLI | 0.547707 | neither_strict_tdmr_match |
| 2203.16804.pdf / 1 | Metric | ROUGE-1 F1 → ROGUE-1 → ROGUE-1 | 0.653527 | neither_strict_tdmr_match |
| 2203.16804.pdf / 2 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 2203.16804.pdf / 2 | Dataset | CNNDM → CNN/DailyMail → QNLI | 0.547707 | neither_strict_tdmr_match |
| 2203.16804.pdf / 2 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | neither_strict_tdmr_match |
| 2203.16804.pdf / 3 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 2203.16804.pdf / 3 | Dataset | CNNDM → CNN/DailyMail → QNLI | 0.547707 | neither_strict_tdmr_match |
| 2203.16804.pdf / 3 | Metric | ROUGE-L F1 → ROGUE-L → F1 | 0.655063 | neither_strict_tdmr_match |
| 2203.16804.pdf / 4 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | both_strict_tdmr_match |
| 2203.16804.pdf / 4 | Dataset | XSum → XSum → XSum | 精确保留 | both_strict_tdmr_match |
| 2203.16804.pdf / 4 | Metric | ROUGE-1 F1 → ROGUE-1 → ROGUE-1 | 0.653527 | both_strict_tdmr_match |
| 2203.16804.pdf / 5 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | both_strict_tdmr_match |
| 2203.16804.pdf / 5 | Dataset | XSum → XSum → XSum | 精确保留 | both_strict_tdmr_match |
| 2203.16804.pdf / 5 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | both_strict_tdmr_match |
| 2203.16804.pdf / 6 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | neither_strict_tdmr_match |
| 2203.16804.pdf / 6 | Dataset | XSum → XSum → XSum | 精确保留 | neither_strict_tdmr_match |
| 2203.16804.pdf / 6 | Metric | ROUGE-L F1 → None → F1 | 0.655063 | neither_strict_tdmr_match |
| 2203.16804.pdf / 7 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | cs_only_strict_tdmr_match |
| 2203.16804.pdf / 7 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | cs_only_strict_tdmr_match |
| 2203.16804.pdf / 7 | Metric | ROUGE-1 F1 → None → ROGUE-1 | 0.653527 | cs_only_strict_tdmr_match |
| 2203.16804.pdf / 8 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | both_strict_tdmr_match |
| 2203.16804.pdf / 8 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | both_strict_tdmr_match |
| 2203.16804.pdf / 8 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | both_strict_tdmr_match |
| 2203.16804.pdf / 9 | Task | Abstractive Summarization → Summarization → Summarization | 0.843448 | llm_only_strict_tdmr_match |
| 2203.16804.pdf / 9 | Dataset | NYT → New York Times (NYT) → New York Times (NYT) | 0.905977 | llm_only_strict_tdmr_match |
| 2203.16804.pdf / 9 | Metric | ROUGE-L F1 → ROGUE-L → F1 | 0.655063 | llm_only_strict_tdmr_match |
| 2203.16804.pdf / 17 | Task | Abstractive Summarization (Few-shot) → Summarization → Summarization | 0.783340 | neither_strict_tdmr_match |
| 2203.16804.pdf / 17 | Dataset | CNNDM → None → QNLI | 0.547707 | neither_strict_tdmr_match |
| 2203.16804.pdf / 17 | Metric | ROUGE-1 F1 → None → ROGUE-1 | 0.653527 | neither_strict_tdmr_match |
| 2203.16804.pdf / 18 | Task | Abstractive Summarization (Few-shot) → Summarization → Summarization | 0.783340 | neither_strict_tdmr_match |
| 2203.16804.pdf / 18 | Dataset | CNNDM → CNN/DailyMail → QNLI | 0.547707 | neither_strict_tdmr_match |
| 2203.16804.pdf / 18 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | neither_strict_tdmr_match |
| 2203.16804.pdf / 19 | Task | Abstractive Summarization (Few-shot) → Summarization → Summarization | 0.783340 | neither_strict_tdmr_match |
| 2203.16804.pdf / 19 | Dataset | CNNDM → None → QNLI | 0.547707 | neither_strict_tdmr_match |
| 2203.16804.pdf / 19 | Metric | ROUGE-L F1 → None → F1 | 0.655063 | neither_strict_tdmr_match |
| 2203.16804.pdf / 20 | Task | Abstractive Summarization (Few-shot) → Summarization → Summarization | 0.783340 | neither_strict_tdmr_match |
| 2203.16804.pdf / 20 | Dataset | XSum → XSum → XSum | 精确保留 | neither_strict_tdmr_match |
| 2203.16804.pdf / 20 | Metric | ROUGE-1 F1 → None → ROGUE-1 | 0.653527 | neither_strict_tdmr_match |
| 2203.16804.pdf / 21 | Task | Abstractive Summarization (Few-shot) → Summarization → Summarization | 0.783340 | neither_strict_tdmr_match |
| 2203.16804.pdf / 21 | Dataset | XSum → XSum → XSum | 精确保留 | neither_strict_tdmr_match |
| 2203.16804.pdf / 21 | Metric | ROUGE-2 F1 → ROGUE-2 → ROGUE-2 | 0.650505 | neither_strict_tdmr_match |
| 2203.16804.pdf / 22 | Task | Abstractive Summarization (Few-shot) → Summarization → Summarization | 0.783340 | neither_strict_tdmr_match |
| 2203.16804.pdf / 22 | Dataset | XSum → XSum → XSum | 精确保留 | neither_strict_tdmr_match |
| 2203.16804.pdf / 22 | Metric | ROUGE-L F1 → None → F1 | 0.655063 | neither_strict_tdmr_match |

## GLUE 及子任务（6 条）

| 论文 / 序号 | 字段 | 原始 → LLM → CS | CS Top-1 | 完整元组分类 |
|---|---|---|---:|---|
| 1905.03197.pdf / 13 | Task | Language Understanding (GLUE Benchmark) → Natural Language Inference (NLI) → Language Modeling | 0.651417 | neither_strict_tdmr_match |
| 1905.03197.pdf / 13 | Dataset | GLUE → None → SNIPS | 0.440465 | neither_strict_tdmr_match |
| 1905.03197.pdf / 13 | Metric | SST-2 Accuracy → Accuracy → Accuracy | 0.676364 | neither_strict_tdmr_match |
| 1905.03197.pdf / 14 | Task | Language Understanding (GLUE Benchmark) → Natural Language Inference (NLI) → Language Modeling | 0.651417 | neither_strict_tdmr_match |
| 1905.03197.pdf / 14 | Dataset | GLUE → None → SNIPS | 0.440465 | neither_strict_tdmr_match |
| 1905.03197.pdf / 14 | Metric | MNLI-m Accuracy → None → Accuracy | 0.679395 | neither_strict_tdmr_match |
| 1905.03197.pdf / 15 | Task | Language Understanding (GLUE Benchmark) → Natural Language Inference (NLI) → Language Modeling | 0.651417 | neither_strict_tdmr_match |
| 1905.03197.pdf / 15 | Dataset | GLUE → None → SNIPS | 0.440465 | neither_strict_tdmr_match |
| 1905.03197.pdf / 15 | Metric | MNLI-mm Accuracy → Accuracy → Accuracy | 0.663882 | neither_strict_tdmr_match |
| 1905.03197.pdf / 16 | Task | Language Understanding (GLUE Benchmark) → Natural Language Inference (NLI) → Language Modeling | 0.651417 | neither_strict_tdmr_match |
| 1905.03197.pdf / 16 | Dataset | GLUE → None → SNIPS | 0.440465 | neither_strict_tdmr_match |
| 1905.03197.pdf / 16 | Metric | QNLI Accuracy → Accuracy → Accuracy | 0.728179 | neither_strict_tdmr_match |
| 1905.03197.pdf / 17 | Task | Language Understanding (GLUE Benchmark) → Natural Language Inference (NLI) → Language Modeling | 0.651417 | neither_strict_tdmr_match |
| 1905.03197.pdf / 17 | Dataset | GLUE → None → SNIPS | 0.440465 | neither_strict_tdmr_match |
| 1905.03197.pdf / 17 | Metric | CoLA MCC → Matthew's Correlation Coefficient (MCC) → Matthew's Correlation Coefficient (MCC) | 0.454776 | neither_strict_tdmr_match |
| 1905.03197.pdf / 18 | Task | Language Understanding (GLUE Benchmark) → Natural Language Inference (NLI) → Language Modeling | 0.651417 | neither_strict_tdmr_match |
| 1905.03197.pdf / 18 | Dataset | GLUE → None → SNIPS | 0.440465 | neither_strict_tdmr_match |
| 1905.03197.pdf / 18 | Metric | STS-B Spearman Corr. → Spearman Correlation → Spearman Correlation | 0.467778 | neither_strict_tdmr_match |

## Intent Detection and Slot Filling（28 条）

| 论文 / 序号 | 字段 | 原始 → LLM → CS | CS Top-1 | 完整元组分类 |
|---|---|---|---:|---|
| 2020.emnlp-main.152.pdf / 1 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | both_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 1 | Dataset | ATIS → ATIS → ATIS | 精确保留 | both_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 1 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | both_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 2 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 2 | Dataset | ATIS → ATIS → ATIS | 精确保留 | neither_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 2 | Metric | F1-score → F1 → F1 | 0.813116 | neither_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 3 | Task | Sentence Accuracy (Intent + Slot) → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.657999 | llm_only_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 3 | Dataset | ATIS → ATIS → ATIS | 精确保留 | llm_only_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 3 | Metric | Sentence Accuracy → Sent-Accuracy → Accuracy | 0.788841 | llm_only_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 4 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | both_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 4 | Dataset | Snips → SNIPS → SNIPS | 0.953786 | both_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 4 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | both_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 5 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 5 | Dataset | Snips → SNIPS → SNIPS | 0.953786 | neither_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 5 | Metric | F1-score → F1 → F1 | 0.813116 | neither_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 6 | Task | Sentence Accuracy (Intent + Slot) → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.657999 | llm_only_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 6 | Dataset | Snips → SNIPS → SNIPS | 0.953786 | llm_only_strict_tdmr_match |
| 2020.emnlp-main.152.pdf / 6 | Metric | Sentence Accuracy → Sent-Accuracy → Accuracy | 0.788841 | llm_only_strict_tdmr_match |
| 1812.09471.pdf / 1 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 1812.09471.pdf / 1 | Dataset | SNIPS-NLU → None → MNLI-m | 0.614452 | neither_strict_tdmr_match |
| 1812.09471.pdf / 1 | Metric | F1 → F1 → F1 | 精确保留 | neither_strict_tdmr_match |
| 1812.09471.pdf / 2 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1812.09471.pdf / 2 | Dataset | SNIPS-NLU → None → MNLI-m | 0.614452 | neither_strict_tdmr_match |
| 1812.09471.pdf / 2 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.09471.pdf / 3 | Task | Overall Accuracy (Joint Slot Filling and Intent Detection) → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.782290 | neither_strict_tdmr_match |
| 1812.09471.pdf / 3 | Dataset | SNIPS-NLU → None → MNLI-m | 0.614452 | neither_strict_tdmr_match |
| 1812.09471.pdf / 3 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.09471.pdf / 4 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | both_strict_tdmr_match |
| 1812.09471.pdf / 4 | Dataset | ATIS → ATIS → ATIS | 精确保留 | both_strict_tdmr_match |
| 1812.09471.pdf / 4 | Metric | F1 → F1 → F1 | 精确保留 | both_strict_tdmr_match |
| 1812.09471.pdf / 5 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1812.09471.pdf / 5 | Dataset | ATIS → ATIS → ATIS | 精确保留 | neither_strict_tdmr_match |
| 1812.09471.pdf / 5 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.09471.pdf / 6 | Task | Overall Accuracy (Joint Slot Filling and Intent Detection) → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.782290 | neither_strict_tdmr_match |
| 1812.09471.pdf / 6 | Dataset | ATIS → ATIS → ATIS | 精确保留 | neither_strict_tdmr_match |
| 1812.09471.pdf / 6 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.10235.pdf / 1 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1812.10235.pdf / 1 | Dataset | ATIS → ATIS → ATIS | 精确保留 | neither_strict_tdmr_match |
| 1812.10235.pdf / 1 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.10235.pdf / 2 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 1812.10235.pdf / 2 | Dataset | ATIS → ATIS → ATIS | 精确保留 | neither_strict_tdmr_match |
| 1812.10235.pdf / 2 | Metric | F1 Score → F1 → F1 | 0.827506 | neither_strict_tdmr_match |
| 1812.10235.pdf / 3 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1812.10235.pdf / 3 | Dataset | Internal Multi-domain (Movie) → Multi-domain Movie → Multi-domain Movie | 0.884147 | neither_strict_tdmr_match |
| 1812.10235.pdf / 3 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.10235.pdf / 4 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 1812.10235.pdf / 4 | Dataset | Internal Multi-domain (Movie) → Multi-domain Movie → Multi-domain Movie | 0.884147 | neither_strict_tdmr_match |
| 1812.10235.pdf / 4 | Metric | F1 Score → F1 → F1 | 0.827506 | neither_strict_tdmr_match |
| 1812.10235.pdf / 5 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1812.10235.pdf / 5 | Dataset | Internal Multi-domain (Food) → Multi-domain Food → Multi-domain Food | 0.868317 | neither_strict_tdmr_match |
| 1812.10235.pdf / 5 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.10235.pdf / 6 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 1812.10235.pdf / 6 | Dataset | Internal Multi-domain (Food) → Multi-domain Food → Multi-domain Food | 0.868317 | neither_strict_tdmr_match |
| 1812.10235.pdf / 6 | Metric | F1 Score → F1 → F1 | 0.827506 | neither_strict_tdmr_match |
| 1812.10235.pdf / 7 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1812.10235.pdf / 7 | Dataset | Internal Multi-domain (Home) → Multi-domain Home → Multi-domain Home | 0.899774 | neither_strict_tdmr_match |
| 1812.10235.pdf / 7 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1812.10235.pdf / 8 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 1812.10235.pdf / 8 | Dataset | Internal Multi-domain (Home) → Multi-domain Home → Multi-domain Home | 0.899774 | neither_strict_tdmr_match |
| 1812.10235.pdf / 8 | Metric | F1 Score → F1 → F1 | 0.827506 | neither_strict_tdmr_match |
| 1907.00390.pdf / 1 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | both_strict_tdmr_match |
| 1907.00390.pdf / 1 | Dataset | ATIS → ATIS → ATIS | 精确保留 | both_strict_tdmr_match |
| 1907.00390.pdf / 1 | Metric | F1-score → F1 → F1 | 0.813116 | both_strict_tdmr_match |
| 1907.00390.pdf / 2 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | both_strict_tdmr_match |
| 1907.00390.pdf / 2 | Dataset | ATIS → ATIS → ATIS | 精确保留 | both_strict_tdmr_match |
| 1907.00390.pdf / 2 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | both_strict_tdmr_match |
| 1907.00390.pdf / 4 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | both_strict_tdmr_match |
| 1907.00390.pdf / 4 | Dataset | Snips → SNIPS → SNIPS | 0.953786 | both_strict_tdmr_match |
| 1907.00390.pdf / 4 | Metric | F1-score → F1 → F1 | 0.813116 | both_strict_tdmr_match |
| 1907.00390.pdf / 5 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | both_strict_tdmr_match |
| 1907.00390.pdf / 5 | Dataset | Snips → SNIPS → SNIPS | 0.953786 | both_strict_tdmr_match |
| 1907.00390.pdf / 5 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | both_strict_tdmr_match |
| 1909.02188.pdf / 1 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 1909.02188.pdf / 1 | Dataset | SNIPS → SNIPS → SNIPS | 精确保留 | neither_strict_tdmr_match |
| 1909.02188.pdf / 1 | Metric | F1 Score → F1 → F1 | 0.827506 | neither_strict_tdmr_match |
| 1909.02188.pdf / 2 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1909.02188.pdf / 2 | Dataset | SNIPS → SNIPS → SNIPS | 精确保留 | neither_strict_tdmr_match |
| 1909.02188.pdf / 2 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
| 1909.02188.pdf / 4 | Task | Slot Filling → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.690075 | neither_strict_tdmr_match |
| 1909.02188.pdf / 4 | Dataset | ATIS → ATIS → ATIS | 精确保留 | neither_strict_tdmr_match |
| 1909.02188.pdf / 4 | Metric | F1 Score → F1 → F1 | 0.827506 | neither_strict_tdmr_match |
| 1909.02188.pdf / 5 | Task | Intent Detection → Intent Detection and Slot Filling → Intent Detection and Slot Filling | 0.808708 | neither_strict_tdmr_match |
| 1909.02188.pdf / 5 | Dataset | ATIS → ATIS → ATIS | 精确保留 | neither_strict_tdmr_match |
| 1909.02188.pdf / 5 | Metric | Accuracy → Accuracy → Accuracy | 精确保留 | neither_strict_tdmr_match |
