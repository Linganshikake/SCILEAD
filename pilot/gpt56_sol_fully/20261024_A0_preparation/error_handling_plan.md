# 失败处理提案

A0零模型请求。后续单篇试跑须先明确授权并冻结接口和参数。默认串行，SDK自动重试0；原始请求状态、响应、request ID、usage先落盘再更新检查点。

|情形|处理|
|---|---|
|HTTP429|保存Retry-After及错误；暂停，不自动重发，核对限流与账单后按明确恢复授权处理|
|HTTP500/get_channel_failed|保存原始错误，停止相关分支；请服务商核对额度/分组/通道，不切换模型|
|连接/读取超时、状态未知|标为UNKNOWN，不假定未计费；先查request ID、日志与账单，禁止盲目重发|
|空响应|记录HTTP、模型ID、状态、usage，标为失败，不能作为有效空数组|
|非法JSON/缺字段/Result类型异常|保留原文，停止该篇下游；不补全、拼接、修正、截取合法片段或重生成挑结果|
|达到输出预算|Chat finish_reason=length，或Responses incomplete/max_output_tokens；记录可见与推理用量，不自动增加预算或续写|
|响应模型标识不匹配|暂停，核查服务商映射；未确认别名不得当成已锁定模型|
|工具调用/拒绝/内容过滤|不执行工具；独立记录失败/拒绝，不将stop当作成功的唯一依据|
|费用/额度提示|按用户最新要求不做费用审批；仍记录usage与额度错误，触发服务拒绝时停止，绝不自动充值或增购|

仅在明确授权后才能对失败位置补发一次；成功检查点同输入哈希直接复用，重复字段仍按原方法独立请求。请求量偏离历史585参照时报告实际原因，不能自动删记录以贴合估算。Normalization实际总数由新的有效Extraction计算并冻结，不把历史请求清单套用到新预测。

Chat成功需HTTP200、模型ID符合已确认映射、finish_reason=stop、正文非空及完整JSON数组/字段验证；Responses需status=completed、无incomplete_details/错误、模型符合映射并校验完整输出内容。官方Normalization只接受候选中的精确原始名称，候选外即null，不去掉额外解释以提高分数。

所有输入不主动截断；Responses提案truncation=disabled。不传历史对话、previous_response_id、工具、搜索、自动压缩或额外Gold。预算或格式失败需要另做记录和协议决策，不在正式批次中悄悄调整。
