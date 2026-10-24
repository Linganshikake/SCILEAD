# 9527.codes接口兼容审计

日期：2026-10-24。结论：**PROVIDER_UNVERIFIED**。仅核查本地配置、历史请求和官方公开文档；没有访问中转站模型、账户、账单、健康检查或生成接口。

## 本地配置与凭据

用户指定`SCILEAD_small_test/.env`可读取，已确认存在密钥；只检查存在性，未显示、复制、写入日志或Git。该文件配置的BASE_URL是`https://9527.codes`，不带`/v1`。旧独立适配器硬编码`https://9527.codes/v1`并调用Chat Completions，因此不应把裸域名直接当成OpenAI SDK的已验证base_url。

后续提案使用`https://9527.codes/v1/chat/completions`这一历史路由形式；这只是根据历史配置提出的路径，不证明其支持gpt-5.6-sol。未修改.env、旧适配器或模型配置。源码内旧GPT分支标签只选择原Prompt角色，不作为实际请求模型。

## 证据与不能外推的事项

|问题|本次可证明的内容|
|---|---|
|既有成功接口|GPT-4.1的43次Extraction＋542次Normalization已保存HTTP200/stop及精确模型ID|
|目标模型是否支持|无已保存的gpt-5.6-sol成功请求或服务商规格；未知|
|目标实际响应model|无，禁止用模型探测补证|
|固定快照映射|服务商未提供可核验映射；待单篇试跑与客服资料验证|
|Responses路由|官方支持；9527是否支持未知，本轮未调用|
|推理与输出参数转发|未知，旧GPT-4.1成功不能证明新参数兼容|
|服务端默认上限、RPM/TPM|未知|
|额度/令牌独立限额/分组|没有控制台或客服确认记录|
|失败是否计费|未知，没有账单明细|

最新统一标准化任务记录共有34次尝试、24次成功、10次失败；失败含早期代理超时和后续HTTP500 `get_channel_failed`。2026-10-24两个单独补发曾成功，随后批次仍出现相同通道错误，不能认定服务已恢复。

服务商返回消息为“此账号限额或者号池负载过大,请重试”。现有证据不能区分额度与通道池负载根因，也没有取得明确服务商处理说明。所有历史请求均保留，A0没有重试它们。逐条来源见`provider_history_audit.json`。

## 接口差异及提案

主提案沿用单轮Chat Completions，保持原system/user消息与逐字段处理：`messages`、`reasoning_effort=medium`、`max_completion_tokens=32768`；读取choices.message.content、finish_reason及usage。无需Agent功能或工具。

Responses作为文档对照：使用`input`、`reasoning.effort`、`max_output_tokens`；检查response.status、incomplete_details和输出消息文本，而不是假定存在finish_reason。设置truncation=disabled，禁止自动压缩输入。不传previous_response_id，不附之前的推理或其他论文内容。切换接口必须在试跑前确认并冻结，不能错误后自动回退。

官方Responses创建参考的完整副本为`official_docs/responses.md`；[Chat Completions参考](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)已通过网页读取，Markdown下载返回404，如实记录。通用字段支持不构成服务商或具体模型兼容保证。

现有SDK/适配器版本见`installed_adapter_versions.json`。旧适配器固定模型、seed、temperature，不可直接拿来执行新实验。A0只提出独立适配要求，没有升级依赖、修改旧脚本或生成可自动运行的付费入口。

## 后续需通过控制台或客服确认

1. gpt-5.6-sol是否开放、映射到哪个底层模型及是否固定版本；返回model规则。
2. 账户、令牌与模型分组权限，及get_channel_failed的明确根因和恢复状态。
3. Chat Completions的reasoning_effort、max_completion_tokens实际支持及服务器默认上限。
4. 上下文、最大输出和频率限制；空响应、超时与HTTP500的账单规则。

确认不必暴露密钥。A1试跑仍需用户明确授权，当前不发请求。
