# SCILEAD 15 篇 Baseline 实验报告

**执行结论：部分完成，14/15 篇完成全流程（93.33%）。** 新增十篇全部完成高精度 PDF 解析与检索，九篇完成抽取、标准化和官方评价；一篇因原定 1024 Tokens 输出上限导致 JSON 截断，保留失败，不重试。前五篇全部结果原样复用。

## 唯一未完成论文及已授权例外

`1912.08777.pdf`：55 页，36 条 Gold，44 个 Table 区域、48 条证据。完整输入为 54,504 Tokens，原 30,000 上限触发时未发送请求；用户明确授权一次完整输入例外后，HTTP 200，服务端 Prompt Tokens=54,504、Completion Tokens=1,024、finish_reason=length。原始输出在 JSON 对象中途结束，不能 json.loads。未手工补全、未标准化、未提高输出上限、未重试。

原超限记录保留在该篇 `extraction/`，真实请求与原始截断输出保存在 `extraction-approved-context/`。授权见 [context_limit_exception.json](context_limit_exception.json)，适配差异见 [context_exception_adapter.diff](context_exception_adapter.diff)。核验确认例外前后的完整消息、证据与缓存完全一致。

因此下方指标仅代表 **14 篇有效结果**，不是完整 15 篇指标。选定 153 条 Gold，进入评价 117 条（76.47%）；未完成论文的 36 条没有静默计为成功，也没有更换论文。

## 完成覆盖率

选定 15 篇，完整完成并进入官方评测 14 篇；Gold 总计 153 条，实际评测覆盖 117 条。未完成项明确列出，不将有效结果子集称为全部十五篇。

## 逐篇阶段结果

| 论文 | Gold | 页数 | 文本块 | Table 区域 | 证据 | 抽取条数 | 标准化调用 | 集合内 / 集合外回答 | 状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2020.findings-emnlp.378.pdf | 6 | 15 | 25 | 12 | 16 | 6 | 12 | 6 / 6 | 复用 |
| 1709.04109.pdf | 3 | 8 | 20 | 10 | 14 | 3 | 8 | 6 / 2 | 复用 |
| D18-1279.pdf | 6 | 10 | 20 | 4 | 8 | 6 | 11 | 10 / 1 | 复用 |
| 2020.emnlp-main.523.pdf | 11 | 13 | 26 | 12 | 16 | 7 | 8 | 7 / 1 | 复用 |
| 1905.03197.pdf | 26 | 14 | 23 | 9 | 13 | 20 | 35 | 20 / 15 | 复用 |
| 1702.02098.pdf | 2 | 13 | 26 | 8 | 12 | 2 | 4 | 2 / 2 | COMPLETE |
| 2020.emnlp-main.152.pdf | 6 | 6 | 12 | 4 | 8 | 6 | 13 | 11 / 2 | COMPLETE |
| 2105.03654.pdf | 7 | 13 | 20 | 8 | 12 | 9 | 15 | 14 / 1 | COMPLETE |
| 1910.13461.pdf | 25 | 10 | 22 | 6 | 10 | 13 | 18 | 8 / 10 | COMPLETE |
| D18-1105.pdf | 2 | 7 | 13 | 3 | 7 | 2 | 4 | 3 / 1 | COMPLETE |
| 1703.06345.pdf | 5 | 10 | 18 | 3 | 7 | 7 | 14 | 12 / 2 | COMPLETE |
| 1903.07785.pdf | 11 | 10 | 19 | 6 | 10 | 10 | 23 | 22 / 1 | COMPLETE |
| 1912.08777.pdf | 36 | 55 | 77 | 44 | 48 | None | 0 | 0 / 0 | NOT_COMPLETE |
| 1711.05568.pdf | 2 | 10 | 25 | 7 | 11 | 2 | 4 | 4 / 0 | COMPLETE |
| wang19f.pdf | 5 | 11 | 20 | 5 | 9 | 5 | 12 | 11 / 1 | COMPLETE |

集合内回答只说明输出属于候选名称，不等于语义映射必然正确。Table 数量是检测区域，不能当作正确表格数。

## 官方聚合指标（覆盖 14/15 篇）

