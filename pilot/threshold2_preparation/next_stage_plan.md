# 后续阶段准备（未授权在本轮执行）

当前状态 BLOCKED。next_stage_configs.json 的 enabled=false，verified_threshold2_path/sha256 与 shared_masked_subset_path/sha256 均为 null；不会把诊断重建清单自动填入输入。

## 解锁材料

需要作者发布或作者提供的 threshold=2 榜单文件，以及可追溯下载页/版本/说明；结构应包含精确 Task、Dataset、Metric 和 paper_id→Result 映射。还需解释其与冻结 Gold、当前 27 榜的任何实质差异。
获得后原样另存并校验哈希、重复键、不同 paper_id 阈值、成员和数值。不能用“正好 62”代替来源核验。现有 141/138 与六个额外三篇组的历史差异应持续披露，不人工修正。

## 复用关系

| 分支/阶段 | 可复用 | 后续动作 |
|---|---|---|
| Zero-shot Extraction | 43 篇/284 条原始预测及全部 source_documents | 不重新抽取、解析、索引或检索 |
| Fully LLM | 现有名称标准化输出 | 数据 READY 后仅离线评价新榜单集合 |
| Fully CS | 现有名称标准化输出 | 数据 READY 后仅离线评价新榜单集合 |
| Partially stage1 | 不直接复用旧动态标准化 | 新 mask 与初始名称集合确定后重新运行 |
| Partially stage2 | 不复用旧 27 榜对齐结果 | 对新 stage1 使用完整新目标榜单进行对齐 |
| Cold Start 三轮 stage1 | 可复用，已核验顺序/种子类型/原输出 | 保持原记录顺序、Result 和证据 |
| Cold Start 三轮 stage2 | 不复用旧 27 榜对齐结果 | 对各自已冻结 stage1 使用完整新目标榜单 |
| Few-shot | 不参与本轮阈值对照 | 继续独立冻结 |

## Partially masking 的原始依赖

原函数 tdm_llm_masked_normalization.py:13–57 根据输入榜单顺序累计各 Task 榜数，从排除最多/最少榜数 Task 后的候选列表，用整数 masking seed=0 抽取 round(Task数/3) 个 Task。
同时 mask 这些 Task 榜中的 Dataset；Task 或 Dataset 满足 mask 的榜组成 masked 子集。初始 Task/Dataset 名称取完整 Gold 排除 mask 的集合，Metric 取完整 Gold。
数据 READY 后才调用原函数，保留作者文件顺序、PYTHONHASHSEED=0，保存候选列表及其顺序、Masked Task/Dataset、masked 榜和三类初始名称集合。使用适当末尾路径分隔符，输出仅写入新目录。
不沿用旧 Masked 10 榜，不预设新 masked 数量，也不为了匹配论文数字更改抽样。当前没有运行 masking_preview。

## Cold Start stage1 独立性

原函数 cold_start=True 分支仅把目标榜单写入 sidecar，三类初始候选集合始终为空；stage1 后续输入只由抽取结果、当前候选状态、Prompt 和论文顺序决定。
main 中 gold_leaderboards 只在读文件和调用 sample_tdms 两处出现（66、81 行），不进入后续模型请求。三轮原 initial_labels 均为空、原 stage1 重放验证 PASS，当前逐篇 Result 字符串、证据和记录数量仍与原始 284 条抽取一致。

| 轮次 | cold_start_seed | 类型 | stage1 SHA256 | 复用结论 |
|---|---|---|---|---|
| order_default | null | NoneType | `d4df0c1983fac7ae1a423aab723839dddca44d59fc01a77b6476c031f0fa1997` | 可复用 stage1；重跑新目标 stage2 |
| order_0 | "0" | str | `ffc32067cbaf77b164548fac5a5a3eb9528d920e5ffb9e1d87c85e56f4a064ac` | 可复用 stage1；重跑新目标 stage2 |
| order_42 | "42" | str | `74b7c2b297799a393c648a138b381a6b9d2ec9a5c25dc299d977ca7293d5e48b` | 可复用 stage1；重跑新目标 stage2 |

使用原 dict key 顺序或 random.sample 重算后的顺序与各轮 paper_order.json 完全一致。字符串 "0"、"42" 不能改成整数；生成模型 seed 仍为整数 0。
未来可以重新生成描述新目标的 sidecar，但不把 sidecar 差异解释为需要重跑 stage1，也不改写原实验目录。

## Stage2 与共同 Masked 评价

leaderboard_llm_normalization.py:17–23 从完整目标榜单构造 TDM 候选集合，所以新目标会影响 stage2 请求。不能把旧 27 榜 stage2 当作 threshold=2 结果。
Stage2 候选是完整新目标集合，不是 masked 子集。后续 Partially 和三轮 Cold Start 都同时评全目标与同一个“新 Partially mask”子集；不能沿用旧 10 榜或把 Cold sidecar 中的全部目标榜当成共同 Masked 评价范围。
保留现有 GPT-4.1 快照、temperature=0、整数 seed=0、不传输出上限、原 Prompt/动态逻辑和无重试适配；不手工映射、不新增缓存。
本轮仅保存依赖与配置，新增模型/API 推理调用为 0，下一阶段尚未启动。
