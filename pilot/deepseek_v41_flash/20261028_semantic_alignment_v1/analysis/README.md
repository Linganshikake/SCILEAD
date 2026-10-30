# Semantic-alignment v1 离线评估与比较

这是已授权的 **Prompt 改进变体** 与 `20261028` 原始基线的同案例比较工具。默认比较 partially、cold_default、cold_0、cold_42 的两个阶段；stage2 为主结果，stage1 为诊断。

## 直接运行

使用基线已有的 Python 环境（已安装 rbo）；默认 `python` 指向的 miniconda base 环境缺少 rbo。

```powershell
$py = 'D:\miniconda3\envs\scilead\python.exe'
$analysis = 'D:\C++\SCILEAD\pilot\deepseek_v41_flash\20261028_semantic_alignment_v1\analysis'

# 检查八个阶段就绪情况，不执行评估
& $py -B -X utf8 "$analysis\evaluate_ready.py" --inspect

# 评估已完成阶段；缺失阶段跳过；已有完整评估验证后复用
& $py -B -X utf8 "$analysis\evaluate_ready.py"

# 可选：最多等待一小时，每 10 秒复查；每次只执行新就绪阶段
& $py -B -X utf8 "$analysis\evaluate_ready.py" --wait-seconds 3600 --poll-seconds 10

# 可选：只处理一个阶段（--case 可以重复）
& $py -B -X utf8 "$analysis\evaluate_ready.py" --case cold_0_stage2

# 生成新的 JSON/CSV/中文比较报告；默认输出到 analysis/comparisons/UTC时间戳
& $py -B -X utf8 "$analysis\compare_results.py"

# 全部就绪后也可指定一个新的报告目录
& $py -B -X utf8 "$analysis\compare_results.py" --out "$analysis\comparison_final"

# 重跑边界/聚合测试和一例基线离线复评，输出到新的 verification/UTC时间戳
& $py -B -X utf8 "$analysis\verify_offline.py"
```

退出码：`0` 所选评估/报告完整，`2` 存在未完成项（检查模式发现 READY 也返回 2），`1` 验证错误。PowerShell 中读取 `$LASTEXITCODE`。`verify_offline.py` 返回 0 表示测试和一致性验证通过。

## 输入、输出与复用规则

固定复用原始 Extraction：`20261028/fully/merged/output.json`，43 篇、295 条预测。Gold 固定为 43 篇/295 条；榜单固定为 all27。

新输入为 `variants/{partially,cold_default,cold_0,cold_42}/stage1/normalized_output.json` 与 `stage2/leaderboard_normalized_output.json`。同目录的 `summary.json` 必须包含：

```json
{
  "status": "COMPLETE",
  "papers": 43,
  "records": 295,
  "output_path": "实际输出文件绝对路径",
  "output_sha256": "实际输出文件的 SHA-256"
}
```

就绪检查也验证论文 ID、每篇原始/归一化行数、source_documents 和 Result 保持不变。未生成文件或未完成摘要标为 PENDING；COMPLETE 摘要的计数、路径或哈希不一致标为 ERROR。stage2 以自己的摘要/文件为输入契约。

评估写入 `analysis/evaluations/{branch}_stage{1,2}`，保存原始官方结果、逐论文指标、榜单诊断、source_hashes、status 和 `verified_complete.json`。后者记录输入与产物哈希；复用时重新验证全部产物、输入与聚合一致性。工具不会覆盖已有非空且无法验证的评估目录；保留现场，修复原因后由操作者在 analysis 内归档该目录，再重跑。

`readiness.json` 记录当前所选阶段；`all_eight_complete` 只有八阶段全部验证成功才为 true。每次报告写入新的目录，防止覆盖前一次报告。报告的 COMPLETE 表示八个变体阶段及对应基线结果均可配对。

## 比较文件与 JSON 接口

- `comparison.json`：完整机器可读数据，遵循同目录工具旁的 `comparison_schema.json`。
- `comparison.csv`：两个阶段全部 24 个标量指标，baseline / variant / delta；数值为比例，乘 100 得百分比或差值百分点。
- `per_paper_differences.csv/json`：每案例、每论文、六种元组指标的 P/R/F1 及配对差值。缺失变体为 null/空白，不填零。
- `report_zh.md`：stage2 主表、三顺序统计、逐论文改善/退化计数及实际待完成项。
- `source_hashes.json`：本次读取的来源哈希；`report_status.json`：报告文件哈希与状态。

`comparison.json` 的关键结构：

