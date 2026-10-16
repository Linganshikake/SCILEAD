# SCILEAD：GPT-4.1 实验复现记录

本仓库保存 EMNLP 2024 论文 [Efficient Performance Tracking: Leveraging Large Language Models for Automated Construction of Scientific Leaderboards](https://aclanthology.org/2024.emnlp-main.453/) 的本地复现实验代码、配置、模型输出和评价记录。

上游作者仓库：[UKPLab/emnlp2024-leaderboard-generation](https://github.com/UKPLab/emnlp2024-leaderboard-generation)。本项目保留上游 commit `8bf74b0a830feb7035c6166dce3394dc344ae532` 的源码，独立实验编排和接口适配位于 `pilot/` 中。

这里的模型是 **`gpt-4.1-2025-04-14`**，不是原论文的 GPT-4 Turbo。实验记录包含接口、输出 Token 配置和运行历史差异，不能把本仓库结果直接称为原论文报告的分数。

## 实验入口

| 实验 | 结果与说明 |
| --- | --- |
| Fully Pre-defined，Zero-shot，统一无客户端输出上限 | [full43_uncapped/report.md](pilot/full43_uncapped/report.md) |
| 同一冻结 Baseline 的 Leaderboard-level Evaluation | [leaderboard_eval_full43_uncapped/](pilot/leaderboard_eval_full43_uncapped/) |
| Fully Pre-defined，CS Normalization | [full43_cs/report.md](pilot/full43_cs/report.md) |
| Partially Pre-defined | [full43_partially/report.md](pilot/full43_partially/report.md) |
| Cold Start，三种论文顺序 | [full43_cold_start/report.md](pilot/full43_cold_start/report.md) |
| Few-shot Extraction + Zero-shot Normalization | [full43_fewshot/report.md](pilot/full43_fewshot/report.md) |
| 作者完整 Few-shot Prompt 分支 | [full43_fewshot_both_prompts/report.md](pilot/full43_fewshot_both_prompts/report.md) |
| threshold=2 数据审计与准备，正式实验受阻 | [threshold2_preparation/report.md](pilot/threshold2_preparation/report.md) |

统一无客户端输出上限的 Fully Zero-shot Baseline 覆盖 **43 篇论文、295 条 Gold TDMR**，产生 284 条原始预测；官方逐篇 Macro P/R 对应的 TDMR F1 为 **0.421578**。完整指标、严格数值辅助指标和逐篇错误分析以相应目录的 JSON 与报告为准。F1 由聚合后的 P/R 计算，与逐篇 F1 的算术平均不同。

`pilot/subset5`、`pilot/subset15`、`pilot/subset15_uncapped_retry`、`pilot/full43` 和 `pilot/outputs` 保留早期实验及其真实参数，不替换成最终版本，也不把不同版本重复计作同一次实验。各阶段的 `report.md` 描述该阶段结束时的状态；跨阶段比较请从上表进入。

## 目录

```text
emnlp2024-leaderboard-generation/  上游原始源码、Prompt、LICENSE 与 NOTICE
pilot/scripts/                   GPT-4.1 适配、编排、检查与汇总脚本
pilot/<实验名>/                  配置、断点、请求/响应、预测、指标与报告
pilot/experiment_settings.json   后续请求的统一设置记录
requirements-*.txt              Windows CPU 环境依赖
constraints-*.txt               依赖约束
scilead-*-freeze.txt            实际安装版本
PUBLICATION.md                  本次 GitHub 上传范围与完整性说明
publication_manifest.json       已发布本地文件的相对路径、大小与 SHA256
```

## 复现环境与阅读顺序

原运行环境为 Windows / PowerShell，Conda 环境名为 `scilead`，Python 3.11.17，PyTorch 2.2.0+cpu，NumPy 1.26.4。其余版本请查看冻结文件及各实验 `environment.json`、`reproducibility/` 下的记录。

1. 阅读 [依赖安装记录](scilead-compatible-installation-report.md) 和 [PDF 依赖记录](scilead-pdf-installation-report.md)。官方 `requirements.txt` 原样保留，Windows CPU 兼容文件另存。
2. 阅读目标实验的 `README.md`、`config.json`、`manifest.json` 和 `verification.json`（实际文件依各实验目录而定）。这些文件记录入口、数据来源、续跑机制与冻结输入。
3. 先检查现有结果。下载本仓库、阅读 JSON 或报告不会发起模型请求。运行 API 入口会产生费用；脚本包含完成阶段跳过及失败检查点，请勿清除检查点后重复请求。
4. 重跑需要另行准备合法获取的 SciLead 数据、PDF、系统工具及模型资源，以及个人 API 凭据。仓库不提供密钥。

这是一份**保持原始字节内容的实验归档**。历史脚本与 manifest 中保留了原机器上的绝对路径，如 `D:\C++\SCILEAD`、`D:\miniconda3\envs\scilead` 和外部 Gold 目录。克隆到不同位置后，需要在新的运行副本中配置路径；不要修改冻结结果来掩盖路径或配置差异。相对路径和 SHA256 清单可用于核对归档文件。

## 数据、资源与许可证

SciLead 的官方入口见 [作者 README](emnlp2024-leaderboard-generation/README.md#scilead-dataset) 和 [ACL 论文附件](https://aclanthology.org/2024.emnlp-main.453/)。论文 PDF、预训练权重、OCR/Poppler 可执行文件、完整环境与下载缓存不包含在本仓库；其本地文件未被删除。

上游源码保持作者的 [Apache-2.0 LICENSE](emnlp2024-leaderboard-generation/LICENSE) 和 [NOTICE](emnlp2024-leaderboard-generation/NOTICE)。数据、论文摘录、第三方模型及实验生成内容不因与源码一同归档而自动获得相同许可证；使用时遵守各自来源的授权。

API Key、`.env`、认证凭据和无关本机配置均不应提交。`.gitignore` 已包含相应防护规则。本次上传不运行任何实验，也不改变 Prompt、Gold、模型输出或评价方法。
