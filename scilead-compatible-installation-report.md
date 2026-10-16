# SCILEAD Windows CPU 第二阶段安装报告

日期：2026-10-13（Asia/Shanghai）

**结果：本轮 Python 基础依赖安装成功，LangChain/LangSmith 冲突已解决。23 项必需验证全部通过。可以进入 PDF 运行依赖准备阶段，但尚不能直接执行完整单篇预处理。**

## 环境与版本

- Python：3.11.17
- Conda 环境：`scilead`
- 解释器：`D:\miniconda3\envs\scilead\python.exe`
- 仓库：`D:\C++\SCILEAD\emnlp2024-leaderboard-generation`
- Git Commit：`8bf74b0a830feb7035c6166dce3394dc344ae532`
- CUDA：`torch.version.cuda is None`；`torch.cuda.is_available() == False`
- pip 26.2.1、setuptools 84.0.0 未升级；Base 环境未修改。

| 依赖 | 官方 requirements.txt | 本次最终版本 | 说明 |
| --- | --- | --- | --- |
| NumPy | 未直接固定 | 1.26.4 | 保留第一阶段版本 |
| PyTorch | 2.2.0+cu118 | 2.2.0+cpu | 保留第一阶段 CPU 构建 |
| LangChain | 0.1.7 | 0.1.17 | 调整 |
| langchain-community | 0.0.20 | 0.0.36 | 调整 |
| langchain-core | 0.1.41 | 0.1.48 | 调整 |
| langchain-openai | 0.1.2 | 0.1.2 | 保留 |
| LangSmith | 未直接固定 | 0.1.147 | 满足共同约束 |
| Pandas | 2.2.1 | 2.2.1 | 保留 |
| Transformers | 4.37.2 | 4.37.2 | 保留 |
| Sentence Transformers | 3.0.1 | 3.0.1 | 保留 |
| Unstructured | 0.12.5 | 0.12.5 | 仅基础依赖，无 all-docs |
| python-dotenv | 1.0.1 | 1.0.1 | 保留；未调用 load_dotenv |
| ml-collections | 0.1.1 | 0.1.1 | 保留 |
| rbo | 0.1.3 | 0.1.3 | 保留 |
| requests | 2.31.0 | 2.31.0 | 保留 |
| tqdm | 4.66.2 | 4.66.2 | 保留 |

## 兼容性依据与必要调整

通过 PyPI 指定版本 JSON 元数据确认：

- LangChain 0.1.17 要求 Community `>=0.0.36,<0.1`、Core `>=0.1.48,<0.2.0`、LangSmith `>=0.1.17,<0.2.0`。
- Community 0.0.36 要求 Core `>=0.1.48,<0.2.0`、LangSmith `>=0.1.0,<0.2.0`。
- Core 0.1.48 要求 LangSmith `>=0.1.0,<0.2.0`。
- langchain-openai 0.1.2 要求 Core `>=0.1.41,<0.2.0`。
- LangSmith 的共同范围为 `>=0.1.17,<0.2.0`，已安装 0.1.147。

采用用户指定的候选组合；兼容 requirements 文件相对第一阶段 CPU 文件只改三项 LangChain 固定版本，其他行保持不变。没有声称该组合是所有历史版本中唯一或数值上最小的可行组合。

另外在独立 constraints 文件中固定三个必要的工具/间接依赖：

1. `packaging==23.2`：Core 要求 `>=23.2,<24`，因此从环境原有 26.3 调整。
2. `wheel==0.45.1`：原有 0.47.0（核查的 0.46.3 亦然）要求 packaging>=24；0.45.1 没有这项运行依赖。只调整 scilead 内的构建工具。
3. `chardet==5.2.0`：Unstructured 的无上界依赖最初解析到 7.6.0，实际导入 Requests 2.31.0 时触发兼容警告。Requests 源码明确检查 `>=3.0.2,<6`；固定 5.2.0 后警告消失，运行时检查通过。

constraints 同时锁定 NumPy 1.26.4 和 Torch 2.2.0+cpu。未使用 `--no-deps`，未全量升级依赖，未修改任何官方核心源码。

## 安装与验证

先完成完整 dry-run，核对解析结果不替换 NumPy/Torch、不含 CUDA 包，再安装。发现 chardet 运行时警告后，再次对完整依赖做 dry-run，结果仅需调整 chardet；随后执行该修正。

最终安装命令等价于下列命令（基于第一阶段已安装的 CPU Torch）：

```powershell
& 'D:\miniconda3\envs\scilead\python.exe' -m pip --isolated --disable-pip-version-check install `
  -r 'D:\C++\SCILEAD\requirements-scilead-win-cpu-compatible.txt' `
  -c 'D:\C++\SCILEAD\constraints-scilead-win-cpu.txt' `
  wheel==0.45.1 --index-url https://pypi.org/simple
