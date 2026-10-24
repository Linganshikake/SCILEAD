# 实验A设计：GPT-5.6 Sol Fully LLM Baseline

研究问题：在同一冻结检索证据和原版任务要求下，更换Extraction与Fully Normalization的模型基座后，端到端TDMR与Leaderboard结果如何变化。A0不预设改善，也不生成预测。

流程：历史PDF解析/MPNet/Chroma所得证据 → 官方Zero-shot Extraction任务 → 逐字段Fully LLM名称映射 → 官方SCILEAD评价。两个生成阶段均使用gpt-5.6-sol；不使用GPT-4.1预测替代，也不是统一GPT后处理的Extraction单因素实验。

固定：43篇、295 Gold TDMR、27 Gold排行榜；每篇4个正文块＋全部表格文档及顺序；官方Prompt和Query；Task23/Dataset71/Metric26候选及字符串顺序；精确名称匹配、null接受规则与Result处理；官方Macro评价。Result不经模型进行数值、单位或语义修正。重复字段不合并缓存。

可变并必须披露：基座与分词器、建议medium推理、推理Token及输出预算、可能需要的接口适配。这些差异使本实验成为端到端模型基座对照，不是严格只改一个模型ID就能消除所有生成机制差异的实验。

Extraction输入只包含原版system/user模板、Query和冻结source_documents；不含Gold、taxonomy、历史预测、评分或错误分析。Normalization候选名称来自完整43篇Gold，但不提供该论文Gold对应关系或追加上下文；只有新模型真实生成的字段才形成请求。

复用范围：证据、Prompt、候选、评价代码与历史对照指标。必须新生成：43篇Extraction及其实际需要的Normalization。无新模型输出可以复用；不重新解析PDF、建立索引或检索。

官方源码归档提交b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25对应作者上游8bf74b0a830feb7035c6166dce3394dc344ae532；具体文件核验见source_version_verification.json。

评价：Task/Dataset/Metric/Result IIM、TDM/TDMR Exact Match的官方Precision/Recall；F1取官方聚合P/R的调和平均，不取逐篇F1算术平均。Leaderboard沿用27榜的官方数值列表指标，辅助论文ID AO与严格数值/一对一诊断沿用既有定义并单列。保留官方字符串包含匹配与重复预测处理，不因异常改公式。失败论文不得静默删除；评价用空预测需明确标注，不能称为有效生成成功。

对照：GPT-4.1全量43篇与新模型同范围比较；Llama-3 V2只能在共同42篇259 Gold范围另报，保留其中失败口径；不得拿其42篇分数直接比较新模型43篇总分。Llama-2如需展示，只能单独使用共同16篇69 Gold范围，不扩展本轮A0为额外实验。记录各模型原始格式接受规则、上下文/输出预算及标准化设置差异。

单篇A1建议固定2020.emnlp-main.152.pdf，依据是既有跨模型输入追溯完整且证据规模适中，不依据预测得分选样。仅提出试跑候选，不调用；长论文1912.08777.pdf保留为43篇候选，不用Llama上下文阈值排除。
