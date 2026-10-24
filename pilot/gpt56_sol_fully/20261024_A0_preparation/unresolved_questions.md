# A0待确认事项

1. 9527.codes是否支持gpt-5.6-sol，是否锁定底层版本，返回model标识如何对应；官方ID不能证明转发后模型身份。
2. 该通道是否接受Chat Completions的reasoning_effort=medium和max_completion_tokens=32768，是否存在更小服务端默认限制。
3. 账户/令牌额度、模型分组与上游通道是否由控制台或客服核实；get_channel_failed根因仍未知。
4. 目标模型的实际tokenizer/Chat开销、请求限制与参数兼容，需资料及获准单篇试跑确认。
5. 用户验收A0并决定是否按提案进入A1。首篇建议2020.emnlp-main.152.pdf；无试跑授权前不生成请求。

费用不再要求审批或详细报告；无需重新提供密钥。A0的零模型调用边界不变。
