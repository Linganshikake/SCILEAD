# 单篇2048输出预算诊断

这是独立预算诊断，不是V2原1024预算的格式修复。仅执行一次Extraction，未混入V2主结果。
输入2639，输出1593 Tokens；停止原因eos；V2结构有效=True；记录数=49。
生成耗时163.758秒，GPU allocated峰值46.973GiB。
唯一允许的生成参数变化为max_new_tokens 1024→2048；真实请求JSON与旧请求逐字段核对。
旧文本由固定tokenizer重建：长度匹配=True；末ID匹配=True；decode round-trip=True。
新实际Token IDs与旧重建IDs的最长共同前缀=1024；前1024一致=True；新文本含完整旧文本前缀=True。
历史没有保存完整生成IDs，因此此ID比较不能称为“两个实际历史张量完全一致”。新IDs为直接捕获，文本前缀另有独立核验。

|单篇设置|指标|P/R/F1（%）|
|---|---|---|
|fully_llm|Task IIM|100.00 / 100.00 / 100.00|
|fully_llm|Dataset IIM|100.00 / 100.00 / 100.00|
|fully_llm|Metric IIM|100.00 / 100.00 / 100.00|
|fully_llm|Result IIM|8.51 / 57.14 / 14.81|
|fully_llm|TDM|100.00 / 100.00 / 100.00|
|fully_llm|TDMR|6.12 / 42.86 / 10.71|
|fully_cs|Task IIM|100.00 / 100.00 / 100.00|
|fully_cs|Dataset IIM|100.00 / 100.00 / 100.00|
|fully_cs|Metric IIM|100.00 / 100.00 / 100.00|
|fully_cs|Result IIM|8.51 / 57.14 / 14.81|
|fully_cs|TDM|100.00 / 100.00 / 100.00|
|fully_cs|TDMR|6.12 / 42.86 / 10.71|

## 新增内容核对

原输出有31个完整对象和第32条的残缺前半段；新生成保留前31个对象的原始文本，完成第32条，随后又生成17条，总计49条。输出较旧上限多569个Tokens（含EOS）。逐条原文和分类保存于record_extension.json，没有拼接新旧响应。

结构完整不等于抽取正确：独立单篇评价的Result IIM F1仅14.81%，TDMR F1为10.71%；未据此筛选、删除或重跑任何记录。
