# SCILEAD 第五阶段：Normalization / Evaluation

日期：2026-10-13（Asia/Shanghai）。**最终状态：12 次 Normalization 请求全部成功，官方 Evaluation 已完成；Task 映射成功，但六个 Dataset 全部标准化为 null，TDM / TDMR 精确匹配均为 0。** 未手工修正预测结果。

## 真实执行与请求记录

用户已明确授权本轮收费步骤。预计与实际 Normalization 请求均为 **12 次**，12 次 HTTP 200、12 次 finish_reason=stop、无重试、无额外抽取请求、无输出截断。保持 max_tokens=15、temperature=0、seed=0。请求及全部响应模型 ID 均为 `gpt-4.1-2025-04-14`；种子参数被接受，但没有额外实验验证确定性。

| 请求 | 记录 | 字段 | 输入值 | 模型原始回答 | 输入 / 输出 Tokens |
|---|---|---|---|---|---|
| 1 | 1 | Task | Named Entity Recognition | Named Entity Recognition (NER) | 224 / 6 |
| 2 | 1 | Dataset | ON5E | None | 527 / 1 |
| 3 | 2 | Task | Named Entity Recognition | Named Entity Recognition (NER) | 224 / 6 |
| 4 | 2 | Dataset | WN16 | None | 527 / 1 |
| 5 | 3 | Task | Named Entity Recognition | Named Entity Recognition (NER) | 224 / 6 |
| 6 | 3 | Dataset | WN17 | None | 527 / 1 |
| 7 | 4 | Task | Named Entity Recognition | Named Entity Recognition (NER) | 224 / 6 |
| 8 | 4 | Dataset | ON4C | None | 527 / 1 |
| 9 | 5 | Task | Named Entity Recognition | Named Entity Recognition (NER) | 224 / 6 |
| 10 | 5 | Dataset | RE | None | 525 / 1 |
| 11 | 6 | Task | Named Entity Recognition | Named Entity Recognition (NER) | 224 / 6 |
| 12 | 6 | Dataset | WE | None | 525 / 1 |

Normalization 合计输入 **4,502**、输出 **42**、总计 **4,544 Tokens**。六次重复 Task 分别发送，没有新增缓存。加上上一阶段一次 Extraction，两个阶段合计 13 次请求、输入 8,718、输出 230、总计 8,948 Tokens。平台实际账单未获取，不宣称具体费用；官方生成的 `normalization_costs.txt` 不作为中转站收费依据。

## 六条 TDMR 前后对照

六条原始 Task 均为 `Named Entity Recognition`，标准化后均为 `Named Entity Recognition (NER)`；Metric 始终为 `F1`。所有 Result 保留原字符串。下表中的 null 是官方保存的真实值，Gold 全称仅用于事后分析，没有写回预测。

| 原始 Dataset | 标准化后 Dataset | Gold Dataset | 原始 / 标准化后 Result | 结果 |
|---|---|---|---|---|
| ON5E | null | Ontonotes v5 - English | `90.32` / `90.32` | 数值正确，Dataset 标准化失败 |
| WN16 | null | WNUT-16 - English | `55.14` / `55.14` | 数值正确，Dataset 标准化失败 |
| WN17 | null | WNUT-17 - English | `50.68` / `50.68` | 数值正确，Dataset 标准化失败 |
| ON4C | null | Ontonotes v4 - Chinese | `81.18` / `81.18` | 数值正确，Dataset 标准化失败 |
| RE | null | Resume - Chinese | `96.62` / `96.62` | 数值正确，Dataset 标准化失败 |
| WE | null | Weibo - Chinese | `69.78` / `69.78` | 数值正确，Dataset 标准化失败 |

## 官方指标与额外 F1

通过 `runpy` 以 `__main__` 和原始 CLI 参数执行了未修改的 `tdm_eval.py`。`eval_results.json` / `eval_values.json` 保留官方输出；下面的 Precision、Recall 来自官方脚本，F1 是额外计算的 2PR/(P+R)，P+R 为 0 时记 0。

