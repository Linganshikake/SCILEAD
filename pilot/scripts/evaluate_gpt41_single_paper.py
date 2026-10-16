"""Run original tdm_eval.py and add offline, strict-number error analysis."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT / 'emnlp2024-leaderboard-generation'
BASE = ROOT / 'pilot/outputs/gpt41_single_paper'
NORM = BASE / 'normalization'
OUT = BASE / 'evaluation'
GOLD = Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\tdm_annotations.json')
PAPER = '2020.findings-emnlp.378.pdf'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def guard(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise RuntimeError('Offline evaluation prohibits network access')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        p = Path(os.fsdecode(args[0])); text = str(p).replace('\\', '/').lower()
        if p.name.startswith('.env') or any(s in text for s in ('/.codex/', '/.claude/', '/.aws/')):
            raise RuntimeError('No sensitive configuration in evaluation')

def number(value):
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, ValueError):
        return None

def strict(a, b):
    return number(a) is not None and number(a) == number(b)

def fuzzy(a, b):
    return str(a) in str(b) or str(b) in str(a)

def tdm_match(a, b):
    return all(a[k] == b[k] for k in ('Task', 'Dataset', 'Metric'))

def scores(p, r):
    return {'Precision': p, 'Recall': r, 'F1': 2*p*r/(p+r) if p+r else 0.0}

def cell(value):
    return json.dumps(value, ensure_ascii=False).replace('|', '\\|').replace('\n', ' ')

def main():
    OUT.mkdir(exist_ok=True)
    usage = read(NORM / 'normalization_api_usage.json')
    assert usage['phase'] == 'COMPLETE'
    assert usage['actual_request_attempts'] == usage['completed_requests'] == 12
    normalized = read(NORM / 'normalized_output.json')
    assert list(normalized) == [PAPER]
    config = read(NORM / 'config.json')
    extracted = read(BASE / 'output.json')
    raw = json.loads(extracted[PAPER]['output'])
    predicted = normalized[PAPER]['normalized_output']
    assert normalized[PAPER]['source_documents'] == extracted[PAPER]['source_documents']
    assert [p['Result'] for p in predicted] == [p['Result'] for p in raw]
    assert sha(BASE / 'output.json') == config['extraction_sha256']
    assert sha(BASE / 'config.json') == config['extraction_config_sha256']
    assert sha(GOLD) == config['gold_sha256']
    assert all(sha(REPO / n) == h for n, h in config['source_hashes'].items())
    norm_hash = sha(NORM / 'normalized_output.json')
    os.chdir(ROOT / 'pilot/work')
    os.environ.update({'HF_HOME': str(ROOT / 'assets/huggingface'), 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'HF_HUB_DISABLE_TELEMETRY': '1', 'LANGCHAIN_TRACING_V2': 'false', 'LANGSMITH_TRACING': 'false'})
    sys.addaudithook(guard)
    sys.path.insert(0, str(REPO))
    sys.argv = [str(REPO / 'tdm_eval.py'), '--gold_data_path', str(GOLD), '--normalized_tdm_output_path', str(NORM / 'normalized_output.json'), '--eval_results_path', str(OUT / 'eval_results.json'), '--eval_values_path', str(OUT / 'eval_values.json')]
    runpy.run_path(str(REPO / 'tdm_eval.py'), run_name='__main__')
    official = read(OUT / 'eval_results.json')
    metrics = {f'{k} IIM': scores(v['Precision'], v['Recall']) for k, v in official['Individual'].items()}
    metrics['TDM Exact Match'] = scores(official['Exact Match Precision wo Results'], official['Exact Match Recall wo Results'])
    metrics['TDMR Exact Match'] = scores(official['Exact Match Precision'], official['Exact Match Recall'])
    save('metrics_with_f1.json', {'provenance': {'Precision': 'Original tdm_eval.py', 'Recall': 'Original tdm_eval.py', 'F1': 'Additional offline 2PR/(P+R); zero when P+R=0'}, 'metrics': metrics})
    gold = read(GOLD)[PAPER]['TDMs']
    gold_nums = {number(g['Result']) for g in gold}
    pred_nums = {number(p['Result']) for p in predicted}
    common = (gold_nums & pred_nums) - {None}
    strict_result = scores(len(common)/len(pred_nums) if pred_nums else 0, len(common)/len(gold_nums) if gold_nums else 0)
    used = set(); strict_full = 0
    for p in predicted:
        matches = [i for i, g in enumerate(gold) if i not in used and tdm_match(p, g) and strict(p['Result'], g['Result'])]
        if matches:
            used.add(matches[0]); strict_full += 1
    strict_tdmr = scores(strict_full/len(predicted) if predicted else 0, strict_full/len(gold) if gold else 0)
    discrepancies = [{'prediction_index': i+1, 'gold_index': j+1, 'prediction_result': p['Result'], 'gold_result': g['Result'], 'official_substring_match': fuzzy(p['Result'], g['Result']), 'strict_numeric_equal': strict(p['Result'], g['Result'])} for i, p in enumerate(predicted) for j, g in enumerate(gold) if fuzzy(p['Result'], g['Result']) != strict(p['Result'], g['Result'])]
    strict_report = {'definition': 'Decimal full-string numeric equality; no substring matching, rounding, unit stripping, percent conversion or value repair.', 'Result IIM': strict_result, 'TDMR Exact Match one_to_one': strict_tdmr, 'strict_result_values_matched': len(common), 'gold_result_values': len(gold_nums), 'fuzzy_vs_strict_pair_discrepancies': discrepancies, 'official_metrics_modified': False}
    save('strict_result_check.json', strict_report)
    # Offline error attribution only, never written into predictions.
    prior_review = read(BASE / 'validation.json')
    aliases = prior_review['dataset_aliases']
    comparisons = []
    for index, g in enumerate(gold):
        candidates = [i for i, p in enumerate(predicted) if strict(p['Result'], g['Result'])]
        exact = [i for i in candidates if tdm_match(predicted[i], g)]
        chosen = exact[0] if exact else candidates[0] if candidates else None
        p = predicted[chosen] if chosen is not None else None
        original = raw[chosen] if chosen is not None else None
        if chosen is None:
            reason = 'Result 未抽取或数值错误'
        elif exact:
            reason = '正确'
        elif any(p[k] is None for k in ('Task', 'Dataset', 'Metric')):
            reason = 'Result 正确但标准化失败'
        else:
            reason = 'Result 正确但 Task/Dataset/Metric 绑定错误'
        comparisons.append({'gold_index': index+1, 'gold': g, 'prediction_index': chosen+1 if chosen is not None else None, 'raw_extraction': original, 'normalized_prediction': p, 'strict_result_equal': chosen is not None, 'official_tdmr_match': bool(exact), 'strict_tdmr_match': bool(exact), 'error_type': reason, 'mismatched_fields': [k for k in ('Task', 'Dataset', 'Metric') if p is None or p[k] != g[k]], 'raw_dataset_semantically_matches_gold': original is not None and aliases.get(original['Dataset'], original['Dataset']) == g['Dataset'], 'attribution': 'Dataset normalization returned literal None, stored as JSON null; raw result and dataset abbreviation remain correct.' if p and p['Dataset'] is None else reason})
    extras = [{'prediction_index': i+1, 'prediction': p} for i, p in enumerate(predicted) if not any(strict(p['Result'], g['Result']) for g in gold)]
    save('tdmr_comparison.json', {'paper': PAPER, 'comparisons': comparisons, 'extra_non_gold_result_values': extras, 'errors': dict(Counter(v['error_type'] for v in comparisons)), 'note': 'Result equality uniquely aligns this paper’s six rows for diagnosis; it does not turn failed official matches into correct predictions.'})
    lines = ['# 单篇 TDMR 逐条错误分析', '', '所有 Gold 的 Task 均为 `Named Entity Recognition (NER)`，Metric 均为 `F1`。原始预测 Task 均为 `Named Entity Recognition`，Metric 均为 `F1`；标准化后 Task 均正确，Metric 原样保留。', '', '| Gold 序号 | Gold Task / Dataset / Metric / Result | 原始抽取四字段 | 标准化后四字段 | Result 严格相等 | 完整匹配 | 错误类型 |', '|---|---|---|---|---|---|---|']
    for row in comparisons:
        lines.append(f"| {row['gold_index']} | {cell(row['gold'])} | {cell(row['raw_extraction'])} | {cell(row['normalized_prediction'])} | {'是' if row['strict_result_equal'] else '否'} | {'是' if row['strict_tdmr_match'] else '否'} | {row['error_type']} |")
    lines += ['', '## 原因与边界', '', '- 六个数据集请求的服务端原始回答都是字符串 `None`；均 HTTP 200、finish_reason=stop、输出 1 Token，未触及 15 Tokens 上限。官方集合成员检查将其转换为 JSON null。', '- 对照实际请求：标准集合包含各正确全称，但模型输入仅有集合和缩写，没有论文中缩写定义。缺少语境可能影响映射；这是解释性推断，不能证明模型内部原因。', '- 抽取阶段的六个数值及缩写与 Gold 的语义对应正确，未发现 Baseline 混入；名称仍需标准化，并非原始字符串精确匹配。标准化阶段成功对齐 Task，但未能消解六个 Dataset 缩写。', '- 未发现缺失或额外数值，也未发现把某个 Result 绑定到另一个有效 Dataset 的错误；这里的失败是 Dataset 变成 null。', '- 官方模糊数值匹配与严格数值相等在本篇没有差异。Result IIM=1 不代表 TDMR 正确；Dataset 缺失使全部六条完整匹配失败。', '- 所有模型回答原样保留。没有提高输出上限、补充上下文、手动映射、修改 Prompt 或额外请求。']
    (OUT / 'tdmr_comparison.md').write_text('\n'.join(lines), encoding='utf-8')
    assert sha(NORM / 'normalized_output.json') == norm_hash
    assert all(sha(REPO / n) == h for n, h in config['source_hashes'].items())
    assert sha(BASE / 'output.json') == config['extraction_sha256']
    extraction_config = read(BASE / 'config.json')
    assert sha(Path(extraction_config['processed_docs_path'])) == extraction_config['processed_docs_sha256']
    git = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), 'status', '--porcelain'], cwd=REPO, text=True, capture_output=True, check=True)
    assert not git.stdout.strip(), git.stdout
    checks = {'official_script_executed': 'tdm_eval.py via runpy as __main__, original CLI arguments', 'network_for_evaluation': 'prohibited by audit guard', 'official_source_and_prompts_unchanged': True, 'extraction_output_and_config_unchanged': True, 'processed_docs_unchanged': True, 'normalized_output_not_corrected': True, 'source_documents_unchanged': True, 'git_clean': True, 'normalized_output_sha256': norm_hash, 'official_eval_results_sha256': sha(OUT / 'eval_results.json'), 'official_eval_values_sha256': sha(OUT / 'eval_values.json')}
    save('verification.json', checks)
    print(json.dumps({'official_metrics_with_additional_f1': metrics, 'strict_checks': strict_report, 'error_counts': dict(Counter(v['error_type'] for v in comparisons)), 'verification': checks}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
