# Llama-3 70B 正式实验 RAG 专项审计

审计日期：2026-10-23。审计对象：`20261021_formal42` 与 `20261021_format_followup` 的本地归档执行产物。只读核查，未连接服务器、未读取凭据、未运行模型、未调用付费 API；新文件只写入本审计目录。

## 1. 直接结论

**正式实验属于“复用预处理 RAG 证据”（第 2 类），不是正式生成时重新执行向量检索。**

历史预处理确实使用原版 PDF → 正文切块 → MPNet → Chroma 相似度检索流程。Llama-3 读取从 GPT-4.1 历史 `source_documents` 导出的冻结证据，通过 `FrozenRetriever` 原样返回文档列表，再由 `RetrievalQA(stuff)` 构造输入。

- 已核对 **43/43 篇**的冻结证据与历史 `processed_docs.pkl`、检索导出和 GPT-4.1 `source_documents` 一致，含内容、metadata 与顺序。
- 每篇均为 **4 个检索正文块 + 该篇全部检测表格文档**。43 篇共有 172 个选中正文块、301 个表格文档。这里的“表格”是解析器识别的文档/区域，并不自动等同于人工确认的独立表格。
- 已核对 **42/42 次正式生成**的保存请求 Prompt 与官方模板加冻结证据的重建字符串完全相等，原始 pipeline 返回中的输入前缀亦一致。正式批次包含 38 次新生成和 4 次历史生成复用。
- **没有把 GPT-4.1 生成的预测文本混入 Llama-3 Extraction Prompt。** 打包代码只选择 `source_documents`；实际完整 Prompt 的逐字核对进一步排除了额外拼入历史预测、Gold 对应答案或标准名称集合的情况。服务器另有 Gold 文件用于后续标准化/评价，其存在不代表进入 Extraction 输入。
- `1912.08777.pdf` 的 **55,324 Tokens 是“4 个已检索正文块 + 44 个表格 + 官方系统指令/Query/Llama-3 模板”的完整候选 Prompt 长度**。它没有进入 Llama-3 正式生成，不能称为“实际已送入模型的长度”。

分类汇总：42 篇正式生成属于第 2 类；长论文的待生成输入也可追溯为第 2 类，但生成状态为 BLOCKED。没有发现第 1 类的本批次向量检索执行，也没有发现第 3 类的全正文绕过检索输入。检索内部距离值等不可恢复细节属于证据边界，见第 8 节。

## 2. 源码版本与真实执行入口

用户给出的 `b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25` 是本地 `D:\C++\SCILEAD-publish` 的发布归档提交；实际作者上游源码提交为 `8bf74b0a830feb7035c6166dce3394dc344ae532`。两者不是同一个仓库的提交。

本次分别读取两个 Git 提交中的文件对象，核对了归档内 `emnlp2024-leaderboard-generation/`、上游提交、当前本地源码及发送到远端的 `stage/source/`。正式 manifest 列出的源码文件在统一 CRLF/LF 后一致，发送源码与上游 Git blob 字节一致。没有把当前工作目录版本未经核对地当作运行版本。

正式入口来自保存的 `command.json`，例如：

```text
/root/autodl-tmp/scilead/envs/llama/bin/python
/root/autodl-tmp/scilead/adapters/run_llama.py extract
--model llama3 --paper-id 2020.emnlp-main.152.pdf
--out /root/autodl-tmp/scilead/runs/llama3/20261021_formal42/extraction/2020.emnlp-main.152
--formal-authorized
```

实际执行的是独立 `run_llama.py`，不是直接调用官方 `tdm_extraction.py` 的 CLI。`remote_batch.py` 在运行前核验固定文件哈希，完成后检查 Prompt 哈希、source_documents、原始响应和结束原因。

关键证据：

