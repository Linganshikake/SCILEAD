# SCILEAD DeepSeek-V4.1-Flash 全量实验报告

执行日期：2026-10-28（北京时间）。状态：全部完成。43 篇论文、295 条 Gold；本轮抽取 295 条预测，六个正式分支均完整覆盖 43 篇。

Fully + LLM 的 TDMR F1 为 **75.75%**，相对原论文 GPT-4 Turbo（55.27%）提高 **20.48 个百分点**；相对 GPT-4.1 提高 **33.59 个百分点**，相对 Sol 下降 **2.22 个百分点**。

Partially 和 Cold Start 的主要问题是新名称向既定排行榜的语义对齐。DeepSeek 多次按字符串相等理解原 Prompt 的“matches”，保留输入缩写；Fully 有完整候选名称时表现明显更好。下文给出官方处理事件和具体实例。

## 1. 实验设置与执行流程

- 实际请求模型：`deepseek-flash`；DeepSeek 官方文档当前将该别名映射到 `DeepSeek-V4.1-Flash-1017`。全部响应模型标识为 `deepseek-flash`，原始响应及 system_fingerprint 已保存。
- 接口：`https://api.deepseek.com/chat/completions`；thinking enabled、reasoning_effort=high、stream=false。每次请求不发送输出 Token 上限、temperature、seed、tools 或 response_format。官方 high 模式在省略上限时采用服务端默认预算。
- 官方源码实际 HEAD：`8bf74b0a830feb7035c6166dce3394dc344ae532`；历史外层归档冻结标识：`b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25`。
- 复用 43 篇冻结 RAG 输入，每篇 4 个检索正文块及全部已检测表格；顺序和内容哈希一致。PDF 解析、Embedding、Chroma 检索均未重跑。Extraction Prompt 不含 Gold、历史预测或错误分析。
- 先进行一次全量 Zero-shot Extraction，再复用这批新预测执行 Fully LLM、Fully CS、Partially 和三种 Cold Start。Fully 的候选名称及顺序固定为 Task 23、Dataset 71、Metric 26；Partially/Cold 使用原版遮蔽和动态名称更新逻辑。
- Fully CS 沿用既有 `Lajavaness/bilingual-embedding-large`、CPU FP32、原版 top-1 余弦相似度；Partially 遮蔽种子 0；Cold 顺序为默认、字符串种子 `"0"`、`"42"`。
- 每个分支内部串行；CS 先单独完成并退出，随后四个 API 分支并行。逐请求保存原始响应、实际请求参数及检查点；无重复名称缓存、重试或模型切换。
- 本轮仅 DeepSeek 基座与相应接口参数变化。Sol 历史配置含 32768 输出预算，本轮采用 DeepSeek high 且不发送客户端上限；实际生成配置差异均有记录。

