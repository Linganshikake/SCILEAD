# SCILEAD Llama-3 格式恢复与预算诊断报告

|论文|原失败原因|是否恢复|规则|新Extraction|有效记录数|归属|
|---|---|---|---|---:|---:|---|
|1901.10430.pdf|正常EOS但三个独立数组|是|V2完整多数组按序合并|0|10|V2主结果|
|2105.03654.pdf|1024上限，截断在第32条Metric键内|V2不恢复|不补写、不截尾|0|0|V2仍计空预测|
|2105.03654.pdf|独立2048预算诊断|True|新响应接受冻结V2检查|1|49|仅token2048_diagnostic|

V2为41/42篇格式有效，281条TDMR；原40篇输出文本和记录逐字不变。有效论文Gold覆盖252/259；评价固定42篇259 Gold。1912.08777.pdf保持BLOCKED，未处理。

## 实验流程与结果

19项解析边界测试通过；先冻结规则/代码哈希，再执行下游和评分。完整原始记录片段、字符偏移、类型及每篇规则命中见audit/papers。
Fully/CS仅处理恢复输入，原40篇不变；Partially按原序从头离线重建，按严格状态匹配复用。完整元组P/R/F1和排行榜对照见[comparison_v1_v2.md](../format_v2/comparison_v1_v2.md)。

|设置|V1 TDMR F1|V2 TDMR F1|差（百分点）|
|---|---:|---:|---:|
|fully_llm|27.247805|28.042767|+0.794962|
|fully_cs|24.644786|25.703469|+1.058684|
|partially_stage1|10.124184|10.919211|+0.795027|
|partially_stage2|22.042476|22.837789|+0.795314|

## 复用、调用与资源

|阶段|严格匹配复用请求|新增生成|
|---|---:|---:|
|fully_llm|566|13|
|partially_stage1|470|13|
|partially_stage2|175|3|
另有1211次历史响应离线重放用于重建位置和状态索引，不属于模型调用。全轮新增本地模型生成169次，其中Extraction 1次、Normalization 168次；付费API为0。输入60,866、输出2,771 Tokens。
实际新增纯生成时间360.136秒；各阶段墙钟及历史CS缓存失败保留在remote_snapshot/workflow_complete.json与cs_repair_complete.json。

## 工程问题与边界

CS首次运行因隔离缓存目录未暴露固定revision自定义代码而失败，发生在新增映射前。修复仅复制两份已校验代码到本轮离线缓存并显式设置缓存路径，模型权重、版本、CPU FP32及Top-1逻辑不变。原日志保留；没有重复已成功的CS论文。
Partially新增行未改变后续响应时，以完整请求/候选状态核验为依据，不能仅凭名称相同复用。该事实及全部原40篇对照见downstream_change_audit.json。
2048诊断的停止状态、完整性和Token前缀证据见[diagnostic_report.md](../token2048_diagnostic/diagnostic_report.md)。不把其输出纳入主结果，不启动Partially预算重跑。
官方字符串包含匹配、重复计数及排行榜后写覆盖全部保留；严格数值一对一指标只是辅助诊断，不裁剪原版Recall。

## 完整性与交付

最终完整性、脱敏、环境、调用计数和传输核验见verification.json；原formal42、官方源码、Prompt、Gold与冻结证据保持受保护。
本地：D:/C++/SCILEAD/pilot/autodl_llama3/20261021_format_followup。
远程：/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup；执行原始文件在根目录，最终报告在delivery/。
未启动其他模型或新实验；任务模型由子进程结束释放，服务器未关机。