- [打包脚本](D:/C++/SCILEAD/pilot/autodl_setup/20261021/scripts/prepare_bundle.py)：分别固定 upstream/archive commit；只导出 source_documents，284 条 GPT 历史预测不迁移。
- [实际适配器快照](D:/C++/SCILEAD/pilot/autodl_setup/20261021/stage/adapters/run_llama.py)：SHA256 `4a3f659fd166d4591f73e73904b70ff0524e82da4afb0a738bb056e82b59586e`，与正式运行前冻结哈希相同。
- [正式批次脚本](D:/C++/SCILEAD/pilot/autodl_llama3/20261021_formal42/remote_snapshot/scripts/remote_batch.py)、[运行前哈希清单](D:/C++/SCILEAD/pilot/autodl_llama3/20261021_formal42/config/remote_expected_hashes.json)、[预检查](D:/C++/SCILEAD/pilot/autodl_llama3/20261021_formal42/preflight.json)。

69 个冻结源码/适配器/数据文件均与正式清单匹配。本次读取的远端归档文件中，292 个可在原远端交付清单中匹配，SHA256 全部一致。这是对历史运行归档的核验，不是本次重新登录检查远端当前文件。

## 3. 官方两条路径的实际含义

冻结 [pdf_loader.py](D:/C++/SCILEAD/pilot/autodl_setup/20261021/stage/source/pdf_loader.py:29) 中：

1. `partition_pdf(strategy='hi_res', infer_table_structure=True)` 提取元素；NarrativeText/Title 按页组成正文，Table 加入原版相邻标题关联后成为表格文档。
2. 正文按 **2,000 字符、200 字符 overlap** 切块，分隔符为 `[' ', '']`，保留 start_index。字符数不是 Token 数。
3. `Chroma.from_documents(self.split_docs, HuggingFaceEmbeddings('multi-qa-mpnet-base-dot-v1'))`，索引对象仅为正文块。
4. `CustomRetriever` 调用向量 Retriever 查询正文，再返回 `vector_docs + external_docs`，其中 external_docs 是全部表格。历史产物验证每篇返回 4 个正文块。

官方 [tdm_extraction.py](D:/C++/SCILEAD/pilot/autodl_setup/20261021/stage/source/tdm_extraction.py:37) 的分支：

| 分支 | 真实行为 | 是否在该次抽取执行相似度检索 |
|---|---|---|
| `is_preprocessed_doc=False` | 创建 Documents，初始化 Embedding/Chroma/CustomRetriever；RetrievalQA 调用实际向量检索，再附全部表格 | 是 |
| `is_preprocessed_doc=True` | 读取 processed_docs_path 的 pickle；PreProcessedDocuments 返回 CustomDummyRetriever，后者不使用 Query 筛选，直接返回保存列表 | 否 |

官方 [doc_preprocess.py](D:/C++/SCILEAD/pilot/autodl_setup/20261021/stage/source/doc_preprocess.py:27) 已执行 `retriever.invoke(config.query)`，然后把 **检索结果** 写入 `processed_docs.pkl` 并删除 Chroma collection。因此这个 pickle 名称不能被解释成“未经检索的全部预处理正文”。

Llama-3 实际 config 的 `is_preprocessed_doc=True`，但适配器并不读取 `processed_docs_path`（该字段未设置）。它读取：

```text
/root/autodl-tmp/scilead/data/evidence/<paper_id>.json
```

随后调用 `FrozenRetriever._get_relevant_documents()`，无条件返回 external_docs，语义上对应官方 DummyRetriever 分支。运行时确实经过 Retriever 接口与 RetrievalQA，但**接口调用不等于相似度检索**；该路径没有实例化 MPNet、没有构建或加载 Chroma，也没有调用向量相似度搜索。

## 4. 输入证据的逐篇追溯

实际证据链：

```text
原始 PDF
→ 历史官方 doc_preprocess / 只观察产物的独立包装器
→ text-chunks.json + table-documents.json
→ Chroma 查询选中 4 个正文块 + 全部表格
→ processed_docs.pkl / retrieval-evidence.json
→ GPT-4.1 output.json 的 source_documents
→ setup/stage/data/evidence/<paper_id>.json
→ FrozenRetriever → RetrievalQA(stuff)
→ calls/000000/request.json → pipeline 输入 → 原始响应
```

