"""Offline, post-response diagnostics. No prediction is rewritten."""
import argparse
from collections import Counter
from decimal import Decimal,InvalidOperation
import json
from pathlib import Path

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def num(x):
    try:
        d=Decimal(str(x));return d if d.is_finite() else None
    except InvalidOperation:return None
def eq(a,b):return num(a) is not None and num(a)==num(b)
def official(a,b):return str(a) in str(b) or str(b) in str(a)
def cell(x):return str(x).replace('|','\\|').replace('\n',' ')
def tdm(x):return ' / '.join(cell(x.get(k)) for k in ('Task','Dataset','Metric','Result'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True);a=ap.parse_args();run=a.run_root
    manifest=read(run/'manifest.json');gold=read(Path(manifest['gold_path']));out=run/'inspection';out.mkdir(exist_ok=True)
    diagnostics=read(run/'evaluation/error_analysis.json');metrics=read(run/'evaluation/metrics_with_f1.json');summaries=read(run/'stage_summary.json')
    rows=[];counts=Counter();findings=['# 全量 43 篇错误分类（离线）','','仅描述原始输出；没有按 Gold 修正预测或再次请求模型。自动分类定位症状，不自动判定所有 Baseline / Dev-Test 归因。','', '## 逐篇症状统计','','| 论文 | Gold | 抽取 | 数值缺失/非纯数值 | 数值存在但字段 null | 数值存在但名称/绑定不匹配 | 严格 TDMR 正确 |','|---|---:|---:|---:|---:|---:|---:|']
    comparison=['# 逐条 Gold 与原始 / 标准化输出对照','','候选索引按数值命中列出，不强行假设一对一关系；`±`、单位等非纯数值文本不满足 Decimal 严格相等。官方字符串包含匹配单独列出。']
    for paper in manifest['papers']:
        ident=paper['id'];ex=Path(paper['extraction_dir']);no=Path(paper['normalization_dir'])
        rawdoc=read(ex/'output.json') if (ex/'output.json').exists() else None
        try:raw=json.loads(rawdoc[ident]['output']) if rawdoc else None
        except ValueError:raw=None
        norm=read(no/'normalized_output.json')[ident]['normalized_output'] if (no/'normalized_output.json').exists() else None
        if ident not in diagnostics:
            findings.append(f'| {ident} | {paper["gold_count"]} | {len(raw) if isinstance(raw,list) else "非法/缺失"} | — | — | — | 未完成 |');continue
        d=diagnostics[ident];c=d['category_counts'];counts.update(c)
        findings.append(f'| {ident} | {paper["gold_count"]} | {len(raw)} | {c.get("numeric_result_missing_or_changed",0)} | {c.get("normalization_null",0)} | {c.get("numeric_match_but_binding_or_label_mismatch",0)} | {c.get("correct",0)} |')
        comparison+=['',f'## {ident}','','| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |','|---|---|---|---|---|']
        for g in d['gold_rows']:
            indices=g['strict_numeric_prediction_indices'];matches=[i+1 for i,p in enumerate(norm) if official(p['Result'],g['gold']['Result'])]
            comparison.append(f'| {g["gold_index"]}: {tdm(g["gold"])} | '+('<br>'.join(f'#{i}: {tdm(raw[i-1])} → {tdm(norm[i-1])}' for i in indices) or '—')+f' | {matches} | {g["strict_tdmr_prediction_indices"]} | {g["category"]} |')
        comparison+=['','### 全部原始预测与标准化结果','','| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |','|---|---|---|']
        for i,(r,n) in enumerate(zip(raw,norm),1):comparison.append(f'| {i} | {tdm(r)} | {tdm(n)} |')
        failures=[];u=read(no/'normalization_api_usage.json')
        for call in u.get('calls',[]):
            if not call.get('exact_member_of_standard_set'):
                expected=call.get('expected',call)
                failures.append({'record':expected['record'],'field':expected['field'],'original':expected['original_value'],'raw_answer':call.get('raw_answer'),'finish_reason':call.get('finish_reason')})
        rows.append({'paper':ident,'categories':c,'normalization_out_of_set':failures,'strict_vs_official_differences':d['substring_vs_strict_discrepancies'],'non_scalar_raw_results':[{'index':i+1,'value':r['Result']} for i,r in enumerate(raw) if num(r['Result']) is None],'extra_predictions_without_strict_numeric_gold_match':d['extra_prediction_values']})
    findings+=['','## 口径边界','','- “数值缺失/非纯数值”由完整 Result 字符串严格 Decimal 比较判定；可能是漏项、数值错误，也可能含 ± / 单位。需结合原文区分。','- “字段 null”表示相同数值的预测中出现标准化空值；不保证其他字段本来都正确。','- “名称/绑定不匹配”不自动证明抽取阶段错误，可能包含未正确标准化的名称。','- 表格检测成功不意味着单元格、标题和页码关联正确；每篇保留 raw-tables、table-documents 和实际 retrieval-evidence。','- 不因低分、null、重复、格式异常重跑；所有原始输出可在逐条对照报告中核验。','','详细记录：[diagnostics.json](diagnostics.json)；完整逐条对照：[tdmr_comparison.md](../evaluation/tdmr_comparison.md)。']
    findings.insert(2,'人工核验、表格页码、截图和 PDF / Gold 差异见 [manual_findings.md](manual_findings.md)；自动分类仅定位症状。')
    save(out/'diagnostics.json',{'automatic_category_counts':dict(counts),'papers':rows})
    (out/'findings.md').write_text('\n'.join(findings),encoding='utf-8')
    (run/'evaluation/tdmr_comparison.md').write_text('\n'.join(comparison),encoding='utf-8')
    print(json.dumps({'new_papers_analyzed':len(rows),'category_counts':dict(counts),'strict_vs_official_difference_pairs':sum(len(r['strict_vs_official_differences']) for r in rows)},ensure_ascii=False))
if __name__=='__main__':main()
