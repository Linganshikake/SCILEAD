# SCILEAD Windows CPU PDF 与检索环境记录

日期：2026-10-13。解释器：`D:\miniconda3\envs\scilead\python.exe`。官方提交：`8bf74b0a830feb7035c6166dce3394dc344ae532`。

**最终结论：环境安装成功，真实 SciLead 单篇官方预处理和 Chroma 检索已实际完成；表格识别存在已记录的质量问题，不能声称无误差复现。** 用户提供的数据已解除此前 Gold 访问阻塞。

## 真实单篇结果

- 论文 `2020.findings-emnlp.378.pdf`，15 页；实际 hi_res + 表格结构推理、嵌入、Chroma 建库与检索全过程约 108.86 秒。
- 原始元素 245 个；官方文本分块 25 个；Table 检测区域 12 个；返回 16 条证据（默认检索的 4 个文本块 + 全部 12 个表格区域）。
- Table 区域所在 PDF 页码：5、6、6、7、7、8、9、14、14、14、15、15。
- 第 7 页 Table 5 的 OURS 行包含 `90.32 55.14 50.68`（ON5E/WN16/WN17）和 `81.18 96.62 69.78`（ON4C/RE/WE），与该篇全部 6 条 Gold 一致；已对照原始 PDF 渲染图核验。
- **12 个区域不等于 12 张独立真实表**：Figure 3（第 9 页）被误检；Table 8(a)/(b)（第 14 页）各自形成区域，完整表标题关联缺失。其余复杂表格还有按列展平、勾选符号失去行对应关系的风险。本轮没有修改、删去或修正这些原始证据。
- `processed_docs.pkl` 已生成并重新读取核对，内容与导出的 16 条 JSON 证据一致；SHA256 为 `8268049bc057a1e9c22a90cc8210c16c534142fa6712aa16020dc57f39f8c9e2`。

输出目录：`D:\C++\SCILEAD\pilot\outputs\scilead-pilot-13.10.2026-16-58-13`。

目录内保存 `config.json`、`processed_docs.pkl`、`pilot-summary.json`、`partition-elements.json`、`raw-tables.json`、`official-table-documents.json`、`text-chunks.json`、`retrieval-evidence.json`、`quality-review.json`、3 张核验页 PNG 和 [逐表全文检查报告](pilot/outputs/scilead-pilot-13.10.2026-16-58-13/inspection.md)。每个表格区域的页码、实际附加标题、原文及 HTML 均保留；人工映射说明与原始输出分开记录。

最终复核 `pip check` 通过、Git 工作区 clean、官方 requirements SHA256 未变。PowerShell 对旧库 stderr 警告产生 NativeCommandError 包装，外层运行回报为 1；Python 最终记录为 PASS，所有官方输出已独立核验成功，未因此重复解析 PDF。首次 GBK 错误发生在加载 Prompt 的阶段，尚未解析 PDF；UTF-8 启动后只进行了一次真实 hi_res 预处理。

**下一阶段条件：本地 PDF/检索输入准备完成，可以进入 GPT-4.1 单篇 TDMR Extraction 的独立配置与验证阶段。** GPT-4.1 的接口配置、实际请求和响应兼容性尚未测试；不要把本地准备完成解释为付费 API 已验证。下一阶段应使用本次原始 pickle 和对应单篇 Gold，记录解析误检对抽取结果的影响，不提前删除误检或修改算法。

## 安装与验证

PDF / 检索扩展安装成功。先执行完整 pip dry-run，在锁定第二阶段全部 103 个既有包的条件下增加 80 个包；现有 103 个版本均未变化，环境共 183 个 distribution。`pip check` 输出 `No broken requirements found.`。没有使用 `--no-deps`，没有修改 Base、官方 requirements.txt 或核心源码。完整版本与检查证据见 `scilead-pdf-validation.json`。

