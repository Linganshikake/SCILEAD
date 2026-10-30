# Partially 第二阶段：指标粒度回退实例

同一批 Extraction 保持不变。4 篇论文的 Metric IIM F1 各下降 0.20，涉及下列 7 条指标名变化。原版官方总体 Metric IIM F1 从 97.1494% 下降至 95.5908%。

| 论文 | 记录序号（从1开始） | Result（保持原样） | 原版 Prompt 后 Metric | 补充 Prompt 后 Metric | 同数值 Gold 的 Metric |
|---|---:|---|---|---|---|
| 2020.emnlp-main.152.pdf | 3 | 88.64% | Sent-Accuracy | Accuracy | Sent-Accuracy |
| 2020.emnlp-main.152.pdf | 6 | 92.96% | Sent-Accuracy | Accuracy | Sent-Accuracy |
| 1812.09471.pdf | 6 | 0.834 | Overall-Accuracy | Accuracy | Overall-Accuracy |
| 1907.00390.pdf | 3 | 86.90 | Sent-Accuracy | Accuracy | Sent-Accuracy |
| 1907.00390.pdf | 6 | 80.57 | Sent-Accuracy | Accuracy | Sent-Accuracy |
| 1909.02188.pdf | 3 | 92.9 | Overall-Accuracy | Accuracy | 未匹配到相同数值 |
| 1909.02188.pdf | 6 | 88.6 | Overall-Accuracy | Accuracy | 未匹配到相同数值 |

例如 2020.emnlp-main.152.pdf 的 ATIS 88.64% 和 SNIPS 92.96% 在 Gold 中均为 Sent-Accuracy；新版第二阶段将它们改为 Accuracy。名称更统一，却丢失了句级准确率与一般准确率的区分。

1909.02188.pdf 的两个数值未命中该论文 Gold 的同数值条目；它们同时带有既存的抽取数值问题，表中保留原数值，不作修正。

本分析只读取完成后的预测与 Gold，用于定位 Metric 指标下降，不改变模型输出或官方评分。详细字段、Gold 对照与来源哈希见 metric_granularity_cases.json。
