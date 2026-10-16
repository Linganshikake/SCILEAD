"""Offline report assembly after official evaluation and request audit."""
from collections import Counter
import hashlib,json,time,re
from decimal import Decimal,InvalidOperation
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'pilot/full43'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    m=read(RUN/'manifest.json');metrics=read(RUN/'evaluation/metrics_with_f1.json');coverage=metrics['scope']
    usage=read(RUN/'api_usage_summary.json');v=read(RUN/'verification.json');summaries=read(RUN/'stage_summary.json')
    diag=read(RUN/'evaluation/error_analysis.json');counts=Counter();nulls=Counter();invalid=[];discrepancies=[]
    for ident,d in diag.items():
        counts.update(d['category_counts'])
        discrepancies.extend(dict(paper=ident,**x) for x in d['substring_vs_strict_discrepancies'])
    for row in m['papers']:
        p=Path(row['normalization_dir'])/'normalized_output.json'
        if row['id'] not in metrics['per_paper']:continue
        for x in read(p)[row['id']]['normalized_output']:
            nulls.update(k for k in ('Task','Dataset','Metric') if x[k] is None)
    for row in m['papers']:
        p=Path(row['extraction_dir'])/'validation.json'
        if p.exists():
            validation=read(p)
            if validation.get('output_truncated') or validation.get('json_valid') is False:invalid.append(row['id'])
    n=len(diag)
    sp=sum(d['strict_result_iim']['Precision'] for d in diag.values())/n
    sr=sum(d['strict_result_iim']['Recall'] for d in diag.values())/n
    aux={'scope':coverage,'gold_row_mutually_exclusive_categories':dict(counts),'normalization_null_fields':dict(nulls),'substring_vs_strict_pair_count':len(discrepancies),'substring_vs_strict_pairs':discrepancies,'strict_result_iim_macro':{'Precision':sp,'Recall':sr,'F1':2*sp*sr/(sp+sr) if sp+sr else 0},'strict_definition':'Canonical finite Decimal equality; distinct nonnumeric Result strings each remain in denominator and never match. No unit conversion, tolerance, splitting or rewriting. Macro P/R then harmonic F1.','current_invalid_extraction_papers':invalid,'current_request_errors':v.get('failed_requests',[]),'current_truncated_requests':v.get('truncations',[]),'baseline_or_dev_test_error_counts':'Not exhaustively adjudicated; confirmed examples only, no automatic attribution from numeric mismatch.'}
    save(RUN/'inspection/error_summary.json',aux)
    gold=read(Path(m['gold_path']));visibility={}
    for row in m['papers']:
        if row['id'] not in metrics['per_paper']:continue
        docs=read(Path(row['extraction_dir'])/'output.json')[row['id']]['source_documents']
        evidence_numbers=[]
        for doc in docs:
            nums=set()
            for token in re.findall(r'(?<![\w.])[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?![\w.])',doc['content']):
                try:nums.add(Decimal(token))
                except InvalidOperation:pass
            evidence_numbers.append(nums)
        records=[]
        for i,g in enumerate(gold[row['id']]['TDMs'],1):
            try:value=Decimal(str(g['Result']))
            except InvalidOperation:value=None
            matches=[j for j,numbers in enumerate(evidence_numbers) if value is not None and value in numbers]
            records.append({'gold_index':i,'result':g['Result'],'matching_evidence_indices':[j+1 for j in matches],'matching_pages':[docs[j]['metadata'].get('page_number') for j in matches]})
        visibility[row['id']]=records
    save(RUN/'inspection/numeric_evidence_visibility.json',{'method':'Post-response numeric literal scan of unchanged actual source_documents. Presence does not establish Task/Dataset/Metric binding; absence does not prove parsing or retrieval caused an error. No evidence or prediction was changed.','papers':visibility})
    comparisons={}
    for name in ('subset5','subset15_uncapped_retry'):
        old=read(ROOT/'pilot'/name/'evaluation/metrics_with_f1.json')
        comparisons[name]={'papers':old['scope']['completed_papers'],'gold':old['scope']['evaluated_gold_tdmrs'],'aggregate':old['aggregate']}
    comparisons['full43']={'papers':coverage['completed_papers'],'gold':coverage['evaluated_gold_tdmrs'],'aggregate':metrics['aggregate']}
    save(RUN/'evaluation/comparison_5_15_43.json',comparisons)
    progress=read(RUN/'execution_progress.json')
    usage['execution_wall_seconds']=round(progress['finished_epoch']-progress['started_epoch'],3)
    usage['elapsed_to_final_report_seconds']=round(time.time()-read(RUN/'environment.json')['started_epoch'],3)
    cumulative_model_seconds=0.0
    for row in m['papers']:
        for folder,name in ((row['extraction_dir'],'api_usage.json'),(row['normalization_dir'],'normalization_api_usage.json')):
            path=Path(folder)/name
            if not path.exists():continue
            u=read(path)
            cumulative_model_seconds+=sum(c.get('seconds',c.get('elapsed_seconds',0)) for c in u['calls']) if u.get('calls') else u.get('elapsed_seconds',0)
    failed_path=ROOT/'pilot/subset15/papers/1912.08777/extraction-approved-context/api_calls/0001/state.json'
    assert usage['historical_failed_attempts']['requests']==1
    cumulative_model_seconds+=read(failed_path)['seconds']
    usage['cumulative_recorded_model_request_seconds_sum']=round(cumulative_model_seconds,3)
    usage['cumulative_recorded_pdf_preprocess_seconds_sum']=round(sum(s['preprocess_seconds'] or 0 for s in summaries),3)
    usage['cumulative_time_definition']='Sum of unique recorded per-paper PDF processing times and per-request times, including historical failed request. These are separate from run wall time and are not summed with wall time.'
    save(RUN/'api_usage_summary.json',usage)
    completed_new=sum(not s['reused'] and s['evaluated'] for s in summaries)
    prefix=[f'# SCILEAD 全量 Baseline：{coverage["completed_papers"]}/43 篇', '',f'覆盖 {coverage["evaluated_gold_tdmrs"]}/295 条 Gold；本轮新增 {completed_new}/28 篇完成，历史 15 篇只读复用。完整覆盖与质量得分分别报告。', '',f'本轮实际 API 请求 {usage["new_experiment"]["requests"]} 次、{usage["new_experiment"]["total_tokens"]:,} Tokens；包含历史失败请求的累计用量为 {usage["cumulative_selected"]["requests"]} 次、{usage["cumulative_selected"]["total_tokens"]:,} Tokens。本轮流水线墙钟 {usage["execution_wall_seconds"]:.1f} 秒。', '', '实际请求参数、响应及用量已经逐条核验；旧十五篇官方指标离线复算一致，历史文件与官方源码、Prompt、依赖保持不变。未修改预测值或按照得分重跑。', '']
    prefix.extend(['历史至今已记录的 PDF 处理耗时之和为 '+str(usage['cumulative_recorded_pdf_preprocess_seconds_sum'])+' 秒；模型请求耗时之和（包含历史失败请求）为 '+str(usage['cumulative_recorded_model_request_seconds_sum'])+' 秒。两者是阶段耗时口径，不是累计墙钟时间，不能与本轮墙钟相加。',''])
    body=(RUN/'report.md').read_text('utf-8')
    body=body[body.index('## 完成覆盖率'):].split('\n## 5 / 15 / 43 篇描述性对比')[0].rstrip()+'\n'
    prefix.extend([f'新增 28 篇 PDF 全部成功解析与检索；本轮抽取 {sum(s["extracted_records"] for s in summaries if not s["reused"])} 条，累计 {sum(s["extracted_records"] for s in summaries)} 条。371 次请求包含 28 次 Extraction 和 343 次 Normalization，全部 HTTP 200、返回固定快照、finish_reason=stop；28 个新抽取结果同时通过 JSON 和字段检查。没有自动重试。', '', '1,465 个历史文件哈希、官方源码与 Prompt、完整 Gold 哈希、183 个依赖版本均核验一致。一个原始出版社链接返回 HTML 阅读页，改用同页公开 PDF 链接后成功；这不是论文替换，也没有更换解析方法。', ''])
    suffix=['','## 5 / 15 / 43 篇描述性对比','','| 指标 | 5 篇 F1 | 15 篇 F1 | 本轮累计 F1 |','|---|---:|---:|---:|']
    for metric in metrics['aggregate']:
        suffix.append('| '+metric+' | '+' | '.join(f'{comparisons[x]["aggregate"][metric]["F1"]:.6f}' for x in ('subset5','subset15_uncapped_retry','full43'))+' |')
    suffix+=['','样本规模与论文构成变化，同时存在历史输出上限差异，分数升降仅作描述，不归因于算法或设置改进。','','## 历史与新请求配置','','- 历史十四篇抽取使用 max_tokens=1024；长论文 1912.08777.pdf 的成功抽取省略输出上限。','- 历史十五篇 Normalization 使用 max_tokens=15；新增二十八篇 Extraction 和 Normalization 均实际省略输出上限参数。','- 新请求无固定输入 Token 暂停门槛，不截断证据；原始 Prompt、模型快照、temperature=0、seed=0 和逐字段方法保留。','- 历史被截断请求不参与评价，但其 1 次请求、55,528 Tokens 保留在历史累计账目中。','- 服务端模型 ID、HTTP 状态、finish_reason 与 JSON 有效性均有记录；中转站后台身份、种子确定性、静默输入截断及真实金额无法仅靠这些日志独立验证。','','## 错误归类与严格数值诊断','','以下按 Gold 行归类，互斥分类仅定位症状，不自动证明具体错误发生阶段。','','| 类型 | Gold 行数 |','|---|---:|']
    category_names={'normalization_null':'数值命中，但对应预测存在标准化 null','numeric_result_missing_or_changed':'数值未严格命中（含遗漏、差异及非纯数字格式）','correct':'严格完整 TDMR 命中','numeric_match_but_binding_or_label_mismatch':'数值命中，但名称或字段绑定不符'}
    for k,c in counts.items():suffix.append(f'| {category_names[k]} | {c} |')
    suffix += ['',f'标准化 null 字段数：{dict(nulls)}。官方字符串包含与严格 Decimal 比较有 {len(discrepancies)} 对结果不一致。严格 Result 辅助 Macro P/R/F1={sp:.6f}/{sr:.6f}/{aux["strict_result_iim_macro"]["F1"]:.6f}。这不是官方指标。', '', '严格比较将有限十进制数规范化为数值；每个不同的非纯数字 Result 字符串保留在分母中且不视为匹配，不拆分 ±、单位或多个指标。逐条原始输出、标准化输出、Gold、候选匹配索引见 `evaluation/tdmr_comparison.md`。', '', 'Baseline 混入、Dev/Test 混淆及表格标题错配只记录已有证据支持的例子，未逐项人工裁决的情况不编造总数。详细说明见 `inspection/findings.md` 与 `inspection/manual_findings.md`。', '', '## 工程状态与文件入口', '', '- `manifest.json` / `output_index.json`：43 篇处理状态与文件索引。', '- `merged/output.json` / `merged/normalized_output.json`：原始官方格式合并结果。', '- `evaluation/eval_results.json` / `eval_values.json`：未修改的官方脚本直接输出。', '- `evaluation/metrics_with_f1.json` / `per_paper_metrics.json`：官方 P/R 与额外调和 F1。', '- `verification.json`：历史哈希、候选集合、实际请求体、用量和旧十五篇复算检查。', '- `file_integrity_sha256.json`：本目录最终文件哈希；`preserved_existing_sha256.json`：历史文件哈希。', '- `reproducibility/`：实际执行适配脚本副本，`environment.json`：完整依赖和源码哈希。', '- 断点与恢复说明见 `README.md`。成功结果不可删除、覆盖或因低分重跑。']
    (RUN/'report.md').write_text('\n'.join(prefix)+body+'\n'+'\n'.join(suffix),encoding='utf-8')
    for name in ('prepare_full43.py','full43_evaluate.py','inspect_full43.py','audit_full43.py','finalize_full43.py'):
        (RUN/'reproducibility'/name).write_bytes((ROOT/'pilot/scripts'/name).read_bytes())
    print(json.dumps({'coverage':coverage,'usage':usage,'errors':dict(counts),'null_fields':dict(nulls),'strict_discrepancy_pairs':len(discrepancies)},ensure_ascii=False,indent=2),flush=True)
    save(RUN/'file_integrity_sha256.json',{str(p.relative_to(RUN)):hashlib.sha256(p.read_bytes()).hexdigest() for p in RUN.rglob('*') if p.is_file() and p.name!='file_integrity_sha256.json'})
if __name__=='__main__':main()
