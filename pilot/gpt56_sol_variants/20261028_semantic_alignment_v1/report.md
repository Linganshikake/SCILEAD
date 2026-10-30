# GPT-5.6 Sol：补充名称对齐 Prompt 后的完整复跑结果

已完成 Partially 与三个 Cold Start 顺序的两个阶段。每组覆盖 43 篇论文、295 条 Gold、27 个排行榜，复用原有 335 条 Sol Extraction。基线为 20261024 的 Sol 原版 Prompt 结果。

## 主要结果：第二阶段

| 设置 | 原版 TDMR F1/% | 补充后 TDMR F1/% | 变化/百分点 |
|---|---:|---:|---:|
| Partially | 39.95 | **66.40** | **+26.45** |
| Cold Start 默认顺序 | 28.38 | **49.70** | **+21.32** |
| Cold Start 字符串种子 0 | 25.50 | **51.47** | **+25.98** |
| Cold Start 字符串种子 42 | 36.18 | **50.41** | **+14.23** |
| Cold Start 三顺序均值 | 30.02 | **50.53** | **+20.51** |

Cold Start 三顺序 TDMR F1 的样本标准差由 5.53 降至 0.89 个百分点。

## 全部主要指标

下表均为百分数，格式为原版 → 补充后。IIM、TDM 和 TDMR 使用 F1；Cold 栏为三个顺序各自指标的算术平均。

| 指标 | Partially | Cold Start 三顺序均值 |
|---|---:|---:|
| Task IIM | 69.36 → 92.69 | 58.35 → 76.14 |
| Dataset IIM | 77.09 → 91.18 | 68.79 → 79.42 |
| Metric IIM | 97.15 → 95.59 | 60.00 → 76.98 |
| Result IIM | 80.60 → 80.60 | 80.60 → 80.60 |
| TDM Exact Match | 46.78 → 83.02 | 37.64 → 61.49 |
| TDMR Exact Match | 39.95 → 66.40 | 30.02 → 50.53 |
| LR | 70.37 → 96.30 | 88.89 → 96.30 |
| 有效非空榜率 | 70.37 → 96.30 | 88.89 → 96.30 |
| PC | 47.56 → 93.79 | 57.30 → 94.20 |
| RC | 41.94 → 72.95 | 45.88 → 73.57 |
| RBO（数值排名） | 35.40 → 69.68 | 49.09 → 70.69 |
| AO（论文ID排名） | 41.70 → 89.89 | 59.65 → 90.65 |

各顺序的官方 P/R 按论文 Macro 聚合，F1=2PR/(P+R)。完整 P/R/F1、第一阶段诊断、逐篇指标及三顺序标准差见[完整指标报告](reporting/report.md)。

## 结果说明

1. **名称对齐是此前损失的重要来源。** 保持 Extraction 的 335 条记录与所有 Result 不变后，Partially 的 Task IIM F1 从 69.36% 提高至 92.69%，Dataset 从 77.09% 提高至 91.18%。例如 1906.05012.pdf 的摘要任务从 Abstractive sentence summarization 对齐为 Summarization，原来失配的三元组得以命中。
2. **Cold Start 的最终收益集中体现在第二阶段对齐后的结果。** 三顺序第一阶段 TDMR F1 均值为 1.38% → 1.12%，最终第二阶段为 30.02% → 50.53%。本轮同时补充两个阶段 Prompt，且第一阶段回答改变动态候选集，比较反映整套补充规则及其候选集演变的联合效果。
3. **指标粒度仍可能被错误合并。** Partially 的 Metric IIM F1 从 97.15% 降至 95.59%。4 篇论文中有 7 条记录将 Sent-Accuracy 或 Overall-Accuracy 改成 Accuracy；ATIS 88.64% 与 SNIPS 92.96% 的句级准确率限定因此丢失。详见[七条回退记录及 Gold 对照](inspection/metric_granularity_cases.md)。
4. **保留更细的数据集描述也会降低精确匹配分数。** 1901.10430.pdf 的 WMT 2016 English-German (newstest2014) 被保留，原版曾映射为 WMT’14 EN-DE，该篇 TDMR F1 从 94.12% 降至 58.82%。完整字段、模型响应与逐篇变化见[事件案例](reporting/alignment_examples.json)。
5. **原有数值问题继续保留。** Result IIM F1 均保持 80.60%；本轮改动只作用于名称标准化，原始数值、证据和记录顺序通过一致性核验。

## 执行与完整性

- 成功标准化逻辑请求：3,523；客户端请求尝试：3,529。
- 6 次失败尝试（HTTP524×3、额度403×2、连接中断×1）均保留；各获准补发一次后成功，自动重试为0。
- 已知输入 Tokens：2,064,765；输出：77,282；总计：2,142,047。6 次失败未返回用量。
- 请求时间窗口约 49.01 分钟，包含授权与接口等待：北京时间2026-10-28 23:42:58至2026-10-29 00:31:58。
- 全部3523个有效响应均为 gpt-5.6-sol、HTTP200、finish_reason=stop。
- 两处补充 Prompt 与 DeepSeek 已批准版本逐字节一致；其余 Sol 参数保持 medium、max_completion_tokens=32768、stream=false。
- 83项核心保护哈希无变化；评价核查139项来源文件、383项来源/产物文件无变化，官方历史指标精确复算一致。
- 所有新增结果在本独立目录；已完成全部授权分支，已停止请求。

## 文件入口

- [完整指标与案例报告](reporting/report.md)
- [逐篇对照 CSV](analysis/comparison_final/per_paper_differences.csv)
- [机器可读完整比较](analysis/comparison_final/comparison.json)
- [请求与 Token 汇总](reporting/api_usage_summary.json)
- [逐请求审计](reporting/request_audit.csv)
- [完整性验证](reporting/verification.json)
- [Prompt 改动原文](prompt_diff.txt)
- [分支输出索引](reporting/output_index.json)