| 指标 | 官方 Precision | 官方 Recall | 额外 F1 |
|---|---:|---:|---:|
| Task IIM | 1.0000 | 1.0000 | 1.0000 |
| Dataset IIM | 0.0000 | 0.0000 | 0.0000 |
| Metric IIM | 1.0000 | 1.0000 | 1.0000 |
| Result IIM | 1.0000 | 1.0000 | 1.0000 |
| TDM Exact Match | 0.0000 | 0.0000 | 0.0000 |
| TDMR Exact Match | 0.0000 | 0.0000 | 0.0000 |

官方 IIM 使用字段去重集合。Dataset 的预测集合是 `{None}`，与六个 Gold 名称无交集；TDM 去重后只有一个 `(NER, None, F1)` 组合，匹配为 0；TDMR 的六条记录也全部因 Dataset 缺失而失败。Result IIM 为 1 不代表完整四元组正确。

严格数值检查使用完整字符串的 Decimal 数值相等，不使用包含关系、不取近似值、不去单位或改百分比：**6/6 数值一致，严格 Result P/R/F1 均为 1，严格 TDMR P/R/F1 均为 0。** 全部预测与 Gold 的数值两两检查中，官方模糊匹配与严格检查没有不一致项。

## 错误归因

- **Extraction 阶段：** 六个结果数值正确，数据集缩写与 Gold 的语义对应正确，未发现 Baseline 混入、数值漏抽或错绑。但抽取给出缩写及非标准 Task 名，尚未达到官方名称精确匹配条件。
- **Normalization 阶段：** Task 六次均成功，Dataset 六次均返回字符串 `None`，按官方集合成员判定转为 JSON null。没有出现“映射到了另一个合法 Dataset”的错绑；表现为无法建立名称对应关系。
- 六个失败回答均为 1 个输出 Token、正常 stop，**不是 15 Tokens 截断**。实际请求包含完整 71 个名称，正确全称均在集合里；没有发送论文内缩写定义。孤立缩写缺少语境可能导致匹配失败，这是基于输入的解释性推断，不能证明模型内部原因。
- 没有删掉失败项、补填数据集、改 Prompt、扩大输出预算或追加修复请求。真实负面结果按原样保留。

完整逐条对照见 [evaluation/tdmr_comparison.md](evaluation/tdmr_comparison.md)，结构化记录见 `evaluation/tdmr_comparison.json`。

## 最终输出与完整性

- `normalization/normalized_output.json`：官方格式标准化结果。
- `normalization/normalization_api_usage.json`：全部 12 次请求、Token、耗时、返回模型、ID、原始回答及集合判断。
- `normalization/call-XX-request.json`、`call-XX-response.json`、`call-XX-attempt.json`：每次脱敏请求体、原始响应和单次标记；不保存 Authorization Header。
- `evaluation/eval_results.json`、`evaluation/eval_values.json`：原样官方指标。
- `evaluation/metrics_with_f1.json`：额外 F1，明确指标来源。
- `evaluation/strict_result_check.json`、`tdmr_comparison.json`、`tdmr_comparison.md`：严格检查与错误分析。
- `evaluation/verification.json`：源码、Prompt、原始抽取 config/output、预处理 pickle、source_documents 与标准化结果的完整性检查。
- `pilot/scripts/evaluate_gpt41_single_paper.py`：可复核的离线评测入口，不联网、不读取密钥。

全部内容位于 `D:\C++\SCILEAD\pilot\outputs\gpt41_single_paper`。官方仓库 Git clean，核心源码、Prompt、原始 output.json 和 processed_docs.pkl 均未变。标准化 API 调用的执行状态为 COMPLETE；评价阶段网络访问被禁止。

## 是否扩展实验

**工程上已具备扩展到总计 3 篇论文的条件**，建议沿用相同方法继续小样本验证，并单独记录缩写导致的标准化失败、PDF 表格质量、调用次数和阶段指标。保持本篇的失败结果作为基线，不先修复再宣称忠实复现。

