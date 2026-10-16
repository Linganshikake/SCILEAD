# 作者完整 Few-shot Prompt 分支：标准化与评价

完成 43/43 篇，293/293 条原始预测；Gold 覆盖 295/295。新增 Extraction 请求为 0。

## Prompt 与方法
Extraction：few-shot-extraction-system-prompt，直接复用上一轮原始结果和 MATCHSUM 示例，未重新解析 PDF、生成嵌入或检索。Normalization：few-shot-normalization-system-prompt，is_few_shot=True，调用未经修改的官方 main 与 NormalizationPrompt。
作者的 Pos tagging、PTB、F1 score 三个示例原样嵌在 System 消息中一次；双花括号按原版机制渲染。示例名称集合保持静态，Human 消息使用当前字段的实际候选集合与原始名称。没有追加论文上下文或 Gold 对应关系。
候选集合 23 Task / 71 Dataset / 26 Metric；PYTHONHASHSEED=0，序列化顺序与 B 完全相同。426 个字段精确命中直接保留，453 个字段需调用模型，未使用跨记录缓存。只有原始回答精确属于候选集合才保留，否则为 null；不去空格或引号，Result 不变。

## API 与复现差异
gpt-4.1-2025-04-14，temperature=0、seed=0、stream=False；实际请求省略 max_tokens/max_completion_tokens/max_output_tokens，未添加 tools/response_format。尝试 453，成功 453，失败/不确定 0，自动重试 0。
Prompt 514,967，Completion 1,950，Total 516,917 Tokens；未知用量请求 0。HTTP 耗时合计 813.9 秒，执行墙钟 837.5 秒。旧 Extraction 请求和 B 的标准化请求均不计入本轮新增请求。第三方费用未按美元估算。
保留 GPT-4.1 替代 GPT-4 Turbo、取消作者默认输出上限的差异。数据版本使用冻结本地 Gold（SHA256 见 input_manifest/freeze_before），不声称与原论文数字完全相同。seed 被接口接受不保证完全确定性。

## 官方元组评价
P/R 为原版 tdm_eval.py 的逐篇 Macro；F1=2PR/(P+R)，不是逐篇 F1 算术平均。

| 指标 | C Precision | C Recall | C F1 | A F1 | B F1 |
| --- | --- | --- | --- | --- | --- |
| Task IIM | 0.958306 | 0.960871 | 0.959587 | 0.966900 | 0.959985 |
| Dataset IIM | 0.893868 | 0.880297 | 0.887030 | 0.800714 | 0.739938 |
| Metric IIM | 0.923984 | 0.882899 | 0.902974 | 0.853224 | 0.766650 |
| Result IIM | 0.724558 | 0.728170 | 0.726360 | 0.703841 | 0.726360 |
| TDM Exact Match | 0.784675 | 0.743762 | 0.763671 | 0.612160 | 0.491680 |
| TDMR Exact Match | 0.555116 | 0.559482 | 0.557291 | 0.421578 | 0.331236 |

Result 不变检查：官方 Result IIM F1=0.726360，严格数值辅助 F1=0.668220（P=0.666419，R=0.670030），均与 B 完全一致。严格指标使用同一有限 Decimal 相等方法，不清洗百分号或 ±，不替代官方字符串包含匹配。

## 排行榜评价（配套补充）
固定同一份 27 个 Gold 榜。PC/RC/数值列表 RBO 使用原版函数；LR 是数值转换前的标准 TDM 命中，有效数值非空率另列；AO 使用论文 ID 排名。保持后写覆盖、排序方向、并列规则、空榜计零与 Macro 分母。RBO 不等于 AO。

| 指标 | A | B | C |
| --- | --- | --- | --- |
| LR_exact_tdm_hit | 0.814815 | 0.740741 | 1.000000 |
| LR_nonempty_finite_result | 0.740741 | 0.740741 | 1.000000 |
| PC_official | 0.487125 | 0.423677 | 0.753131 |
| RC_official | 0.317989 | 0.282628 | 0.550000 |
| RBO_official_value_rankings | 0.247654 | 0.340514 | 0.496518 |
| AO_paper_id_macro_all_gold_boards | 0.462500 | 0.421502 | 0.672388 |

