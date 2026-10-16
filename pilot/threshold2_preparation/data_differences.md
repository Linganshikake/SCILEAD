# Gold 版本与分组差异

状态：BLOCKED。以下均比较原始标注，未进行排行榜 Result 清洗、乘除 100、排序或模型输出修正。

| 范围 | 唯一 TDM / 榜数 | 原始记录数 | 不同论文数 | 性质 |
|---|---:|---:|---:|---|
| 完整冻结 Gold | 141 | 295 | 43 | 官方附件中的原始标注 |
| 作者独立提供的榜单 | 27 | 140 | 43 | 当前正式 threshold=3 评价输入 |
| 完整 Gold 按至少 3 个不同 paper_id 分组 | 33 | 158 | 43 | 数量/差异诊断 |
| 完整 Gold 按至少 2 个不同 paper_id 分组 | 62 | 216 | 43 | 数量/差异诊断，禁止正式评分 |
| 独立作者 threshold=2 文件 | 未找到 | 未核验 | 未核验 | BLOCKED |

## 33 / 27：定位到六个分组，未解释作者排除原因

完整 Gold 中满足至少三篇条件的 33 个 TDM，包含全部作者 27 榜。额外六组如下，每组都是同三篇论文，合计 18 条原始记录。

| Task | Dataset | Metric | 1905.03197.pdf | 1910.13461.pdf | 1903.07785.pdf |
|---|---|---|---:|---:|---:|
| Linguistic Acceptability | CoLA | Matthew's Correlation Coefficient (MCC) | 61.1 | 62.8 | 53.1 |
| Sentiment Analysis | SST-2 | Accuracy | 94.5 | 96.6 | 94.6 |
| Natural Language Inference (NLI) | MNLI-m | Accuracy | 87.0 | 89.9 | 84.3 |
| Natural Language Inference (NLI) | MNLI-mm | Accuracy | 85.9 | 90.1 | 83.8 |
| Natural Language Inference (NLI) | QNLI | Accuracy | 92.7 | 94.9 | 89.8 |
| Natural Language Inference (NLI) | RTE | Accuracy | 70.9 | 87.0 | 63.7 |

因此 33=27+6、158=140+18。没有证据表明应删除这些记录或合并名称；本轮未这样操作。六组的定位解释了数量差额，不能解释作者历史选择原因。

## 141 / 138：仍未解决

原论文 Table 1（本地参考文本 page-03.txt:55）报告 138 unique TDM；冻结 JSON、本次重新取得的官方 Data JSON、原始 TSV 都得到 141。
TDM 按三个原始字符串构成 tuple，未 strip、改大小写、改拼写或合并别名。没有找到另一版 138-TDM 标注，不能指定三组进行人为合并。

## 62 的来源边界

诊断分组有 16 个 Task、62 个 TDM、216 条原始记录、43 篇论文。其相对作者 27 榜增加 35 组/76 条记录，即 29 个两篇组和上述六个三篇组。
数量与原论文 threshold=2 描述相符，但来源只是本轮从当前 Gold 重建；不能据此宣称获得作者正式 62 榜。
诊断文件为 diagnostics/current_gold_ge2_NOT_FOR_SCORING.json，带禁止评分标识，并保留所有原始行和 paper_id。

## 共有 27 榜与结构检查

全部 27 榜的精确 TDM、论文成员、原始 Result 与完整 Gold 及诊断 62 组完全一致。没有未知论文 ID、重复榜单、重复 JSON 对象键、重复 Gold 行或同 paper/TDM 多 Result 冲突。
尚未进行 threshold=2 正式评价，所以不存在可报告的“共有榜单新旧逐榜得分比较”；这里只核实原始成员与数值。

## 官方附件版本比较

本次 Data ZIP 与本地原始 ZIP SHA256 完全相同。其 JSON 标注与冻结标注逐条相同：新增/删除/修改记录均为 0，名称集合仍为 23 Task、71 Dataset、26 Metric。
TSV 与 JSON 的结构化记录也一致；比较时仅将 TSV 数值 Result 解码为数字，原文件不变，名称字符串不变。具体差异数组和哈希保存在 data_audit.json、source_manifest.json、diagnostics/tsv_vs_json.json。
