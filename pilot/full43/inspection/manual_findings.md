# 原始输出错误现象复核

只对已返回模型结果的论文进行离线检查。以下根据保存的原始表格文本、页码、模型输出、标准化响应及 Gold 比较，不回写预测，不改变后续模型输入。表格文本来自已经完成的官方解析缓存，没有重新运行 PDF 解析。

## 128538.pdf：数值均命中，名称映射丢失

第 4 页 Table 1 的 Ours 行包含 53.48、50.52、93.76、74.17，四个原始 Result 均命中 Gold。`WNUT 2016`、`WNUT 2017` 的 Dataset 映射为 null；`Named Entity Recognition (Multimodal)` 的 Task 映射为 null。不能将四个数值命中等同于四条 TDMR 正确。

证据：`../papers/128538/preprocess/table-documents.json`；原始及标准化结果在该论文 `extraction/` 下，逐次返回内容在 `normalization/api_calls/`。

## 1511.08308.pdf：标准化失败与表格检测语义边界

原始抽取两个 F1 值 91.62、86.28，对应第 6 页 Table 5 作者 BLSTM-CNN + emb + lex 的结果，均与 Gold 一致。Dataset `CoNLL-2003`、`OntoNotes 5.0` 标准化均为 null。

第 4 页 Figure 4 的 lexicon feature 示例被保存为 Table 区域；它是带行列的示例而非结果表。这说明 Table 区域数量不等同于实验结果表数量。没有排除该证据。

## 1603.01354.pdf：检索中有数值，抽取遗漏指标

第 6 页 Table 3 的 Test NER 结果含 Precision=91.35、Recall=91.06、F1=91.21；原始抽取只返回 NER F1=91.21 与 POS Accuracy=97.55，遗漏两个 Gold 指标。91.35 和 91.06 均保留在实际表格证据中，因此这里不能归因于整个数值未进入检索上下文。

同页后续表格保存时，NER 模型比较内容附上了 Table 4 的 POS 说明段落；第 7 页 embedding 对比表又附上 Table 5 的 NER 说明段落。记录了标题/内容关联异常，但没有重关联或修正证据。

## 1804.09849.pdf：作者模型变体与 Gold 选择不同

Gold 采用 RNMT+ 的 41.00、28.49（第 6 页 Tables 1/2）。模型抽取第 8 页 Table 6 中作者混合模型的更高结果 `41.67 ± 0.11`、`28.84 ± 0.06`。这是模型变体/实验范围与 Gold 不一致，并保留了误差项，不能简单归为抄取他人 Baseline。没有改为 Gold 指定的 RNMT+ 行。

## 1806.03489.pdf：非 Gold 分体裁结果与误差项

两个总体 F1 被抽取为 `91.73 (± 0.10)`、`87.95 (± 0.13)`；官方字符串包含可以命中 Gold 的 91.73、87.95，严格 Decimal 相等不接受这些复合字符串。另抽取第 8 页 Table 6 的六个作者模型分体裁结果（86.33、90.46、85.91、89.75、76.17、80.39），而 Gold 只标注两个总体结果。它们属于额外实验结果，不能仅因不在 Gold 中便称为 Baseline 混入。

第 1 页作者机构信息被检测为一个 Table 区域；第 7 页 Table 4 保存的表格文本缺少末列实际数值，而第 9 页 Table 7 仍提供两个总体值。记录这些解析现象，不修复表格或过滤证据。

## 1809.08370.pdf：数值精度与字符串包含的差异

第 16 页 Table 5 给出的作者模型均值包括 96.05、96.98、92.61、88.81、97.74、96.61、95.02；翻译结果 29.58 出现在同表其他作者模型配置中。抽取保留这些精度，而 Gold 分别为 96.1、97.0、92.6、88.8、97.74、96.6、95.0、29.6。

例如 `92.6 in 92.61`、`95.0 in 95.02` 满足官方包含关系，但不是严格数值相等；另一些四舍五入相关值连包含关系也不成立。这里不能一概认定为模型捏造数值，因为相应精度的值实际存在于证据。另有五个 Dataset 映射为 null。没有四舍五入、修正或重新抽取。

## 1812.09471.pdf：Baseline/字段错位及联合指标

目视复核第 6 页 Table 3：CAPSULE-NLU 的 ATIS Intent Accuracy 为 0.950，模型返回 0.948；0.948 对应该列的 IntentCapsNet Baseline，也在相邻 Slot 列的其他行出现。因展平后的行列不充分，无法仅凭输出判定它具体取自哪一格，但可确认没有取对作者完整模型的 ATIS Intent 值。

模型把 Overall Accuracy 写入 Task，而 Metric 仍为通用 Accuracy；它已经在标准集合内，官方逻辑不会对该 Metric 再调用模型。原始联合任务与 Gold 的字段组织不同，不能靠数值命中认定整条正确。

截图：[第 6 页](1812.09471-page6.png)。只渲染已有 PDF 页面，没有重新解析或请求模型。

## 1812.10235.pdf：PDF 与 Gold 的 Home/Food 绑定不一致

