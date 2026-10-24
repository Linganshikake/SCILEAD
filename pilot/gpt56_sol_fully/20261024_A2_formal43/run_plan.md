# A2正式批量运行准备（未启动）

43篇固定顺序采用A0清单原顺序；不得依据单篇表现重排、删样或修改方法。A1只作验证，不复用为正式结果，因此计划43次新Extraction；标准化约542次、总约585次仅历史参照，真实请求清单待新预测产生后逐字段展开。

启动门槛：用户明确批准A2；从服务商控制台/客服或用户确认获得当前可用状态，不发送额外探测。A1的14次成功只能证明当时该接口接受参数；不能证明通道已永久恢复、隐藏预算或固定上游快照。43篇实际服务商上下文是否合规目前均未知，不虚构上限；应先确认限制或由用户明确接受按服务端结果判定。已知超过限制的样本标BLOCKED_CONTEXT，不截断。不要套用Llama或旧30k规则。

执行前核验输入/配置哈希、目录独立性、Python依赖、可用内存和磁盘；一次一篇，无模型本地加载。输入Token离线重算为o200k_base代理值，正式API返回后逐请求补充真实usage；不得把代理数称为精确目标模型Token。

每篇Extraction先将不含凭据的请求正文和唯一attempt编号落盘，再标SENDING并只发一次。保留HTTP、原始响应、response model、finish_reason、request ID、usage及耗时，原始响应保存成功后再更新checkpoint。验证完整JSON数组、四字段、字符串Result和stop；空数组可为VALID_EMPTY，异常JSON不得修复或部分接受。

只有完整有效Extraction才展开该篇Normalization。使用A0冻结候选字符串及顺序、官方逐字段/逐记录顺序和Prompt；精确命中跳过；重复待映射字段独立请求，不缓存合并；Result原样保留；候选外返回null。记录每条映射及原始返回，不能因为低分、null或内容错误重跑。

HTTP500/get_channel_failed、429、超时或UNKNOWN：保存状态，停止调度以排查共享服务状态；不重发、不换模型、不改Prompt。格式失败仅停止该篇下游，保留其他结果。断点恢复只跳过哈希一致的成功阶段；SENDING/UNKNOWN/FAILED不能自动重发，须明确有限恢复授权。未开始的位置保持PENDING。恢复按请求位置而非内容缓存。

请求日志字段由resource_and_request_status.csv给出；未来每次请求扩展一行，绝不能将当前43篇占位行当成43次已发送请求。checkpoint当前全部待授权，normalization_jobs_materialized为0。

每篇输出目录papers/<paper_id>/，保存extraction/request.json、response_raw.txt、response.json、state.json、output.json及normalization/requests/<position>/、normalized_output.json。合并和正式评价仅在已批准运行完成后执行；失败覆盖率明示，原Gold、官方评价重复处理和Macro口径不变。

本轮没有API执行器或自动启动任务，没有读凭据、联网、模型生成、重新检索、PDF解析或配置升级。准备结束暂停。
