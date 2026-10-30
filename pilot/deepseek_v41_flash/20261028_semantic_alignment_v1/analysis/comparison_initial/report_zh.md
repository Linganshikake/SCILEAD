# DeepSeek 语义对齐 Prompt 改进变体：离线比较

状态：**INCOMPLETE**；生成时间：2026-10-28T14:14:37.177119+00:00。
这是已授权的 Prompt 改进变体，不代表原始基线。阶段完成仅由实际 summary、文件及 SHA-256、完整离线评估验证；本报告不认证全局运行或用量完成。

方法变更（主任务提供）：仅 masked-normalization、leaderboard-normalization 的 system Prompt 增加通用语义匹配规则；默认 MetricPrompt、候选项精确接受规则不变。Cold observer 沿用复制前缀，仅调整 Prompt 断言绑定。具体 Prompt/运行完整性、API 用量及来源案例由主任务单独审计。

Extraction 完全复用基线；每个可比较结果均为 43 篇论文、295 条预测、295 条 Gold、全部 27 个榜单。stage2 为主要结果，stage1 仅作诊断。

## Stage2 元组指标

数值为百分比，单元格为 P / R / F1。F1 由官方逐论文宏平均 P/R 求调和平均，不是论文 F1 的平均。

| Case / 版本 | Task IIM | Dataset IIM | Metric IIM | Result IIM | TDM Exact Match | TDMR Exact Match |
|---|---|---|---|---|---|---|
| partially_stage2 / 原始基线 | 41.02 / 47.13 / 43.87 | 51.84 / 54.83 / 53.29 | 94.98 / 95.14 / 95.06 | 81.63 / 80.89 / 81.26 | 25.25 / 23.82 / 24.51 | 20.92 / 19.51 / 20.19 |
| partially_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |
| cold_default_stage2 / 原始基线 | 35.60 / 41.69 / 38.41 | 41.71 / 45.60 / 43.57 | 45.63 / 48.20 / 46.88 | 81.63 / 80.89 / 81.26 | 14.10 / 12.99 / 13.52 | 12.06 / 10.76 / 11.38 |
| cold_default_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |
| cold_0_stage2 / 原始基线 | 33.13 / 39.15 / 35.89 | 41.81 / 43.40 / 42.59 | 45.74 / 47.11 / 46.41 | 81.63 / 80.89 / 81.26 | 13.11 / 11.85 / 12.45 | 11.85 / 10.40 / 11.08 |
| cold_0_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |
| cold_42_stage2 / 原始基线 | 33.95 / 38.01 / 35.86 | 41.23 / 43.34 / 42.26 | 42.53 / 41.22 / 41.86 | 81.63 / 80.89 / 81.26 | 11.66 / 10.48 / 11.04 | 10.50 / 9.12 / 9.76 |
| cold_42_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |

## Stage2 榜单指标

LR 为精确 TDM 命中率；finite nonempty 额外要求可转换的有限数值。PC/RC 保持官方定义；RBO 排列去重数值，AO 排列论文 ID。空榜单保留在 27 个榜单分母内。

| Case / 版本 | LR | finite nonempty | PC | RC | RBO 数值 | AO 论文ID |
|---|---|---|---|---|---|---|
| partially_stage2 / 原始基线 | 77.78 | 77.78 | 30.05 | 22.55 | 31.07 | 36.11 |
| partially_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |
| cold_default_stage2 / 原始基线 | 29.63 | 29.63 | 12.07 | 10.59 | 8.02 | 9.95 |
| cold_default_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |
| cold_0_stage2 / 原始基线 | 29.63 | 29.63 | 11.68 | 9.52 | 6.87 | 6.87 |
| cold_0_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |
| cold_42_stage2 / 原始基线 | 25.93 | 25.93 | 11.93 | 10.45 | 20.78 | 24.49 |
| cold_42_stage2 / Prompt 改进变体 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 | 待完成 |

## Cold 三顺序

仅三个顺序全部完成时计算均值与样本标准差（ddof=1）。下表为 stage2 榜单；两个阶段所有元组 P/R/F1、榜单指标和配对差值的 mean/sampleSD 见 JSON。

| 版本 | LR | finite nonempty | PC | RC | RBO | AO |
|---|---|---|---|---|---|---|
| baseline | 28.40 ± 2.14 | 28.40 ± 2.14 | 11.90 ± 0.20 | 10.19 ± 0.58 | 11.89 ± 7.72 | 13.77 ± 9.41 |
| prompt_improvement_variant | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 |
| paired_delta | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 | 待三个顺序完成 |

## 待完成项与使用边界

- prompt_improvement_variant / partially_stage1: PENDING；Missing stage files
- prompt_improvement_variant / partially_stage2: PENDING；Missing stage files
- prompt_improvement_variant / cold_default_stage1: PENDING；Missing stage files
- prompt_improvement_variant / cold_default_stage2: PENDING；Missing stage files
- prompt_improvement_variant / cold_0_stage1: PENDING；Missing stage files
- prompt_improvement_variant / cold_0_stage2: PENDING；Missing stage files
- prompt_improvement_variant / cold_42_stage1: PENDING；Missing stage files
- prompt_improvement_variant / cold_42_stage2: PENDING；Missing stage files

逐论文差异见 per_paper_differences.csv；Δ=变体−基线，缺失值留空，不能解释为零。comparison.csv 包含两个阶段全部指标；comparison.json 保留全精度结果及路径。
Sol / GPT-4.1 及论文已发表数值只作为基线 comparison_final/comparison.json 的不可变历史引用，保留原有范围与定义；没有重新运行这些模型，不与本变体混作同一实验。
当前结果不足时不作“提升”判断；完整结果也只描述本次固定 Extraction 和三种顺序，不外推统计显著性。
