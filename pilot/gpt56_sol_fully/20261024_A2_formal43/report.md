# GPT-5.6 Sol Fully LLM A2正式实验报告


状态：QUEUE_FINISHED_WITH_FORMAT_FAILURES。完成 41/43篇，Gold覆盖 282/295；Extraction有效 41 篇，共 322 条预测。

请求 696 次（Extraction 43，Normalization 653），HTTP200 696；已报告输入 367682、输出 37077、总Tokens 404759；缺失用量 0 次。A1的14次请求不计入。

停止原因：null。无自动重发、无模型切换、无Prompt修改。

参数：gpt-5.6-sol、medium、max_completion_tokens=32768、stream=false；不传temperature/seed/tools/response_format。原始证据与候选顺序保持不变。

本轮传输来自直连TLS校验连接。中转站底层身份、推理参数执行和全局隐藏限制不能仅凭响应标签证明。102次用量出现推理Token口径差异，原样保留，不重复叠加，不核算费用。


## 官方评价


仅完成子集的指标不能称为43篇全量。

|指标|P|R|F1|
|---|---:|---:|---:|
|Task|0.981030|0.985095|0.983058|
|Dataset|0.972974|0.976023|0.974496|
|Metric|0.964656|0.975610|0.970102|
|Result|0.770681|0.832789|0.800532|
|TDM|0.953086|0.960459|0.956758|
|TDMR|0.743005|0.805444|0.772965|

## 逐篇状态


|论文|Gold|抽取状态|记录数|标准化状态|标准化请求完成/计划|null字段|
|---|---:|---|---:|---|---|---:|
|2020.findings-emnlp.378.pdf|6|COMPLETE|6|COMPLETE|12/12|1|
|1709.04109.pdf|3|COMPLETE|3|COMPLETE|8/8|0|
|D18-1279.pdf|6|COMPLETE|6|COMPLETE|17/17|0|
|2020.emnlp-main.523.pdf|11|COMPLETE|15|COMPLETE|31/31|0|
|1905.03197.pdf|26|COMPLETE|38|COMPLETE|64/64|4|
|1702.02098.pdf|2|COMPLETE|2|COMPLETE|4/4|0|
|2020.emnlp-main.152.pdf|6|COMPLETE|6|COMPLETE|13/13|0|
|2105.03654.pdf|7|COMPLETE|8|COMPLETE|21/21|0|
|1910.13461.pdf|25|COMPLETE|25|COMPLETE|41/41|0|
|D18-1105.pdf|2|COMPLETE|2|COMPLETE|4/4|0|
|1703.06345.pdf|5|COMPLETE|5|COMPLETE|13/13|0|
|1903.07785.pdf|11|COMPLETE|12|COMPLETE|24/24|2|
|1912.08777.pdf|36|COMPLETE|36|COMPLETE|75/75|0|
|1711.05568.pdf|2|COMPLETE|2|COMPLETE|4/4|0|
|wang19f.pdf|5|COMPLETE|8|COMPLETE|20/20|0|
|128538.pdf|4|COMPLETE|4|COMPLETE|11/11|0|
|1511.08308.pdf|2|COMPLETE|2|COMPLETE|6/6|0|
|1603.01354.pdf|4|COMPLETE|2|COMPLETE|5/5|0|
|1804.09849.pdf|2|COMPLETE|2|COMPLETE|6/6|0|
|1806.03489.pdf|2|COMPLETE|2|COMPLETE|4/4|0|
|1808.08745.pdf|3|COMPLETE|5|COMPLETE|12/12|0|
|1809.08370.pdf|8|COMPLETE|8|COMPLETE|17/17|0|
|1811.05021.pdf|2|COMPLETE|2|COMPLETE|3/3|0|
|1811.09242.pdf|6|COMPLETE|9|COMPLETE|19/19|2|
|1812.09471.pdf|6|FORMAT_FAILED|0|PENDING|0/None|None|
|1812.10235.pdf|8|COMPLETE|8|COMPLETE|18/18|0|
|1901.10430.pdf|8|COMPLETE|9|COMPLETE|9/9|0|
|1905.12598.pdf|6|COMPLETE|6|COMPLETE|4/4|0|
|1906.05012.pdf|3|COMPLETE|3|COMPLETE|9/9|0|
|1907.00390.pdf|6|COMPLETE|6|COMPLETE|13/13|0|
|1908.08345.pdf|9|COMPLETE|15|COMPLETE|36/36|0|
|1909.02188.pdf|6|COMPLETE|6|COMPLETE|10/10|0|
|1911.09483.pdf|4|COMPLETE|4|COMPLETE|8/8|0|
|1911.10390.pdf|8|COMPLETE|12|COMPLETE|22/22|2|
|2001.04063.pdf|9|COMPLETE|12|COMPLETE|32/32|0|
|2002.03184.pdf|7|FORMAT_FAILED|0|PENDING|0/None|None|
|2008.07772.pdf|6|COMPLETE|8|COMPLETE|12/12|0|
|2203.16804.pdf|9|COMPLETE|9|COMPLETE|24/24|0|
|C18-1139.pdf|4|COMPLETE|4|COMPLETE|10/10|0|
|D18-1523.pdf|3|COMPLETE|3|COMPLETE|2/2|0|
|D19-1367.pdf|2|COMPLETE|2|COMPLETE|2/2|0|
|K19-1036.pdf|3|COMPLETE|3|COMPLETE|6/6|0|
|N19-1373.pdf|2|COMPLETE|2|COMPLETE|2/2|0|

