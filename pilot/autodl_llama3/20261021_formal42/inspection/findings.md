# 实际错误与边界（离线诊断）

以下分类不修改预测。数值相同不证明语义对应；非Gold数值不自动等于Baseline混入。未据Gold重写名称、补全结果或选择更高分输出。

|配置|严格TDMR命中Gold行|格式失败Gold行|严格数值未出现|数值存在但含null|数值存在但名称/绑定不匹配|
|---|---:|---:|---:|---:|---:|
|fully_llm|32|15|186|15|11|
|fully_cs|28|15|186|0|30|
|partially_stage1|13|15|186|7|38|
|partially_stage2|25|15|186|7|26|

这些是以259条Gold逐行统计的辅助计数，不是官方Precision或Recall；同一预测值可能对应多个Gold值，不能当作一对一匹配总数。严格一对一辅助TDMR指标另存于evaluation。

## 可直接验证的现象

- 2105.03654.pdf：NON_EOS；原始响应保留，不进入标准化，固定42篇评价记空。
- 1901.10430.pdf：NON_UNIQUE_OR_INCOMPLETE_STRUCTURE；原始响应保留，不进入标准化，固定42篇评价记空。
- fully_llm：{'calls': 566, 'non_newline_prefix_author_sliced_anyway': 0, 'candidate_match_after_official_slice': 510, 'literal_None_after_slice': 44, 'would_only_match_after_extra_strip_not_applied': 0}；重复Prompt仍逐次真实调用，共90组；没有加入缓存。
- partially_stage1：{'calls': 470, 'non_newline_prefix_author_sliced_anyway': 0, 'candidate_match_after_official_slice': 412, 'literal_None_after_slice': 19, 'would_only_match_after_extra_strip_not_applied': 0}；重复Prompt仍逐次真实调用，共80组；没有加入缓存。
- partially_stage2：{'calls': 175, 'non_newline_prefix_author_sliced_anyway': 0, 'candidate_match_after_official_slice': 86, 'literal_None_after_slice': 0, 'would_only_match_after_extra_strip_not_applied': 0}；重复Prompt仍逐次真实调用，共32组；没有加入缓存。

## 代表性名称问题（按固定论文/Gold顺序取例，不筛选高分）

- {"paper_id": "2020.findings-emnlp.378.pdf", "gold_index": 0, "gold": {"Task": "Named Entity Recognition (NER)", "Dataset": "Ontonotes v5 - English", "Metric": "F1", "Result": 90.32}, "category": "RESULT_NOT_PRESENT_AS_STRICT_NUMBER", "predictions": []}
- {"paper_id": "2020.findings-emnlp.378.pdf", "gold_index": 1, "gold": {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-16 - English", "Metric": "F1", "Result": 55.14}, "category": "RESULT_NOT_PRESENT_AS_STRICT_NUMBER", "predictions": []}
- {"paper_id": "2020.findings-emnlp.378.pdf", "gold_index": 2, "gold": {"Task": "Named Entity Recognition (NER)", "Dataset": "WNUT-17 - English", "Metric": "F1", "Result": 50.68}, "category": "RESULT_NOT_PRESENT_AS_STRICT_NUMBER", "predictions": []}
- {"paper_id": "1910.13461.pdf", "gold_index": 21, "gold": {"Task": "Question Answering", "Dataset": "ELI5", "Metric": "ROGUE-1", "Result": 30.6}, "category": "VALUE_PRESENT_WITH_NORMALIZATION_NULL", "predictions": [{"index": 2, "extracted": {"Task": "ELI5", "Dataset": "Abstractive question answering", "Metric": "R1", "Result": "30.6"}, "normalized": {"Task": null, "Dataset": "SQuAD 1.1", "Metric": "ROGUE-1", "Result": "30.6"}}]}
- {"paper_id": "1603.01354.pdf", "gold_index": 3, "gold": {"Task": "Part-of-Speech (POS) Tagging", "Dataset": "Penn Treebank (PTB)", "Metric": "Accuracy", "Result": 97.55}, "category": "VALUE_PRESENT_WITH_NORMALIZATION_NULL", "predictions": [{"index": 0, "extracted": {"Task": "POS Tagging", "Dataset": "WSJ", "Metric": "Accuracy", "Result": "97.55"}, "normalized": {"Task": "Part-of-Speech (POS) Tagging", "Dataset": null, "Metric": "Accuracy", "Result": "97.55"}}]}
- {"paper_id": "1811.09242.pdf", "gold_index": 3, "gold": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-Score (F-S)", "Result": 62.9}, "category": "VALUE_PRESENT_WITH_NORMALIZATION_NULL", "predictions": [{"index": 0, "extracted": {"Task": "Word Sense Induction", "Dataset": "SemEval 2010", "Metric": "F-Score", "Result": 62.9}, "normalized": {"Task": "Word Sense Induction", "Dataset": null, "Metric": "F-Score (F-S)", "Result": "62.9"}}]}
- {"paper_id": "1910.13461.pdf", "gold_index": 11, "gold": {"Task": "Paraphrase Detection", "Dataset": "MRPC", "Metric": "Accuracy", "Result": 90.4}, "category": "VALUE_PRESENT_NAMES_OR_BINDING_UNRESOLVED", "predictions": [{"index": 0, "extracted": {"Task": "SQuAD", "Dataset": "Wikipedia paragraphs", "Metric": "F1", "Result": "90.4"}, "normalized": {"Task": "Question Answering", "Dataset": "WikiHow", "Metric": "F1", "Result": "90.4"}}]}
- {"paper_id": "1910.13461.pdf", "gold_index": 13, "gold": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-1", "Result": 44.16}, "category": "VALUE_PRESENT_NAMES_OR_BINDING_UNRESOLVED", "predictions": [{"index": 5, "extracted": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "R2", "Result": "44.16"}, "normalized": {"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROGUE-2", "Result": "44.16"}}]}
- {"paper_id": "1910.13461.pdf", "gold_index": 19, "gold": {"Task": "Dialogue Generation", "Dataset": "ConvAI2", "Metric": "F1", "Result": 20.72}, "category": "VALUE_PRESENT_NAMES_OR_BINDING_UNRESOLVED", "predictions": [{"index": 4, "extracted": {"Task": "ConvAI2", "Dataset": "Dialogue response generation", "Metric": "Valid F1", "Result": "20.72"}, "normalized": {"Task": "Dialogue Generation", "Dataset": "Dailydialog (DyDA)", "Metric": "F1", "Result": "20.72"}}]}

## 解读限制

Baseline混入、Dev/Test混淆、表格读取错误需要回查论文证据。当前自动诊断只将它们列为待人工核对候选，不将所有额外数值强行归因于Baseline。
官方Result采用双向字符串包含关系，可能出现不同数值的匹配；严格整串Decimal检查单独报告。百分号、区间、±值不在严格辅助指标里被自动修正。
官方元组评价保留重复项的影响；同论文同TDM的排行榜构建使用后写覆盖。报告保留大于1的原版分数（若有），不裁剪、不去重改分。