每个环节均对照文件；没有仅凭脚本注释判定执行。历史预处理日志、summary、输入/输出哈希，与正文块和检索结果的子集关系互相印证。历史包装器 `subset5_preprocess.py` 调用官方 `doc_preprocess.main`，观察并保存元素、切块和表格，不修改正文筛选方法。

所有 43 篇的选中正文均能映射回原始 text-chunks；全部表格与保存的 table-documents 顺序一致；与 pickle 和历史 GPT source_documents 完全相等。首篇 `.378` 的诊断 JSON 使用字段名 `text`，其他导出使用 `content`，本审计只在内存中统一字段名比较，未改历史文件。

逐篇完整路径、SHA256、页码、start_index、证据顺序及其原始正文/表格下标见 [source_traceability.json](source_traceability.json)。历史 timestamp 来自各目录 started.json，未以 Windows 文件复制时间冒充预处理时间。

| 论文 | 原始正文块 | 实际选中正文 | 表格文档 | 最终证据数 | Prompt Tokens | 正式生成 |
|---|---:|---:|---:|---:|---:|---|
| 1912.08777.pdf | 77 | 4 | 44 | 48 | 55,324，候选 Prompt 审计值 | 否，BLOCKED |
| 1511.08308.pdf | 27 | 4 | 11 | 15 | 4,661，实际 generate 输入 | 是，EOS；复用已有生成 |
| 2020.emnlp-main.152.pdf | 12 | 4 | 4 | 8 | 2,388，实际 generate 输入 | 是，EOS；正式批次新生成 |

**不存在输入接近 8,192 Tokens 的成功样本。** 42 篇中最长是 `1511.08308.pdf` 的 4,661；加 1,024 输出预算为 5,685，仍有 2,507 Tokens 余量。本表将其标为“最长已运行样本”，没有把它描述成接近上限。

三个样本的历史来源分别是：

- `pilot/subset15/papers/1912.08777/preprocess/`
- `pilot/full43/papers/1511.08308/preprocess/`
- `pilot/subset15/papers/2020.emnlp-main.152/preprocess/`

它们均有原始切块、表格、检索结果、配置和运行日志；并非只有历史 GPT 输出可用。

## 5. 55,324 Tokens 与实际 Prompt

长度审计和正式适配器均采用作者 Llama-3 模板：system header + 官方 Zero-shot system prompt + user header + Query + `Retrieved document contents:` + 按原顺序以两个换行拼接的文档内容 + `Output json:` + assistant header。不把文档 metadata 作为正文额外添加。模板示例 JSON 的双大括号经 PromptTemplate 格式化后成为单大括号。

Query 精确为 `Main task, datasets and evaluation metrics.`。完整序列化输入包含角色控制符，不是单独计算 PDF 文字或 context 字段。

长论文的证据正文字符数为 **3,960**，表格内容字符数为 **229,040**，证据内容合计 233,000 字符；表格占约 **98.30%（字符比例，不是 Token 比例）**。加模板、指令和分隔符后完整 Prompt 为 233,954 字符。其 SHA256 为：

```text
39ac494a7c7504d63fcaf280463592d969cf61a11667f4fb0fd1aa8a77729cfe
```

该值与历史长度审计及正式 preflight 一致。本次使用本地 tokenizer.json 重新分词，`add_special_tokens=False`、不截断，亦得到 **55,324 Tokens**。没有导入 torch/transformers 或加载模型。独立分词使用本地 tokenizers 0.15.2，历史运行是 0.19.1；结果与归档长度及实际生成观测交叉校验，而不是据此声称两套运行环境相同。

原始默认 tokenizer 调用会额外加 BOS，旧中间记录因此为 55,325；正式 pipeline 对齐审计为 55,324。不能把两者混为不同证据输入。

