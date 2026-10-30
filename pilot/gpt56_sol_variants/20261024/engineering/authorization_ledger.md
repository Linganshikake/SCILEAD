# 本轮恢复授权记录

以下授权来自本次对话，均在对应额外请求发送之前获得。每个请求位置只允许额外一次，成功响应不重发；原失败state和response保留，成功恢复存于`retry_1/`。

|位置|原失败|用户确认|结果|
|---|---|---|---|
|cold_0 / stage1 / 0118|HTTP 524|允许仅补发一次，接受可能重复计费|HTTP 200，stop|
|partially / stage1 / 0510|HTTP 403，insufficient_user_quota|充值后继续，并允许各补发一次；已经到账，可以继续|HTTP 200，stop|
|cold_42 / stage2 / 0140|HTTP 403，insufficient_user_quota|充值后继续，并允许各补发一次；已经到账，可以继续|HTTP 200，stop|
|cold_42 / stage2 / 0227|HTTP 524|允许仅补发一次，接受可能重复计费|HTTP 200，stop|

对应`retry_authorization.json`保存请求SHA256、原始状态、允许次数和scope。初始中文备注经PowerShell标准输入传递时出现编码丢失，本表补充可读授权原文；未更改那些原始记录中的请求哈希、scope或执行状态。最终逐项检查scope与实际目录一致、重发payload逐字相同、每个位置仅一次额外请求。

Windows文件占用恢复只重试本地相同内容的写入，不属于HTTP请求重试。所有失败响应及未知用量保留，不将其计为零用量。
