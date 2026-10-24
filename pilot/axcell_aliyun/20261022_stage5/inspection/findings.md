# AxCell错误记录（不修复预测）

标准化123次成功HTTP请求，84个回答精确属于候选集合，39个回答为原始字符串None并按官方规则变为null：Task4、Dataset17、Metric18。另72字段无需模型直接保留。API成功不表示语义标准化正确；null不按网络失败重试。

| 原始记录 | 来源单元格 | 原Result | 已核实错误类型 | 标准化后原样保留 |
|---|---|---|---|---|
| 1511.08308.pdf#001 | 1511.08308v5/table_06.csv/6.2 | 91.85 | METRIC_CELL_BINDING_RECALL_AS_F1 | {"Task": "Named Entity Recognition (NER)", "Dataset": "CoNLL-2003 - English", "Metric": "F1", "Result": "91.85"} |
| 1511.08308.pdf#002 | 1511.08308v5/table_11.csv/2.4 | 4696.0 | ENTITY_COUNT_AS_SCORE | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "4696.0"} |
| 1603.01354.pdf#002 | 1603.01354v5/table_06.csv/3.1 | 300.0 | EMBEDDING_DIMENSION_AS_SCORE | {"Task": "Named Entity Recognition (NER)", "Dataset": null, "Metric": "F1", "Result": "300.0"} |

三例都属于AxCell原始抽取/绑定错误，标准化不读取表格上下文、不纠正Result或Metric语义。不存在根据Gold筛除错误样本。

严格逐Gold诊断共248条：{"RESULT_MISSING_OR_VALUE_SCALE_ERROR": 217, "STRICT_TDMR_MATCH": 11, "NUMERIC_MATCH_WITH_NULL_LABEL": 15, "NUMERIC_MATCH_LABEL_OR_BINDING_MISMATCH": 5}。217条没有任何严格相等数值候选，仅能归为“遗漏、值错误或比例/格式差异”，不能进一步断言全部是抽取遗漏。15条有相等数值但候选出现null字段，5条有相等数值但标签/绑定未匹配；这些是对照分类，不自动证明唯一错误环节。11条通过严格TDMR一对一匹配。

官方字符串包含与严格相等不同的两对均在1809.08370.pdf：96.61对96.6，95.02对95.0。官方分数完整保留，严格诊断另报。官方TDMR F1=10.6283%，严格一对一F1=9.7786%。

其他现象：原始模型名含Oracle (Intent)、without transfer、Joint等变体的记录均保留，不按名称过滤。是否属于其他工作Baseline或Dev/Test混淆需逐论文正文复核，本轮不能仅据名称下结论。正文/表格输入未变，不开展修正规则或改进实验。
