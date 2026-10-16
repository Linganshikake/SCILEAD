# GPT-4.1 Partially Pre-defined 全量实验

43/43 篇完成两阶段标准化与评价；295 条 Gold、284 条预测。复用冻结 Extraction，没有 PDF 解析、Embedding、Retrieval 或新 Extraction。

## Masked 设置与处理顺序

直接调用未修改 sample_tdms：cold_start=False，seed=0（整数），启动前 PYTHONHASHSEED=0。隐藏3个 Task、8个 Dataset，得到10个 Masked 榜；没有为匹配论文数量手工调整。

隐藏 Task：Intent Detection and Slot Filling；Dialogue Act Classification；Named Entity Recognition (NER)。

隐藏 Dataset：ATIS；Switchboard Dialog Act Corpus (SWDA)；ICSI Meeting Recorder Dialog Act Corpus (MRDA)；WNUT-17 - English；SNIPS；Ontonotes v5 - English；CoNLL-2003 - English；WNUT-16 - English。

| 榜单 Task | 榜数 | 是否被隐藏 |
|---|---:|---|
| Summarization | 9 | False |
| Named Entity Recognition (NER) | 4 | True |
| Text Chunking | 1 | False |
| Part-of-Speech (POS) Tagging | 1 | False |
| Machine Translation | 3 | False |
| Word Sense Induction | 3 | False |
| Intent Detection and Slot Filling | 4 | True |
| Dialogue Act Classification | 2 | True |

Masked 榜完整名单：

| Task | Dataset | Metric | Gold 条数 |
|---|---|---|---:|
| Named Entity Recognition (NER) | Ontonotes v5 - English | F1 | 5 |
| Named Entity Recognition (NER) | WNUT-16 - English | F1 | 3 |
| Named Entity Recognition (NER) | WNUT-17 - English | F1 | 3 |
| Named Entity Recognition (NER) | CoNLL-2003 - English | F1 | 14 |
| Intent Detection and Slot Filling | ATIS | F1 | 5 |
| Intent Detection and Slot Filling | ATIS | Accuracy | 5 |
| Intent Detection and Slot Filling | SNIPS | F1 | 4 |
| Intent Detection and Slot Filling | SNIPS | Accuracy | 4 |
| Dialogue Act Classification | Switchboard Dialog Act Corpus (SWDA) | Accuracy | 5 |
| Dialogue Act Classification | ICSI Meeting Recorder Dialog Act Corpus (MRDA) | Accuracy | 4 |

原始预测按 frozen_output_key_order 处理，记录和字段顺序不变。本地 Gold JSON 顺序另行记录，无法证明作者历史执行顺序；未依据模型表现排序。

## 两阶段动态行为

| 名称类型 | 初始 | 最终 | 原名新增 |
|---|---:|---:|---:|
| Task | 20 | 70 | 50 |
| Dataset | 63 | 119 | 56 |
| Metric | 26 | 26 | 0 |

阶段一 null 字段：{'Task': 0, 'Dataset': 1, 'Metric': 67}；阶段二 null 字段：{'Task': 0, 'Dataset': 1, 'Metric': 67}。阶段二修改完整 TDM 15 条。完整新增名称和逐字段状态见 stage_statistics.json、stage1/label_update_events.jsonl。

阶段一分支统计：{'original_name_added': 106, 'exact_or_result': 796, 'existing_candidate': 166, 'null': 68}。阶段二分支统计：{'unmatched_preserved': 189, 'tuple_mapped': 15, 'null_skipped': 68, 'exact_tuple': 12}。

精确名称直接保留；Task/Dataset 仅在原版精确回答条件下扩展集合；Metric 不扩展。阶段二跳过含 null 的三元组，集合外回答保留阶段一值。每次请求保存候选序列化、Prompt 哈希、实际 wire JSON、原始响应和动态后状态。实际付费响应已离线送回未修改的原版 main 重放，全部状态事件、输出与实际运行一致，没有新增请求。

## 两阶段 TDMR / IIM

| 指标 | 阶段一 P | 阶段一 R | 阶段一 F1 | 阶段二 P | 阶段二 R | 阶段二 F1 |
|---|---:|---:|---:|---:|---:|---:|
| Task IIM | 0.268162 | 0.313584 | 0.289100 | 0.352270 | 0.486065 | 0.408491 |
| Dataset IIM | 0.479679 | 0.485064 | 0.482356 | 0.576190 | 0.583514 | 0.579829 |
| Metric IIM | 0.866833 | 0.820566 | 0.843065 | 0.866833 | 0.820566 | 0.843065 |
| Result IIM | 0.690160 | 0.718075 | 0.703841 | 0.690160 | 0.718075 | 0.703841 |
| TDM Exact Match | 0.113990 | 0.107919 | 0.110872 | 0.220977 | 0.218043 | 0.219500 |
| TDMR Exact Match | 0.086028 | 0.092239 | 0.089025 | 0.162800 | 0.176524 | 0.169384 |

P/R 为原版逐篇 Macro；F1=2PR/(P+R)，不是逐篇 F1 平均。阶段一输入 stage1/normalized_output.json；阶段二输入 stage2/leaderboard_normalized_output.json。两者独立保存，阶段二未修改阶段一。

两个阶段的 Result IIM F1 均为0.703840880674，严格 Decimal 数值 Result F1 均为0.586781786324；逐篇及聚合都与冻结基线一致。严格诊断不替代官方字符串包含匹配。

## 排行榜

