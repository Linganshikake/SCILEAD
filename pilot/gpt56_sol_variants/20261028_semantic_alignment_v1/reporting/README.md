# GPT-5.6 Sol 离线审计与报告

主进程可在运行期间或全部完成后调用；本工具不轮询、不运行评测、不导入 runtime，不读凭据，不启动子进程，也不调用 API、网络或模型。全部输出只写本 reporting 目录；源码、输入、analysis 和历史结果只读。

```powershell
$root = 'D:\C++\SCILEAD\pilot\gpt56_sol_variants\20261028_semantic_alignment_v1'
$python = 'D:\miniconda3\envs\scilead\python.exe'

# 独立离线测试；临时合成样本也仅在 reporting 下。
& $python -B -X utf8 "$root\reporting\verify_offline.py"

# 一次审计与报告；默认读取 analysis\comparison_final\comparison.json。
& $python -B -X utf8 "$root\reporting\audit_and_report.py" --out $root
$auditExit = $LASTEXITCODE

# 如果主进程选择了其他实际 comparison 目录，只读指定文件。
& $python -B -X utf8 "$root\reporting\audit_and_report.py" --out "$root\reporting" --comparison "$root\analysis\comparisons\<actual-timestamp>\comparison.json"
```

`--out` 只接受本实验根目录或其 reporting 目录。退出码：**0 = 完整报告 COMPLETE；2 = INCOMPLETE/PENDING；1 = 审计或 schema 失败**。请紧接命令读取退出码。一次运行会读取数万个现有证据文件，约数分钟；逐分支打印进度。请只运行一个报告进程；产物会刷新当前快照。

正式调用顺序由主进程控制：完成八阶段 → 主进程运行 analysis 工具并生成实际 comparison_final/comparison.json → 调用本脚本。缺失比较时仍输出审计和 pending 报告。八阶段未完成时，即使给了 COMPLETE comparison，也不会产生最终评分结论或最终案例。

产物：

- `report.md`：中文报告，stage2 主要结果、stage1 诊断；完整 IIM/TDM/TDMR P/R/F1 与六项 LB；三 Cold 顺序全部指标均值/样本 SD；Sol 配对前后变化。
- `api_usage_summary.json`：逻辑请求/已接受请求与物理尝试分列；授权重试、自动重试、发送未知、用量未知分别记录。只累计顶层 usage，嵌套 billing_usage 不再累加。

`logical_accepted` 按父级 accepted 指针与响应 hash 验证；`physical_http200_attempts` 与 `physical_valid_model_stop_responses` 按逐尝试实际 state/response 独立计算。不会读取 runtime 的 api_usage 成功计数来代替核验。
- `verification.json`：审计状态、比较状态、每阶段检查、83 项选定保护文件前后哈希及变化。只用新根目录 protected_hashes.json，不遍历历史 42k 文件。
- `request_audit.csv`：包括未完成阶段的失败、未知、成功、重试记录。空 token 表示未知而非零；HTTP403 拒绝与 5xx 完成情况未知分开。
- `alignment_event_summary.json`：按真实记录位置配对的全部事件变化及来源哈希。
- `alignment_examples.json`：全部完成后选择 2–3 条实际 Sol 变化，优先包含真实逐篇回退；附 Extraction、Gold、事件、accepted 响应路径/哈希和逐篇分差。只描述数据支持的匹配情况，不将每个分差归因于语义改变。
- `output_index.json`、`index.json`、`index.md`：阶段输出及报告产物索引。
- `offline_safety_proof.json`：实际审计的写入路径、保护文件前后检查和运行时隔离证明。
- `test_results.json/.txt`：独立合成测试结果和源码指纹。

完整性约束：43 篇 / 335 原始预测 / 295 Gold / 27 榜；Result、source_documents、记录顺序不变；八个阶段真实 COMPLETE summary、输出路径和哈希、逐记录事件、accepted 引用都必须一致。Prompt 文件与 DeepSeek 补充版逐字节一致；实际请求必须等于 expected.json 的消息及固定 user 模板；参数精确为 gpt-5.6-sol / medium / 32768 / stream=false。无需导入运行时代码或评测器。

运行中的 checkpoint 可能晚于旧 PAUSED summary；活动状态显示较新的 checkpoint，但只有合法 COMPLETE summary 才能确认阶段完成。HTTP524 原始 HTML、没有 response.json/usage 的尝试仍计入；retry_1 经授权文件/原请求 SHA/HTTP 状态/可用时的最早重试时间核验。HTTP403 余额重试要求已有运行时协议中的 balance_replenished_confirmed 和 insufficient_user_quota 授权字段。本工具从不创建授权或重试。

UNKNOWN 恢复使用实际 `manual_recovery_authorization.json` 协议（authorized、max_additional_attempts、request_sha256、original_state_sha256）。父级 accepted 指向 retry_1/response.json 即可，不要求 child accepted 标记。helper 哈希单独记录；若授权包含 helper_sha256 则校验该 pin，若提供 recovery_offline_tests.json 则另核对已测试 helper 字节。launch、无 API 重放或在授权门禁退出的进程都不作为 API 请求；只统计请求目录证据和 state.post_calls。

报告时间使用实际 UTC 和 Asia/Shanghai（UTC+08:00），包括跨午夜。首个请求和最后观察到的结束时间来自日志，后者不等同于整个运行完成时间。

所有新指标只来自实际 comparison.json，校验其 16 行范围与输入哈希、八组差值、三 Cold 统计、逐篇改善/回退汇总。缺失指标不会补零。Result IIM 不硬编码新分数，而是检查其配对值相同并从原版比较行呈现。
