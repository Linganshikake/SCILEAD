# 执行与复核

所有命令使用 D:\miniconda3\envs\scilead\python.exe；从 full43_cs 目录执行。prepare.py 为一次性准备入口，已有 freeze_before.json 时故意拒绝覆盖。模型已下载校验，推理完全离线。

```powershell
$env:PYTHONHASHSEED='0'
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\run_cs.py
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\evaluate_cs.py
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\leaderboard_evaluation\run_official_leaderboard_eval.py
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\leaderboard_evaluation\evaluate_paper_metrics.py
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\write_report.py
```

run_cs.py 按 normalization/papers/<paper>/complete.json 跳过已完成论文，同时核对输入与候选哈希。中断时只恢复缺少完成检查点的论文；没有付费 API 或自动重试模型请求。现有全部完成时也会加载模型后跳过所有论文，重新汇总检查点；仅复核时可使用 verify_artifacts.py，避免加载模型。

原版 main 分单篇验证及剩余论文两批执行，候选均来自同一完整 Gold；每批仍按原版生成候选 embeddings，没有为重复名称添加缓存。独立适配仅设备/路径/固定代码版本与审计日志。

排行榜评价入口复用冻结版本；唯一验证性差异是允许原版 RC >1，不改公式。原版 tdm_eval.py 与 leaderboard_eval.py 未编辑。模型代码不做修改。

完整代码与依赖、权重 SHA256 记录在 model_manifest.json、freeze_before.json、reproducibility/；所有记录均不含密钥。报告中的 P/R 为官方结果，F1、严格 Decimal 数值核对、论文 ID AO 是明确标注的补充统计。