| 指标 | Precision | Recall | 额外 F1 |
|---|---:|---:|---:|
| Task IIM | 0.935714 | 0.910431 | 0.922899 |
| Dataset IIM | 0.699915 | 0.642090 | 0.669757 |
| Metric IIM | 0.932143 | 0.892136 | 0.911701 |
| Result IIM | 0.693886 | 0.659974 | 0.676505 |
| TDM Exact Match | 0.530938 | 0.493724 | 0.511655 |
| TDMR Exact Match | 0.351073 | 0.342984 | 0.346981 |

P/R 由未修改的官方脚本对已完成论文逐篇计算后取算术平均；此处 F1 由聚合 P/R 计算，**不是逐篇 F1 的平均**。后者单独保存在 metrics_with_f1.json。

## 逐篇 F1

| 论文 | Result IIM | TDM | TDMR |
|---|---:|---:|---:|
| 2020.findings-emnlp.378.pdf | 1.000000 | 0.000000 | 0.000000 |
| 1709.04109.pdf | 0.000000 | 0.333333 | 0.000000 |
| D18-1279.pdf | 1.000000 | 0.833333 | 0.833333 |
| 2020.emnlp-main.523.pdf | 0.333333 | 0.666667 | 0.222222 |
| 1905.03197.pdf | 0.521739 | 0.238095 | 0.086957 |
| 1702.02098.pdf | 0.500000 | 0.000000 | 0.000000 |
| 2020.emnlp-main.152.pdf | 0.666667 | 0.666667 | 0.333333 |
| 2105.03654.pdf | 0.500000 | 0.125000 | 0.000000 |
| 1910.13461.pdf | 0.578947 | 0.125000 | 0.052632 |
| D18-1105.pdf | 1.000000 | 0.500000 | 0.500000 |
| 1703.06345.pdf | 0.500000 | 0.909091 | 0.333333 |
| 1903.07785.pdf | 0.761905 | 0.857143 | 0.666667 |
| 1711.05568.pdf | 1.000000 | 1.000000 | 1.000000 |
| wang19f.pdf | 1.000000 | 0.800000 | 0.800000 |

所有逐篇六类指标 P/R/F1 见 evaluation/metrics_with_f1.json；逐条 Gold 数值、字段匹配和额外预测见 evaluation/error_analysis.json。

## 未完成论文

{
  "1912.08777.pdf": {
    "extraction": {
      "status": "INVALID_OUTPUT",
      "records": null,
      "seconds": 13.094,
      "evidence_count": 48,
      "tokens": 54504
    },
    "normalization": {},
    "reason": "No complete compatible normalization output; excluded from official metrics with explicit coverage disclosure"
  }
}

## 用量与耗时

```json
{
  "new_experiment": {
    "requests": 117,
    "prompt_tokens": 113419,
    "completion_tokens": 3676,
    "total_tokens": 117095
  },
  "reused_historical": {
    "requests": 79,
    "prompt_tokens": 43746,
    "completion_tokens": 1913,
    "total_tokens": 45659
  },
  "cumulative_selected": {
    "requests": 196,
    "prompt_tokens": 157165,
    "completion_tokens": 5589,
    "total_tokens": 162754
  },
  "new_stage_seconds_sum": 1325.458,
  "new_model_request_seconds_sum": 258.787,
  "wall_seconds_since_selection": 1841.023,
  "billing_cost": "UNVERIFIED; provider bill unavailable",
  "offline_mock_tests_excluded": true
}
```

API 次数按实际持久化请求计数；重复名称逐次收费调用，无名称缓存。中断恢复只重放同一位置已成功的历史响应，不产生新请求。未完成/不确定请求不自动重发。

## 复现边界

- 前五篇的 494 个历史文件逐一 SHA256 核对未变；旧五篇重新运行原始评价脚本得到完全相同的逐篇和聚合结果，TDMR F1 仍为 0.230415。
- 固定种子 20261013，沿用已提供扩展入口的四个 Gold 数量分层、层内洗牌、层间轮转顺序。所有候选顺序在下载前保存，十篇首选 PDF 均下载成功，无按模型表现换样。年份覆盖 2017–2021。
- 保留原始 hi_res、表格推理、2000/200 分块、MPNet、Chroma 默认检索、原始 Query 和两个 Prompt。
- Extraction 固定 1024 输出 Tokens、temperature=0、seed=0；Normalization 15 Tokens、全 43 篇名称集合、原始逐字段循环。
- 无手工改值、无规则标准化、无扩大输出窗口、无失败请求自动重试。模型响应中的快照名已保存；中转站后端身份和种子确定性未独立验证。
- 官方 Result 包含匹配与额外 Decimal 严格相等检查分开保留；不得用数值命中代替完整 TDMR 正确率。

