# SCILEAD实验A — GPT-5.6 Sol Fully LLM A0

本目录是2026-10-24的正式A0交付：43篇、295 Gold TDMR、27榜，目标模型gpt-5.6-sol，计划服务商9527.codes。Extraction与Fully LLM Normalization均换用目标模型，其余原版流程保持。

**A0资料与输入准备完成；PROVIDER_UNVERIFIED；真实模型API调用0。** 不允许直接运行单篇测试、模型探测或历史请求重试。下一阶段是用户验收并明确授权后的单篇A1。

先读A0_summary.md、generation_config_proposal.json和provider_compatibility_audit.md。配置是提案，不是已经执行的请求参数。按最新指示不制作费用报告，只给请求量参考；官方价格文档作为资料保留。

核心文件：input_manifest.csv、input_token_estimate.csv、normalization_request_estimate.json、request_count_estimate.md、model_specification.md、official_pricing_reference.md、experiment_design.md、error_handling_plan.md、unresolved_questions.md、verification.json。

inputs/只有原样证据与两条Extraction消息；Gold计数仅位于审计manifest，不作为消息传入。official_docs/是公开文档离线副本，抓取没有认证也不是模型API请求。scripts均为离线核验或公开文档下载，没有模型调用入口。

相邻a0_20261024是收到完整后半段要求前的草稿，保留不覆盖；以本目录最终交付为准。此前统一GPT-4.1标准化中断任务没有继续运行。
