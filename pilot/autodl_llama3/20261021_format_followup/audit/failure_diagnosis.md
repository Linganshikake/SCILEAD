# 两篇原始响应的结构诊断

只读输入来自formal42真实response.txt，并与合并raw_output.json逐字一致；Token数和末尾ID来自complete.json。原正式文件在protected_before.json中受保护。

## 1901.10430.pdf

输入3330 Tokens，输出355 Tokens，EOS，最后Token128009。不是长度截断。

|组|零基字符区间（左闭右开）|完整记录数|Result类型|
|---|---|---:|---|
|Machine Translation|[74,440)|4|float|
|Language Modeling|[465,762)|3|float|
|Summarization|[783,1062)|3|float|

三组分别由Markdown任务标题分组。每条记录已有完整Task、Dataset、Metric、Result，不需标题补字段；标题与组内Task一致，没有作废、修正版或候选替代说明。重复键、嵌套数组、未闭合字符串检查均通过。按V2原顺序合并10条，每个对象的原始文本片段保留，包括26.60等数值表示和重复项；没有重跑Extraction。

## 2105.03654.pdf

输入2639 Tokens，输出正好1024 Tokens，finish_reason=length_or_other，最后Token55410而非EOS。原始文本包含31个完整对象；第32个对象从字符2556开始，在Metric键字符串内部结束。结尾为：

```text
  {"Task": "NER", "Dataset": "E-commerce", "Metric
```

因此缺失内容不仅是数组结束符，还包括未完成键、值及对象。V2不补写、不删除半条尾记录、不将前31条作为完整预测。逐对象边界和异常位置见audit/papers/2105.03654/parse.json。

预算诊断上下文算术：2639+2048=4687≤8192。远程执行前还会使用相同tokenizer、Prompt和add_special_tokens=False复核。只允许一次新Extraction，单独存放token2048_diagnostic。

## Token记录的实际限制

旧正式调用保存了原始文本、输入/输出Token总数及最后Token ID，没有完整生成ID数组。本轮不会伪造“历史原始IDs”：可从固定tokenizer重建，并核对总数、末ID与文本round-trip；比较结果标明重建来源。2048诊断则直接捕获真实input_ids和generated_ids。文本前缀比较另行保存，不把重建ID比较当作原始张量的严格证明。
