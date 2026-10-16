# SCILEAD Windows CPU environment record

> 第二阶段已完成：LangChain 冲突已修复，当前版本和验证结果见 [第二阶段安装报告](scilead-compatible-installation-report.md)。以下保留第一阶段历史记录；freeze 文件已更新为第二阶段环境。

Date: 2026-10-13 (Asia/Shanghai)
Status: PARTIAL SUCCESS; official dependency installation blocked by incompatible LangSmith requirements.

## Environment
- Python: 3.11.17 | packaged by Anaconda, Inc. | (main, Oct  1 2026, 20:16:54) [MSC v.1942 64 bit (AMD64)]
- Interpreter: D:\miniconda3\envs\scilead\python.exe
- Conda environment: scilead
- Environment path: D:\miniconda3\envs\scilead
- Repository: D:\C++\SCILEAD\emnlp2024-leaderboard-generation
- Git commit: 8bf74b0a830feb7035c6166dce3394dc344ae532
- pip: 26.2.1 (unchanged)
- Torch: 2.2.0+cpu
- torch.version.cuda: None
- torch.cuda.is_available(): False

## Installed versions and import checks
| Package | Installed version | Import result |
| --- | --- | --- |
| numpy | 1.26.4 | PASS |
| torch | 2.2.0+cpu | PASS |
| pandas | not installed | ModuleNotFoundError: No module named 'pandas' |
| langchain | not installed | ModuleNotFoundError: No module named 'langchain' |
| langchain-community | not installed | ModuleNotFoundError: No module named 'langchain_community' |
| langchain-core | not installed | ModuleNotFoundError: No module named 'langchain_core' |
| langchain-openai | not installed | ModuleNotFoundError: No module named 'langchain_openai' |
| transformers | not installed | ModuleNotFoundError: No module named 'transformers' |
| sentence-transformers | not installed | ModuleNotFoundError: No module named 'sentence_transformers' |
| unstructured | not installed | ModuleNotFoundError: No module named 'unstructured' |
| python-dotenv | not installed | ModuleNotFoundError: No module named 'dotenv' |

## Validation
- NumPy/Torch shared memory, tensor-to-NumPy conversion and CPU autograd: PASS.
- Validation process blocked socket connections and DNS lookup; Hugging Face offline flags enabled.
- Tracked Python syntax: PASS (14 files, parsed with ast.parse; no project modules executed).
- LangChain legacy APIs, Transformers/Sentence Transformers runtime compatibility and Unstructured imports: NOT VALIDATED because packages were not installed.
- pip check exit code: 0
```text
No broken requirements found.
```
pip check describes the installed subset only; it does not mean the full official requirements are satisfied.

## Blocking conflict
Official CPU requirements were pre-resolved with pip install --dry-run -r; result: ResolutionImpossible (exit code 1). No third-stage runtime dependencies were installed.
- langchain==0.1.7 requires langsmith>=0.0.83,<0.1.
- langchain-community==0.0.20 requires langsmith>=0.0.83,<0.1.
- langchain-core==0.1.41 requires langsmith>=0.1.0,<0.2.0.
- These ranges have an empty intersection.
- langchain-openai==0.1.2 additionally requires langchain-core>=0.1.41,<0.2.0, so independently downgrading core cannot solve all pins.
- All four LangChain packages declare Python 3.11 support; this conflict is not caused by the Python version. Updating pip cannot create an intersection.
- sentence-transformers==3.0.1 declares transformers>=4.34.0,<5.0.0 and torch>=1.11.0. Requested versions satisfy these declared bounds; runtime compatibility remains untested.
- Core package versions were not changed; no --no-deps workaround or broad upgrade was used.

## Installation actions
Commands below were invoked with D:\miniconda3\envs\scilead\python.exe:
```text
-m pip --isolated --disable-pip-version-check install numpy==1.26.4 --index-url https://pypi.org/simple
-m pip --isolated --disable-pip-version-check install torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu
-m pip --isolated --disable-pip-version-check install --dry-run -r D:\C++\SCILEAD\requirements-scilead-win-cpu.txt --index-url https://pypi.org/simple
```
Only NumPy, CPU Torch and its required dependencies were installed in scilead. Script-not-on-PATH warnings are due to using the interpreter directly; no global PATH edit was made.

## Files and integrity
- requirements-scilead-win-cpu.txt: exact byte-preserving copy except the single torch==2.2.0+cu118 line.
- scilead-win-cpu-freeze.txt: current pip freeze output; partial environment, not a complete runnable reproduction lockfile.
- scilead-win-cpu-environment-report.md: this report.
- Official requirements.txt SHA256, unchanged: 9a074c4962e8dd756bf46ee5bf87d54b75f09542a9de0e16da3962b037e4adf1
- No source changes; no Base/global Python/package upgrades; no API calls, model weights, PDF processing or sensitive configuration access.

## Next stage (not performed)
First agree on a compatible set of LangChain package pins and validate it without changing official requirements.txt.
Then assess PDF-only dependencies for unstructured==0.12.5 in a separate dependency plan; do not blindly install the latest all-docs stack.
The local pdf_loader.py uses partition_pdf(strategy="hi_res", infer_table_structure=True), so plain text extraction alone will not reproduce its preprocessing.
The official README calls for Poppler, Tesseract, and NLTK punkt/averaged_perceptron_tagger resources. Plan and verify their versions separately.
Check required layout/table inference models and any first-run model downloads before executing one local PDF; no such downloads or execution happened in this task.

## Dependency metadata sources
https://pypi.org/pypi/langchain/0.1.7/json
https://pypi.org/pypi/langchain-community/0.0.20/json
https://pypi.org/pypi/langchain-core/0.1.41/json
https://pypi.org/pypi/langchain-openai/0.1.2/json
https://pypi.org/pypi/sentence-transformers/3.0.1/json
