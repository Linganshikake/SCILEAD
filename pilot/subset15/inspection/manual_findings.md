# 新增论文的可核查错误样例

仅在模型返回后对照 Gold、原始证据和 PDF 页面。本文件不用于生成输入，未据此修改预测或重新请求。渲染既有 PDF 页面只用于查看，不重新执行 partition_pdf。

## 1702.02098.pdf：非纯数值字符串及模型行差异

模型返回 `90.65 ± 0.15` 和 `86.84 ± 0.19`。第 8 页 Table 4/5 的 ID-CNN=90.65；Table 7 的 ID-CNN-CRF=86.84，而 Gold=86.99 对应该表 Bi-LSTM-CRF 行。这里应记录所选模型行与 Gold 不一致，不能把所有差异都归为幻觉，也不能忽略 Gold 与论文提出方法边界的差异。

`CoNLL-2003` 和 `OntoNotes` 都被标准化为 null。官方 Result 包含匹配能匹配 `90.65`，而完整字符串 Decimal 严格相等不匹配 `90.65 ± 0.15`；原始 Result 未被去除误差项。

页面核验：[第 8 页](1702.02098-page-8.png)。

## 2020.emnlp-main.152.pdf：方法变体选择、Baseline 和错列

第 5 页 Table 3：ATIS Slot 的最佳值是 SlotRefine with GloVe=96.24，模型选择同方法 BERT 变体的 96.16。Snips Slot 的正确值是 97.05；模型输出的 99.00 实际位于 Baseline `Stack-Propagation with BERT` 的 Snips Intent 列，同时出现 Baseline 混入和 Metric 绑定错误。

两条 Sentence-level Joint Accuracy 的 Task 标准化为 null；这些记录的 88.64 / 92.96 数值本身正确。原始表格缓存按列展平，Snips Slot 与 Intent 数值相邻且行顺序难恢复；没有重新排列模型证据。

页面核验：[第 5 页](2020.emnlp-main.152-page-5.png)。

## 2105.03654.pdf：Metric 误标、Dataset 错绑和实验子项

抽取前七条将 Metric 统一写成 Accuracy，Gold 为 F1。由于 Accuracy 已属于官方标准名称集合，官方标准化直接跳过，不能纠正这种语义错误。

第 7 页 Table 2 缓存中 CoNLL-03 最佳值为 93.56，CoNLL++ 为 94.81。抽取把 94.81 绑定到 CoNLL-03，并选 94.62 作为 CoNLL++。NCBI 取 89.22 而非 Gold 89.24；E-commerce 输出 84.10，与主表 Gold 83.99 不同。该表按列展平，保留原状。

额外抽取第 7 页不同实验子项的 76.38（跨域测试）和 Table 5 的 62.29（re-ranking BEST）。跨域 Dataset 经过标准化从 `CBS SciTech News (trained on CoNLL-03)` 变成 `CoNLL-2003 - English`，把训练语料名称当成了标准 Dataset；这种集合内映射不等于语义正确。

以上归因基于保存的 table-documents 与逐条输出；未逐单元格人工复核所有表格。

## 1910.13461.pdf：BERT Baseline 混入及多指标漏项

第 6 页 Table 2 的 BERT 行 SQuAD F1=90.9、MNLI-m=86.6 被抽取为本论文结果；BART 行对应为 94.6、89.9。Gold 的大量 GLUE、SQuAD 指标未抽取。表格缓存保留了 BART 值，但最后几列 STS-B / RTE / MRPC / CoLA 的标题在展平文本中缺失；完整 PDF 图像能看到这些标题。

摘要与 ELI5 的多项 ROUGE 数值抽取正确，但因标准集合拼写为 ROGUE，九个 ROUGE 字段标准化为 null。13 条输出少于 25 条 Gold，finish_reason=stop，并非输出长度截断。ConvAI2 仅抽取 PPL=11.85，漏掉 F1=20.72。

页面核验：[第 6 页](1910.13461-page-6.png)。

## D18-1105.pdf：正确数值被 Dataset 标准化阻断

两条原始数值 83.1 / 86.7 均与 Gold 相同。`SwDA` 的标准化原始回答为 `None`，于是保存 null；`MRDA` 成功映射到 `ICSI Meeting Recorder Dialog Act Corpus (MRDA)`。四次调用均 finish_reason=stop，Dataset 失败不是 15 Tokens 截断所致。

## 1703.06345.pdf：表头缺失、跨任务错绑和 Baseline 数值

第 8 页 Table 3 在 PDF 中包含 CoNLL 2000 / CoNLL 2003 / Spanish / Dutch / PTB 2003 表头，但这些表头没有保留在实际 Table 文本中。抽取把 CoNLL 2000 Chunking 的 95.41 绑定为 PTB POS Accuracy；Chunking 又选择未使用迁移的 94.66。英语 NER 取 Ma & Hovy Baseline 的 91.21，而作者行是 91.26。

西班牙语和荷兰语的 85.77 / 85.19 正确；另输出 Genia、Twitter 的实验结果，未包含在本篇 Gold 中。以上均保留，没有修复表头或重跑。

页面核验：[第 8 页](1703.06345-page-8.png)。

## 1903.07785.pdf：表题错配导致跨任务绑定；实验设置选择差异

第 6 页 Table 3 的 NER test F1=93.5，Table 4 的 Constituency Parsing test F1=95.6。缓存却给后者附加了 Table 3 的 NER 标题，模型因此输出 NER=95.6，并漏掉独立的 Constituency Parsing 记录。

CoLA=56.6 来自第 8 页 Table 6 的不同训练数据规模实验，Gold=53.1 对应主表；RTE=65.1 对应 BPE Large 变体，Gold=63.7 对应 CNN Large。此处记录实验分组/模型变体差异，不将它们无依据地统一归为 Dev/Test 混淆。

页面核验：[第 6 页](1903.07785-page-6.png)。

## 1912.08777.pdf：输入上限例外后的输出截断

55 页完整 PDF 解析出 44 个 Table 区域，48 条证据；输入 54,504 Tokens。原 30,000 上限触发时没有 API 请求。用户明确授权保留全部输入调用一次后，服务端 HTTP 200、Prompt Tokens=54,504、Completion Tokens=1,024、finish_reason=length。

输出在一个 TDMR 对象中途结束，json.loads 失败。保留原始字符串与响应，不从前半段修复数组，不提高输出上限，不重试，不标准化。该篇有 36 条 Gold，未进入官方指标分母，覆盖率明确为 14/15，不能称为完整 15 篇结果。

## 1711.05568.pdf：本次未发现 TDMR 失配

两条数值 81.3 / 91.7 及标准化后的 Task、Dataset、Metric 均与 Gold 对应。四次标准化调用都返回标准集合内的正确名称，没有 null；这只说明本次两条目标结果匹配，不代表人工验证了全文所有表格。

## wang19f.pdf：翻译方向与 Gold 标准名称不一致

五个 Result 数值均命中 Gold。最后一条原始 Dataset 为 `IWSLT2014 German-English (De→En)`，Gold 候选名称为 `IWSLT’14 EN-DE`，标准化返回 None，原样保存 null。其余四条完整匹配。此处记录翻译方向命名冲突，不通过手工逆转方向修正预测或 Gold。

## Dev/Test 分类的证据边界

新增论文中已确认数值/字段错绑、模型变体选择、实验分组选择、Baseline 混入及表头/表题异常；没有把未核实的差异直接归为 Dev/Test 混淆。旧五篇中既有 LUKE Dev/Test 错选记录原样保留，详见 subset5/inspection/findings.md。
