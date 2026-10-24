# 原始预测的来源检查

仅依据保留的原始表格/单元格、列头和行名记录现象，不计算Gold命中、IIM、ETM或Leaderboard指标，不修正任何预测。两条历史错误及新增维度误作分数均保留；明确标为“待核实”的项目不能等同于已确认错误。这里不是完整错误率评价。

| 论文 | 类别 | 原始模型/指标/分数 | 单元格来源 | 结论 |
|---|---|---|---|---|
| 1511.08308.pdf | METRIC_CELL_BINDING | BLSTM-CNN + emb + lex / F1 / 91.85 | 1511.08308v5/table_06.csv/6.2 | 已核实：列为Recall，原预测为F1 |
| 1511.08308.pdf | COUNT_AS_SCORE | Test set size (# entities) / F1 / 4696.0 | 1511.08308v5/table_11.csv/2.4 | 已核实：Test set size (# entities)，4,696为实体数 |
| 1603.01354.pdf | DIMENSION_AS_SCORE | Word2Vec / F1 / 300.0 | 1603.01354v5/table_06.csv/3.1 | 已核实：原表列为Dimension，Word2Vec的300是向量维度；同一行NER列为84.91。原预测F1=300.0完整保留 |
| 2020.findings-emnlp.378.pdf | DATASET_COLUMN_BINDING_CANDIDATE | Ours Ours / F1 / 96.62 | 2010.15466v1/table_05.csv/14.6 | 来源列头为RE，原预测数据集为ontontoes chinese v5；数值96.62与单元格一致，数据集绑定需结合正文复核，不作人工修正 |

VALID_EMPTY表示官方流程成功结束且最终过滤后无记录。不能根据空输出重新生成，也不能用空预测冒充程序异常。FAILED/BLOCKED单列于extraction_status.csv。
原始来源全部见prediction_source_inspection.json；中间候选和筛选原因见remote_results/papers/*/raw_outputs/events与pipeline_events.json。源CSV的坐标从0开始。模型列随原始记录保留，不依据其名称手工剔除Baseline。
是否混入其他工作Baseline、是否存在Dev/Test或跨数据集绑定问题，需要进一步结合论文正文核查；本轮未用Gold筛选或指导输出。不能声称这里已全面确认每条预测的科学正确性。

## 9篇有效空预测的原过滤轨迹

| 论文 | 最终阶段输入候选数 | 原日志汇总的剔除原因 |
|---|---:|---|
| 1811.09242.pdf | 125 | confidence 0.79 < 0.8: 125 |
| 1912.08777.pdf | 320 | empty-model-type: 305；model-competing: 3；confidence 0.79 < 0.8: 12 |
| 1808.08745.pdf | 97 | empty-model-type: 40；confidence 0.79 < 0.8: 57 |
| wang19f.pdf | 91 | confidence 0.79 < 0.8: 91 |
| 1906.05012.pdf | 108 | confidence 0.79 < 0.8: 78；empty-model-type: 30 |
| 1905.12598.pdf | 39 | confidence 0.79 < 0.8: 39 |
| K19-1036.pdf | 37 | confidence 0.79 < 0.8: 37 |
| 1811.05021.pdf | 12 | confidence 0.79 < 0.8: 12 |
| 2020.emnlp-main.152.pdf | 93 | confidence 0.79 < 0.8: 93 |

剔除原因直接来自原版pipeline_events，未改变0.8/0.85阈值或model-competing处理。长论文1912.08777.pdf已完成全部流程，空结果来自原筛选，而非再次被保护中断。
