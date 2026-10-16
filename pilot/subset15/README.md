# SCILEAD 15 篇 Baseline：执行与扩展

本阶段固定清单见 `selection_fixed.json`；`manifest.json` 记录最新状态。前五篇以绝对路径引用既有结果，新十篇位于 `papers/<论文ID>/`。`output_index.json` 是所有输出的入口。

**实际完成状态：14/15。** `1912.08777.pdf` 已解析成功；用户授权 54,504 Tokens 完整输入例外后，唯一一次抽取请求 HTTP 200，但 1024 Tokens 输出被截断，JSON 非法。未标准化、未重试。该论文不能被标为 COMPLETE。

超限前记录位于该篇 `extraction/`，实际请求及截断输出位于 `extraction-approved-context/`；批准记录为 `context_limit_exception.json`，纯输入门限适配差异为 `context_exception_adapter.diff`。原始缓存与全部输入完全一致。

## 设置不变

官方 Commit `8bf74b0a830feb7035c6166dce3394dc344ae532`；Python 3.11.17，Unstructured 0.12.5，hi_res + infer_table_structure，原始 2000/200 切分、MPNet、Chroma、Query 与 Prompt。

GPT-4.1 快照 `gpt-4.1-2025-04-14`，temperature=0，seed=0；Extraction 1024 Tokens，Normalization 15 Tokens；标准集合由完整 43 篇 Gold 构造。模型响应中的快照 ID、seed 参数接受情况可以记录，但不等于独立验证中转站后台身份或确定性。

## 查看与恢复

```powershell
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\run_scilead_subset.py' --run-root 'D:\C++\SCILEAD\pilot\subset15'
```

逐篇顺序执行，已成功阶段跳过。读取已有成功请求只用于同一位置、同一消息的断点恢复，不按重复字段名称去重。`api_calls/<序号>/attempt.json` 标记已经尝试发送；无完整成功状态时禁止自动重发，需先核对服务商状态。非法 JSON、输入超限及 PDF 未完成状态均保留，不修改 Prompt 或参数重跑。不要删除检查点绕过保护。

阶段日志在每篇的 `preprocess/run.log`、`extraction/run.log`、`extraction/normalization/run.log`；调度进度为 `execution_progress.json`。

## 免费重新聚合与核验

```powershell
$env:SCILEAD_RUN_ROOT = 'D:\C++\SCILEAD\pilot\subset15'
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\subset15_evaluate.py'
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\audit_scilead_subset.py' --run-root 'D:\C++\SCILEAD\pilot\subset15'
```

这些命令不调用模型，也不解析 PDF；会重新生成当前规模的聚合报告和核验文件。官方 P/R 是逐篇 Macro 平均，附加 F1 是这些聚合 P/R 的调和平均。逐篇 F1 的算术平均另存，不能混用。

`evaluation/prior5_recomputed` 保存从本阶段合并结果中重新选择原五篇、运行原始 tdm_eval.py 的输出，核对历史指标完全一致。不会写入 subset5。

## 后续 43 篇

本阶段不执行下列命令；后续授权后才使用：

```powershell
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\extend_scilead_manifest.py' --source 'D:\C++\SCILEAD\pilot\subset15' --destination 'D:\C++\SCILEAD\pilot\subset43' --target 43 --seed 20261013 --download
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\run_scilead_subset.py' --run-root 'D:\C++\SCILEAD\pilot\subset43'
```

扩展入口要求源规模全部完成。若本阶段有非法 JSON、超时、超出上下文限制或其他未完成论文，先处理并明确记录这些检查点；不能静默排除后宣称全量完成。不能用提高 max_tokens、修改 Prompt 或手工补全来掩盖本轮 Baseline 失败。

当前源清单含一篇未完成，因此扩展入口会拒绝直接创建“已完整完成 15 篇”的后续运行。这是覆盖率保护，不能通过手工改为 COMPLETE 绕过。剩余 28 篇可在后续明确授权和失败状态处理方案确定后继续；当前不执行，也不修改 Baseline 参数。

43 篇的 PDF 可得性及资源限制尚未全部运行验证；剩余论文的缺失下载必须披露，核对 target_count=实际选定数=43 后才执行。成功的旧论文仍只读复用。

费用为服务端 Token Usage 记录，不将 LangChain 内置估价视为第三方实际账单。总累计调用=复用历史调用+本轮新增调用，不能把历史文件中的调用再次计费。