Llama-3 原生 context 为 8,192。长论文仅输入就超出 47,132；若按正式协议预留 1,024 输出，总需求是 **56,348**。该篇在清单筛选阶段被排除，没有正式 request/complete 生成记录，没有发生“实际推理时自动截断”。它的长度异常主要来自官方路径全部附加表格，不能归因于未做正文检索。

额外发现：`1811.05021.pdf` 的预检查是 2,343 Tokens，实际 generate 是 2,342。正文出现一次字面量 `<pad>`；作者 `model_init.llama` 会向 tokenizer 添加 `<pad>` 特殊 Token。离线分别执行添加前后分词，准确复现 2,343 → 2,342。42 次实际输入均与添加后的分词结果一致；Prompt 和证据未改变。这不是截断或少传一块文档。详见 [tokenizer_recount.json](tokenizer_recount.json) 与 [prompt_length_reconciliation.csv](prompt_length_reconciliation.csv)。

## 6. 与原论文及冻结实现逐环节对照

依据本地原论文全文第 4.1 节、Appendix C，以及已核验的作者源码。论文正文说文本块和表格形成嵌入；但作者代码只把正文块送入 Chroma，表格全部外接。两者存在描述粒度差异；本实验遵循的是冻结源码行为，不能把“全部表格外接”单独认定为本地适配器改变方法。

| 环节 | 原版方法/冻结实现 | Llama-3 正式实验实际做法 | 证据 | 是否一致 |
|---|---|---|---|---|
| PDF/正文解析 | Unstructured hi_res + 表格结构识别 | 复用历史原版解析产物，正式批次不再解析 | partition-elements、summary、日志、源代码 | 方法一致；执行时间分离 |
| 正文切块 | 2,000 字符，overlap 200，原版 separators | 复用历史切块及检索子集 | text-chunks、metadata/start_index、子集逐项比较 | 一致 |
| Embedding 模型 | multi-qa-mpnet-base-dot-v1 | 历史检索使用；正式生成不加载该模型 | 预处理包装器、summary、官方 init_retriever | 一致地复用历史结果 |
| 向量索引 | Chroma，仅索引正文块 | 历史构建，预处理后删除 collection；正式不建/不加载 | doc_preprocess、原始日志/产物 | 与原版预处理复用分支一致 |
| 查询与检索 | 固定 Query，相似度检索正文，再附表格 | 历史执行；正式 FrozenRetriever 直接返回保存列表 | config.query、retrieval-evidence、actual request | Query 一致；无本次重新检索 |
| 正文证据选择 | Retriever 选择相关正文，当前版本默认 k=4 | 所有 43 篇均保存并使用 4 个原始正文块 | text-chunks 与 source_documents 全量比较 | 一致；未拼接全部正文 |
| 表格处理 | 全部检测表格附到检索正文后，按原版标题关联 | 全部原始表格按保存顺序输入 | table-documents 与 ordered source_documents | 与源码一致；表格质量未在本审计重评 |
| 最终 Prompt | 作者 Llama-3 Zero-shot；RetrievalQA stuff | 原模板、Query、证据顺序；独立 checkpoint wrapper | 42 个 request 与原始 pipeline 返回逐字比较 | 内容一致；入口/持久化格式不同 |
| 上下文长度统计 | 原版模板/模型；论文未提供本地每篇长度记录 | 完整序列化 Prompt 审计 + 1,024 输出预留；超限阻塞；记录 generate 输入长度 | audit CSV、preflight、complete、离线复核 | 新增工程保护；42/43 范围差异必须披露 |

还应保留环境差异：正式运行归档为 A800 80GB、Transformers 4.40.2、LangChain 0.1.17；原论文报告 A100 80GB，官方依赖并非全部等同于当前环境。作者原始 HuggingFacePipeline 输出封装由固定副本适配。以上差异不能被概括成“与原论文完全相同的软硬件运行”，也不构成未使用 RAG 的证据。

## 7. 格式恢复与 Llama-2 比较的影响

