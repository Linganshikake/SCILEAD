# 统一配置 Baseline 与断点续跑

本目录是独立实验版本；旧 full43、subset5、subset15、subset15_uncapped_retry 均只读保留。manifest 的 source_* 路径索引历史数据，*_reused 指示每个阶段是否复用。长论文抽取文件复制到新目录，仅为官方标准化脚本的相对输出路径服务；复制不会产生 API 请求，哈希一致并按历史用量计一次。

执行入口（scilead Python）：`pilot/scripts/uniform43_run.py --run`。只执行明确选定的 API 阶段；绝不调用 PDF 预处理或向量检索。完整阶段跳过，已完成的单次请求仅可在同序号、同消息下重放本地响应；重复名称仍独立调用。未完成/失败 attempt 拒绝自动重试，非法或截断输出停止该篇后续阶段。不可再次使用 --prepare 覆盖实验。

离线评测：`uniform43_evaluate.py`；逐条检查：`inspect_full43.py --run-root D:\C++\SCILEAD\pilot\full43_uncapped`；核验与对照：`uniform43_finalize.py`。重新生成汇总时先执行评测，再检查、核验。最终 file_integrity_sha256.json 是汇总写入结束后的文件清单，重新汇总后应再生成。

源码、依赖、Gold、历史文件哈希与新旧输入比较均在 verification.json / preserved_existing_sha256.json / environment.json / input_preflight.json 中。实际脱敏请求和响应在每个阶段 api_calls；候选名称及顺序在 normalization/candidate_sets.json，逐条计划在 request_plan.json。

API Key 仅由已验证适配器在运行时从指定安全配置读取，不进入本目录记录。服务商账单不可用，Token Usage 不等同于实际货币账单。
