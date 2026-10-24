# AxCell Extraction + GPT-4.1 Fully Normalization：P5完成报告

本轮37/37可运行论文标准化及官方评价完成，28篇非空、9篇VALID_EMPTY，65条原始记录无增删。P4获用户“同意，可以进入下一阶段”后执行。123/123请求HTTP200，返回模型均为gpt-4.1-2025-04-14、finish_reason均stop；无失败、无重试、无用量未知请求。API成功不代表预测正确。

## 设置与实际调用

直接复用P3 AxCell结果，未重新解析、抽取或加载AxCell模型。原Prompt和23 Task/71 Dataset/26 Metric集合及顺序不变；官方tdm_llm_normalization.main逐字段处理，仅在独立适配层替换模型初始化。temperature=0、seed=0、n=1、stream=false；123个实际HTTP payload逐项等于P4清单，均没有max_tokens/max_completion_tokens/max_output_tokens、tools、response_format。固定seed已接受，不声称服务端完全确定性。

123次中84个有效集合映射，39个null（Task4/Dataset17/Metric18），另外72字段精确命中原样保留。重复名称没有缓存去重。Result字符串、顺序、65条来源及9篇空输出全部保留。来源原表另有可追溯索引，不加入标准化请求。

实际输入41,714、输出454、总计42,168 Tokens；标准化批次墙钟323.717秒（5.40分钟），请求耗时合计299.798秒。按P4核实的OpenAI公开参考价计算$0.087060；9527.codes实际账单/价格仍未知，不能称为实际已扣费。官方callback生成的成本文件不作为中转站账单。所有状态、请求ID（服务端未提供时为null）、响应ID、模型、usage和原始回答均保留。

## 官方tuple指标

范围为37篇/248条Gold，9篇零预测进入分母。使用完整43篇Gold文件、官方函数按输出37篇计算Macro P/R；F1额外由聚合P/R计算，不是逐篇F1算术平均。

| 指标 | Precision/% | Recall/% | F1/% |
|---|---:|---:|---:|
| Task IIM | 67.1171 | 56.7139 | 61.4785 |
| Dataset IIM | 54.0541 | 27.5228 | 36.4741 |
| Metric IIM | 59.3694 | 44.5195 | 50.8831 |
| Result IIM | 41.6216 | 16.3190 | 23.4455 |
| TDM Exact Match | 33.9640 | 15.9172 | 21.6759 |
| TDMR Exact Match | 16.8468 | 7.7628 | 10.6283 |

## Leaderboard

原27个Gold榜限制到同37paper IDs后剩119条；其中两榜剩2条，不重复应用>=3阈值。官方PC/RC/数值列表RBO保持原实现和重复预测最后赋值行为；LR、有效非空榜率、论文ID AO为复用既有辅助实现，AO并列按paper ID字典序，空榜0，全部27榜Macro。

| 指标 | 结果 |
|---|---:|
| LR_exact_TDM | 29.6296% |
| valid_nonempty_board_rate | 29.6296% |
| PC_official | 14.7082% |
| RC_official | 7.7385% |
| RBO_official_numeric_lists | 6.7726% |
| AO_paper_ID_supplementary | 9.6842% |
| strict_joint_paper_result_coverage | 7.4018% |

## 严格诊断与比较

严格数值一对一Result IIM F1=22.5755%，严格TDMR F1=9.7786%，仅补充诊断，不替代官方分数。不缩放、不去百分号、不将字符串包含视为数值相等；65条原记录保留。

同37篇冻结GPT-4.1 Extraction + Fully：Result IIM F1=70.0386%，TDM F1=61.3196%，TDMR F1=42.0561%。只离线复算既有预测，没有新GPT抽取。详细P/R及排行榜对照见comparison_with_gpt41.md及对应JSON。

原论文AxCell TDMR F1=19.26%、TDM F1=35.12%、Result IIM F1=26.18%，使用作者36篇和GPT-4 Turbo；本地范围/TeX版本/标准化模型/客户端上限/索引语料等不能确认完全一致，因此只作描述性比较，不做严格因果归因。见comparison_with_paper.md。

三例已知错误（Recall91.85误绑F1、实体数4696、向量维度300误作分数）保留。官方包含匹配的两对差异及逐Gold类别见inspection/findings.md、evaluation/tdmr_comparison.md和strict_diagnostics.json。此处不计算完整Baseline混入率或Dev/Test错误率。

## 论文范围及逐篇结果

作者原36篇成员仍UNVERIFIED；不将本地37篇称为作者36篇严格复现。39篇TeX中两篇解析失败1905.03197.pdf与2203.16804.pdf保留未运行；另4篇尚无已核实TeX。37/39输入流程覆盖与37/43数据集覆盖单独报告；未静默删除失败项，未给它们编造标准化结果。

