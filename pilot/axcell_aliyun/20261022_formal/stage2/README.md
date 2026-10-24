# AxCell 阶段2：解析检查点

授权仅限本阶段，完成后停在 P2。没有模型抽取、ES、GPT 或评价。

远端目录：`/root/scilead/axcell/runs/20261022_formal/stage2/`

本地目录：`D:\C++\SCILEAD\pilot\axcell_aliyun\20261022_formal\stage2`

只读进度：使用既有 SSH 别名登录后，查看 `parse_status.csv`、`parse_manifest.json`、`batch_resume2.log`，以及 `parse_logs/<paper_id>/conversion_linux_resources.jsonl`。不要重启任务仅为刷新状态。

输入被冻结在 `queue.json`，对应阶段0 `input_manifest.csv`。初始配置与修复后的调度哈希分开记录于 `configuration.json`、`orchestration_revision2.json`。官方解析入口脚本 `parse_one.py` 未变。

断点原则：

- PARSE_COMPLETE 只有输入、科学配置和全部产物哈希匹配才跳过。
- 已尝试 FAILED 不自动重跑；RUNNING 若有有效完成结果及正常清理可恢复为完成，其他情况保留 BLOCKED，等待检查。
- 没有 attempt 的 BLOCKED 可以在下一次明确恢复时重新检查资源，进入未尝试队列。
- 独占 task.lock 防止双启动；先核对 batch_owner PID、tmux 和容器状态。
- 不删除 attempt 文件，不修改旧预测或已完成解析文件。

本轮存在一次工程保护修复后的恢复，详见 `orchestration_repair.md`。v1 检查点保留，失败论文没有再次转换。

待 P2 确认后才能进入阶段3。此处不提供自动串联抽取或 GPT 的入口。
