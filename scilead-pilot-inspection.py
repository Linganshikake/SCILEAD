"""Inspect already-produced outputs; never rerun PDF parsing or retrieval."""
import hashlib
import json
from pathlib import Path
import pickle
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
P = ROOT / 'pilot'
summary = json.loads((P / 'latest-run.json').read_text(encoding='utf-8'))
O = Path(summary['output_path'])
provenance = json.loads((P / 'data-provenance.json').read_text(encoding='utf-8'))
tables = json.loads((O / 'official-table-documents.json').read_text(encoding='utf-8'))
raw = json.loads((O / 'raw-tables.json').read_text(encoding='utf-8'))
evidence = json.loads((O / 'retrieval-evidence.json').read_text(encoding='utf-8'))
with (O / 'processed_docs.pkl').open('rb') as f:
    official = pickle.load(f)
assert summary['status'] == 'PASS'
assert len(official) == 1 and len(official[provenance['paper']]) == 16
assert len(tables) == len(raw) == 12
assert len(json.loads((O / 'text-chunks.json').read_text(encoding='utf-8'))) == 25
assert all({'text': d.page_content, 'metadata': d.metadata} == e for d, e in zip(official[provenance['paper']], evidence[provenance['paper']]))
source_req = ROOT / 'emnlp2024-leaderboard-generation/requirements.txt'
assert hashlib.sha256(source_req.read_bytes()).hexdigest() == '9a074c4962e8dd756bf46ee5bf87d54b75f09542a9de0e16da3962b037e4adf1'
check = subprocess.run([sys.executable, '-m', 'pip', 'check'], text=True, capture_output=True, check=True)
repo = ROOT / 'emnlp2024-leaderboard-generation'
status = subprocess.run(['git', '-c', 'safe.directory=' + repo.as_posix(), 'status', '--porcelain'], cwd=repo, text=True, capture_output=True, check=True)
assert not status.stdout.strip(), status.stdout

observations = [
    '12 个 Table 检测区域并非 12 张独立真实表：第 9 页 Figure 3 被误检；Table 8 的 (a)/(b) 子表在第 14 页分为两个区域。',
    '视觉核对第 7、9、14 页。第 7 页 Table 5 OURS 的六个结果值与 Gold 一致，并完整出现在官方证据文本中。',
    'Table 8(a) 的官方表格文档没有标题，8(b) 仅附带子标题，完整 Table 8 标题未被附加；报告中的对应关系来自人工视觉核对。',
    '复杂表格原始文本会按列展平、勾选标记脱离行，不能把数值存在当作逐单元格结构完全准确。未全面核验其余表格单元格。',
    '不修改或删除误检证据，不校正原始文本，不更改官方 processed_docs.pkl；下一阶段需保留这些误差作为预处理边界。',
]
mapping = ['Table 1: dataset statistics', 'Table 2: individual syntactic information', 'Table 3: syntax combinations', 'Table 4: gate mechanism', 'Table 5: comparison with previous studies', 'Table 6: embedding combinations', 'FALSE POSITIVE: Figure 3', 'Table 7: BERT vs ZEN', 'Table 8(a): English context encoders', 'Table 8(b): Chinese context encoders', 'Table 9: hyperparameters', 'Table 10: development configurations']
gold_checks = []
for row in provenance['gold']['TDMs']:
    score = str(row['Result'])
    present = bool(re.search(r'(?<![\d.])' + re.escape(score) + r'(?![\d.])', tables[4]['text']))
    assert present
    gold_checks.append({**row, 'present_in_page7_table5': present, 'visual_verified': True})
quality = {'observations': observations, 'gold_checks': gold_checks, 'output_verified': True, 'pip_check': check.stdout.strip(), 'git_clean': True, 'processed_docs_sha256': hashlib.sha256((O / 'processed_docs.pkl').read_bytes()).hexdigest()}
(O / 'quality-review.json').write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding='utf-8')
lines = ['# SciLead 单篇预处理人工检查报告', '', f"论文：{provenance['paper_title']}；文件：`{provenance['paper']}`；15 页。", '', '结果：CPU hi_res 表格推理与原始 MPNet/Chroma 检索实际完成；25 个文本块、245 个元素、12 个 Table 区域、16 条证据（4 Text + 12 Table）。耗时 108.86 秒。', '', '## 质量核验与限制', '']
lines += ['- ' + s for s in observations]
lines += ['', '## Gold 结果对照（NER / F1，第 7 页 Table 5）', '', '| Gold 数据集 | Gold 结果 | 原始证据中存在 |', '|---|---:|---|']
lines += [f"| {g['Dataset']} | {g['Result']} | 是；已视觉核对 OURS 行 |" for g in gold_checks]
lines += ['', '## 可视化抽查', '']
for page in [7, 9, 14]: lines += [f'### PDF 第 {page} 页', '', f'![page {page}](page-{page}.png)', '']
lines += ['## 全部表格区域（保留原始文本及 HTML）', '']
for i, (t, r) in enumerate(zip(tables, raw)):
    lines += [f"### 区域 {i+1} / 第 {t['metadata']['page_number']} 页 / {mapping[i]}", '', '上面的表号映射是检查记录，不写回官方输出。以下为官方原始表格文档（含其实际附加的标题）：', '', '```text', t['text'], '```', '', 'Unstructured 原始表格 HTML：', '', '```html', r['metadata'].get('text_as_html', '(none)'), '```', '']
lines += ['## 官方查询与完整检索证据', '', '```json', (O / 'config.json').read_text(encoding='utf-8'), '```', '']
for i, e in enumerate(evidence[provenance['paper']], 1):
    lines += [f"### 证据 {i} / {e['metadata']['type']} / PDF 第 {e['metadata']['page_number']} 页", '', '```text', e['text'], '```', '']
(O / 'inspection.md').write_text('\n'.join(lines), encoding='utf-8')
vpath = ROOT / 'scilead-pdf-validation.json'
v = json.loads(vpath.read_text(encoding='utf-8'))
v.update(status='Installation and real single-paper preprocessing passed; documented table detection/structure limitations', real_scilead_papers_processed=1, dataset_status='User supplied local Gold, matching their data ZIP; 43 papers / 295 TDMRs', official_doc_preprocess_run=True, pilot=summary, quality_review=quality, pip_check=check.stdout.strip())
vpath.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'verification': 'PASS', 'pip_check': check.stdout.strip(), 'git_clean': True, 'summary': summary, 'quality': quality, 'inspection_report': str(O / 'inspection.md')}, ensure_ascii=False, indent=2))
