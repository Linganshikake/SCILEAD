"""Offline inspection only. No model/client initialization or normalization."""
import hashlib
import importlib.util
import json
from pathlib import Path
import pickle
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'pilot/outputs/gpt41_single_paper'
REPO = ROOT / 'emnlp2024-leaderboard-generation'
PAPER = '2020.findings-emnlp.378.pdf'

def load(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

usage, config, validation = load('api_usage.json'), load('config.json'), load('validation.json')
assert usage['http_status'] == 200 and usage['actual_model_request_attempts'] == 1
assert usage['returned_model'] == 'gpt-4.1-2025-04-14'
output = load('output.json')
assert list(output) == [PAPER]
records = json.loads(output[PAPER]['output'])
raw_api = load('raw_api_response.json')
assert raw_api['choices'][0]['message']['content'] == output[PAPER]['output']
assert len(records) == 6 and validation['results_are_strings'] and not validation['duplicates']
source = Path(config['processed_docs_path'])
assert digest(source) == config['processed_docs_sha256']
with source.open('rb') as f:
    original = pickle.load(f)
assert output[PAPER]['source_documents'] == [{'content': d.page_content, 'metadata': d.metadata} for d in original[PAPER]]
for name, value in config['source_hashes'].items():
    assert digest(REPO / name) == value
status = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), 'status', '--porcelain'], cwd=REPO, text=True, capture_output=True, check=True)
assert not status.stdout.strip()

# These aliases are a post-response inspection mapping, never sent to the model.
aliases = {'ON5E': 'Ontonotes v5 - English', 'WN16': 'WNUT-16 - English', 'WN17': 'WNUT-17 - English', 'ON4C': 'Ontonotes v4 - Chinese', 'RE': 'Resume - Chinese', 'WE': 'Weibo - Chinese'}
gold = json.loads((ROOT / 'pilot/gold/tdm_annotations.json').read_text(encoding='utf-8'))[PAPER]['TDMs']
matched = []
for row in records:
    matches = [g for g in gold if aliases.get(row['Dataset']) == g['Dataset'] and row['Task'] == 'Named Entity Recognition' and g['Task'] == 'Named Entity Recognition (NER)' and row['Metric'] == g['Metric'] and row['Result'] == str(g['Result'])]
    matched.append(bool(matches))
assert all(matched)
literal_matches = sum(any(all(str(row[k]) == str(g[k]) for k in ('Task', 'Dataset', 'Metric', 'Result')) for g in gold) for row in records)
review = {'numeric_gold_matches': 6, 'gold_count': 6, 'manual_semantic_binding_matches': sum(matched), 'literal_field_matches_before_normalization': literal_matches, 'binding_errors_found': [], 'baseline_contamination_found': False, 'baseline_review_basis': 'All six tuples match Table 5 OURS row, PDF page 7; no extra baseline-valued records returned.', 'dataset_aliases': aliases, 'alias_source': 'Cached stage3 partition-elements.json, PDF page 5, dataset definitions. Read offline after response; not appended to request.', 'metric': 'F1', 'task_name_difference': 'Named Entity Recognition vs Gold Named Entity Recognition (NER)', 'normalization_performed': False, 'official_evaluation_performed': False, 'warning': 'Manual semantic check is not an official normalized evaluation score and does not establish multi-paper accuracy.'}
validation.update(review)
save('validation.json', validation)
comparison = load('gold_comparison.json')
comparison['binding_and_baseline_status'] = 'Reviewed: six semantic bindings correct; no baseline contamination; abbreviated dataset and task names differ from Gold labels.'
save('gold_comparison.json', comparison)

# Verify that the persisted one-attempt guard rejects another launch before key reading.
spec = importlib.util.spec_from_file_location('single_request_adapter', Path(__file__).with_name('run_gpt41_single_paper.py'))
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
try:
    adapter.main(False)
except RuntimeError as exc:
    assert 'Persistent request marker exists' in str(exc)
else:
    raise AssertionError('Repeat-launch protection failed')

# Secret-presence check emits only a boolean, never a credential or excerpt.
from dotenv import dotenv_values
values = dotenv_values(ROOT / 'SCILEAD_small_test/.env', interpolate=False, encoding='utf-8-sig')
import os
secrets = [v for k, v in values.items() if k in ('API_KEY', 'OPENAI_API_KEY') and v]
secrets += [os.environ[k] for k in ('OPENAI_API_KEY', 'API_KEY') if os.environ.get(k)]
for path in OUT.iterdir():
    if path.is_file():
        content = path.read_bytes()
        assert not any(value.encode() in content for value in secrets), 'Credential found in artifact'
verification = {'original_sources_unchanged': True, 'processed_docs_unchanged': True, 'source_documents_exact_match': True, 'raw_model_output_unmodified': True, 'git_clean': True, 'single_request_marker_present': True, 'repeat_launch_blocked_before_key_read': True, 'credentials_absent_from_saved_artifacts': True, 'actual_request_attempts': 1}
save('final_verification.json', verification)