## 完整性与恢复


2238个受保护文件及A2准备文件全部保持原哈希。逐请求attempt.lock/状态/原始响应防止重复发送；失败或UNKNOWN不能自动重发。输入重建、PDF解析和检索均未执行。

原始与标准化结果位于papers/及merged/；官方评价和逐条独立数值诊断位于evaluation/。未匹配预测不能仅据Gold缺席断言Baseline混入，需原文进一步确认。

批次墙钟耗时1663.05秒，进程峰值RSS 47.42MiB。

全部请求结束后的秘密扫描尝试读取本进程锁文件，Windows返回PermissionError；已复现根因并修复独立编排层（不扫描固定单字节锁）。4项回归测试通过，仅离线补齐汇总，新增请求0。实际执行脚本快照及哈希保留，官方源码未改。

两篇格式失败分别为1812.09471.pdf（6条）和2002.03184.pdf（7条）；均为完整JSON数组且stop，仅Result为浮点数。本轮严格字符串协议未允许转换，保持原始响应，未进行Llama实验的兼容转换或自动恢复。


## 官方Leaderboard指标


```json

{
  "gold_results": {
    "Paper Coverage": 0.9172398589065257,
    "Result Coverage": 0.7588624338624338,
    "RBO": 0.7708039484031547
  }
}

```

完整27榜。通过独立Namespace适配官方CLI参数命名不一致，评价函数未改动。RBO基于官方数值列表，非论文ID排名。


## 固定43篇分母评价（失败为空预测，仅评价副本）


实际成功41/43篇。失败论文原响应不变，只在独立fixed43评价输入中置空；不将其标为模型有效空输出或完整成功。

|指标|P|R|F1|
|---|---:|---:|---:|
|Task|0.935401|0.939276|0.937334|
|Dataset|0.927719|0.930626|0.929171|
|Metric|0.919789|0.930233|0.924981|
|Result|0.734836|0.794055|0.763298|
|TDM|0.908756|0.915787|0.912258|
|TDMR|0.708446|0.767981|0.737013|

## 与冻结GPT-4.1 Fully基线的描述性对照


|指标|GPT-4.1 F1|GPT-5.6 Sol F1|差值|
|---|---:|---:|---:|
|Task|0.966900|0.937334|-0.029566|
|Dataset|0.800714|0.929171|+0.128457|
|Metric|0.853224|0.924981|+0.071757|
|Result|0.703841|0.763298|+0.059458|
|TDM|0.612160|0.912258|+0.300098|
|TDMR|0.421578|0.737013|+0.315435|
两阶段均更换基座，并使用medium reasoning及32768输出预算，不能把差异单独归因于Extraction或模型强弱；未进行Prompt优化或按得分选择重跑。



## Result表示差异的补充诊断

严格Decimal诊断有155条TDMR匹配，但其余条目不都代表数值错误：带%或±标准差的原始Result不能直接解析成单个Decimal。独立诊断识别主数值及后缀，不进行单位换算、不改原预测、不替换官方评价。

|诊断|Gold条数|
|---|---:|
|SIMPLE_NUMERIC_TDM_MATCH|155|
|CENTRAL_VALUE_PRESENT_WITH_NULL_OR_TDM_MISMATCH|12|
|SAME_TDM_DIFFERENT_OR_UNINTERPRETABLE_VALUE|65|
|DECORATED_RESULT_SAME_CENTRAL_VALUE_AND_TDM|45|
|NO_MATCHING_TDM_OR_CENTRAL_VALUE|5|

例如2020.emnlp-main.152.pdf的6个结果含百分号，主数值与Gold一致；D18-1279.pdf的结果保留±标准差。1709.04109.pdf的97.53±0.03与Gold97.59仍不相等，不能因格式解释而认定数值正确。详细逐条记录见inspection/result_representation_audit.json。