| 组件 | 最终版本 |
|---|---|
| Python / NumPy | 3.11.17 / 1.26.4 |
| PyTorch / torchvision | 2.2.0+cpu / 0.17.0+cpu |
| LangChain / community / core | 0.1.17 / 0.0.36 / 0.1.48 |
| Transformers / Sentence Transformers | 4.37.2 / 3.0.1 |
| Unstructured / unstructured-inference | 0.12.5 / 0.7.23 |
| ChromaDB | 0.4.24 |
| pdf2image / pdfminer.six | 1.17.0 / 20221105 |
| pdfplumber / pikepdf / pillow-heif | 0.10.4 / 8.13.0 / 0.15.0 |
| unstructured.pytesseract | 0.3.12 |
| ONNX Runtime / ONNX | 1.15.1 / 1.15.0 |
| opencv-python / layoutparser | 4.9.0.80 / 0.3.4 |
| effdet / timm / matplotlib | 0.4.1 / 0.9.12 / 3.8.3 |
| NLTK | 3.10.3（既有版本） |

Unstructured 0.12.5 的 PDF extra 固定 inference==0.7.23，而该 inference 要求 onnxruntime<1.16；因此没有安装最新版推理框架。Chroma 选择 0.4.24，另约束 posthog==3.5.0、build==1.0.3。导入时发现 inference 间接需要但元数据未完整声明的 matplotlib，经单独 dry-run 后补装 3.8.3。CPU Torch/NumPy/LangChain 均保持原样。

`partition_pdf`、`Chroma`、`HuggingFaceEmbeddings` 及此前关键 API 导入成功。Torch CUDA=False；ONNX provider 为 CPUExecutionProvider。合成诊断页的 Poppler 渲染、英语 OCR、真正的 hi_res 布局/表格推理和 MPNet+Chroma 检索均成功。该诊断页有 11 个元素、1 个表格，检索返回默认 k=4。它只证明功能运行，不能替代真实论文复现。

## 系统依赖

- MiKTeX 自带工具在实际版本测试中报安装未完成，未把“PATH 中存在”视为可用，也未修改 MiKTeX。
- Poppler 24.08.0 位于 `tools\pdf-system\Library\bin`。Conda 安装前检查独立 prefix 的计划：43 个系统包约 51 MB，无 Python、无 UNLINK，不替换 scilead 或 Base。PDF 页数读取和实际转换成功。
- Tesseract 5.5.3.20260724 位于 `tools\tesseract\tesseract.exe`。从官方发布下载安装包、核对 SHA256 后便携解包，没有执行安装程序或改变注册表。`--version` 成功，`--list-langs` 仅有 eng；实际 OCR 识别测试通过。英语权重来自官方 tessdata_fast 4.1.0。
- NLTK 资源位于 `assets\nltk_data`。准备了 punkt、punkt_tab、averaged_perceptron_tagger、averaged_perceptron_tagger_eng 的英语资源。当前 NLTK 下载器拒绝代理方式；使用官方固定 URL、TLS 校验和官方索引 SHA256 校验后解包，未关闭下载器安全机制。分句和 POS 实测通过。
- 对本次英语 PDF，已无缺失的必需系统工具。未安装其他语言 OCR；若下一篇依赖其他语言，需另行评估。

## 模型资源

| 用途 | 官方模型 | 本次所需文件约大小 |
|---|---|---|
| 官方检索嵌入 | sentence-transformers/multi-qa-mpnet-base-dot-v1 | 438.7 MB |
| 默认 YOLOX 布局 | unstructuredio/yolo_x_layout：yolox_l0.05.onnx | 216.6 MB |
| 表格结构 | microsoft/table-transformer-structure-recognition | 115.4 MB |
| 表格模型的预训练骨干 | timm/resnet18.a1_in1k | 46.8 MB |

总计约 817.5 MB，无单个资源超过 1 GB。这些是嵌入、布局和表格模型，与聊天模型或 GPT-4.1 无关。全部已在 CPU 实际加载。缓存位于 `assets\huggingface`，版本 revision、文件大小和下载记录见 `assets\pdf-model-manifest.json`、`pdf-model-downloads.json`、`pdf-backbone-downloads.json`。首次未缓存运行会尝试下载；本次测试设置离线并用审计钩子禁止网络请求。

## 真实数据来源与运行方式

