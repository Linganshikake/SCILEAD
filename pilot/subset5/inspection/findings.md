# 五篇 Baseline 的错误现象核验

本记录只描述实际输出，不修正预测，不改变 Prompt、解析方式或候选集合。只渲染已下载 PDF 的六页进行目视核验，没有重新调用 partition_pdf，也没有额外模型请求。

## 1709.04109.pdf：mean 与 maximum 混淆

PDF 第 5 页 Table 4 中，作者方法 LM-LSTM-CRF 的 NER mean=91.71，max=91.85；第 6 页 Table 5 的 POS mean=97.53，maximum=97.59；Table 7 的 Chunking mean=95.96，maximum=96.13。模型抽取的是三个 mean，Gold 是三个 maximum，故 Result IIM=0。

这是作者方法的不同统计口径，不能简单称为 Baseline 混入。两个 Dataset 名称 `CoNLL03 NER`、`WSJ` 又被标准化为 null。官方输出均保留。

表格解析也出现列/标题对应异常：第 6 页两个并排表格的实际内容与附加的 Table 6 / Table 8 标题对调；部分行标签或最大值在文本展平中缺失。没有通过重新排序或 OCR 修复修改输入。

核验图：[第 5 页](1709.04109-page-5.png)、[第 6 页](1709.04109-page-6.png)。

## D18-1279.pdf：名称标准化丢失

六个抽取结果值与 Gold 一致，五条 TDMR 最终完整匹配。`Penn Treebank WSJ` 被标准化为 null，造成最后一条 POS 记录失败；该篇 TDMR F1=0.833333。没有把名称集合内的映射自动当作语义正确，而是结合官方逐条评价核对。

## 2020.emnlp-main.523.pdf：Dev / Test 选择与漏项

第 7 页 Table 4 的 LUKE 行，ReCoRD Dev EM/F1=90.8/91.4，Test EM/F1=90.6/91.2。模型取了 Dev，Gold 取 Test。

第 8 页 Table 5 的 LUKE 行，SQuAD Dev EM/F1=89.8/95.0，Test EM/F1=90.2/95.4。模型同样取了 Dev。都是作者方法数值，但实验 split 与 Gold 不一致。

模型还遗漏 Open Entity 与 TACRED 的 Precision/Recall，只输出各自 F1。`CoNLL-2003` 被标准化为 null。因此 11 条 Gold 只抽取出 7 条，其中仅 2 条最终 TDMR 匹配，F1=0.222222。

核验图：[第 7 页](2020.emnlp-main.523-page-7.png)、[第 8 页](2020.emnlp-main.523-page-8.png)。

## 1905.03197.pdf：表格合并、标题关联及跨指标错绑

- 第 7 页并列的 Table 5、6、7 被合并成一个 Table 区域，SQuAD 和 CoQA 的不同任务/模型结果展平后相邻。
- 第 8 页 Table 9 中真实存在增强训练后的 SQuAD EM/F1=84.7/87.6；这两个数值没有出现在实际送入模型的证据中。输出中的 90.0、87.7 则与 GLUE 表内 MRPC F1 / STS-B 相关性数值相同，却被绑定为 SQuAD QA 的 F1 / EM，属于可观察的跨字段错绑，不能据数值存在认定抽取正确。
- 第 8 页 Table 10 是 DSTC7 response generation，但缓存中附加了 Table 9 的标题。模型将 9.195（表中 Entropy-4）绑定为 METEOR，而 Gold METEOR=8.27。
- Question Generation 的 BLEU-4 输出 25.61；PDF 的 25.61 位于 METEOR 列，BLEU-4 的对应最佳值是 23.75。模型还选择了另一实验分组的 METEOR=25.06。
- GLUE 部分存在 Baseline 混入/错列：模型输出 SST-2=94.9（PDF Table 11 中 BERT LARGE，而 UNILM=94.5），MRPC=92.7、STS-B=89.3 也与正确列不一致。
- Gold 的三个 ROUGE 名称拼为 `ROGUE-1/2/L`。原始模型输出 `ROUGE-1/2/L`，本轮标准化均返回 None，按官方逻辑保存 null；未修正 Gold 拼写，也未补充映射规则。

该篇返回 20 条合法 JSON 记录，finish_reason=stop，**没有 1024 Tokens 截断**，但 Gold 有 26 条且存在大量漏项、额外结果、绑定错误与标准化 null。不能把 JSON 合法视为信息完整。

核验图：[第 7 页](1905.03197-page-7.png)、[第 8 页](1905.03197-page-8.png)。Table 11 的归因以缓存原始表格文本与列标签核对；本轮未逐单元格核验全部论文。

## 官方数值匹配的边界

五篇的官方双向字符串包含匹配与完整字符串 Decimal 数值相等，逐预测 / Gold 数值两两比较均未出现不一致。但 `1905.03197.pdf` 中若数值错绑到了另一任务，Result IIM 仍可能命中该论文其他 Gold 数值；严格数值相等也不能代替 Task-Dataset-Metric-Result 绑定检查。

原有 `2020.findings-emnlp.378.pdf` 的 Figure 3 误检和 Dataset 全 null 结果直接复用，没有重跑。
