# 冻结 GPT-4.1 Baseline 的 Leaderboard-level Evaluation

已完成全部 43 篇冻结标准化结果的离线排行榜构建与评价。使用已有 27 个 Gold Leaderboards、140 条榜内论文记录；输入仍为 43 篇 / 295 条 Gold TDMR，TDMR F1 保持 0.421578。没有重新运行 PDF、Embedding、Retrieval、Extraction 或 Normalization，新增 LLM/API 请求为 0。

## 主要结果与来源

| 指标 | 结果 | 来源及含义 |
|---|---:|---|
| LR：TDM 精确命中 | 81.4815%（22/27） | 补充实现；允许 Result 无法转换 |
| LR：有效数值非空榜 | 74.0741%（20/27） | 补充实现；存在可排序结果 |
| PC | 48.7125% | 原始官方评价 |
| RC | 31.7989% | 原始官方评价，数值命中规则 |
| AO | 46.2500% | 论文公式，论文 ID 排名，全部 27 榜 Macro |
| 官方 RBO | 24.7654% | 原代码的去重 Result 数值排名，不能冒充 AO |

LR 两种口径相差两个 WSI 榜：模型有准确 TDM，但 Result 为带括号的复合字符串，原始转换拒绝。7 个空榜仍进入 PC/RC/AO 的 27 榜平均；未以非空榜平均替代主分数。

## 与论文 Table 5 对照

原论文 Fully Pre-defined GPT-4 Turbo 的 LR/PC/RC/AO 分别为 100.00% / 70.37% / 51.79% / 53.87%。当前可排序非空榜 LR/PC/RC/AO 为 74.0741% / 48.7125% / 31.7989% / 46.2500%；TDM 命中 LR 另为 81.4815%。模型快照不同，且存在数据统计及实现边界差异，不将差值解释为受控模型优劣。[详细对照](comparison_with_paper.md)。

## 每个榜的覆盖与排序

| # | Task / Dataset / Metric | Gold / 预测 | 正确论文覆盖 | PC | RC | 官方 RBO | AO |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Summarization / Gigaword / ROGUE-1 | 5 / 0 | 0/5 | 0.0000% | 0.0000% | 0.0000% | 0.0000% |
| 2 | Summarization / Gigaword / ROGUE-2 | 5 / 0 | 0/5 | 0.0000% | 0.0000% | 0.0000% | 0.0000% |
| 3 | Summarization / Gigaword / ROGUE-L | 5 / 0 | 0/5 | 0.0000% | 0.0000% | 0.0000% | 0.0000% |
| 4 | Summarization / CNN/DailyMail / ROGUE-1 | 8 / 2 | 2/8 | 25.0000% | 0.0000% | 0.0000% | 75.0000% |
| 5 | Summarization / CNN/DailyMail / ROGUE-2 | 8 / 4 | 4/8 | 50.0000% | 37.5000% | 0.0000% | 52.0833% |
| 6 | Summarization / CNN/DailyMail / ROGUE-L | 8 / 4 | 4/8 | 50.0000% | 37.5000% | 0.0000% | 52.0833% |
| 7 | Summarization / XSum / ROGUE-1 | 5 / 3 | 3/5 | 60.0000% | 60.0000% | 61.1111% | 61.1111% |
| 8 | Summarization / XSum / ROGUE-2 | 5 / 3 | 3/5 | 60.0000% | 40.0000% | 0.0000% | 61.1111% |
| 9 | Summarization / XSum / ROGUE-L | 5 / 1 | 1/5 | 20.0000% | 20.0000% | 0.0000% | 0.0000% |
| 10 | Named Entity Recognition (NER) / Ontonotes v5 - English / F1 | 5 / 1 | 1/5 | 20.0000% | 0.0000% | 0.0000% | 0.0000% |
| 11 | Named Entity Recognition (NER) / WNUT-16 - English / F1 | 3 / 0 | 0/3 | 0.0000% | 0.0000% | 0.0000% | 0.0000% |
| 12 | Named Entity Recognition (NER) / WNUT-17 - English / F1 | 3 / 0 | 0/3 | 0.0000% | 0.0000% | 0.0000% | 0.0000% |
| 13 | Text Chunking / CoNLL-2000 / F1 | 5 / 5 | 5/5 | 100.0000% | 60.0000% | 38.6667% | 100.0000% |
| 14 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 | 14 / 4 | 4/14 | 28.5714% | 28.5714% | 27.0833% | 27.0833% |
| 15 | Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy | 5 / 3 | 3/5 | 60.0000% | 40.0000% | 61.1111% | 61.1111% |
| 16 | Machine Translation / WMT’14 EN-FR / BLEU | 5 / 5 | 5/5 | 100.0000% | 60.0000% | 41.6667% | 100.0000% |
| 17 | Machine Translation / WMT’14 EN-DE / BLEU | 6 / 6 | 6/6 | 100.0000% | 66.6667% | 56.3889% | 65.2778% |
| 18 | Machine Translation / IWSLT’14 EN-DE / BLEU | 4 / 1 | 1/4 | 25.0000% | 25.0000% | 0.0000% | 0.0000% |
| 19 | Word Sense Induction / SemEval 2013 Task 13 / Fuzzy normalized mutual information (FNMI) | 3 / 0 | 0/3 | 0.0000% | 0.0000% | 0.0000% | 0.0000% |
| 20 | Word Sense Induction / SemEval 2013 Task 13 / Fuzzy B-Cubed (FBC) | 3 / 0 | 0/3 | 0.0000% | 0.0000% | 0.0000% | 0.0000% |
| 21 | Word Sense Induction / SemEval 2013 Task 13 / AVG | 3 / 2 | 2/3 | 66.6667% | 33.3333% | 25.0000% | 25.0000% |
| 22 | Intent Detection and Slot Filling / ATIS / F1 | 5 / 5 | 5/5 | 100.0000% | 60.0000% | 58.6667% | 100.0000% |
| 23 | Intent Detection and Slot Filling / ATIS / Accuracy | 5 / 5 | 5/5 | 100.0000% | 60.0000% | 87.0000% | 100.0000% |
| 24 | Intent Detection and Slot Filling / SNIPS / F1 | 4 / 3 | 3/4 | 75.0000% | 25.0000% | 11.1111% | 100.0000% |
| 25 | Intent Detection and Slot Filling / SNIPS / Accuracy | 4 / 3 | 3/4 | 75.0000% | 50.0000% | 61.1111% | 88.8889% |
| 26 | Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy | 5 / 5 | 5/5 | 100.0000% | 80.0000% | 54.3333% | 80.0000% |
| 27 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy | 4 / 4 | 4/4 | 100.0000% | 75.0000% | 85.4167% | 100.0000% |