格式恢复 V2 的 41 篇有效输出仍保留与冻结证据完全相同的 source_documents；V2 没有重新检索或重新生成 Extraction。`2105.03654.pdf` 的单独 2,048 输出预算诊断保存于独立目录，其 Prompt 哈希和证据与原 1,024 预算请求相同。本次核查二者分开，未把诊断并入 V2 主结果。

`2020.emnlp-main.152.pdf` 的 Llama-2 P5 原始输出 source_documents 与 Llama-3 完全相等：均为 4 正文 + 4 表格。Llama-2 实际输入 2,880 Tokens，Llama-3 为 2,388，是不同模板/tokenizer 的计数，不代表 Llama-2 使用更多证据。

对后续模型比较的含义：

1. 本次没有证据支持“Llama-3 因漏用 RAG 而长输入”；不能据此重置 Llama-2 合规范围。Llama-2 4,096 原生上下文、各自 tokenizer 和生成预算应继续使用其已有审计；既有 16 合规/27 阻塞范围不因本审计自动改变。
2. 同论文、同冻结检索证据能控制检索差异，有利于模型间比较。但 Llama-3 为 42 篇、GPT-4.1 为 43 篇、Llama-2 为 16 篇时，整组指标不能直接视为同一范围的模型能力比较。应披露分母并在共同论文范围比较；本次没有运行任何新评价。
3. 同一证据对不同 tokenizer 的上下文成本不同；全部表格外接仍会让 RAG 输入超长。RAG 不保证输入必定小于模型窗口。
4. 正文检索遗漏与表格解析错误仍可能存在，本审计证明输入来源/调用路径，并不证明证据覆盖完美、预测正确或归一化无误。

## 8. 证据强度与未能确定的事项

已确认：源码/归档对应关系、正式执行入口及配置、43 篇证据的内容与顺序、历史检索子集关系、42 个实际请求字符串、pipeline 输入前缀、真实 generate Token 数、无额外 GPT 预测拼入、长论文未进入正式生成。源文件/输入/执行日志形成交叉证据链，不是仅看到代码支持 RAG。

仍有限制：

- 历史 Chroma collection 按作者预处理代码删除，未保存每次检索的完整向量、距离值和逐候选排序。因此可以证明当前输入来自保存的历史检索输出，并核对正文子集；不能在不重新构建索引的条件下独立复算当时最近邻排名或完全排除浮点/依赖影响。若要审计精确排序，最小补充证据为当时的索引/embedding 快照与相似度排序日志；本轮不重建。
- 对远端执行的证据来自已同步并带 SHA256 的历史归档。本次未登录服务器，不能据此声明远端“当前状态”与历史时刻完全相同。当前状态也不是本次历史 RAG 结论的必要前提。
- 原始 token ID 张量未全部保存；实际长度来自观察 generate 的日志。我们重建的 Prompt 与原始 pipeline 输入前缀一致，且独立 tokenizer 复核吻合，但不声称拥有当时全部 token ID 的逐元素快照。
- 不能从这些记录推断原论文作者实际运行时每篇的精确检索结果；本地复现数据与作者隐藏的执行轨迹不是同一份证据。

## 9. 交付与保护核验

本审计读取并前后复核 746 个文件，未发现变化；69 个正式冻结文件匹配，292 个已访问的远端归档文件匹配历史交付哈希。核查覆盖范围见 verification 的路径清单，不夸大为重算全部模型权重或整个实验盘。

- [逐篇执行证据](rag_execution_evidence.csv)
- [Prompt 长度核对](prompt_length_reconciliation.csv)
- [证据来源、文档顺序及哈希](source_traceability.json)
- [完整性验证](verification.json)
- [离线分词复核](tokenizer_recount.json)
- `audit.py` / `tokenizer_readonly.py`：本次只读审计脚本，仅写此目录。

正式配置、源码、Gold、Prompt、预测及原始证据均保持不变。审计完成后停止，未重新检索、重新解析、重新生成或开展评价。
