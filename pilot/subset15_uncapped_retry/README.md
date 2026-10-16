# SCILEAD 当前运行入口

当前累计完成 15/15 篇，覆盖 153 条 Gold。`pilot/current_run.json` 指向本目录。十四篇结果直接复用，仅对未完成论文进行一次用户授权的重新抽取并完成标准化。旧文件和历史费用均保留。

后续实验统一设置保存在 `D:\C++\SCILEAD\pilot\experiment_settings.json`：输入 Token 不设客户端门限，Extraction 和 Normalization 均不发送 max_tokens / max_completion_tokens；检查实际 finish_reason 是否为 length，并检查 JSON/字段有效性。仍不自动重试。

批处理入口 `run_scilead_subset.py` 已使用 `scilead_api.py`。已完成请求保持历史参数记录，不因设置变化重新运行。服务商自身仍可能有上下文、输出或超时限制，按实际响应记录。

后续获得执行授权后，以本目录为 source，通过 `extend_scilead_manifest.py` 创建独立 subset43 清单；再用原预处理和上述统一 API 入口执行剩余论文。本轮没有执行剩余 28 篇。

评价读取未经修改的官方 tdm_eval.py；F1 是官方聚合 P/R 的调和平均。完整指标见 evaluation/metrics_with_f1.json，使用量见 api_usage_summary.json。历史截断请求的费用仍计入累计数。