## 可复核案例

- Text Chunking / CoNLL-2000 / F1：5/5 篇覆盖，AO=100%，但 RC=60%。说明论文顺序完全一致并不要求所有绝对数值正确。
- Machine Translation / WMT’14 EN-FR / BLEU：5/5 篇覆盖，AO=100%、RC=60%；43.2 的并列按论文 ID 排序，Gold 与预测均保留两篇。
- Dialogue Act Classification / MRDA / Accuracy：4/4 覆盖，AO=100%、RC=75%。
- SNIPS / F1：3/4 覆盖但 AO=100%，这是 k 取较短榜长度的公式性质，不能把 AO=100% 解读为全榜恢复。
- 最差的 7 个空榜：Gigaword 的 ROGUE-1/2/L、WNUT-16/17 F1、WSI 的 FNMI/FBC，PC/RC/AO 全为 0。

## 既有错误如何影响排行榜

- Gigaword 多条原始 ROUGE-* 记录在标准化后 Metric 为 null；冻结 Gold 的标准名称为 ROGUE-*。原始抽取与标准化行都已保留，没有据此纠正拼写或映射。
- WNUT 的已有原始缩写 WN16/WN17、WNUT 2016/2017 等对应多条 Dataset=null，未形成精确标准 TDM；例如首篇论文的 55.14、50.68 虽已抽取，仍无法进入对应榜。
- WSI 的 21.4 (0.5) 与 64.0 (0.5) 有准确标准 TDM，但 float 转换失败，造成两个“命中 TDM 但空榜”的案例。
- 44.16/21.56/41.30、87.95 (± 0.13) 等按原始转换规则跳过，未拆分或修复。

284 条标准化行中，88 条命中这 27 个 TDM；6 条数值转换失败，13 条有效旧记录被同篇同 TDM 的后续记录覆盖，最终 69 条预测榜记录。其余 196 条不匹配这 27 榜，其中既可能有合法但不在该子集的 TDM，也可能有标准化错误，不能全部归为错误。没有出现预测论文不属于对应 Gold 榜的情况。

## 数据与定义的限制

27 榜、每榜至少 3 篇、平均 5.1852 篇与论文规模一致，所有条目都与本地 Gold TDMR 相同；但完整 Gold 实际为 141 Unique TDM、33 个三篇以上分组，而论文写的是 138/27。未自行重建或扩大榜集；input_audit.json 列出多出的 6 个分组。不能凭数量相同宣称已独立证明作者历史数据版本完全一致。

原代码缺少 LR/AO 直接输出，RBO 元素与论文 AO 不同，RC 不要求论文和数值共同正确。AO 并列与空榜约定、LR 数值有效性条件均已公开，详细见 [metric_definition_audit.md](metric_definition_audit.md)。本次补齐当前本地 Fully Pre-defined Baseline 的端到端评价；与论文成绩的严格一一可比性仍受这些差异限制。

## 冻结与复现

正式 Baseline 的 1167 个文件及所有文件名集合执行前后相同；官方源码、Prompt、Gold、模型配置与 183 个依赖版本均保持不变。快照为 freeze_before.json；结果核验为 verification.json。只有独立评测目录发生新增写入；评价过程禁止网络与敏感配置读取。

[完整榜单排名](leaderboards/gold_vs_predicted.md) · [逐榜机器可读结果](leaderboards/gold_vs_predicted.json) · [运行说明](README.md)