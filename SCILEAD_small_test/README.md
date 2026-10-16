# SciLead API + 1–3 PDF 小样本测试

本包不包含 API Key 或 `.env`，不会自动调用全部数据集。

## 0. 准备

在可信的本机 / AutoDL / 导师服务器上：

```bash
# 放置本包文件、.env（不要推送至 Git）、官方 SCILEAD 仓库
python -m pip install requests
```

上传的 `.env` 包含 `BASE_URL` / `API_KEY`，留在本地，不要复制进公开仓库。
教程中的域名是 `api.iotwq.top`，用户 `.env` 给的是 `cn.iotwq.top`；脚本**只使用 `.env` 指定的地址**，不会自行重定向去另一个域名（服务器 HTTPS 重定向需单独检查）。

## 1. 最小模型探测（共最多 3 次，每次输出上限 8 tokens）

```bash
python probe_models.py --env .env --models gpt-4.1-2025-04-14 gpt-4.1 gpt-4-turbo-2024-04-09
```

打印请求模型、服务器自报模型、计费 token 数、异常类型；从不打印密钥。`SUCCESS` **不保证中转后台真实使用了指定快照**。

先验证 `gpt-4.1-2025-04-14` 成功，再考虑下一步。若具体快照名报不支持而 `gpt-4.1` 成功，说明可用别名，但不保证固定版本。

## 2. SCILEAD 单篇真实论文测试

准备官方代码：

```bash
git clone https://github.com/UKPLab/emnlp2024-leaderboard-generation.git
```

新建 Python 3.11 环境，按官方 README 安装依赖：

```bash
conda create -n scilead python=3.11 -y
conda activate scilead
pip install -r emnlp2024-leaderboard-generation/requirements.txt
pip install 'unstructured[all-docs]' requests
# 另外安装 Tesseract、Poppler、NLTK punkt / averaged_perceptron_tagger 等官方依赖
```

把 **SciLead 数据集的 1–3 篇真实 PDF** 放到 `scilead_pdfs/`，不要用无关论文代替。

```bash
python run_scilead_subset.py \
  --env .env \
  --repo ./emnlp2024-leaderboard-generation \
  --pdf-dir ./scilead_pdfs \
  --max-papers 1 \
  --model gpt-4.1-2025-04-14 \
  --max-output-tokens 1024 \
  --output ./scilead_subset_output.json
```

程序直接调用官方仓库 `pdf_loader.Documents` 中的 `hi_res` PDF 解析、嵌入检索、附加表格逻辑，并尽量沿用 GPT chat 的原 Prompt；仅更换 API 调用部分。

**注意**：这是连通性和单篇抽取 smoke test，未执行官方 normalization/evaluation，不能宣称论文 F1 复现成功。

## 3. 后续准确复现

在确认 API 可用后，冻结 PDF 文件、Git commit、Embedding 模型、Prompt、请求模型快照，再跑相同数据和设置下的 full baseline / modified ablation。重要：中转模型身份无法仅凭返回 `model` 字段得到独立证明。

## 安全提醒

不要公开 `.env`、不要把 KEY 发到聊天或代码仓库。考虑将已分享过的 Key 设为临时测试用途；若怀疑泄露，请在平台撤销并新建 Key。
