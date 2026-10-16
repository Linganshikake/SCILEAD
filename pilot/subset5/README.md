# SCILEAD Baseline 实验运行说明

当前完成：5/5 篇，52 条 Gold。所有结果独立于官方仓库。`manifest.json` 是论文索引，`output_index.json` 指向各篇原始文件，`report.md` 是阶段报告，`inspection/findings.md` 是错误现象说明。

## 目录

- `papers/<paper-id>/input`：只有该篇 PDF。
- `papers/<paper-id>/preprocess`：官方 config / processed_docs.pkl、原始 partition 元素、表格、文本块、证据、耗时及日志。
- `papers/<paper-id>/extraction`：output/config、Token 预检查、格式检查、api_calls 请求/响应/持久标记。
- `papers/<paper-id>/extraction/normalization`：原始逐字段标准化结果、完整候选集合及顺序、逐次原始回答和用量。
- `merged/output.json`、`merged/normalized_output.json`：官方兼容的聚合文件。
- `evaluation/eval_results.json`、`eval_values.json`：原始官方 P/R；`metrics_with_f1.json`：额外 F1 及全部逐篇指标。
- `environment.json`、`preserved_existing_sha256.json`、`verification.json`：环境及不可变输入审计。
- `offline_adapter_test`：纯模拟测试，明确不属于实验请求量或预测。

## 恢复当前实验

以下命令会跳过成功论文。当前五篇已经全部完成，不会为了提高得分重新运行。

```powershell
$env:SCILEAD_RUN_ROOT = 'D:\C++\SCILEAD\pilot\subset5'
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\subset5_preprocess.py'
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\subset5_api.py' --stage all
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\subset5_evaluate.py'
```

运行批处理驱动时会为 API 子进程固定 PYTHONHASHSEED=0。不要直接启动 API worker 绕过驱动的环境设置。阶段也可分别运行 `--stage extract` / `--stage normalize`。

Normalization 中断恢复从相同的逐字段位置重放该次已成功响应，不跨字段按名称去重；所有相同 Task 的原始多次请求仍各有独立记录。已有 attempt 但没有完整响应/完成标记时禁止自动重发，需人工核对请求状态。某篇失败不会删除其他论文成功结果。

PDF 的成功结果直接跳过。出现 started 标记但未完成时不会盲目重复高精度解析；其他论文可继续，故障论文需先检查日志。非法/截断的 Extraction 原样保留并停止该篇后续标准化，不自动补全或再生成。

汇总可以重复运行而不产生模型请求。每个规模使用不同目录，避免覆盖上一规模的聚合结果。不要删除请求标记来重跑模型。

## 以后扩展到 15 / 43 篇

已提供 `extend_scilead_manifest.py`，本轮没有执行扩展。它在新目录引用已完成结果，不复制或改动旧预测；按固定种子对剩余 Gold 数量分层、轮转确定候选顺序，按顺序替换 PDF 获取失败项，不按得分换样。

以下仅为以后授权执行时的示例：

```powershell
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\extend_scilead_manifest.py' --source 'D:\C++\SCILEAD\pilot\subset5' --destination 'D:\C++\SCILEAD\pilot\subset15' --target 15 --seed 20261013 --download
$env:SCILEAD_RUN_ROOT = 'D:\C++\SCILEAD\pilot\subset15'
# 随后依次运行上面三个阶段脚本。
```

省略 `--download` 只创建下一阶段清单和候选顺序，不下载 PDF、不调用 API。15 篇完成后可将 source 改为 subset15、destination 改为 subset43、target 改为 43。检查 manifest 的 target_count、实际 papers 数和下载失败记录；全量 PDF 若不可获得，不能宣称 43 篇完成。

当前工程支持继续扩展到 15 篇；扩展时必须保留已观察到的低分结果、明确报告覆盖率，不将方法变更混入 Baseline。扩展辅助入口完成语法检查，尚未执行 15/43 篇下载或实验。
