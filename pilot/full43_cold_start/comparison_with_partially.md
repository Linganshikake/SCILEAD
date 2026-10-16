# 与已冻结 Baseline 的描述性对比

全部数据从原始评测 JSON 读取；路径和哈希见 summary/baseline_comparison.json。不同实验的名称候选协议不同，以下仅作描述性对比，不是单因素因果实验。

## 全部 27 榜
| Baseline | LR | 有效非空榜率 | PC | RC | RBO | AO |
| --- | --- | --- | --- | --- | --- | --- |
| Fully + LLM | 0.814815 | 0.740741 | 0.487125 | 0.317989 | 0.247654 | 0.462500 |
| Fully + CS | 0.925926 | 0.888889 | 0.631570 | 0.411905 | 0.303420 | 0.522212 |
| Partially all27 | 0.481481 | 0.407407 | 0.133289 | 0.086067 | 0.110535 | 0.155802 |
| Cold Start 三轮均值 | 0.395062 | 0.395062 | 0.104159 | 0.080850 | 0.087514 | 0.113577 |

## 同一 Masked 10 榜
| Baseline | LR | 有效非空榜率 | PC | RC | RBO | AO |
| --- | --- | --- | --- | --- | --- | --- |
| Partially | 0.400000 | 0.400000 | 0.139048 | 0.114048 | 0.120667 | 0.120667 |
| Cold Start 三轮均值 | 0.300000 | 0.300000 | 0.118175 | 0.090794 | 0.102954 | 0.106657 |

未根据任何分数修改候选、Prompt、返回值或选择运行结果。

## 开放名称与 null 观察
Partially 阶段一最终候选规模：{'Task': 70, 'Dataset': 119, 'Metric': 26}；null 字段：{'Task': 0, 'Dataset': 1, 'Metric': 67}。
| Cold Start 运行 | 最终候选规模 | null 字段 |
| --- | --- | --- |
| order_default | {'Task': 66, 'Dataset': 114, 'Metric': 66} | {'Task': 0, 'Dataset': 0, 'Metric': 0} |
| order_0 | {'Task': 66, 'Dataset': 115, 'Metric': 61} | {'Task': 0, 'Dataset': 0, 'Metric': 0} |
| order_42 | {'Task': 64, 'Dataset': 112, 'Metric': 66} | {'Task': 0, 'Dataset': 3, 'Metric': 0} |

Partially 的 Metric 使用固定名称集合，Cold Start 则允许 Metric 原名新增，两者按作者各自协议执行。较少 null 不代表更高的语义正确率；候选别名分散和最终榜单对齐需要分别观察。
