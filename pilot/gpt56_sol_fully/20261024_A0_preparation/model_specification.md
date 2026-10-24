# GPT-5.6 Sol模型规格

查询日期：2026-10-24。来源：[官方模型说明](https://developers.openai.com/api/docs/models/gpt-5.6-sol)。可离线读取的原始Markdown为`official_docs/model.md`，下载状态、日期与SHA256见`official_docs/retrieval_manifest.json`。

|项目|官方文档值|
|---|---|
|模型ID/默认snapshot标识|gpt-5.6-sol|
|上下文窗口|1,050,000 Tokens|
|最大输入|922,000 Tokens|
|最大输出|128,000 Tokens|
|推理强度|none、low、medium（默认）、high、xhigh、max|
|API|Chat Completions、Responses，亦支持Batch|
|输入/输出|文本、图像输入；文本输出|
|Structured Outputs|支持，但本baseline建议不启用额外schema约束|

页面只列出`gpt-5.6-sol`，未列出日期后缀快照。不得虚构日期版ID。`gpt-5.6`是官方路由到Sol的别名，本实验仍使用明确的`gpt-5.6-sol`。服务商同名请求是否映射到该官方模型、是否固定底层版本，目前不能从历史GPT-4.1记录证明；响应模型ID待另获授权的单篇试跑检查，即便字符串相同也不能独立证明底层版本锁定。

## 生成设置依据与边界

建议Extraction与Normalization统一固定medium；不做强度对比或中途调整。官方将medium列为默认；本轮选择默认中等推理以避免把模型基座对照变成强度调参。Responses建议standard模式，不启用pro、跨请求历史、previous_response_id或Agent功能。[Reasoning文档](https://developers.openai.com/api/docs/guides/reasoning)，副本`official_docs/reasoning.md`。

目标模型对temperature、seed的逐项兼容性在本次取得的模型专页中没有明确保证。通用API出现这些字段不代表目标模型在medium下接受它们。因此建议都不发送；do_sample是本地生成接口习惯参数，不在拟定HTTP请求中使用。不声称这三个字段均被官方模型明确禁止。

推理Token占用输出预算。官方Reasoning指南建议初次实验预留至少25,000 Tokens供推理与输出。结合历史可见输出最大值Extraction 996、Normalization 11，本轮提案统一给两阶段32,768个总输出Tokens；它是本轮工程建议，不是官方必需值，也不是预期每次都会消费的数量。预算仍可能耗尽，必须记录incomplete/length，不补写或自动扩大预算。

服务商上下文、默认输出限制、参数转发、速率与真实模型均待确认。上述官方规格不能直接作为9527.codes的服务承诺。