## 三组定义与映射变化
A. Zero-shot Extraction + Zero-shot Normalization；来源 D:\C++\SCILEAD\pilot\full43_uncapped
B. Few-shot Extraction + Zero-shot Normalization；来源 D:\C++\SCILEAD\pilot\full43_fewshot
C. Few-shot Extraction + Few-shot Normalization；来源 D:\C++\SCILEAD\pilot\full43_fewshot_both_prompts
C 对齐作者官方完整 Few-shot Prompt 分支，Table 7 的 ETM/IIM 对照应使用 C。B 保留为只改变抽取 Prompt 的实验，不能替代 C；无论分数高低都不选择性覆盖。排行榜级评价是配套补充。

| 设置 | Task null | Dataset null | Metric null | 总 null |
| --- | --- | --- | --- | --- |
| A | 5 | 51 | 63 | 119 |
| B | 15 | 51 | 77 | 143 |
| C | 17 | 25 | 25 | 67 |

B→C 映射变化：{"null_to_label": 81, "label_to_null": 5}
所有字段变化保存在 evaluation/comparison_of_three_settings.json，以 paper_id + 原始记录序号 + 字段关联。null→标签不自动等于语义正确，本文只记录变化，不进行科学因果归因。

| 论文 | 记录 | 字段 | 原始名称 | B | C |
| --- | --- | --- | --- | --- | --- |
| D18-1279.pdf | 6 | Dataset | Penn Treebank WSJ | None | Penn Treebank (PTB) |
| 1905.03197.pdf | 1 | Metric | ROUGE-1 | None | ROGUE-1 |
| 1905.03197.pdf | 2 | Metric | ROUGE-2 | None | ROGUE-2 |
| 1905.03197.pdf | 3 | Metric | ROUGE-L | None | ROGUE-L |
| 1905.03197.pdf | 7 | Dataset | SQuAD | None | SQuAD 1.1 |
| 1702.02098.pdf | 2 | Dataset | OntoNotes 5.0 | None | Ontonotes v5 - English |
| D18-1105.pdf | 1 | Dataset | SwDA | None | Switchboard Dialog Act Corpus (SWDA) |
| 1703.06345.pdf | 3 | Dataset | CoNLL 2003 | None | CoNLL-2003 - English |
| 1903.07785.pdf | 8 | Task | Single Sentence Classification | Linguistic Acceptability | None |
| 1903.07785.pdf | 10 | Dataset | CoNLL-2003 | None | CoNLL-2003 - English |
| 1912.08777.pdf | 3 | Metric | ROUGE-L F1 | None | ROGUE-L |
| 1912.08777.pdf | 4 | Metric | ROUGE-1 F1 | None | ROGUE-1 |
| 1912.08777.pdf | 35 | Metric | ROUGE-2 F1 | None | ROGUE-2 |
| wang19f.pdf | 5 | Dataset | IWSLT2014 De→En | None | IWSLT’14 EN-DE |
| 128538.pdf | 1 | Dataset | WNUT 2016 | None | WNUT-16 - English |

## 每篇结果