| 指标 | Fully LLM 全27 | Fully CS 全27 | Partially 阶段二全27 | Partially 阶段二 Masked |
|---|---:|---:|---:|---:|
| LR（精确 TDM 命中） | 0.814815 | 0.925926 | 0.481481 | 0.400000 |
| 有效数值非空榜率 | 0.740741 | 0.888889 | 0.407407 | 0.400000 |
| 官方 PC | 0.487125 | 0.631570 | 0.133289 | 0.139048 |
| 官方 RC | 0.317989 | 0.411905 | 0.086067 | 0.114048 |
| 官方数值列表 RBO | 0.247654 | 0.303420 | 0.110535 | 0.120667 |
| 论文 ID AO（补充） | 0.462500 | 0.522212 | 0.155802 | 0.120667 |

全部27榜：TDM命中 13/27，有效非空 11/27。Masked10榜：TDM命中 4/10，有效非空 4/10。全部43篇预测参与两种范围的构榜。

沿用官方 Result 转换、缩放、同论文同TDM后写覆盖规则。PC/RC/数值列表RBO与论文ID AO分别报告，空榜计0并保留全部目标榜Macro分母；不裁剪RC。逐榜排名、额外论文、覆盖记录见 leaderboard_evaluation/*/leaderboards/gold_vs_predicted.json。

## Fully 对照

| 指标 F1 | Fully LLM | Fully CS | Partially 阶段一 | Partially 阶段二 |
|---|---:|---:|---:|---:|
| Task IIM | 0.966900 | 0.972757 | 0.289100 | 0.408491 |
| Dataset IIM | 0.800714 | 0.877961 | 0.482356 | 0.579829 |
| Metric IIM | 0.853224 | 0.858958 | 0.843065 | 0.843065 |
| Result IIM | 0.703841 | 0.703841 | 0.703841 | 0.703841 |
| TDM Exact Match | 0.612160 | 0.713128 | 0.110872 | 0.219500 |
| TDMR Exact Match | 0.421578 | 0.542610 | 0.089025 | 0.169384 |

两阶段与论文表格的对应存在未明确到具体JSON的歧义，详见 comparison_with_fully.md；不选择较高阶段分数作为作者设置。本地 GPT-4.1 无客户端输出上限，与作者默认15/100及GPT-4 Turbo不同，已明确记录。

## 错误分析范围

按相同数值关联 Gold 的配对分类：{'neither_strict_match': 251, 'stage2_only_strict_match': 9, 'both_strict_match': 24}。发现 12 个“映射到仍可见但同值 Gold 名称不同”的字段候选，见 evaluation/visible_entity_mismatch_candidates.json。这是离线疑似错误证据；相同数值可能属于多个实验，不能无条件当作语义真值。没有用这些分析修正模型结果。

## 实际调用与耗时

| 阶段 | 请求尝试 | 成功 | 失败/未知状态 | 未知用量 | Prompt Tokens | Completion Tokens | Total Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| stage1 | 340 | 340 | 0 | 0 | 140768 | 1466 | 142234 |
| stage2 | 204 | 204 | 0 | 0 | 108399 | 3141 | 111540 |
| total | 544 | 544 | 0 | 0 | 249167 | 4607 | 253774 |

请求耗时合计 1233.776 秒；准备开始至验收约 1873.722 秒。实际请求均检查HTTP状态、响应模型、finish_reason及字符串结构。没有SDK自动重试，没有模型切换，没有客户端输出上限；第三方实际账单金额未知，不采用LangChain默认美元估价。模拟测试和离线重放不计入API用量。

## 完整性与后续条件

三个冻结目录的全部文件及文件名集合、官方源码、Prompt、Gold和依赖版本均未改变。43篇ID、284条预测数量/顺序、Result及source_documents保持原样，详见 verification.json。

动态集合、顺序执行、断点重放及两级评价链路已经验证，可为下一轮原版 Cold Start 的三种论文顺序实验做准备。需先明确三种顺序按官方参数执行并分别冻结；本轮没有启动 Cold Start、Few-shot、阈值2或任何改进实验。

## 代表性失败现象

阶段二 189 个不匹配回答中，189 个是完整原输入三元组的原样返回，而非因额外引号、JSON包裹或截断而无法接受。它们按原版逻辑保留，不能人工改为最相近候选。

例如2020.findings-emnlp.378.pdf中的ON5E、WN16、WN17、RE、WE在动态集合中成为名称，阶段二仍返回原三元组，未形成Gold标准名称；相同Result数值因此不能保证TDMR命中。Chunking、Syntactic Chunking、Abstractive Summarization等原名也被新增，未都合并到已有的Text Chunking/Summarization。另一方面，D18-1279.pdf的CoNLL-2003 English被阶段二对齐到CoNLL-2003 - English及标准NER任务，是实际成功案例。

67个Metric null使对应记录在阶段二被原版逻辑跳过，阶段二没有补全Metric。模型新增名称、保留原三元组和跳过null的行为共同影响本次分数；这些是观察记录，不是根据分数修改方法的依据。

## 检查点工程问题

第132次请求已成功返回HTTP200/stop，且响应哈希与COMPLETE状态一致；随后Windows拒绝原子替换state.json。暂存文件只多出耗时字段。已归档原状态、暂存状态及暂停日志，修复为有界文件写入重试，并重放前132次已保存响应继续；没有重发这132个请求。锁占用进程未能确定。回归测试在修复前失败、修复后通过；这一文件系统事件与API失败分别记录，见 reproducibility/incident_atomic_write/。

同值Gold字段不一致的12个候选中，9个字段从Extraction起原样保留，3个发生了名称映射；不能把12个都归因于标准化。例如1903.07785.pdf第3条的MRPC任务描述映射到仍可见的Text Similarity，而同数值Gold任务是Paraphrase Detection。另有原始Accuracy/F1或BLEU-4/METEOR绑定不一致的候选，属于抽取阶段已存在的问题，需要保留与标准化错误的区别。所有同值关联仍保留数值重复可能导致歧义的限制。
