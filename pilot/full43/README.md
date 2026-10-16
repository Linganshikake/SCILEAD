# SCILEAD 全量 Baseline

本目录固定包含完整 Gold 的 43 篇、295 条 TDMR。前 15 篇通过绝对路径只读复用，新增 28 篇为完整差集，不抽样、不换样。当前完成情况以 `execution_progress.json`、`manifest.json` 及最终 `evaluation/coverage.json` 为准。

## 执行与断点恢复

```powershell
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\run_scilead_subset.py' --run-root 'D:\C++\SCILEAD\pilot\full43'
```

每篇依次执行原始 PDF 解析与检索、Extraction、Normalization。完成阶段自动跳过；已尝试但未明确完成的 API 请求不会自动重发。已完成请求仅在同一序号、完全相同消息下重放本地响应，不是重复名称缓存。恢复前应检查失败状态，保留所有 `attempt.json`、`state.json`、原始响应与日志。不要删除检查点以强制重试。单篇失败后继续其他论文。

`prepare_full43.py` 创建固定差集与历史哈希，检查依赖和源码后，从已有本地文件或 Gold 的原始公开来源获取 PDF。`128538.pdf` 的 Gold URL 返回出版社阅读网页，实际 PDF 使用该网页链接的同出版社下载地址；原失败记录保留，没有更换论文。

## 固定方法与历史参数

- 官方 commit：`8bf74b0a830feb7035c6166dce3394dc344ae532`。
- hi_res + infer_table_structure，原始 2000/200 分块，MPNet `multi-qa-mpnet-base-dot-v1`，Chroma 原始检索，四条语义文本和全部表格，原始 Query、Zero-shot Prompt 和消息角色。
- GPT-4.1 固定快照、temperature=0、seed=0、SDK max_retries=0。新请求实际省略 `max_tokens`、`max_completion_tokens` 等输出上限参数；没有固定输入 Token 门限。输入估算、实际请求体、HTTP 状态、返回模型、finish_reason 和原始响应保存在逐篇日志中。
- 标准化候选来自完整 43 篇 Gold 的 23 Task / 71 Dataset / 26 Metric，原始逐字段调用，不额外缓存或增加上下文，保存实际候选集合顺序。Result 字符串不变，集合外回答按官方实现记 null。
- 历史 14 篇的抽取上限为 1024；长论文 `1912.08777.pdf` 的成功抽取无客户端输出上限。历史 15 篇标准化均使用 15 上限。本次新增 28 篇两个阶段均省略上限。历史截断请求保留在累计费用中，但不参加评价。不可声称所有历史请求配置完全相同。
- finish_reason=length 标记截断；finish_reason=stop 还需通过 JSON、字段及 Result 类型验证。中转站后端身份、种子确定性、账单和静默输入截断无法仅凭响应独立验证。

## 评价与审计

```powershell
$env:SCILEAD_RUN_ROOT='D:\C++\SCILEAD\pilot\full43'
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\full43_evaluate.py'
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\inspect_full43.py' --run-root $env:SCILEAD_RUN_ROOT
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\audit_full43.py' --run-root $env:SCILEAD_RUN_ROOT
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 'D:\C++\SCILEAD\pilot\scripts\finalize_full43.py'
```

评价直接运行未修改的官方 `tdm_eval.py`，使用完整 Gold，但只评价确实完成的标准化输出；覆盖率与失败项单列。官方 P/R 是逐篇 Macro 平均，额外 F1=2PR/(P+R)，不是逐篇 F1 的算术平均。严格 Decimal 数值匹配只是辅助诊断，不替换官方字符串包含逻辑。

每篇 `input/`、`preprocess/`、`extraction/`、`extraction/normalization/` 独立保存。`merged/` 为官方格式合并结果；`output_index.json` 为 43 篇索引；历史文件哈希在 `preserved_existing_sha256.json`；最终验证见 `verification.json`。累计 API 用量以原 15 篇的 228 次历史请求为基础加本次真实请求，保留此前失败请求，不重复计数。审计离线复算历史 15 篇指标并比较文件哈希、候选集合、实际请求参数及依赖版本。
