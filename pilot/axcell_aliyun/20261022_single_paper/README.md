# AxCell 阿里云 ECS 单篇验证

最新结论请读 [single_paper_resource_report.md](single_paper_resource_report.md)，论文和输出索引见 [manifest.json](manifest.json)。

`1511.08308.pdf` 的原版 CPU 抽取已完成，返回 2 条原始预测。结果存在 Recall/F1 绑定错误及把数据集数量当成分数的错误，未人工修改。只完成单篇资源验证，未进行 GPT Normalization、评价或批量。

远端：`/root/scilead/axcell/runs/20261022_single_paper`；独立环境：`/root/scilead/axcell/envs/axcell-original`。

`remote_reports/` 为远端任务记录的同步副本；其中 `config.json`、`progress.md` 是执行早期快照。最新配置为本目录 `final_config.json`，最终状态为本目录 `verification.json`，不能用早期进度快照代替最终报告。

保留第一次初始化失败记录。唯一成功结果在 `remote_reports/attempts/console_progress_compat/`。不要重新执行已有 `launch_*` 脚本：这些脚本绑定已经完成的单篇任务，检查点会拒绝覆盖。未来批量必须先获得授权，在独立运行目录创建新任务；不得按结果质量重跑本篇。

可以通过 VS Code 已配置的 `scilead-aliyun` 查看远端目录。无需启动服务即可阅读 JSON、日志和解析 HTML。结果所需镜像、环境、模型均保留，任务容器已停止。

后续仍需确认作者 36 篇 AxCell 子集与本地 39 篇 TeX 的对应关系。未来付费标准化固定 `gpt-4.1-2025-04-14`，先统计请求量及费用，再等待授权。
