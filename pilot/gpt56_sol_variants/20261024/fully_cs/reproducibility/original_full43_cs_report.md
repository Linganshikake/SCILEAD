# GPT-4.1 + 原版 CS：全量复现报告

完成 43/43 篇、295 条 Gold 的评价，复用 284 条原始 GPT-4.1 Extraction。没有重新抽取、解析 PDF 或构建检索索引。新增远程推理/API 请求为 0。

## 方法与模型

执行固定 commit `8bf74b0a830feb7035c6166dce3394dc344ae532` 的未修改 `tdm_embedding_normalization.main`。适配仅将原来的模型构造器指向固定本地快照，返回 CPU FP32 实例，并对原版 semantic_search 返回值及逐篇完成结果做日志记录；候选构建、精确分支、encode、top_k=1 选择和输出逻辑保持原版。

模型 `Lajavaness/bilingual-embedding-large`；权重 revision `e83179d7a66e8aed1b3015e98bb5ae234ed89598`；实现代码 `dangvantuan/bilingual_impl` revision `8079a782f9671d3696b5ab189781480fcca58d25`。实际动态导入代码已与下载文件 SHA256 对照。Transformer → mean Pooling → Normalize；1024 维，无额外 Prompt。`PYTHONHASHSEED=0` 在启动前设置，原版 set→list 的实际顺序保存在 candidate_labels.json。

现有 Python 3.11.17、torch 2.2.0+cpu、NumPy 1.26.4、Transformers 4.37.2、Sentence Transformers 3.0.1 可以直接加载；未安装或升级任何包。使用 XLMRobertaTokenizerFast 和现有 tokenizer.json，未因缺少 sentencepiece 包而安装依赖。

全部 284 条预测包含 852 个名称字段：310 个精确保留，542 个 CS Top-1 映射。候选为 23 Task、71 Dataset、26 Metric。实际最高分并列 0 次。旧 LLM 有 119 个 null，新 CS 为 0；集合内输出不等于语义正确。

## TDMR / IIM

| 指标 | LLM P | LLM R | LLM F1 | CS P | CS R | CS F1 |
|---|---:|---:|---:|---:|---:|---:|
| Task IIM | 0.960465 | 0.973422 | 0.966900 | 0.972093 | 0.973422 | 0.972757 |
| Dataset IIM | 0.820100 | 0.782224 | 0.800714 | 0.892248 | 0.864125 | 0.877961 |
| Metric IIM | 0.871096 | 0.836070 | 0.853224 | 0.873164 | 0.845208 | 0.858958 |
| Result IIM | 0.690160 | 0.718075 | 0.703841 | 0.690160 | 0.718075 | 0.703841 |
| TDM Exact Match | 0.639614 | 0.586965 | 0.612160 | 0.732087 | 0.695126 | 0.713128 |
| TDMR Exact Match | 0.411842 | 0.431786 | 0.421578 | 0.532588 | 0.553017 | 0.542610 |

P/R 保留官方逐篇 Macro；表内 F1 为聚合 P/R 的调和平均。另存逐篇 F1 均值，不与此表混用。
严格数值 Result P=0.579695、R=0.594044、F1=0.586782；Result IIM 与严格 Result 都与旧版本完全一致。

## Leaderboard-level

| 指标 | LLM 标准化 | CS 标准化 |
|---|---:|---:|
| LR：标准 TDM 命中 | 0.814815 | 0.925926 |
| 有效数值非空榜率 | 0.740741 | 0.888889 |
| 官方 PC | 0.487125 | 0.631570 |
| 官方 RC | 0.317989 | 0.411905 |
| 官方数值列表 RBO | 0.247654 | 0.303420 |
| 论文 ID AO（补充） | 0.462500 | 0.522212 |

标准 TDM 命中 25/27；有效非空 24/27。相对旧版本新增 5 个非空榜、1 个榜变为空。详细榜名、转换及覆盖原因见 leaderboard_evaluation/comparison_with_llm.md。

保持冻结 Gold：27 榜、140 条榜内记录。本地完整 Gold 含 141 个唯一 TDM、33 个至少三篇的分组，与论文统计的已知差异没有通过修改 Gold 消除。

## 配对诊断

相同抽取输入下，严格完整 TDMR 命中：双方 74 条、仅 CS 33 条、仅 LLM 9 条、双方均未命中 168 条。这些是预测记录计数，不是官方 Macro 得分或独立 Gold 覆盖数。

正确案例：WN16→WNUT-16 - English、WN17→WNUT-17 - English；失败案例：ON5E→BC5CDR、RE→RTE、WE→WNUT-16 - English、ROUGE-L→BLEU、GLUE→SNIPS。联合任务的 Sentence Accuracy→Accuracy 丢失了指标区别。IWSLT 的形式匹配与方向争议分开记录；未手工修正。全部重点案例见 inspection/findings.md。

## 耗时、内存、完整性

模型加载及短名称测试约 12.703 秒；正式程序含加载、单篇验证及 43 篇标准化共 98.922 秒，不含模型下载和后续评价。峰值工作集约 3.047 GiB，峰值私有提交约 5.459 GiB；两者含义不同。运行结束可用物理内存约 0.750 GiB，存在内存余量较小的实际限制。

full43_uncapped、leaderboard_eval_full43_uncapped 的文件名集合及逐文件 SHA256 全部未变；官方源码、Prompt、Gold、依赖版本未变；Git 工作区干净。原始副本按字节相同；43 篇的 ID、记录顺序/数量、Result 字符串和 source_documents 均保留。verification.json 保存验收结论，freeze_before.json 保存证据清单。

## 后续状态

本地模型加载、名称编码、全量候选及两级评价已具备运行条件，可以准备原版 Partially Pre-defined。下一阶段仍需按官方定义核对掩蔽配置、候选集合及对应输入；本轮没有启动 Partially、Cold Start、Few-shot 或任何优化实验。

## 文件索引

- normalization/embedding_normalized_output.json：官方兼容预测。
- normalization/mapping_audit.jsonl：852 个字段的实际映射记录。
- evaluation/metrics_with_f1.json、per_paper_metrics.json：总体及逐篇指标。
- evaluation/paired_comparison.md、tdmr_comparison.md：284 条预测配对与295 条 Gold 对齐。
- leaderboard_evaluation/：原版 PC/RC/RBO 与复用的 LR/AO 评价、各榜与转换轨迹。
- candidate_labels.json、model_manifest.json、config.json：候选顺序、固定版本与配置。
- README.md、verification.json、freeze_before.json：续跑说明及完整性核验。