目视复核第 5 页 Table 2，Food 行的作者模型是 F1=95.8%、Accuracy=99.49%；Home 行为 F1=98.2%、Accuracy=99.27%。原始抽取的对应关系与该 PDF 表格相同。但本地 Gold 将前一组标作 Multi-domain Home、后一组标作 Multi-domain Food，涉及四条 Gold。

因此这些对应不一致不能直接全部归咎于模型绑定错误。这里只记录当前 PDF 与 Gold 的差异，**不修改 Gold、不交换预测字段、不另行计算“修正后”得分**。原始 `%` 字符串继续保留，严格 Decimal 诊断不会去掉单位。

截图：[第 5 页](1812.10235-page5.png)。PDF 来源和 SHA256 见 manifest。

## 1908.08345.pdf：最佳作者变体漏项

第 7 页 Table 3 的 NYT 行含 BERTSUMEXT（46.66/26.35/42.62）、BERTSUMABS（48.92/30.84/45.41）、BERTSUMEXTABS（49.02/31.02/45.55）。Gold 取最后一组；模型输出前两组，漏掉最高的 BERTSUMEXTABS 三项。三组值都在实际表格证据中，不是整个最佳行未进入检索。模型还输出了 CNN/DailyMail 的两个变体，导致总输出 15 条，高于 Gold 的 9 条。

## 1909.02188.pdf：模型配置差异与明确 Baseline 混入

Gold 使用普通 Our model 的六项结果；模型主要选用第 8 页 Table 4 的 Our model + BERT（如 92.9、88.6），因此与 Gold 模型配置范围不同。此外，SNIPS Intent Accuracy 输出 98.6，目视核验该值属于 BERT SLU (Chen et al., 2019) 行，作者 Our model + BERT 对应 99.0，构成明确的 Baseline 行混入。

截图：[第 8 页](1909.02188-page8.png)。这里只核验原始响应，不执行任何名为 Oracle 的对照实验，也不使用表中 Oracle 行替换输出。

## 1911.10390.pdf：整组数据集结果遗漏

Gigaword 的四个 Gold 值 39.19、20.47、36.69、61.51 均在实际第 6 条证据（PDF 第 6 页表格文档）中。该表格文档以 System 列开始，未附表格标题。模型只输出 Newsroom 的四项自动指标和三项人工评价，遗漏 Gigaword 四项。

这是“数值已进入证据但没有被抽取”的已确认案例；标题缺失是同步观察到的解析现象，不据此断言单一因果关系。

## 2203.16804.pdf：变体和额外实验范围

Gold 的 CNNDM 三项来自第 5 页 Table 2 的 BRIO-Mul（47.78/23.55/44.57）；模型选择第 6 页 BRIO-Loop 的 48.01/23.80/44.67。该表格文档附上 Figure 2 标题。另抽取 BERTScore、校准误差、Confidence 和论文中的 Few-shot 结果，共 22 条，而 Gold 有 9 条。这里的 Few-shot 是论文内实验设置标签，本轮 Extraction 调用仍为官方 Zero-shot Prompt。

这些值没有因偏离 Gold 被删除；54 次逐字段标准化全部执行，14 个集合外返回按原逻辑为 null。

## D18-1523.pdf：遗漏主评价指标，额外抽取相关性指标

第 5 页 Table 2 明确包含作者的 FNMI=11.26、FBC=57.49、AVG=25.43（均带标准差），但模型只抽取 AVG，另输出第 8 页 Table 3 中 tense/sense 相关性的 NMI=0.22±0.12。这是主评价指标漏项及额外分析指标混入，相关数值均在表格证据中。

## D19-1367.pdf：数值列未进入实际证据

第 4 页保存的 NER 表格文档只有模型名称列，并附上 Figure 2 标题，没有 F1 数值列；Gold 的 93.47 不在任何实际检索证据中。模型将该 Result 输出为“Best result for I-DARTS (n = 1) (exact value not provided in the excerpt)”。字符串字段类型合法，但没有得到数值，不能把 JSON 合法当作抽取正确。

该篇还输出 PTB 的 Validation Perplexity=58.0，而 Gold 仅标注 Test Perplexity=56.0。原始预测和文字占位说明均保留，没有从 Gold 补值。

## 历史十五篇已确认现象

历史结果和原报告保持原样。详细证据可查看：

- `../../subset5/inspection/findings.md`：1709.04109 的 mean/max 统计口径差异；2020.emnlp-main.523 的 Dev/Test 混淆；1905.03197 的表格关联、字段绑定和 Baseline 混入。
- `../../subset15/inspection/manual_findings.md`：新增九篇的逐案复核，包括 BERT/BART Baseline 混入、任务/指标混淆、名称映射空值。
- `../../subset15_uncapped_retry/inspection/manual_findings.md`：1912.08777 将多个 ROUGE 指标和值保留为复合字符串，未拆分以对应 Gold 标量。

这里不提供未完整人工裁决的 Baseline、Dev/Test 错误总数。全量逐条症状计数与所有原始/标准化结果由 `findings.md`、`diagnostics.json` 和 `../evaluation/tdmr_comparison.md` 提供。