| 论文 | Gold | 预测数 | 请求数 | null字段 | Result IIM F1/% | TDM F1/% | TDMR F1/% | 标准化状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1911.10390.pdf | 8 | 6 | 15 | 8 | 57.14 | 0.00 | 0.00 | COMPLETE |
| 2001.04063.pdf | 9 | 3 | 9 | 4 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1905.03197.pdf | 26 | — | 0 | — | — | — | — | NOT_RUN_UPSTREAM_FAILURE_OR_NO_INPUT |
| 1912.08777.pdf | 36 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1906.05012.pdf | 3 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 2203.16804.pdf | 9 | — | 0 | — | — | — | — | NOT_RUN_UPSTREAM_FAILURE_OR_NO_INPUT |
| 1910.13461.pdf | 25 | 2 | 3 | 0 | 14.81 | 7.41 | 7.41 | COMPLETE |
| 1908.08345.pdf | 9 | 2 | 6 | 2 | 36.36 | 0.00 | 0.00 | COMPLETE |
| 1808.08745.pdf | 3 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 2020.findings-emnlp.378.pdf | 6 | 1 | 2 | 1 | 28.57 | 0.00 | 0.00 | COMPLETE |
| 1809.08370.pdf | 8 | 5 | 10 | 4 | 30.77 | 30.77 | 30.77 | COMPLETE |
| 1806.03489.pdf | 2 | 2 | 4 | 1 | 50.00 | 50.00 | 50.00 | COMPLETE |
| 1702.02098.pdf | 2 | 1 | 2 | 1 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1511.08308.pdf | 2 | 2 | 4 | 1 | 0.00 | 50.00 | 0.00 | COMPLETE |
| 2020.emnlp-main.523.pdf | 11 | 2 | 0 | 0 | 15.38 | 30.77 | 15.38 | COMPLETE |
| 2105.03654.pdf | 7 | 4 | 6 | 2 | 54.55 | 36.36 | 18.18 | COMPLETE |
| 128538.pdf | 4 | — | 0 | — | — | — | — | NOT_RUN_UPSTREAM_FAILURE_OR_NO_INPUT |
| 1903.07785.pdf | 11 | 4 | 6 | 0 | 26.67 | 26.67 | 26.67 | COMPLETE |
| D19-1367.pdf | 2 | — | 0 | — | — | — | — | NOT_RUN_UPSTREAM_FAILURE_OR_NO_INPUT |
| C18-1139.pdf | 4 | — | 0 | — | — | — | — | NOT_RUN_UPSTREAM_FAILURE_OR_NO_INPUT |
| D18-1279.pdf | 6 | 2 | 5 | 1 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1703.06345.pdf | 5 | 3 | 7 | 1 | 75.00 | 25.00 | 0.00 | COMPLETE |
| 1603.01354.pdf | 4 | 3 | 6 | 2 | 28.57 | 28.57 | 28.57 | COMPLETE |
| 1709.04109.pdf | 3 | 1 | 3 | 0 | 50.00 | 0.00 | 0.00 | COMPLETE |
| 2008.07772.pdf | 6 | 1 | 2 | 1 | 28.57 | 0.00 | 0.00 | COMPLETE |
| 1911.09483.pdf | 4 | 1 | 1 | 0 | 40.00 | 40.00 | 40.00 | COMPLETE |
| 1901.10430.pdf | 8 | 3 | 9 | 3 | 54.55 | 0.00 | 0.00 | COMPLETE |
| 2002.03184.pdf | 7 | 1 | 2 | 1 | 25.00 | 0.00 | 0.00 | COMPLETE |
| wang19f.pdf | 5 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1804.09849.pdf | 2 | 1 | 2 | 0 | 0.00 | 66.67 | 0.00 | COMPLETE |
| D18-1523.pdf | 3 | 2 | 6 | 6 | 40.00 | 0.00 | 0.00 | COMPLETE |
| 1905.12598.pdf | 6 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1811.09242.pdf | 6 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1812.10235.pdf | 8 | 2 | 2 | 0 | 0.00 | 40.00 | 0.00 | COMPLETE |
| 2020.emnlp-main.152.pdf | 6 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1909.02188.pdf | 6 | 4 | 4 | 0 | 0.00 | 80.00 | 0.00 | COMPLETE |
| 1907.00390.pdf | 6 | 1 | 1 | 0 | 0.00 | 28.57 | 0.00 | COMPLETE |
| 1812.09471.pdf | 6 | 4 | 4 | 0 | 20.00 | 80.00 | 20.00 | COMPLETE |
| D18-1105.pdf | 2 | — | 0 | — | — | — | — | NOT_RUN_UPSTREAM_FAILURE_OR_NO_INPUT |
| N19-1373.pdf | 2 | 1 | 1 | 0 | 66.67 | 66.67 | 66.67 | COMPLETE |
| K19-1036.pdf | 3 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1811.05021.pdf | 2 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | COMPLETE |
| 1711.05568.pdf | 2 | 1 | 1 | 0 | 66.67 | 66.67 | 66.67 | COMPLETE |

## 完整性与工程记录

P3/P4及此前受保护文件3847份、历史用量参考文件1626份哈希保持一致；冻结full43_uncapped共1167文件及清单核验一致；7个E盘模型/词表匹配冻结值。未修改官方源码、Prompt、Gold、原解析产物或既有实验。无SSH、Docker或模型实验启动。

独立代码复核发现两个编排校验缺口：合并副本需与已校验官方输出比较；测试通过状态须来自实际执行记录。已补齐并经测试验证，未发现输出损坏，未重跑任何API。最终三组离线测试共11项通过（网络mock、严格诊断、合并一致性）。历史版运行入口与最终版的差异仅为输出一致性保护，不涉及方法或请求参数。

官方评价导入依赖时有HF缓存路径权限提示和LangChain旧入口警告，评价退出码0；无网络模型下载、未升级依赖。保持原结果，未为警告重跑付费请求。

输出根目录 `D:\C++\SCILEAD\pilot\axcell_aliyun\20261022_stage5`；E盘同步目标 `E:\SCILEAD\axcell\reports\20261022_stage5`，以sync_verification.json为准。后续只可读取已有成功请求检查点，禁止再次生成挑选结果。批次已完成并停止，不自动进入其他实验。
