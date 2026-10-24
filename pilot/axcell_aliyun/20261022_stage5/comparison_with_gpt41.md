# 同范围与冻结GPT-4.1结果比较

双方都使用同一37篇（含9篇AxCell零预测），相同完整候选名称集合和官方评价函数。GPT-4.1只读取冻结full43_uncapped预测，不重新调用模型。排行榜为原27榜按37paper IDs限制后的119条Gold记录，不重新应用>=3筛选（其中2榜剩2条），两种方法使用相同分母。

| 指标 | AxCell + GPT-4.1 Fully F1/% | GPT-4.1 Extraction + Fully F1/% | 差值/百分点 |
|---|---:|---:|---:|
| Task IIM | 61.4785 | 97.4299 | -35.9514 |
| Dataset IIM | 36.4741 | 80.7638 | -44.2897 |
| Metric IIM | 50.8831 | 84.4049 | -33.5218 |
| Result IIM | 23.4455 | 70.0386 | -46.5930 |
| TDM Exact Match | 21.6759 | 61.3196 | -39.6437 |
| TDMR Exact Match | 10.6283 | 42.0561 | -31.4278 |

| 排行榜指标 | AxCell/% | GPT-4.1/% |
|---|---:|---:|
| LR_exact_TDM | 29.6296 | 81.4815 |
| valid_nonempty_board_rate | 29.6296 | 74.0741 |
| PC_official | 14.7082 | 47.4299 |
| RC_official | 7.7385 | 31.4422 |
| RBO_official_numeric_lists | 6.7726 | 18.4660 |
| AO_paper_ID_supplementary | 9.6842 | 32.5617 |
| strict_joint_paper_result_coverage | 7.4018 | 31.4422 |

这是同一当前可运行论文集合上的描述性比较；AxCell输入为既有特定TeX版本，GPT-4.1为先前PDF证据，输入模态/版本、抽取模型与原始覆盖均不同。不能把差值归因为单一标准化因素，也不能与GPT-4.1全43篇分数作相同分母比较。无重新抽取、无方法优化。