## 与旧五篇对比

| 指标 F1 | 原五篇 | 当前有效十四篇 | 差值 |
|---|---:|---:|---:|
| Task IIM | 0.923077 | 0.922899 | -0.000177 |
| Dataset IIM | 0.547721 | 0.669757 | +0.122036 |
| Metric IIM | 0.873902 | 0.911701 | +0.037799 |
| Result IIM | 0.574781 | 0.676505 | +0.101725 |
| TDM | 0.419676 | 0.511655 | +0.091980 |
| TDMR | 0.230415 | 0.346981 | +0.116566 |

这里改变的是样本组成和有效覆盖范围，方法及旧预测不变，不能据得分上升认定方法提升。重新聚合的 P/R 与逐篇 Macro 算术平均独立核对一致。

## 请求、时间与完整性核验

- 本轮 10 次 Extraction、107 次 Normalization，共 117 次真实请求；全部 HTTP 200，116 次 stop、1 次 length，模型响应 ID 均唯一，没有自动重试。JSON 成功与 HTTP 成功分开统计。
- 九篇完成标准化的论文共有 56 条原始预测；107 次逐字段请求中，87 次回答属于标准集合、20 次不属于集合而保存 null。集合内不意味着语义必然正确。
- 新增 117,095 Tokens（输入 113,419，输出 3,676）。历史 79 次 / 45,659 Tokens；累计 196 次 / 162,754 Tokens。截断失败的请求已包含在内，不漏计、不重复计历史。
- 从选样到首次官方聚合评价完成约 1,841 秒（30 分 41 秒）；各新增阶段内部耗时之和 1,325.458 秒，模型请求之和 258.787 秒。墙钟时间还包含下载、Python 启动、工程准备及等待；人工复核和最终打包另计。第三方实际账单金额未获取。
- 包含最终离线核验和报告整理，记录时总墙钟耗时为 2,310.651 秒（约 38 分 31 秒），见 api_usage_summary.json 的 wall_seconds_to_final_report。
- 官方源码、Prompt、requirements、依赖版本及旧文件未变；已验证的 PDF/API 基础适配程序哈希未变。例外仅采用独立输入门限适配，不改变发送内容。
- 对已完成的 14 篇进行离线跳过测试，未启动任何子进程，新增请求数 0。失败论文保留 INVALID_OUTPUT 检查点，不能通过移除检查点盲目重试。

## 错误分类与核验入口

新增九篇有效论文的 65 条 Gold，严格完整 TDMR 对照中：19 条正确、26 条缺少严格数值候选（含 ± 等非纯数值情况）、15 条数值候选有标准化 null、5 条数值存在但名称/绑定不匹配。这是辅助症状分类，不替代官方指标，也不自动认定唯一原因。

主要现象包括：表头缺失及表题错配、Baseline 数值混入、跨 Task / Dataset / Metric 绑定、不同方法变体与实验分组选择、Dataset 缩写标准化失败、ROUGE/ROGUE 名称差异。`90.65 ± 0.15` 是本次唯一官方包含匹配与完整字符串严格数值相等不一致的数值对。

- [逐条 Gold / 原始预测 / 标准化输出对照](evaluation/tdmr_comparison.md)
- [自动分类与口径边界](inspection/findings.md)
- [人工核验的具体数值、表格和页面截图](inspection/manual_findings.md)
- [逐篇及聚合指标](evaluation/metrics_with_f1.json)
- [旧五篇复算一致性](evaluation/comparison_with_subset5.json)
- [文件与请求核验](verification.json)
- [论文和输出索引](output_index.json)

## 后续扩展状态

具备逐篇缓存、成功阶段跳过、请求检查点和原始官方评价的工程基础，但**当前不能宣称已完成十五篇，也不能直接得到完整四十三篇 Baseline**。尚有这篇截断失败未完成，剩余 28 篇尚未运行。当前扩展入口要求源清单全部完成，因此会明确阻止把本次 14/15 当成已完成十五篇继续。未擅自提高输出上限或更换方法。

后续执行说明见 [README.md](README.md)。本轮没有执行剩余 28 篇，也没有进行方法优化或对照实验。
