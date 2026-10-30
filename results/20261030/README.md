# 2026-10-30 新增实验结果索引

本次新增6组已完成实验归档。各实验原始报告、预测、标准化结果、评价、Prompt变更和脱敏请求记录按本地原路径保存。

| 实验 | 范围 | 报告 | 指标JSON | 实验目录 |
|---|---|---|---|---|
| GPT-5.6 Sol：Fully + CS、Partially、Cold Start | 43篇 / 295 Gold | [完整报告](../../pilot/gpt56_sol_variants/20261024/实验结果汇总.md) | [指标数据](../../pilot/gpt56_sol_variants/20261024/metrics_summary.json) | [打开目录](../../pilot/gpt56_sol_variants/20261024/) |
| GPT-5.6 Sol：Partially / Cold Start 增强 Prompt | 43篇 / 295 Gold | [完整报告](../../pilot/gpt56_sol_variants/20261028_semantic_alignment_v1/report.md) | [指标数据](../../pilot/gpt56_sol_variants/20261028_semantic_alignment_v1/analysis/comparison_final/comparison.json) | [打开目录](../../pilot/gpt56_sol_variants/20261028_semantic_alignment_v1/) |
| DeepSeek-V4.1-Flash：Fully LLM / CS、Partially、Cold Start | 43篇 / 295 Gold | [完整报告](../../pilot/deepseek_v41_flash/20261028/report.md) | [指标数据](../../pilot/deepseek_v41_flash/20261028/results_summary.json) | [打开目录](../../pilot/deepseek_v41_flash/20261028/) |
| DeepSeek：Partially / Cold Start 增强 Prompt | 43篇 / 295 Gold | [完整报告](../../pilot/deepseek_v41_flash/20261028_semantic_alignment_v1/report.md) | [指标数据](../../pilot/deepseek_v41_flash/20261028_semantic_alignment_v1/results_summary.json) | [打开目录](../../pilot/deepseek_v41_flash/20261028_semantic_alignment_v1/) |
| DeepSeek：RAG / 完整解析文本 / 整页图片输入对照 | 同一5篇 / 28 Gold | [完整报告](../../pilot/deepseek_v41_flash/20261029_input_ablation/report.md) | [指标数据](../../pilot/deepseek_v41_flash/20261029_input_ablation/evaluation/report.json) | [打开目录](../../pilot/deepseek_v41_flash/20261029_input_ablation/) |
| DeepSeek：五篇子集 Fully 增强 Prompt 对照 | 同一5篇 / 28 Gold | [完整报告](../../pilot/deepseek_v41_flash/20261029_input_ablation_fully_semantic_v1/report.md) | [指标数据](../../pilot/deepseek_v41_flash/20261029_input_ablation_fully_semantic_v1/evaluation/comparison.json) | [打开目录](../../pilot/deepseek_v41_flash/20261029_input_ablation_fully_semantic_v1/) |

## 最近两组五篇子集实验

两组均固定 D19-1367.pdf、1901.10430.pdf、1808.08745.pdf、2020.emnlp-main.523.pdf、1911.09483.pdf，共28条Gold；排行榜为原27榜限定这五篇后保留的10榜、14个条目。

### 输入方式对照

目录：`pilot/deepseek_v41_flash/20261029_input_ablation/`。

| 文件/子目录 | 内容 |
|---|---|
| `report.md` | 实验设置、完整结果和主要案例 |
| `metrics.csv`、`per_paper_metrics.csv` | 汇总及逐篇数据 |
| `baseline_rag/merged/` | 复用的历史RAG抽取和Fully标准化结果 |
| `parsed_full/fully/merged/` | 完整解析文本抽取和标准化结果 |
| `page_images/fully/merged/` | 整页图片抽取和标准化结果 |
| `evaluation/report.json` | T/D/M/R IIM、TDM/TDMR P/R/F1、LR、PC、RC、RBO、AO |

### Fully 增强 Prompt 对照

目录：`pilot/deepseek_v41_flash/20261029_input_ablation_fully_semantic_v1/`。

复用上述三组抽取，仅迁移名称语义匹配要求到Fully；保持23/71/26固定候选和无匹配返回None。没有运行Partially或Cold Start。

| 文件/子目录 | 内容 |
|---|---|
| `report.md` | 原版→增强版完整指标和原因分析 |
| `metrics.csv`、`leaderboard_metrics.csv`、`per_paper_metrics.csv` | 完整指标与逐篇结果 |
| `baseline_rag/merged/`、`parsed_full/merged/`、`page_images/merged/` | 三组抽取副本及增强Fully输出 |
| `prompt_diff.txt`、`enhanced_prompt.txt`、`prompt_migration.json` | 具体Prompt变化与迁移规则 |
| `inspection/changed_records.json`、`inspection/field_response_pairs.csv` | 15条字段变化记录及144次新旧回答对照 |
| `evaluation/comparison.json` | 全部新旧P/R/F1、排行榜指标及差值 |

## 结果速查

以下为冻结报告中已经报告的TDMR F1（%），不同范围分开列示。

| 全量43篇设置 | 原Prompt | 增强Prompt |
|---|---:|---:|
| Sol Partially（第二阶段） | 39.95 | 66.40 |
| Sol Cold Start（三顺序第二阶段F1均值） | 30.02 | 50.53 |
| DeepSeek Partially（第二阶段） | 20.19 | 60.40 |
| DeepSeek Cold Start（三顺序第二阶段F1均值） | 10.74 | 51.18 |

全量Fully参考：Sol + LLM 77.97%，Sol + CS 65.07%；DeepSeek + LLM 75.75%，DeepSeek + CS 59.82%。Sol + LLM记录已在上次归档中。

| 五篇输入组 | 原Fully | 增强Fully |
|---|---:|---:|
| RAG | 71.85 | 69.71 |
| 完整解析文本 | 82.83 | 68.21 |
| 整页图片 | 83.31 | 83.08 |

Partially/Cold主表采用第二阶段，第一阶段产物与指标一并保留。各次F1按官方Macro P/R计算；三顺序均值另行汇总。历史报告的阶段命名保持原文，使用时按所需阶段读取相应JSON。

## 归档范围与验证

- [发布文件与SHA256清单](../../publications/20261030/manifest.json)、[复制核验](../../publications/20261030/verification.json)。
- 所有入选实验文件保持原始字节。未重新运行模型或评价，也未更改本地冻结实验。
- 密钥、认证文件、模型权重、运行环境、PDF、整页渲染图片及含整页图片base64的请求载荷保留本地。图片来源、页数、哈希和抽取响应等追溯记录已归档；省略路径见发布清单。
- Llama-2、未完成的共同16篇任务、未完成诊断及已取消的子集Partially/Cold准备不纳入此次发布。
- 历史绝对路径和原始完整性清单保持不变；其中模型、环境和被排除资源的本地路径不代表GitHub上存在同名资源。

## 既有实验

[2026-10-24 完整结果汇总](../README.md)：GPT-4.1、Llama-3、AxCell以及Sol Fully LLM。