**尚不能凭这一篇结果认定 43 篇的质量与成本可控。** 先完成另外两篇并审查阶段性失败率、请求量和资源用量，再决定是否正式全量运行；本次没有处理其他论文。若另行研究上下文增强或别名映射，应作为独立方法变体，不能混入本轮官方方法结果。

---

## 以下为执行前预检查记录（历史快照）

以下“预计”“待确认”描述保留当时状态；用户随后已授权并完成上述真实执行。

## 预检查结论

Gold 来源：`C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\tdm_annotations.json`。

SHA256：`603dd077ae174e4beefc24a9a73b7436e1e3cb6c9aaee042adc4d4aa5ea75aaf`。文件与第三阶段保存的 Gold 逐字节一致。结构为“论文文件名 → PaperURL / TDMs”，每条 TDM 含 Task、Dataset、Metric、Result，符合官方要求。

- 完整数据：43 篇论文，295 条 TDMR。
- 标准名称集合：23 个 Task、71 个 Dataset、26 个 Metric，全部由完整 Gold 构造，没有只用目标论文筛选。
- 目标论文：`2020.findings-emnlp.378.pdf`，论文 ID 完全一致；Gold 6 条，抽取 JSON 可解析为 6 条。
- 原始抽取及 `source_documents` 保留原文件，不重新解析 PDF、不重新抽取或检索。

## 原始预测与调用计划

以下六条 Task 均为 `Named Entity Recognition`，不与标准名称 `Named Entity Recognition (NER)` 完全一致。Metric 均为 `F1`，已在标准集合中。下表中的 Result 是原始字符串，不送入 Normalization Prompt，也不做标准化。

| 记录 | 原始 Task | 原始 Dataset | Metric | Result | Task 调用 | Dataset 调用 |
|---|---|---|---|---|---:|---:|
| 1 | Named Entity Recognition | ON5E | F1 | `90.32` | 1 | 1 |
| 2 | Named Entity Recognition | WN16 | F1 | `55.14` | 1 | 1 |
| 3 | Named Entity Recognition | WN17 | F1 | `50.68` | 1 | 1 |
| 4 | Named Entity Recognition | ON4C | F1 | `81.18` | 1 | 1 |
| 5 | Named Entity Recognition | RE | F1 | `96.62` | 1 | 1 |
| 6 | Named Entity Recognition | WE | F1 | `69.78` | 1 | 1 |

**预计 12 次 API 请求：Task 6 次 + Dataset 6 次 + Metric 0 次。** 低于用户设置的 18 次上限。六个 Dataset 缩写均不与标准名称集合完全匹配。

Task 输入重复 6 次，理论上使用缓存可以将总请求数减少为 7 次，但官方代码没有缓存。本次将保留 12 次原始逐字段调用，不引入缓存。

## Token 与费用风险

- o200k_base 本地估算：12 次输入总计约 **4,502 Tokens**；逐次估算保存在 `normalization/request_plan.json`。
- 每次 max_tokens=15，保持官方 CLI 默认值；12 次输出上限合计 **180 Tokens**。输入估算加输出上限约 **4,682 Tokens**，实际以各响应 usage 为准。
- 服务商 `https://9527.codes/v1` 的价格、最低计费粒度、失败请求收费策略和平台账单未验证。因此不能承诺具体人民币或美元费用，也不把 LangChain 的美元估算当作账单。
- 15 Tokens 可能导致模型的多余解释或长回答截断；如发生，将记录 finish_reason，保持原样，不提高上限、不重试。
- API 错误立即停止后续调用，保存已完成请求记录；持久标记阻止自动重跑。若调用中途停止，最终 normalized_output.json 可能尚未生成，不能把部分结果伪装为完整成功。
- seed=0、temperature=0。上阶段服务商接受过 seed 参数，但是否实际使用以及确定性均未验证。

## 官方方法与适配边界

已核对 `tdm_llm_normalization.py`、`tdm_eval.py`、`prompting.py`、`utils.py`、`model_init.py`、`prompts.json`。官方提交仍为 `8bf74b0a830feb7035c6166dce3394dc344ae532`。

