# GitHub 上传范围与完整性

## 2026-10-24 增量归档

新增 Llama-3 70B 正式42篇、V2格式恢复及其历史诊断，AxCell阶段0至最终37篇评价的完整追溯记录，以及 GPT-5.6 Sol A0/A1/A2与43篇Result类型恢复版。新增结果从本地冻结文件逐字节复制，原实验文件不改。Llama-2和未完成的共同16篇GPT-4.1标准化任务不在本次发布范围。

本次指标入口：[results/README.md](results/README.md)，机器可读文件为 [metrics_summary.json](results/metrics_summary.json) 和 [tuple_metrics.csv](results/tuple_metrics.csv)。新增文件清单、排除范围、SHA256及核验见 [publications/20261024/](publications/20261024/)。历史 `publication_manifest.json` 不重写，仍仅对应下方2026-10-16归档。

模型权重、环境、PDF/TeX原始资源、缓存、下载归档和认证文件未上传。保留历史失败日志与诊断，不能把它们混入当前主结果；复用关系以各阶段manifest为准。本次只发布，不调用模型、不重算实验指标。

## 2026-10-16 初次归档

归档日期：2026-10-16。目标：[Linganshikake/SCILEAD](https://github.com/Linganshikake/SCILEAD)。

## 已包含

- 上游原始源码及其 LICENSE、NOTICE，固定 commit `8bf74b0a830feb7035c6166dce3394dc344ae532`。
- 本地独立实验脚本、环境依赖与安装记录。
- `pilot/` 内历史和正式实验的配置、检查点、候选集合、模型原始请求/响应记录、预测与标准化输出、评测与错误分析、来源和完整性记录。
- 已有检索证据、轻量 `processed_docs.pkl` 缓存、Gold 快照及来源说明。Gold 与论文内容仍按原始来源的授权使用。
- 本地项目的 `memory.html` 背景说明，保留原文；正式结果以对应实验的冻结记录为准。

从本地原目录复制 **46,479 个文件，共 374,478,488 bytes（357.13 MiB）**。所有这些文件均与本次读取的本地原文件逐字节相同，没有重写路径、预测、Prompt 或日志内容。`publication_manifest.json` 保存相对路径、大小、SHA256 与 Git blob SHA1；清单本身和五个发布说明文件不计入此复制数。

## 留在本地

- `.env`、API Key 与认证文件：不读取其内容，也不上传。
- `assets/` 中的模型权重、NLTK 与 Hugging Face 缓存。
- `tools/` 中的 OCR、Poppler、安装器及系统二进制。
- 原始 PDF、下载 ZIP、模型二进制、Python 字节码和运行缓存。
- `cleanup_records/`、`smoke/` 与环境验证缓存等本机维护文件。
- 嵌套上游 `.git`：上传源码快照，保留上游归属及固定 commit 信息，不混入其 Git 元数据。

排除列表与根目录排除规则见 `publication_manifest.json`；`.gitignore` 对未来提交提供相同类型的防护。**排除不代表删除本地文件。** 历史完整性清单中的部分路径因此不会出现在发布仓库中，不应把这种有记录的发布范围差异误判成实验输出发生变化。

## 使用限制

本次只归档和上传，没有安装依赖、重新调用模型、重新解析 PDF 或重新计算实验。历史成功和失败记录均按发布范围保留，没有根据得分筛选结果。

文件中的原机器绝对路径、请求 ID、使用量和原始日期属于实验记录，保持不变。它们不包含本次检查识别出的实际密钥。重新运行前需在新的运行副本中配置路径和个人凭据；现有冻结结果应只读使用。

GitHub 原有初始化提交保留。本次新增根目录 README、上传说明、忽略规则、字节保留属性和发布文件清单，不改动原实验目录。
