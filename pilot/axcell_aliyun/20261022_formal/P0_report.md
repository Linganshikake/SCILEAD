# P0：环境与范围确认

阶段 0 已执行；**等待用户确认，未进入阶段 1**。

| 项目 | 结果 |
|---|---|
| 当前资源 | 8 vCPU；可用 RAM 最低 28.95 GiB；磁盘余量 56.16 GiB |
| 环境 | 依赖无变更，pip check 通过，固定镜像和 7 个模型/词表文件完整 |
| 服务 | Docker active；运行容器 0；ES 保持停止，本阶段未启动 |
| 输入 | 39 篇 TeX 完整性通过，对应 283 Gold；31 篇直接 arXiv、8 篇书目映射 |
| 缺失 | 128538.pdf、D19-1367.pdf、C18-1139.pdf、D18-1105.pdf，共 12 Gold |
| 作者 36 篇 | 具体成员及 TeX 版本仍 UNVERIFIED；实时官方元数据访问超时 |
| 服务器已存 TeX | 单篇验证的一篇；其余 38 篇待后续授权再传送 |
| 单篇结果 | 原 2 条预测/证据保留；Recall/F1 绑定与实体数量误抽错误未修正 |
| 系统/费用 | 不需当前配置修改或新增云资源；本阶段模型生成和付费 API 均 0 |

建议待确认口径：保留作者范围未核实标记，使用“当前可用 TeX 39 篇”作为独立复现范围提案；与 GPT-4.1 按 39 篇、与 Llama-3/GPT-4.1 按共同 38 篇另行比较。尚未批准正式评价，所有 input_manifest 行的 `formal_evaluation_allowed` 仍为 False。

文件：`input_manifest.csv`、`experiment_manifest.json`、`environment_preflight.md`、`resource_preflight.md`、`scope_and_gold_audit.md`。后续阶段状态见 `stage_gate.json`。

请确认 P0 的范围与环境记录；确认后只进入 P1 单篇回归，不会自动进入 P2 批量解析。若必须严格取得作者 36 篇名单才继续，则保持范围阻塞并等待可靠名单。
