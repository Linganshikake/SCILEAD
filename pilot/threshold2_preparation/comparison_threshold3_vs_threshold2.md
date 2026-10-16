# Threshold=3 与 Threshold=2 比较状态

本轮未获得可核验的作者 threshold=2 文件，未生成新的正式分数。下表只摘录冻结 threshold=3 结果；没有将诊断 62 组用作 Gold。

| 指标（0–1） | Fully LLM：旧 27 榜 | Fully CS：旧 27 榜 | threshold=2 |
|---|---:|---:|---|
| 目标榜数 | 27 | 27 | 未运行：数据 BLOCKED |
| Gold 榜内记录数 | 140 | 140 | 未运行：数据 BLOCKED |
| 精确 TDM 命中榜数 | 22 | 25 | 未运行：数据 BLOCKED |
| 有效数值非空榜数 | 20 | 24 | 未运行：数据 BLOCKED |
| LR：精确 TDM 命中率 | 0.814815 | 0.925926 | 未运行：数据 BLOCKED |
| 有效数值非空榜率 | 0.740741 | 0.888889 | 未运行：数据 BLOCKED |
| PC（官方） | 0.487125 | 0.631570 | 未运行：数据 BLOCKED |
| RC（官方） | 0.317989 | 0.411905 | 未运行：数据 BLOCKED |
| RBO（官方数值列表） | 0.247654 | 0.303420 | 未运行：数据 BLOCKED |
| AO（论文 ID） | 0.462500 | 0.522212 | 未运行：数据 BLOCKED |

旧指标来源及 SHA256 已保存到 threshold3_frozen_reference.json。Fully LLM 来源 leaderboard_eval_full43_uncapped/paper_metrics/leaderboard_metrics.json；CS 来源 full43_cs/leaderboard_evaluation/paper_metrics/leaderboard_metrics.json。本轮没有重新执行其评测。

本表按本轮要求把 LR 明确列为“标准 TDM 精确命中率”，并另列非空有效数值榜率。历史文件 conventions.LR_primary 曾把非空数值率作为主口径，这里不覆盖旧字段，只显式区分两种口径，避免同名误比。

共有 27 榜的原始 Gold 与诊断分组一致；冻结预测文件哈希未变。由于正式 threshold=2 评价未运行，逐榜得分一致性为 NOT_RUN，不冒称已复算通过。以后应在已核验新 Gold 下比较同 27 榜，发现差异时检查重复数值缩放、对象复用、排序及缓存。

全部 43 篇的预测与 tdm_annotations 未变；因此本轮没有改变 TDMR/IIM 的评价输入，也没有产生新的 TDMR/IIM 分数。改变排行榜评价集合不代表抽取能力变化。

## 后续必须继承的评价边界

- 使用未修改的 leaderboard_eval.py 和已审计的独立 CLI/AO 补充入口；每次从原始文件新读对象，避免再次缩放。
- Result 沿用官方清洗/缩放，同 paper/TDM 使用原输入顺序中最后一个可转换记录；不替换复合数值、不修正名称或语言方向。
- 排序方向沿用官方实现；AO 的数值并列按 paper_id 升序确定次序，保留并列论文。
- 空榜 AO 为 0；全部目标 Gold 榜都计入 Macro 分母。没有“预测少于两篇则删榜”的额外规则。
- RBO 使用官方去重数值排名和已安装 rbo=0.1.3 的原调用；AO 使用论文 ID。两者不互换名称。
- 新目标榜单中的转换/覆盖边界尚未运行检查，不能宣称与旧范围完全相同；后续逐榜保存原值、转换值和排名。

对照原论文 Table 15 时，本地模型是 GPT-4.1 固定快照，原文是 GPT-4 Turbo；同时必须披露数据版本、LR 两种口径、官方 RBO 与论文 ID AO 的差别。本轮不计算相对 Table 15 的性能差异。