模型映射与参数依据：[DeepSeek 官方文档](https://api-docs.deepseek.com/)、[模型说明](https://api-docs.deepseek.com/quick_start/pricing/)。读取时的文档副本见 `documentation/`。

## 2. 评价口径

Tuple 指标调用未经修改的官方 `tdm_eval.py`：先求逐篇 Precision / Recall，再做 Macro 平均；F1=2PR/(P+R)，由聚合 P/R 计算。Partially 和 Cold Start **统一以第二阶段为主指标**，第一阶段作为过程诊断单独保存。

排行榜评价使用冻结的 27 个 Gold Leaderboards（本地文件含 140 个条目，原论文报告 138 个）。LR 是 TDM 命中榜比例，同时报告有效数值非空榜率；PC、RC、数值列表 RBO 沿用官方实现，论文 ID AO 是单独的辅助实现。原论文 AO 按作者报告值列示，不替换成 RBO。

所有表格均为百分数。Cold 三顺序汇总为各次结果的算术均值与样本标准差（ddof=1）；各次 F1 均先按该次 Macro P/R 计算。

## 3. 本轮全部 IIM 与 ETM 指标

### Fully + LLM

| 指标 | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Task IIM | 97.97 | 97.60 | 97.78 |
| Dataset IIM | 96.23 | 96.35 | 96.29 |
| Metric IIM | 95.21 | 95.14 | 95.18 |
| Result IIM | 81.63 | 80.89 | 81.26 |
| TDM Exact Match | 93.63 | 90.68 | 92.13 |
| TDMR Exact Match | 76.38 | 75.13 | 75.75 |

### Fully + CS

| 指标 | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Task IIM | 97.92 | 98.38 | 98.15 |
| Dataset IIM | 88.15 | 87.74 | 87.95 |
| Metric IIM | 89.46 | 86.33 | 87.87 |
| Result IIM | 81.63 | 80.89 | 81.26 |
| TDM Exact Match | 78.43 | 74.16 | 76.23 |
| TDMR Exact Match | 60.72 | 58.94 | 59.82 |

### Partially 第二阶段

| 指标 | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Task IIM | 41.02 | 47.13 | 43.87 |
| Dataset IIM | 51.84 | 54.83 | 53.29 |
| Metric IIM | 94.98 | 95.14 | 95.06 |
| Result IIM | 81.63 | 80.89 | 81.26 |
| TDM Exact Match | 25.25 | 23.82 | 24.51 |
| TDMR Exact Match | 20.92 | 19.51 | 20.19 |

### Cold Start 默认顺序

| 指标 | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Task IIM | 35.60 | 41.69 | 38.41 |
| Dataset IIM | 41.71 | 45.60 | 43.57 |
| Metric IIM | 45.63 | 48.20 | 46.88 |
| Result IIM | 81.63 | 80.89 | 81.26 |
| TDM Exact Match | 14.10 | 12.99 | 13.52 |
| TDMR Exact Match | 12.06 | 10.76 | 11.38 |

### Cold Start 字符串种子 0

| 指标 | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Task IIM | 33.13 | 39.15 | 35.89 |
| Dataset IIM | 41.81 | 43.40 | 42.59 |
| Metric IIM | 45.74 | 47.11 | 46.41 |
| Result IIM | 81.63 | 80.89 | 81.26 |
| TDM Exact Match | 13.11 | 11.85 | 12.45 |
| TDMR Exact Match | 11.85 | 10.40 | 11.08 |

### Cold Start 字符串种子 42

| 指标 | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Task IIM | 33.95 | 38.01 | 35.86 |
| Dataset IIM | 41.23 | 43.34 | 42.26 |
| Metric IIM | 42.53 | 41.22 | 41.86 |
| Result IIM | 81.63 | 80.89 | 81.26 |
| TDM Exact Match | 11.66 | 10.48 | 11.04 |
| TDMR Exact Match | 10.50 | 9.12 | 9.76 |

### Cold Start 三顺序汇总

| 指标 | P 均值 ± SD | R 均值 ± SD | F1 均值 ± SD |
| --- | --- | --- | --- |
| Task IIM | 34.23 ± 1.26 | 39.62 ± 1.89 | 36.72 ± 1.46 |
| Dataset IIM | 41.58 ± 0.31 | 44.12 ± 1.29 | 42.81 ± 0.68 |
| Metric IIM | 44.63 ± 1.82 | 45.51 ± 3.75 | 45.05 ± 2.77 |
| Result IIM | 81.63 ± 0.00 | 80.89 ± 0.00 | 81.26 ± 0.00 |
| TDM Exact Match | 12.96 ± 1.23 | 11.77 ± 1.26 | 12.34 ± 1.25 |
| TDMR Exact Match | 11.47 ± 0.85 | 10.09 ± 0.86 | 10.74 ± 0.86 |

## 4. 本轮排行榜指标

| 设置 | LR | 有效非空榜率 | PC | RC | RBO（数值列表） | AO（论文ID） |
| --- | --- | --- | --- | --- | --- | --- |
| Fully + LLM | 100.00 | 100.00 | 94.12 | 77.26 | 73.26 | 93.89 |
| Fully + CS | 88.89 | 88.89 | 75.20 | 55.16 | 53.23 | 71.15 |
| Partially 第二阶段 | 77.78 | 77.78 | 30.05 | 22.55 | 31.07 | 36.11 |
| Cold Start 默认顺序 | 29.63 | 29.63 | 12.07 | 10.59 | 8.02 | 9.95 |
| Cold Start 字符串种子 0 | 29.63 | 29.63 | 11.68 | 9.52 | 6.87 | 6.87 |
| Cold Start 字符串种子 42 | 25.93 | 25.93 | 11.93 | 10.45 | 20.78 | 24.49 |
| Cold 三顺序均值 ± SD | 28.40 ± 2.14 | 28.40 ± 2.14 | 11.90 ± 0.20 | 10.19 ± 0.58 | 11.89 ± 7.72 | 13.77 ± 9.41 |

## 5. 与原论文、GPT-4.1、Sol 对比

### 同设置 Tuple F1

| 设置 | 模型 | Task | Dataset | Metric | Result | TDM | TDMR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fully + LLM | 原论文 GPT-4 Turbo | 90.86 | 89.22 | 87.31 | 69.26 | 72.75 | 55.27 |
| Fully + LLM | GPT-4.1 | 96.69 | 80.07 | 85.32 | 70.38 | 61.22 | 42.16 |
| Fully + LLM | Sol | 98.38 | 97.57 | 97.15 | 80.60 | 95.88 | 77.97 |
| Fully + LLM | DeepSeek | 97.78 | 96.29 | 95.18 | 81.26 | 92.13 | 75.75 |
| Fully + CS | 原论文 GPT-4 Turbo | 90.73 | 83.02 | 83.85 | 69.26 | 66.29 | 49.26 |
| Fully + CS | GPT-4.1 | 97.28 | 87.80 | 85.90 | 70.38 | 71.31 | 54.26 |
| Fully + CS | Sol | 97.51 | 91.09 | 88.37 | 80.60 | 80.60 | 65.07 |
| Fully + CS | DeepSeek | 98.15 | 87.95 | 87.87 | 81.26 | 76.23 | 59.82 |
| Partially 第二阶段 | 原论文 GPT-4 Turbo | 70.32 | 81.36 | 90.72 | 69.26 | 53.90 | 40.07 |
| Partially 第二阶段 | GPT-4.1 | 40.85 | 57.98 | 84.31 | 70.38 | 21.95 | 16.94 |
| Partially 第二阶段 | Sol | 69.36 | 77.09 | 97.15 | 80.60 | 46.78 | 39.95 |
| Partially 第二阶段 | DeepSeek | 43.87 | 53.29 | 95.06 | 81.26 | 24.51 | 20.19 |

### 同设置排行榜

| 设置 | 模型 | LR | PC | RC | RBO | AO |
| --- | --- | --- | --- | --- | --- | --- |
| Fully + LLM | 原论文 GPT-4 Turbo | 100.00 | 70.37 | 51.79 | — | 53.87 |
| Fully + LLM | GPT-4.1 | 81.48 | 48.71 | 31.80 | 24.77 | 46.25 |
| Fully + LLM | Sol | 100.00 | 98.73 | 81.97 | 78.31 | 94.78 |
| Fully + LLM | DeepSeek | 100.00 | 94.12 | 77.26 | 73.26 | 93.89 |
| Fully + CS | 原论文 GPT-4 Turbo | 92.59 | 63.70 | 45.59 | — | 38.66 |
| Fully + CS | GPT-4.1 | 92.59 | 63.16 | 41.19 | 30.34 | 52.22 |
| Fully + CS | Sol | 88.89 | 78.42 | 62.37 | 55.31 | 71.39 |
| Fully + CS | DeepSeek | 88.89 | 75.20 | 55.16 | 53.23 | 71.15 |
| Partially 第二阶段 | 原论文 GPT-4 Turbo | 88.89 | 55.92 | 40.06 | — | 43.71 |
| Partially 第二阶段 | GPT-4.1 | 48.15 | 13.33 | 8.61 | 11.05 | 15.58 |
| Partially 第二阶段 | Sol | 70.37 | 47.56 | 41.94 | 35.40 | 41.70 |
| Partially 第二阶段 | DeepSeek | 77.78 | 30.05 | 22.55 | 31.07 | 36.11 |

### Cold Start 排行榜三顺序均值 ± SD

| 模型 | LR | PC | RC | RBO | AO |
| --- | --- | --- | --- | --- | --- |
| 原论文 GPT-4 Turbo | 81.48 ± 14.81 | 58.74 ± 7.42 | 46.13 ± 3.10 | — | 48.15 ± 4.42 |
| GPT-4.1 | 39.51 ± 8.55 | 10.42 ± 2.65 | 8.08 ± 3.74 | 8.75 ± 1.25 | 11.36 ± 2.83 |
| Sol | 88.89 ± 0.00 | 57.30 ± 3.61 | 45.88 ± 5.16 | 49.09 ± 2.54 | 59.65 ± 3.14 |
| DeepSeek | 28.40 ± 2.14 | 11.90 ± 0.20 | 10.19 ± 0.58 | 11.89 ± 7.72 | 13.77 ± 9.41 |

原论文数据来自已核对的 Tables 3、4、5、12、17；逐行表号、页码和历史 JSON 路径见 `analysis/comparison_final/comparison.json`。GPT-4.1 Fully CS 的 LR 为 25/27，而有效非空榜率为 24/27，两者保持分列。

## 6. 结果解释与可核查案例

**Fully 下数值覆盖较好，完整绑定仍有损失。** Result IIM F1 为 81.26%，比 Sol 高 0.66 个百分点；TDMR F1 比 Sol 低 2.22 个百分点。取到数值和正确绑定到任务、数据集、指标仍是两个不同的环节。

**本轮 CS 的主要损失在 Dataset 和 Metric。** 在完全相同的 295 条抽取上，Fully LLM 改为 CS 后，TDMR F1 从 75.75% 降到 59.82%，相差 15.93 个百分点。Result IIM 保持相同，差异来自名称映射。

**Partially/Cold 的名称对齐明显不足。** 下面是第二阶段原版观察器的逐事件计数；“未匹配保留”表示模型回答未进入候选 TDM 集合，官方代码保留原输入。

| 分支 | 原本精确匹配 | 成功映射 | 未匹配保留 | null 跳过 | 回答等于输入 tuple |
| --- | --- | --- | --- | --- | --- |
| Partially 第二阶段 | 32 | 9 | 248 | 6 | 248 |
| Cold Start 默认顺序 | 3 | 12 | 280 | 0 | 280 |
| Cold Start 字符串种子 0 | 3 | 10 | 282 | 0 | 281 |
| Cold Start 字符串种子 42 | 3 | 12 | 280 | 0 | 280 |

例如默认 Cold 的首条输入为 `(Named Entity Recognition, ON5E, F1)`，候选包含 `(Named Entity Recognition (NER), Ontonotes v5 - English, F1)`。原始回答仍是输入 tuple；返回的 reasoning 明确按“Not exact”作出判断。此条没有 HTTP、JSON 或候选传递故障，失败发生在模型对原版匹配要求的解释和语义名称对齐。三个 Cold 顺序分别只有 12、10、12 条发生映射。原始请求、响应和事件保存在 `variants/cold_default/stage2/api_calls/0001/` 等目录。

| 论文 | 环节 | 实际现象 | 证据位置 |
| --- | --- | --- | --- |
| D18-1523.pdf | Extraction 遗漏 | Prompt 中已有 FNMI 11.26±0.48、FBC 57.49±0.23、AVG 25.43±0.48；只输出 AVG。此篇无需名称请求，遗漏已发生在抽取阶段。 | 第5页 Table，证据索引5 |
| 1811.09242.pdf | Extraction 列绑定 | SemEval 2010 的 V-M 与 AVG 对应 10.1 / 25.2；预测绑定为 25.20 / 10.1。标准化保留原数值，未纠正错列。 | 第5页 Table，证据索引5 |
| C18-1139.pdf | Normalization 限定信息丢失 | 原始 Task 含 NER German、Dataset=CoNLL-2003、Result=88.32±0.20；逐字段标准化将 Dataset 映射为 CoNLL-2003-English，Task 中 German 限定被移除。 | 第3页 Table及对应字段请求 |

具体预测、Gold、证据文本与文件哈希见 `inspection/examples.json`；前三类案例说明遗漏、错列和名称映射损失均仍存在。所有结果均按原样纳入评价。

严格有限数值相等辅助检查的 Result F1 为 **72.73%**，官方 Result IIM F1 为 **81.26%**。官方允许字符串包含匹配；辅助检查不解析 ± 不确定度字符串，也不做单位换算，因此差距同时受格式和数值匹配规则影响。详见各分支 `strict_result_metrics.json`。

## 7. 实际请求、Token 与资源

| 分支 | Extraction | Normalization | 请求合计 | 输入Tokens | 输出Tokens（含推理） | 总Tokens |
| --- | --- | --- | --- | --- | --- | --- |
| cold_0 | 0 | 573 | 573 | 263266 | 58347 | 321613 |
| cold_42 | 0 | 589 | 589 | 267844 | 56977 | 324821 |
| cold_default | 0 | 569 | 569 | 261025 | 61809 | 322834 |
| fully | 43 | 518 | 561 | 351949 | 247847 | 599796 |
| partially | 0 | 608 | 608 | 279577 | 101554 | 381131 |
| fully_cs | 0 | 0 | 0 | 0 | 0 | 0 |

合计 **2,900 次模型请求**：43 次 Extraction、2,857 次标准化；总 Tokens **1,950,195**，其中输入 1,423,661、输出 526,534，输出含 reasoning Tokens 490,724。所有请求 HTTP 200、finish_reason=stop；重试 0 次，未知用量 0 次，格式失败 0 篇。额外一次认证模型列表 GET 未计入模型请求。

从首个请求到最后响应约 **52.78 分钟**，包含阶段间准备间隔；各请求耗时求和为 80.77 分钟，分支并行使两者不同。CS 耗时 82.58 秒，进程峰值 working set **4.46 GiB**，未新增 API 请求或依赖。

43 篇 Extraction 的输入 Token 数取自服务端 Usage。最长 `1912.08777.pdf` 为 54,967 输入 Tokens，输出 4,321 Tokens（含 3,325 reasoning），36 条合法记录，finish_reason=stop。全部论文页级证据数量、预测数量、调用数及输入长度见 `fully/paper_index.csv`。

## 8. 完整性与结果位置

已核验 343 个输入、源码、历史结果及评价来源文件，变化 0；43 篇 source_documents 与冻结版本完全一致。所有分支均保留记录数量、顺序和 Result；本轮原始 Result 全为字符串，兼容转换次数为 0。实际请求均无客户端输出上限。

| 文件/目录 | 内容 |
| --- | --- |
| report.md | 本中文汇总报告 |
| results_summary.json | 全部主指标、Cold三顺序统计和实际用量 |
| fully/paper_index.csv | 43篇输入证据、预测数量、Token及逐篇路径 |
| fully/merged/raw_output.json / output.json / normalized_output.json | 全量新Extraction及Fully LLM标准化 |
| variants/fully_cs/normalization/embedding_normalized_output.json | Fully CS |
| variants/partially/stage1、stage2 | Partially两阶段原始响应、事件和输出 |
| variants/cold_default、cold_0、cold_42 | 三种Cold顺序各两阶段 |
| analysis/evaluations/各分支/ | 官方原始评价JSON、全部P/R/F1、逐篇指标、排行榜及严格数值辅助指标 |
| analysis/comparison_final/ | 原论文、GPT-4.1、Sol、DeepSeek的JSON/CSV对照及逐篇比较 |
| inspection/ | 遗漏、列绑定、名称限定损失及第二阶段对齐行为的原始证据 |
| api_usage_summary.json / request_audit.csv | 所有实际请求参数、响应模型、finish_reason和Token汇总 |
| verification.json / delivery_protected_hashes.json | 全分支完成与文件完整性核验 |

实验已完成并停止。检查点只用于核验和定位，已成功请求无需再次执行；历史 GPT-4.1、Sol、Llama、AxCell 结果及原版源码保持不变。
