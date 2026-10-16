# 本轮观察（不修改预测）

最终候选规模：{'Task': 66, 'Dataset': 115, 'Metric': 61}；新增：{'Task': 66, 'Dataset': 115, 'Metric': 61}。
阶段一分支：{'original_name_added': 242, 'exact_or_result': 843, 'existing_candidate': 51}；null：{'Task': 0, 'Dataset': 0, 'Metric': 0}。
阶段二分支：{'unmatched_preserved': 271, 'exact_tuple': 2, 'tuple_mapped': 11}；其中原样回答 271 次。

阶段一为开放名称空间，未与 Gold 精确相等不代表语义错误。阶段二集合外回答按原版保留；仅凭字符串和相同数值不能断定字段错绑。完整逐条候选对照保存在 observations.json，Gold 仅用于输出后的离线诊断。

| 集合外回答的证据分类 | 数量 |
| --- | --- |
| UNREVIEWED: open-vocabulary aliases and extraction bindings cannot be decided from string nonmembership alone | 257 |
| Exact Gold TDM exists outside the 27-board target | 8 |
| Reviewed existing target board but abbreviation/name not aligned | 3 |
| Reviewed legitimate dataset alias outside the 27-board target | 3 |

## 阶段一 null 原始回答
| 论文/记录 | 字段 | 输入原名 | 原始回答 |
| --- | --- | --- | --- |

## all27 非空及缺失榜
| Task | Dataset | Metric | 有效预测论文数 | Gold 论文数 |
| --- | --- | --- | --- | --- |
| Summarization | Gigaword | ROGUE-1 | 0 | 5 |
| Summarization | Gigaword | ROGUE-2 | 0 | 5 |
| Summarization | Gigaword | ROGUE-L | 0 | 5 |
| Summarization | CNN/DailyMail | ROGUE-1 | 0 | 8 |
| Summarization | CNN/DailyMail | ROGUE-2 | 1 | 8 |
| Summarization | CNN/DailyMail | ROGUE-L | 1 | 8 |
| Summarization | XSum | ROGUE-1 | 0 | 5 |
| Summarization | XSum | ROGUE-2 | 0 | 5 |
| Summarization | XSum | ROGUE-L | 1 | 5 |
| Named Entity Recognition (NER) | Ontonotes v5 - English | F1 | 0 | 5 |
| Named Entity Recognition (NER) | WNUT-16 - English | F1 | 0 | 3 |
| Named Entity Recognition (NER) | WNUT-17 - English | F1 | 0 | 3 |
| Text Chunking | CoNLL-2000 | F1 | 1 | 5 |
| Named Entity Recognition (NER) | CoNLL-2003 - English | F1 | 5 | 14 |
| Part-of-Speech (POS) Tagging | Penn Treebank (PTB) | Accuracy | 1 | 5 |
| Machine Translation | WMT’14 EN-FR | BLEU | 0 | 5 |
| Machine Translation | WMT’14 EN-DE | BLEU | 0 | 6 |
| Machine Translation | IWSLT’14 EN-DE | BLEU | 0 | 4 |
| Word Sense Induction | SemEval 2013 Task 13 | Fuzzy normalized mutual information (FNMI) | 0 | 3 |
| Word Sense Induction | SemEval 2013 Task 13 | Fuzzy B-Cubed (FBC) | 0 | 3 |
| Word Sense Induction | SemEval 2013 Task 13 | AVG | 1 | 3 |
| Intent Detection and Slot Filling | ATIS | F1 | 0 | 5 |
| Intent Detection and Slot Filling | ATIS | Accuracy | 0 | 5 |
| Intent Detection and Slot Filling | SNIPS | F1 | 0 | 4 |
| Intent Detection and Slot Filling | SNIPS | Accuracy | 0 | 4 |
| Dialogue Act Classification | Switchboard Dialog Act Corpus (SWDA) | Accuracy | 0 | 5 |
| Dialogue Act Classification | ICSI Meeting Recorder Dialog Act Corpus (MRDA) | Accuracy | 2 | 4 |

## masked10 非空及缺失榜
| Task | Dataset | Metric | 有效预测论文数 | Gold 论文数 |
| --- | --- | --- | --- | --- |
| Named Entity Recognition (NER) | Ontonotes v5 - English | F1 | 0 | 5 |
| Named Entity Recognition (NER) | WNUT-16 - English | F1 | 0 | 3 |
| Named Entity Recognition (NER) | WNUT-17 - English | F1 | 0 | 3 |
| Named Entity Recognition (NER) | CoNLL-2003 - English | F1 | 5 | 14 |
| Intent Detection and Slot Filling | ATIS | F1 | 0 | 5 |
| Intent Detection and Slot Filling | ATIS | Accuracy | 0 | 5 |
| Intent Detection and Slot Filling | SNIPS | F1 | 0 | 4 |
| Intent Detection and Slot Filling | SNIPS | Accuracy | 0 | 4 |
| Dialogue Act Classification | Switchboard Dialog Act Corpus (SWDA) | Accuracy | 0 | 5 |
| Dialogue Act Classification | ICSI Meeting Recorder Dialog Act Corpus (MRDA) | Accuracy | 2 | 4 |