```text
status: COMPLETE | INCOMPLETE | ERROR
scope: {papers:43, predictions:295, gold_annotations:295, gold_boards:27,
        primary_stage:"stage2", diagnostic_stage:"stage1"}
local_rows[]: {
  model: "baseline" | "prompt_improvement_variant",
  case: "partially_stage1" | ... | "cold_42_stage2",
  role: "primary" | "diagnostic", status:"COMPLETE",
  coverage: {...}, source: evaluation_directory, normalized: input_path, input_sha256,
  tuple: {"Task IIM": {Precision,Recall,F1}, ...},
  leaderboard: {gold_leaderboards:27, LR_exact_tdm_hit, LR_nonempty_finite_result,
                PC_official, RC_official, RBO_official_value_rankings,
                AO_paper_id_macro_all_gold_boards, ...},
  per_paper: {paper_id: {"Task IIM": {Precision,Recall,F1}, ...}}
}
paired_differences[]: {case, role, unit, metrics: {flat_metric_name: variant_minus_baseline}}
cold_three_order_summaries[]: {
  model: "baseline" | "prompt_improvement_variant" | "paired_delta",
  stage: "stage1" | "stage2", status, orders_present,
  metrics: {flat_metric_name: {mean, sample_sd, n:3}} | null, definition
}
stage2_paper_changes[]: {
  case, metric: "TDM Exact Match" | "TDMR Exact Match", paired_papers,
  improved, regressed, unchanged, equality_tolerance:1e-12,
  top_improvements/top_regressions: [{paper_id,baseline_F1,variant_F1,delta_F1}]
}
missing[]: {model, case, status:"PENDING"|"ERROR", reason, ...}
method: {label, declared_change, raw_extraction, raw_sha256, ...}
immutable_prior_references: {source, source_sha256, local_rows, original_paper, provenance, status}
source_integrity: {files_checked, changed:[]}
```

六个元组指标键固定为 `Task IIM`、`Dataset IIM`、`Metric IIM`、`Result IIM`、`TDM Exact Match`、`TDMR Exact Match`。平铺键为 `Task IIM/Precision` 等 18 项，加上 6 项榜单指标。差值统一为 **variant − baseline**。三顺序统计须 cold_default、cold_0、cold_42 全部完成；`paired_delta.sample_sd` 是三个配对差值的样本 SD。

F1 保持官方宏平均 P/R 的调和平均。LR 是精确 TDM 命中率，finite nonempty 另计有限数值非空率。PC、RC、RBO 使用官方结果；RBO 为去重数值排名，AO 为论文 ID 排名。空榜单保留在 27 个榜单分母中。官方重复记录/Result 子串匹配等行为保持原样，不截断指标。

Sol/GPT-4.1 和已发表论文数值从基线 `analysis/comparison_final/comparison.json` 原样引用，保留原始范围和定义。具体 Prompt 变更、全局 usage/integrity、Arnet→SemEval 2013 等事件解释由主任务根报告汇总；这里提供同案例数值和正负方向的逐论文差异。

## 实现与验证

`evaluate_offline.py` 及 `audited_helpers/` 两个脚本与基线审计版本逐字节相同。`offline_support.py` 仅改变 ANALYSIS 与 HELPERS 两个路径常量；`audit_manifest.json` 固定来源及基线文件的哈希。新增代码为 `evaluation_contract.py`、`evaluate_ready.py`、`compare_results.py`、`verify_offline.py` 和 `test_utilities.py`。

Python 使用 `-B` 禁止生成 bytecode。IO 边界限制写入本 analysis，拒绝网络、子进程、凭据读取与模型/传输库导入。所有评估在同一 Python 进程内执行。

最终验证记录：`verification/validated/verification.json`，**11 tests / 0 failures / 0 errors，PASSED**；对应输出为 `verification/validated/tests.log`。原始基线 partially_stage2 的 10 份数值/诊断 JSON、全部汇总、逐论文和覆盖范围均完全一致，重复读取已封存评估没有改写产物。224 个审计来源/基线文件哈希无变化。

首次默认 Python 的验证记录保留在 `verification/initial`：单元测试通过，但该环境没有 rbo，复评失败；后续使用上面指定的 scilead 环境。`verification/final` 是最终小修前的中间验证记录，当前交付以 `verification/validated` 为准。

`comparison_ready_template/` 是交接时的 INCOMPLETE 报告快照（8 条基线记录、0 个完成评估的变体配对），中文报告已删除泛化免责声明，并新增逐论文改善/退化汇总。实际变体评估由主任务调用工具执行，完成后运行比较命令生成新报告。