| 论文 | 条数 | B TDMR F1 | C Result F1 | C TDM F1 | C TDMR F1 |
| --- | --- | --- | --- | --- | --- |
| 2020.findings-emnlp.378.pdf | 6 | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| 1709.04109.pdf | 3 | 0.000000 | 0.000000 | 0.333333 | 0.000000 |
| D18-1279.pdf | 6 | 0.833333 | 1.000000 | 1.000000 | 1.000000 |
| 2020.emnlp-main.523.pdf | 7 | 0.222222 | 0.333333 | 0.666667 | 0.222222 |
| 1905.03197.pdf | 26 | 0.076923 | 0.461538 | 0.326531 | 0.230769 |
| 1702.02098.pdf | 2 | 0.000000 | 0.500000 | 0.500000 | 0.000000 |
| 2020.emnlp-main.152.pdf | 12 | 0.444444 | 0.444444 | 1.000000 | 0.444444 |
| 2105.03654.pdf | 8 | 0.000000 | 0.533333 | 0.000000 | 0.000000 |
| 1910.13461.pdf | 17 | 0.047619 | 0.619048 | 0.571429 | 0.380952 |
| D18-1105.pdf | 2 | 0.500000 | 1.000000 | 1.000000 | 1.000000 |
| 1703.06345.pdf | 7 | 0.333333 | 0.666667 | 0.909091 | 0.333333 |
| 1903.07785.pdf | 10 | 0.380952 | 0.761905 | 0.571429 | 0.380952 |
| 1912.08777.pdf | 36 | 0.000000 | 0.000000 | 1.000000 | 0.000000 |
| 1711.05568.pdf | 2 | 0.500000 | 1.000000 | 1.000000 | 1.000000 |
| wang19f.pdf | 5 | 0.800000 | 1.000000 | 1.000000 | 1.000000 |
| 128538.pdf | 4 | 0.500000 | 1.000000 | 1.000000 | 1.000000 |
| 1511.08308.pdf | 2 | 0.000000 | 1.000000 | 1.000000 | 1.000000 |
| 1603.01354.pdf | 2 | 0.333333 | 0.666667 | 0.666667 | 0.666667 |
| 1804.09849.pdf | 2 | 0.000000 | 0.000000 | 1.000000 | 0.000000 |
| 1806.03489.pdf | 2 | 0.500000 | 1.000000 | 1.000000 | 1.000000 |
| 1808.08745.pdf | 5 | 0.000000 | 0.750000 | 0.857143 | 0.750000 |
| 1809.08370.pdf | 8 | 0.000000 | 0.625000 | 0.875000 | 0.500000 |
| 1811.05021.pdf | 2 | 0.500000 | 1.000000 | 1.000000 | 1.000000 |
| 1811.09242.pdf | 6 | 0.500000 | 0.666667 | 0.333333 | 0.333333 |
| 1812.09471.pdf | 6 | 0.000000 | 0.833333 | 0.400000 | 0.000000 |
| 1812.10235.pdf | 8 | 0.500000 | 1.000000 | 1.000000 | 0.500000 |
| 1901.10430.pdf | 8 | 0.500000 | 1.000000 | 0.875000 | 0.875000 |
| 1905.12598.pdf | 6 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| 1906.05012.pdf | 3 | 0.000000 | 1.000000 | 1.000000 | 1.000000 |
| 1907.00390.pdf | 6 | 0.666667 | 1.000000 | 0.666667 | 0.666667 |
| 1908.08345.pdf | 9 | 0.000000 | 1.000000 | 0.666667 | 0.666667 |
| 1909.02188.pdf | 6 | 0.000000 | 0.000000 | 0.666667 | 0.000000 |
| 1911.09483.pdf | 4 | 0.750000 | 1.000000 | 1.000000 | 1.000000 |
| 1911.10390.pdf | 7 | 0.000000 | 0.533333 | 0.363636 | 0.266667 |
| 2001.04063.pdf | 9 | 0.222222 | 1.000000 | 0.777778 | 0.777778 |
| 2002.03184.pdf | 7 | 0.428571 | 1.000000 | 0.714286 | 0.714286 |
| 2008.07772.pdf | 10 | 0.625000 | 0.625000 | 1.000000 | 0.625000 |
| 2203.16804.pdf | 9 | 0.000000 | 1.000000 | 0.500000 | 0.444444 |
| C18-1139.pdf | 4 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| D18-1523.pdf | 2 | 0.400000 | 0.400000 | 0.800000 | 0.400000 |
| D19-1367.pdf | 2 | 0.500000 | 0.500000 | 0.500000 | 0.500000 |
| K19-1036.pdf | 3 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| N19-1373.pdf | 2 | 0.000000 | 0.000000 | 1.000000 | 0.000000 |

## 完整性与文件
43 篇通过原版标准化离线回放；39680 个历史文件 SHA256 未改变，官方源码、Prompt、Gold、依赖版本和 Git 状态未改变。B 与 C 原始抽取、证据、293 条记录及 Result 顺序全部一致。
核心产物：input_manifest.json、normalization/normalized_output.json、normalization/api_calls/、evaluation/、leaderboard_evaluation/、api_usage_summary.json、verification.json。历史实验文件未修改。
完成后停止，未启动 threshold=2 或其他实验。