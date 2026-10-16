# 单篇 TDMR 逐条错误分析

所有 Gold 的 Task 均为 `Named Entity Recognition (NER)`，Metric 均为 `F1`。原始预测 Task 均为 `Named Entity Recognition`，Metric 均为 `F1`；标准化后 Task 均正确，Metric 原样保留。

| Gold 序号 | Gold Task / Dataset / Metric / Result | 原始抽取四字段 | 标准化后四字段 | Result 严格相等 | 完整匹配 | 错误类型 |
|---|---|---|---|---|---|---|
| 1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 90.32} | {"Task": "Named Entity Recognition", "Dataset": "ON5E", "Metric": "F1", "Result": "90.32"} | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "90.32"} | 是 | 否 | Result 正确但标准化失败 |
| 2 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 55.14} | {"Task": "Named Entity Recognition", "Dataset": "WN16", "Metric": "F1", "Result": "55.14"} | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "55.14"} | 是 | 否 | Result 正确但标准化失败 |
| 3 | {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 50.68} | {"Task": "Named Entity Recognition", "Dataset": "WN17", "Metric": "F1", "Result": "50.68"} | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "50.68"} | 是 | 否 | Result 正确但标准化失败 |
| 4 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v4 - Chinese", "Metric": "F1", "Result": 81.18} | {"Task": "Named Entity Recognition", "Dataset": "ON4C", "Metric": "F1", "Result": "81.18"} | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "81.18"} | 是 | 否 | Result 正确但标准化失败 |
| 5 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Resume - Chinese", "Metric": "F1", "Result": 96.62} | {"Task": "Named Entity Recognition", "Dataset": "RE", "Metric": "F1", "Result": "96.62"} | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "96.62"} | 是 | 否 | Result 正确但标准化失败 |
| 6 | {"Task": "Named Entity Recognition (NER)", "Dataset": "Weibo - Chinese", "Metric": "F1", "Result": 69.78} | {"Task": "Named Entity Recognition", "Dataset": "WE", "Metric": "F1", "Result": "69.78"} | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "69.78"} | 是 | 否 | Result 正确但标准化失败 |

## 原因与边界

- 六个数据集请求的服务端原始回答都是字符串 `None`；均 HTTP 200、finish_reason=stop、输出 1 Token，未触及 15 Tokens 上限。官方集合成员检查将其转换为 JSON null。
- 对照实际请求：标准集合包含各正确全称，但模型输入仅有集合和缩写，没有论文中缩写定义。缺少语境可能影响映射；这是解释性推断，不能证明模型内部原因。
- 抽取阶段的六个数值及缩写与 Gold 的语义对应正确，未发现 Baseline 混入；名称仍需标准化，并非原始字符串精确匹配。标准化阶段成功对齐 Task，但未能消解六个 Dataset 缩写。
- 未发现缺失或额外数值，也未发现把某个 Result 绑定到另一个有效 Dataset 的错误；这里的失败是 Dataset 变成 null。
- 官方模糊数值匹配与严格数值相等在本篇没有差异。Result IIM=1 不代表 TDMR 正确；Dataset 缺失使全部六条完整匹配失败。
- 所有模型回答原样保留。没有提高输出上限、补充上下文、手动映射、修改 Prompt 或额外请求。