lines = ['# GPT-4.1 单篇 TDMR 抽取实验', '', '时间：2026-10-13（Asia/Shanghai）。结果：成功。HTTP 200；客户端实际仅发起一次模型请求，无重试、无额外 LLM 调用。', '', '## 实验条件', '', '- 论文：`2020.findings-emnlp.378.pdf`。复用已有 16 条检索证据，未重新解析 PDF、未重新检索。', '- 请求及响应模型 ID 均为 `gpt-4.1-2025-04-14`；固定快照名称已请求且响应一致，无法独立验证中转站的后端实现。', '- 接口：`https://9527.codes/v1/chat/completions`；现有 `langchain-openai==0.1.2` + `ChatOpenAI`。', '- temperature=0，seed=0，max_tokens=1024，n=1，stream=False，SDK max_retries=0；连接超时 20 秒、读取超时 180 秒。', '- seed 参数随成功请求被接收，但不能由单次调用证明服务端确实使用该种子或确定性复现。', '- 原始 `TDMPrompt` 的 GPT 分支、System Prompt、Query、system/user 角色、`RetrievalQA(stuff)` 均保留。没有新增 JSON mode、few-shot 或额外指令。', '- Gold 仅在模型响应和原始输出保存之后读取；实际消息体已保存并与离线 Prompt 构造结果逐字比较。', '- 原始源码、prompts.json、processed_docs.pkl 均以 SHA256 复核未变；独立结果目录未覆盖预处理输出。', '', '## Dry Run 与用量', '', '| 项目 | 值 |', '|---|---:|', f"| 本地输入估算 | {usage['estimated_prompt_tokens']} Tokens |", f"| 服务端 Prompt Tokens | {usage['prompt_tokens']} |", f"| Completion Tokens | {usage['completion_tokens']} |", f"| Total Tokens | {usage['total_tokens']} |", f"| 请求耗时 | {usage['elapsed_seconds']} 秒 |", '| 实际客户端模型请求 | 1 |', '', '估算采用 o200k_base 和 Chat 消息开销，服务端本次报告与估算一致。词表来自 OpenAI 官方公开地址，SHA256 校验通过。服务商的完整上下文上限仍为 UNVERIFIED；用户明确授权在完整输入不超过 30,000 Tokens 时执行一次，本次请求成功仅验证了当前长度。OpenAI 官方模型文档为 1,047,576 上下文、32,768 最大输出，不据此推定中转站上限。', '', f"响应 ID：`{usage['response_id']}`。系统指纹：`{usage['system_fingerprint']}`。HTTP `x-request-id` / `request-id` 未返回。结束原因：`{usage['finish_reason']}`。平台账单未获取，实际费用和计费一致性无法核对；没有使用 LangChain 美元估算替代平台结算。", '', '## 原始结果与 Gold 对照', '', '原始返回为可直接 json.loads() 解析的完整数组，共 6 条；字段齐全、Result 全为字符串、无重复、未截断。Task 均为 Named Entity Recognition，Metric 均为 F1。', '', '| 模型 Dataset | Gold Dataset | 模型 Result | Gold Result | 绑定检查 |', '|---|---|---|---:|---|']
for row in records:
    g = next(g for g in gold if g['Dataset'] == aliases[row['Dataset']])
    lines.append(f"| {row['Dataset']} | {g['Dataset']} | `{row['Result']}` | {g['Result']} | 正确 |")
lines += ['', '六个数值命中 6/6；人工语义绑定检查 6/6，未发现数值正确但 Task/Dataset/Metric 错配，也未发现 Baseline 混入。核对依据是第 7 页 Table 5 的 OURS 行和已缓存的第 5 页数据集定义。', '', '**命名差异保留：** Dataset 是论文缩写，Task 没有 Gold 中的 `(NER)` 后缀。若四字段字符串逐字比较，当前匹配为 0/6（Result 仅作字符串比较），不能将数值/人工语义命中率视为官方评测指标。没有将缩写展开写回 output.json，没有运行自动 Normalization 或 Evaluation。', '', '原始模型输出：', '', '```json', output[PAPER]['output'], '```', '', '## 已知输入局限', '', '保留第三阶段所有证据，包括第 9 页 Figure 3 的表格误检及附录标题关联问题。本轮没有清理、纠正、筛选证据或调整 Prompt。检索文本未包含完整的数据集缩写定义，模型沿用结果表中的缩写；本次离线检查使用缓存全文确认其含义。', '', '## 保存文件', '', '- `output.json`：官方核心结构，原始模型 JSON 文本与 16 条 source_documents。', '- `config.json`、`dry_run_report.json`：参数、约束、来源及哈希；不含密钥。', '- `input_messages.json`、`request_payload.json`：实际消息和请求体，不含 Authorization Header。', '- `raw_api_response.json`、`api_usage.json`：原始响应与用量。', '- `validation.json`、`gold_comparison.json`：格式、重复、绑定与离线 Gold 检查。', '- `run.log`、`request-attempt.json`：脱敏日志与禁止重复请求的持久标记。', '- `offline_sdk_test.json`、`final_verification.json`：本地 SDK 参数测试和最终完整性验证。', '', '## 后续阶段', '', '可以进入 Normalization 与 Evaluation 的独立阶段，主要处理论文缩写与 Gold 标准名称的对齐。当前只验证了一篇论文，不能外推整体性能。若后续选择需要 LLM 的官方 normalization 脚本，应另行授权请求次数和费用；本轮没有运行。', '', '官方模型信息来源：https://developers.openai.com/api/docs/models/gpt-4.1 。']
(OUT / 'extraction_analysis.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'final_verification': verification, 'records': len(records), 'numeric_matches': 6, 'semantic_bindings_correct': 6, 'baseline_contamination_found': False, 'analysis_report': str(OUT / 'extraction_analysis.md')}, ensure_ascii=False, indent=2))