独立脚本 `pilot/scripts/normalize_gpt41_single_paper.py` 默认仅运行免费预检查。付费入口 `--execute` 只在用户确认后使用。

该脚本直接调用**未修改的官方 `tdm_llm_normalization.main`**，仅在进程内适配：

1. 原始 config 读取结果补充 `is_few_shot=False` 和官方 GPT Prompt 分支名 `gpt4-turbo-128k`；不写回抽取 config.json。
2. 将 LLM 初始化替换为现有 langchain-openai 0.1.2 的 ChatOpenAI，固定模型 `gpt-4.1-2025-04-14`、指定中转接口、temperature=0、seed=0、max_tokens=15、max_retries=0。
3. 保留官方 normalization-system-prompt 和 GPT ChatPromptTemplate 的 system/user 消息、空白与模板文本。
4. 保留 `str(set)` 的名称集合序列化方式；设置 PYTHONHASHSEED=0 固定 Python 集合遍历顺序，避免免费计划和实际请求的名称顺序因新进程不同。不改为排序列表、不删减集合。
5. 每次实际消息与免费计划逐字比较，记录原始回答、参数、Token usage、请求耗时、响应模型 ID、可用的请求 ID，以及答案是否精确属于标准集合。

官方 GPT 分支直接对回答作集合成员判断：**不去空白、不去引号、不手工纠正；集合外回答变为 Python None（JSON null）**。Result 经过原始 `str(...)` 分支保留字符串。

发送内容只有当前字段的完整标准名称集合，以及当前预测字段值。不会包含论文 ID、结果数值、Gold TDMR 组合、其他字段的对应关系或 PDF 证据。标准集合由完整 Gold 得到，属于官方方法本身；没有借用目标论文的正确配对指导模型。

## 已完成的免费验证

- 官方循环通过内存模拟 LLM 测试：准确产生 12 次模拟调用，其中重复 Task 6 次；F1 跳过调用；Result 字符串保持不变；非法回答按官方规则转为 None。
- 模拟预测仅存在于内存，没有写成真实 normalized_output.json，没有网络或付费模型请求。
- 证据见 `normalization/offline_official_loop_test.json`。
- 预检查与付费记录分开；当前 `normalization_api_usage.json` 的实际请求次数为 0。

## 确认后执行的 Evaluation

待真实 Normalization 完成后，使用原始 `tdm_eval.py`，Gold 仍读取完整文件，但预测文件只有目标一篇，官方循环仅评价这一篇。

官方直接提供 Task / Dataset / Metric / Result Individual Precision、Recall，TDM Exact Match Precision、Recall（wo Results）和 TDMR Exact Match Precision、Recall。保留 `eval_results.json` / `eval_values.json` 原始内容，再另算 F1=2PR/(P+R)；分母为零时额外 F1 记 0。

注意：官方 `eval_values.json` 的 TDM Precision 字段存在名称拼写问题 `Exact Match Recall wo Precision`，其值实际来自 precision_scores_wo_results；本次保留原名并在分析报告解释，不修改官方实现。

官方 Result IIM 与 TDMR 的 Result 判定都允许双向字符串包含关系。将另外使用严格十进制数值相等检查，并检查字段绑定、重复和额外记录。官方指标不被严格检查结果替换。

标准化后再生成逐条 Gold 对照表和错误类型分析。本轮预检查不预设模型会得到六条正确映射，也不提前填入标准化后字段或评测分数。

## 本阶段已新增文件

- `pilot/scripts/normalize_gpt41_single_paper.py`
- `normalization/preflight_report.json`
- `normalization/request_plan.json`
- `normalization/standard_name_sets.json`
- `normalization/config.json`
- `normalization/normalization_api_usage.json`
- `normalization/offline_official_loop_test.json`
- `normalization/run.log`
- 本报告 `normalization_eval_report.md`

**待用户确认：是否按上述配置执行最多 12 次收费 Normalization 请求，并在完成后进行不收费的官方 Evaluation 与逐条错误分析。**