用户提供 `C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data`。README、Gold JSON、leaderboards JSON 均与同目录上级的 `2024.emnlp-main.453.data.zip` 内容逐字节一致，计 43 篇、295 条 TDMR、27 个排行榜，字段和统计符合数据说明。当前 ACL 附件猜测地址返回 404，TUdatalib 页面有访问限制，因此不声称已独立认证本地附件来源。保留本地文件 SHA256 和来源记录于 `pilot\data-provenance.json`。

只下载 Gold 中的 `2020.findings-emnlp.378.pdf`：*Improving Named Entity Recognition with Attentive Ensemble of Syntactic Information*，15 页、6 条 Gold。PDF 来自 Gold 指定的 [ACL 官方地址](https://aclanthology.org/2020.findings-emnlp.378.pdf)。`pilot\papers` 中只有这一篇 PDF。用户桌面的 `SCILEAD.pdf` 是其他文件，本次未拿它代替 Gold 论文。

外部启动器 `scilead-pilot-preprocess.py` 调用原版 `doc_preprocess.main` 和 `get_config`，使用原版 `prompts.json`、chunk_size=2000、chunk_overlap=200、默认 YOLOX、hi_res、infer_table_structure=True、multi-qa-mpnet-base-dot-v1、默认 similarity k=4。仅将输出目录时间戳内 Windows 禁止的冒号改为连字符，保持末尾路径分隔符。使用 Python `-X utf8` 解决官方文件 open 默认 GBK 解码失败的问题。观察包装只保存原函数返回值，不更改元素、文本、算法或官方 pickle。

命令：

```powershell
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 -u 'D:\C++\SCILEAD\scilead-pilot-preprocess.py'
```

运行禁用网络、遥测、追踪，并阻止敏感配置文件读取。无需提供 API Key。本轮没有执行 TDM Extraction / Evaluation，没有付费 API 调用。

## 文件记录

- `requirements-scilead-pdf-win-cpu.txt`：PDF 扩展直接依赖。
- `constraints-scilead-pdf-win-cpu.txt`：最终全部 183 个包的版本约束。
- `scilead-pdf-win-cpu-freeze.txt`、`scilead-win-cpu-freeze.txt`：安装后 pip freeze；第二阶段快照保留在 `assets\scilead-stage2-freeze.txt`。
- `scilead-pdf-session.ps1`：仅当前 PowerShell 进程的工具路径、资源路径和离线设置。
- `scilead-pdf-validation.json`：版本、导入、pip check、源码与功能测试证据。
- `assets\`：dry-run / 安装日志、源文件、下载和校验清单、NLTK 和模型缓存。
- `tools\`：独立 Poppler、便携 Tesseract 与解包工具。
- `scilead-pdf-smoke-test.py`、`smoke\inspection.md` 及诊断原始输出：合成诊断与已知结构误差。
- `scilead-pilot-preprocess.py`、`pilot\gold`、`pilot\papers`、`pilot\data-provenance.json`：真实单篇输入与启动器。

## 限制与核验边界

合成页推理虽成功，其 HTML 多出一个空列，并把 F1 识别为 Fl。原始输出完整保留，没有手工修正或更换解析策略。表格被检测出来不代表结构与数值全部准确，真实论文的逐表核验结果应与其原始 PDF 对照。旧版库出现弃用提示，表格骨干有 3 个不使用的 BatchNorm 计数权重提示，均未阻止诊断执行。

本次官方 requirements.txt SHA256：`9a074c4962e8dd756bf46ee5bf87d54b75f09542a9de0e16da3962b037e4adf1`。第二阶段相对官方的 LangChain 兼容调整保持不变；本阶段只增加 PDF/检索依赖与 CPU torchvision。

依赖元数据来源：[Unstructured 0.12.5](https://pypi.org/pypi/unstructured/0.12.5/json)、[inference 0.7.23](https://pypi.org/pypi/unstructured-inference/0.7.23/json)、[ChromaDB 0.4.24](https://pypi.org/pypi/chromadb/0.4.24/json)。模型来源：[MPNet](https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-dot-v1)、[YOLOX](https://huggingface.co/unstructuredio/yolo_x_layout)、[Table Transformer](https://huggingface.co/microsoft/table-transformer-structure-recognition)、[ResNet18](https://huggingface.co/timm/resnet18.a1_in1k)。
