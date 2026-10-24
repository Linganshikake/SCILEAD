# GPT-5.6 Sol 单篇试跑

论文：2020.emnlp-main.152.pdf。状态：SINGLE_PAPER_COMPLETE。

实际请求 14 次，HTTP 200 14 次；抽取 6 条，完成标准化 6 条。

已报告 Tokens：6605；未返回用量的请求 0 次，不能推断未计费。

错误：null。A0文件完整性：True。

仅使用单篇冻结证据；未重做检索、未调用其他模型、未修改Prompt、未修复预测；未开始全量实验。

请求参数与响应均保存在各请求目录。reasoning_effort实际服务端执行情况、底层模型身份无法仅由HTTP成功独立证明。

## 最终独立核验

14次请求均HTTP200、finish_reason=stop，响应模型均为gpt-5.6-sol；13个标准化返回均在候选集合内。2013个冻结来源文件哈希未变。

接口输入Tokens 6206、输出Tokens 399、合计6605；约80.14秒。Extraction实际输入2345，离线代理估算2346。

Extraction用量存在口径差异：顶层reasoning_tokens=0，嵌套billing_usage/openai_usage/output_tokens_details/reasoning_tokens=158；原始字段均保留，不重复叠加推理Token，不声称平台账单已核对。响应中还有缓存写入统计，未主动配置缓存或据此计算费用。

所有Task标准化为Intent Detection and Slot Filling。以下为真实标准化结果，尚未开展正式Gold评价，候选内匹配不等于语义正确。

| Dataset | Metric | Result |
|---|---|---|
| ATIS | F1 | 96.24 |
| ATIS | Accuracy | 97.74 |
| ATIS | Sent-Accuracy | 88.64 |
| SNIPS | F1 | 97.05 |
| SNIPS | Accuracy | 99.04 |
| SNIPS | Sent-Accuracy | 92.96 |

本轮只验证单篇Extraction和Fully Normalization。API接受参数不等于证明中转站完全按该参数执行；固定上游快照和隐藏预算仍无法独立核实。完成后暂停，未启动43篇批量。
