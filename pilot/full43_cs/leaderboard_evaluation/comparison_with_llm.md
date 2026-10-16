# 排行榜对照

同一冻结的 27 榜、140 条记录，所有 27 榜参与 Macro；不为预测新增至少三篇过滤。LR 与有效非空榜率分开。

| 指标 | LLM 标准化 | CS 标准化 |
|---|---:|---:|
| LR：标准 TDM 命中 | 0.814815 | 0.925926 |
| 有效数值非空榜率 | 0.740741 | 0.888889 |
| 官方 PC | 0.487125 | 0.631570 |
| 官方 RC | 0.317989 | 0.411905 |
| 官方数值列表 RBO | 0.247654 | 0.303420 |
| 论文 ID AO（补充） | 0.462500 | 0.522212 |

## 非空榜变化

| TDM | 变化 | 旧条数 | 新条数 |
|---|---|---:|---:|
| ('Summarization', 'Gigaword', 'ROGUE-1') | became_nonempty | 0 | 2 |
| ('Summarization', 'Gigaword', 'ROGUE-2') | became_nonempty | 0 | 2 |
| ('Summarization', 'XSum', 'ROGUE-L') | became_empty | 1 | 0 |
| ('Named Entity Recognition (NER)', 'WNUT-16 - English', 'F1') | became_nonempty | 0 | 2 |
| ('Named Entity Recognition (NER)', 'WNUT-17 - English', 'F1') | became_nonempty | 0 | 3 |
| ('Word Sense Induction', 'SemEval 2013 Task 13', 'Fuzzy normalized mutual information (FNMI)') | became_nonempty | 0 | 1 |

Gigaword ROGUE-1/2 来自原始 ROUGE-1/2 的 CS 映射；WNUT-16/17 包括 WN16/WN17 缩写映射；FNMI 榜来自对应指标名称的 CS 映射。XSum ROGUE-L 消失：原始 ROUGE-L F1 被映射为 F1。每条转换与后写覆盖记录均保存在 comparison_with_llm.json 和 leaderboards/gold_vs_predicted.json。

共有 112 条预测匹配 27 榜的 TDM；其中 6 条 Result 无法按官方规则转换，16 条较早有效记录被同论文同 TDM 的后写记录覆盖；最终 90 条榜内预测。另 172 条不属于这 27 个 TDM。

实际 RC 最大值 0.800000，没有超过 1；没有裁剪。额外论文条目数 0。RC 按数值命中，不要求同论文对应；RBO 使用去重数值列表，不能重命名为论文 ID AO。

## 各榜

| TDM | Gold/CS 条数 | PC | RC | RBO | 论文 ID AO | 额外论文 |
|---|---:|---:|---:|---:|---|
| ('Summarization', 'Gigaword', 'ROGUE-1') | 5/2 | 0.400000 | 0.400000 | 0.750000 | 0.750000 | [] |
| ('Summarization', 'Gigaword', 'ROGUE-2') | 5/2 | 0.400000 | 0.400000 | 0.250000 | 0.250000 | [] |
| ('Summarization', 'Gigaword', 'ROGUE-L') | 5/0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | [] |
| ('Summarization', 'CNN/DailyMail', 'ROGUE-1') | 8/5 | 0.625000 | 0.500000 | 0.346667 | 0.386667 | [] |
| ('Summarization', 'CNN/DailyMail', 'ROGUE-2') | 8/5 | 0.625000 | 0.500000 | 0.246667 | 0.286667 | [] |
| ('Summarization', 'CNN/DailyMail', 'ROGUE-L') | 8/2 | 0.250000 | 0.250000 | 0.000000 | 0.000000 | [] |
| ('Summarization', 'XSum', 'ROGUE-1') | 5/4 | 0.800000 | 0.600000 | 0.208333 | 0.729167 | [] |
| ('Summarization', 'XSum', 'ROGUE-2') | 5/4 | 0.800000 | 0.600000 | 0.208333 | 0.729167 | [] |
| ('Summarization', 'XSum', 'ROGUE-L') | 5/0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | [] |
| ('Named Entity Recognition (NER)', 'Ontonotes v5 - English', 'F1') | 5/4 | 0.800000 | 0.200000 | 0.000000 | 0.395833 | [] |
| ('Named Entity Recognition (NER)', 'WNUT-16 - English', 'F1') | 3/2 | 0.666667 | 0.333333 | 0.000000 | 0.250000 | [] |
| ('Named Entity Recognition (NER)', 'WNUT-17 - English', 'F1') | 3/3 | 1.000000 | 0.666667 | 0.388889 | 1.000000 | [] |
| ('Text Chunking', 'CoNLL-2000', 'F1') | 5/4 | 0.800000 | 0.600000 | 0.333333 | 0.854167 | [] |
| ('Named Entity Recognition (NER)', 'CoNLL-2003 - English', 'F1') | 14/11 | 0.785714 | 0.571429 | 0.386236 | 0.554175 | [] |
| ('Part-of-Speech (POS) Tagging', 'Penn Treebank (PTB)', 'Accuracy') | 5/3 | 0.600000 | 0.600000 | 0.888889 | 0.888889 | [] |
| ('Machine Translation', 'WMT’14 EN-FR', 'BLEU') | 5/5 | 1.000000 | 0.600000 | 0.416667 | 1.000000 | [] |
| ('Machine Translation', 'WMT’14 EN-DE', 'BLEU') | 6/6 | 1.000000 | 0.666667 | 0.563889 | 0.652778 | [] |
| ('Machine Translation', 'IWSLT’14 EN-DE', 'BLEU') | 4/3 | 0.750000 | 0.750000 | 1.000000 | 1.000000 | [] |
| ('Word Sense Induction', 'SemEval 2013 Task 13', 'Fuzzy normalized mutual information (FNMI)') | 3/1 | 0.333333 | 0.000000 | 0.000000 | 0.000000 | [] |
| ('Word Sense Induction', 'SemEval 2013 Task 13', 'Fuzzy B-Cubed (FBC)') | 3/0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | [] |
| ('Word Sense Induction', 'SemEval 2013 Task 13', 'AVG') | 3/2 | 0.666667 | 0.333333 | 0.250000 | 0.250000 | [] |
| ('Intent Detection and Slot Filling', 'ATIS', 'F1') | 5/5 | 1.000000 | 0.600000 | 0.586667 | 1.000000 | [] |
| ('Intent Detection and Slot Filling', 'ATIS', 'Accuracy') | 5/5 | 1.000000 | 0.400000 | 0.713333 | 0.933333 | [] |
| ('Intent Detection and Slot Filling', 'SNIPS', 'F1') | 4/3 | 0.750000 | 0.250000 | 0.111111 | 1.000000 | [] |
| ('Intent Detection and Slot Filling', 'SNIPS', 'Accuracy') | 4/3 | 0.750000 | 0.250000 | 0.000000 | 0.388889 | [] |
| ('Dialogue Act Classification', 'Switchboard Dialog Act Corpus (SWDA)', 'Accuracy') | 5/5 | 1.000000 | 0.800000 | 0.543333 | 0.800000 | [] |
| ('Dialogue Act Classification', 'ICSI Meeting Recorder Dialog Act Corpus (MRDA)', 'Accuracy') | 4/1 | 0.250000 | 0.250000 | 0.000000 | 0.000000 | [] |
