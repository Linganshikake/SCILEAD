# SCILEAD 五篇 Baseline 实验报告

本轮已完成：新增四篇全部完成高精度解析、检索、抽取、标准化和官方评价；原有一篇直接复用。完整索引见 [manifest.json](manifest.json) 和 [output_index.json](output_index.json)。

## 最终核验与主要错误现象

- 新增 66 次真实请求全部 HTTP 200、finish_reason=stop，响应 ID 唯一；没有自动重试或输出截断。4 次 Extraction、62 次 Normalization；候选集合内返回并不保证语义正确。
- 原有论文全部历史文件及官方源码、Prompt、依赖文件的哈希均未改变。已完成阶段跳过测试新增请求为 0，详见 [verification.json](verification.json)。
- `1709.04109.pdf` 抽取作者方法的 mean，而 Gold 使用 maximum；`2020.emnlp-main.523.pdf` 混淆 Dev / Test 并遗漏部分指标；`1905.03197.pdf` 存在表格合并、标题关联异常、跨指标绑定和 Baseline 混入；多篇名称标准化返回 null。所有原始结果保留。
- 官方字符串包含与严格 Decimal 数值相等的两两检查未发现差异，但数值相等不能证明 Task / Dataset / Metric 绑定正确。
- 人工核验的页码、原始数值和截图见 [inspection/findings.md](inspection/findings.md)；逐条 Gold 对照见 [evaluation/error_analysis.json](evaluation/error_analysis.json)。没有重新执行 PDF 解析或额外模型请求。
- 下文 `wall_seconds_since_selection=799.986` 是从选样到首次官方聚合评价完成的实测墙钟时间（约 13 分 20 秒），不包括后续人工检查和文档整理。阶段耗时之和为 470.875 秒，模型请求耗时之和为 134.84 秒；这些口径不能相加。
- 已具备继续扩展到 15 篇的工程基础，操作与恢复说明见 [README.md](README.md)。扩展辅助程序仅完成语法检查，本轮没有执行 15 / 43 篇实验；当前五篇也不能代表全部 43 篇的得分。

## 完成覆盖率

选定 5 篇，完整完成并进入官方评测 5 篇；Gold 总计 52 条，实际评测覆盖 52 条。未完成项不会被视为完整五篇结果。

## 逐篇阶段结果

| 论文 | Gold | 页数 | 文本块 | Table 区域 | 证据 | 抽取条数 | 标准化调用 | 集合内 / 集合外回答 | 状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2020.findings-emnlp.378.pdf | 6 | 15 | 25 | 12 | 16 | 6 | 12 | 6 / 6 | 复用 |
| 1709.04109.pdf | 3 | 8 | 20 | 10 | 14 | 3 | 8 | 6 / 2 | COMPLETE |
| D18-1279.pdf | 6 | 10 | 20 | 4 | 8 | 6 | 11 | 10 / 1 | COMPLETE |
| 2020.emnlp-main.523.pdf | 11 | 13 | 26 | 12 | 16 | 7 | 8 | 7 / 1 | COMPLETE |
| 1905.03197.pdf | 26 | 14 | 23 | 9 | 13 | 20 | 35 | 20 / 15 | COMPLETE |

集合内回答只说明输出属于候选名称，不等于语义映射必然正确。Table 数量是检测区域，不能当作正确表格数。

## 官方聚合指标（覆盖 5/5 篇）

| 指标 | Precision | Recall | 额外 F1 |
|---|---:|---:|---:|
| Task IIM | 0.960000 | 0.888889 | 0.923077 |
| Dataset IIM | 0.606667 | 0.499216 | 0.547721 |
| Metric IIM | 0.950000 | 0.809091 | 0.873902 |
| Result IIM | 0.605714 | 0.546853 | 0.574781 |
| TDM Exact Match | 0.467262 | 0.380886 | 0.419676 |
| TDMR Exact Match | 0.243810 | 0.218415 | 0.230415 |

P/R 由未修改的官方脚本对已完成论文逐篇计算后取算术平均；此处 F1 由聚合 P/R 计算，**不是逐篇 F1 的平均**。后者单独保存在 metrics_with_f1.json。

## 逐篇 F1

| 论文 | Result IIM | TDM | TDMR |
|---|---:|---:|---:|
| 2020.findings-emnlp.378.pdf | 1.000000 | 0.000000 | 0.000000 |
| 1709.04109.pdf | 0.000000 | 0.333333 | 0.000000 |
| D18-1279.pdf | 1.000000 | 0.833333 | 0.833333 |
| 2020.emnlp-main.523.pdf | 0.333333 | 0.666667 | 0.222222 |
| 1905.03197.pdf | 0.521739 | 0.238095 | 0.086957 |

所有逐篇六类指标 P/R/F1 见 evaluation/metrics_with_f1.json；逐条 Gold 数值、字段匹配和额外预测见 evaluation/error_analysis.json。

## 未完成论文

{}

## 用量与耗时

```json
{
  "new_experiment": {
    "requests": 66,
    "prompt_tokens": 35028,
    "completion_tokens": 1683,
    "total_tokens": 36711
  },
  "reused_historical": {
    "requests": 13,
    "prompt_tokens": 8718,
    "completion_tokens": 230,
    "total_tokens": 8948
  },
  "cumulative_five_selected": {
    "requests": 79,
    "prompt_tokens": 43746,
    "completion_tokens": 1913,
    "total_tokens": 45659
  },
  "new_stage_seconds_sum": 470.875,
  "new_model_request_seconds_sum": 134.84,
  "wall_seconds_since_selection": 799.986,
  "billing_cost": "UNVERIFIED; provider bill unavailable",
  "offline_mock_tests_excluded": true
}
```

API 次数按实际持久化请求计数；重复名称逐次收费调用，无名称缓存。中断恢复只重放同一位置已成功的历史响应，不产生新请求。未完成/不确定请求不自动重发。

## 复现边界

- 旧论文所有文件逐一 SHA256 核对未变，其 Result=1、TDMR=0 的历史结果直接复用。
- 固定种子 20261013，四个 Gold 数量分层，预先指定年代偏好及公开 PDF 获取优先级。所有候选顺序在下载前保存，无基于模型表现的换样。
- 保留原始 hi_res、表格推理、2000/200 分块、MPNet、Chroma 默认检索、原始 Query 和两个 Prompt。
- Extraction 固定 1024 输出 Tokens、temperature=0、seed=0；Normalization 15 Tokens、全 43 篇名称集合、原始逐字段循环。
- 无手工改值、无规则标准化、无扩大输出窗口、无失败请求自动重试。模型响应中的快照名已保存；中转站后端身份和种子确定性未独立验证。
- 官方 Result 包含匹配与额外 Decimal 严格相等检查分开保留；不得用数值命中代替完整 TDMR 正确率。
