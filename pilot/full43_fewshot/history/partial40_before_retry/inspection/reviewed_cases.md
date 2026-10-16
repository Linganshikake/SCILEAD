# 已核查的证据案例

本文件仅在对应论文模型输出完成后用于离线分析，不参与模型输入，不改变任何预测。

## 1912.08777.pdf：更多条目来自另一个提出方法配置

Few-shot 返回 36 条，Zero-shot 返回 15 条，Gold 有 36 条。新输出按 12 个数据集 × 3 个 ROUGE 指标展开，数值对应冻结证据第 8 条（PDF 第 9 页 Table 4）的 **PEGASUSLARGE (mixed, stochastic)**。例如 XSum 为 47.60 / 24.83 / 39.64，WikiHow 为 46.39 / 22.12 / 38.41。

Gold 的 XSum 为 47.21 / 24.56 / 39.25，出现在冻结证据第 5 条（PDF 第 7 页 Table 1）的 PEGASUSLARGE (HugeNews) 行。Gold 其他结果取自 Table 1 中的 C4 / HugeNews 配置；例如 WikiHow 43.06 / 19.71 / 34.80 在该表可见。

因此，条目数量更多并不代表 Gold 数值召回更高。本例有直接证据支持“选择了另一种提出方法配置，与 Gold 所标注的结果口径不同”，不应笼统归类为 Baseline 混入或 PDF 表格识别错误。Table 4 的 BIGPATENT 脚注明确说明数据保留大小写并调整清洗，进一步提示实验配置差异。保留所有真实输出，不做替换。

对照 Zero-shot 后需进一步限定：Zero-shot 的前 12 条也对应 Table 4，只是每条把三个 ROUGE 结果合写为一个斜杠分隔的 Result（如 `47.60/24.83/39.64`）。Few-shot 将它们拆成 36 条独立指标记录。因此这里明确观察到的是 **Result/Metric 粒度变化**，不能把 Table 4 配置选择差异说成 Few-shot 新引入的错误。

## Result 表达粒度

直接按有限 Decimal 数值解析时，Zero-shot 有 39 条 Result 不能作为单个纯数值解析，Few-shot 为 13 条。减少的内容包括长论文的斜杠复合结果，以及若干 `±` 或括号标准差信息；Few-shot 仍保留 8 条百分号、C18-1139 的 4 条 `±` 结果和 D19-1367 的 1 条描述性结果。这里只记录表示方式，不对任何结果作数值清洗。严格数值辅助指标会受此影响，必须与原版字符串包含指标区分。

## 作者示例原有不一致

prompts.json 的 MATCHSUM 输入 Table 5 将 46.20 / 16.51 / 41.89 列为 Multi-News 结果；示例末尾三条输出却标为 WikiHow。实验完全保留该不一致及 ROGUE 拼写，没有自行纠正，也不能仅据此认定本轮某个预测错误由该示例导致。

## 1703.06345.pdf：字段绑定与基线数值

Few-shot 的 `POS Tagging / PTB / Accuracy = 95.41` 实际对应 Gold 的 Text Chunking / CoNLL-2000；其 `Chunking / CoNLL 2000 / F1 = 91.26` 实际对应 Gold 的 CoNLL-2003 NER。这两个数值本身在原文中存在，但 Task/Dataset 绑定错位，不能依靠名称标准化修复。

其 CoNLL-2003 NER 输出 91.21。冻结证据 #7（第 8 页 Table 3）按作者列出的模型顺序，NER 一列中 Ma & Hovy (2016) 为 91.21，Ours w/o transfer 为 91.20，Ours w/ transfer 为 91.26。因此该预测与基线数值一致，而非作者带迁移模型的结果。该表在线性化证据中列标题未明确保留，记录这一证据局限，不重新解析或修补表格。

新增 Twitter 83.65、Genia 92.62 来自证据 #6（第 7 页 Table 2）的低资源迁移实验；它们不是这篇 Gold 的五个 TDMR。属于新增实验设置结果，不应自动称作凭空编造。

## 2020.emnlp-main.152.pdf：多个实验配置与最优值/列绑定问题

Few-shot 从 6 条扩为 12 条：前六条对应证据 #6（第 3 页 Table 1）的基础 SlotRefine，后六条主要对应证据 #8（第 5 页 Table 3）的 BERT 配置。未只保留各指标最优值。

例如 ATIS Slot F1 输出 96.16（BERT），而同表 GloVe 配置有 96.24，后者为 Gold。Snips Slot F1 输出 99.00，而 Gold 为 BERT Slot F1 97.05；99.00 出现在同表 previous-work 的 Intent 数值区域。该错误涉及指标/行列绑定，不能把它当作合法名称映射问题。原表线性化内容及预测均保留。

## C18-1139.pdf：Dataset 表达更明确，TDMR F1 0.5 → 1.0

四条 Result 未改变。Zero-shot 把 English/German 写在 Task 中，两个 Dataset 均为 `CONLL03`，标准化均得到 null。Few-shot 把语言写入 Dataset（`CONLL03 English`、`CONLL03 German`），分别映射到 Gold 的英语和德语数据集，最终四条均符合官方匹配。这里观察到字段信息位置变化及后续映射变化，没有人工补充语言信息。

## D18-1105.pdf：抽取相同，但标准化模型答案变化，TDMR F1 1.0 → 0.5

两条原始 TDMR 的字段和值逐项相同。对 `SwDA` 的标准化请求，包括完整候选列表、Prompt、模型与采样参数在内的实际 HTTP JSON payload 经比较也完全相同（见 `normalization_repeat_variation.json`）。旧回答为 `Switchboard Dialog Act Corpus (SWDA)`，本次回答为 `None`。两次均返回同一快照名称并以 stop 结束。

因此本例分数下降发生在标准化模型回答阶段，不能归因于 Few-shot Extraction Prompt 改变了输入。固定 seed/temperature 不构成完全确定性的实证保证；不据此推断服务商使用了其他模型，也不重新生成答案来恢复分数。