```

验证脚本：`scilead-validate-compatible.py`。脚本开启 Hugging Face 离线模式，关闭追踪/遥测，阻止网络连接和 DNS 查询，并阻止读取 `.env`、Codex 与 AWS 敏感配置路径。

```text
Required checks: 23/23 PASS
pip check (exit 0): No broken requirements found.
Torch: 2.2.0+cpu
NumPy: 1.26.4
CUDA: False
RetrievalQA local invocation: result=42
Tracked Python syntax: 14/14 PASS
Official requirements and tracked Python source: unchanged
```

- 全部 15 项直接包导入通过，另有 NumPy/Torch、固定版本、API、仓库与 pip 检查。
- `RetrievalQA`：使用本地 FakeListLLM 与内存检索器执行真实调用，返回预期结果；无 API 请求。
- `ChatOpenAI`、`AzureChatOpenAI`：导入及方法检查通过，未创建真实提供商客户端，未读取密钥。
- `Chroma`、`HuggingFaceEmbeddings`：LangChain 接口导入及方法检查通过；未创建向量库或加载嵌入模型。
- 官方使用的旧版 splitter、prompt、retriever、callback 路径导入通过；文本切分和模板格式化通过。
- Transformers 配置对象、Sentence Transformers 余弦相似度计算通过；无预训练模型加载。
- Unstructured 基础导入及 Text/Table 对象通过；未执行 PDF 解析。
- NumPy/Torch 共享内存、双向转换及 CPU 自动求导通过。
- 旧版 LangChain 导入仍出现弃用提示，未造成失败；为保持官方源码不变，未迁移 API。
- 验证时的沙箱 Git 所有权限制用单命令 `-c safe.directory=<本仓库>` 处理，没有修改全局 Git 配置。
- Hugging Face 验证缓存改到项目外侧的 `.scilead-validation-cache`；只生成 `hub/version.txt`，没有模型文件。

官方 requirements.txt SHA256：`9a074c4962e8dd756bf46ee5bf87d54b75f09542a9de0e16da3962b037e4adf1`。

## 仍未具备的 PDF / 检索条件

| 项目 | 实际检查结果 |
| --- | --- |
| Chroma 数据库后端 | `chromadb` 未安装；接口导入成功不等于数据库可运行 |
| Unstructured PDF 入口 | 仅尝试导入时即报缺少 `pdf2image`，未调用解析函数 |
| PDF Python 扩展 | `pdf2image`、`pdfminer.six`、`pillow-heif`、`unstructured-inference`、`unstructured.pytesseract`、`onnxruntime` 未安装 |
| Tesseract | PATH 未找到；常见安装目录和 scilead 的 Library/bin 也未发现 |
| Poppler 工具 | PATH 中存在 MiKTeX 的 `pdftoppm.exe` / `pdfinfo.exe`；未执行，尚未验证能否满足 pdf2image/Unstructured 的实际需求 |
| NLTK 数据 | punkt、averaged_perceptron_tagger、punkt_tab/english、averaged_perceptron_tagger_eng 均未找到；未下载 |
| 模型资源 | 未下载布局/表格模型或 `multi-qa-mpnet-base-dot-v1` 嵌入模型，加载能力未验证 |

下一阶段先单独确定与 Unstructured 0.12.5、当前 CPU Torch 和 NumPy 兼容的 PDF/Chroma 扩展版本，并完整 dry-run。随后补齐、验证系统工具和对应 NLTK 数据，再明确允许哪些布局/表格/嵌入模型资源下载，最后只处理一篇本地 PDF。官方代码使用 `strategy='hi_res', infer_table_structure=True`，基础包安装成功不能替代这些运行条件。

本轮未运行 SCILEAD 处理/评估脚本，未下载论文、数据集或模型权重，未调用付费 API，未读取或修改敏感配置。

## 保存的文件

- `requirements-scilead-win-cpu-compatible.txt`：最终直接依赖，只有三个 LangChain 版本变化。
- `constraints-scilead-win-cpu.txt`：CPU 基础与必要间接依赖约束，安装时应一并使用。
- `scilead-win-cpu-freeze.txt`：实际 `pip freeze` 输出，共 100 行，已替换第一阶段的部分环境清单。
- `scilead-compatible-validation.json`：23 项检查、可选组件缺失情况及全部 103 个已安装发行包版本；包括 pip/setuptools/wheel。
- `scilead-validate-compatible.py`、`scilead-compatible-validation.log`：可复跑的离线检查及最终输出。
- `scilead-compatible-pypi-metadata.json`：四项候选包的实际 PyPI 元数据。
- `scilead-compatible-dry-run.*`、`scilead-compatible-final-dry-run.*`：完整预解析的 JSON 报告和日志。
- `scilead-compatible-install.*`、`scilead-compatible-chardet-fix.*`：安装和后续单包兼容修正的 JSON 报告与日志。
- 本报告；第一阶段报告保留历史内容，并添加第二阶段报告入口。

说明：标准 `pip freeze` 在 Python 3.11 下默认省略 pip/setuptools/wheel。其版本均另行保存在验证 JSON 中。尝试 `freeze --all` 时发现 Conda 的 pip 带有本地构建来源 URL，故最终采用用户指定的标准 freeze 命令，而不把这条不可移植的构建路径当作复现安装要求。

PyPI 核对来源：[LangChain 0.1.17](https://pypi.org/pypi/langchain/0.1.17/json)、[Community 0.0.36](https://pypi.org/pypi/langchain-community/0.0.36/json)、[Core 0.1.48](https://pypi.org/pypi/langchain-core/0.1.48/json)、[OpenAI 0.1.2](https://pypi.org/pypi/langchain-openai/0.1.2/json)、[wheel 0.45.1](https://pypi.org/pypi/wheel/0.45.1/json)。
