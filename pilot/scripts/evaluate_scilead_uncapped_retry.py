"""Merge immutable outputs, run official evaluation, disclose subset coverage."""
from collections import Counter
from decimal import Decimal,InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];SUB=Path(os.environ.get('SCILEAD_RUN_ROOT',str(ROOT/'pilot/subset15_uncapped_retry'))).resolve();REPO=ROOT/'emnlp2024-leaderboard-generation'
assert SUB.is_relative_to((ROOT/'pilot').resolve()),'Run root must remain inside SCILEAD/pilot'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');t.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f1(p,r):return 2*p*r/(p+r) if p+r else 0.0
def metric(p,r):return {'Precision':p,'Recall':r,'F1':f1(p,r)}
def number(x):
    try:
        d=Decimal(str(x));return d if d.is_finite() else None
    except InvalidOperation:return None
def strict(a,b):return number(a) is not None and number(a)==number(b)
def fields(a,b):return all(a[k]==b[k] for k in ('Task','Dataset','Metric'))
def main():
    manifest=read(SUB/'manifest.json');env=read(SUB/'environment.json');gold=read(Path(manifest['gold_path']))
    assert sha(Path(manifest['gold_path']))==manifest['gold_sha256']
    for p,h in read(SUB/'preserved_existing_sha256.json').items():assert sha(Path(p))==h,'Existing baseline changed: '+p
    for p,h in env['source_sha256'].items():assert sha(Path(p))==h,'Official file changed: '+p
    output={};normalized={};summaries=[];new_totals={'requests':0,'prompt_tokens':0,'completion_tokens':0,'total_tokens':0};historical=dict(new_totals);errors={}
    process_seconds=0.0;api_seconds=0.0
    for row in manifest['papers']:
        ident=row['id'];pre=Path(row['preprocess_dir']);ex=Path(row['extraction_dir']);norm=Path(row['normalization_dir']);reuse=row['reused']
        pre_summary=pre/'summary.json' if (pre/'summary.json').exists() else pre/'pilot-summary.json'
        ps=read(pre_summary) if pre_summary.exists() else {}
        es=read(ex/'summary.json') if (ex/'summary.json').exists() else {}
        ns=read(norm/'summary.json') if (norm/'summary.json').exists() else {}
        raw_rows=None
        if (ex/'output.json').exists():
            data=read(ex/'output.json');assert list(data)==[ident];output.update(data)
            try:raw_rows=json.loads(data[ident]['output'])
            except ValueError:pass
        complete=(norm/'normalized_output.json').exists() and (reuse or ns.get('status')=='COMPLETE')
        if complete:
            data=read(norm/'normalized_output.json');assert list(data)==[ident];normalized.update(data)
            assert data[ident]['source_documents']==output[ident]['source_documents']
            assert [r['Result'] for r in data[ident]['normalized_output']]==[r['Result'] for r in raw_rows]
        u=read(norm/'normalization_api_usage.json') if (norm/'normalization_api_usage.json').exists() else {}
        calls=u.get('calls',[])
        legal=sum(bool(c.get('exact_member_of_standard_set')) for c in calls)
        illegal=len([c for c in calls if c.get('raw_answer') is not None])-legal
        nr=normalized[ident]['normalized_output'] if complete else []
        s={'paper':ident,'reused':reuse,'gold_count':row['gold_count'],'pdf_pages':row.get('pdf_pages',15 if reuse else None),'text_chunks':ps.get('text_chunks'),'table_regions':ps.get('table_count'),'table_pages':ps.get('table_pages'),'evidence_count':ps.get('evidence_count'),'preprocess_seconds':ps.get('seconds'),'extracted_records':len(raw_rows) if isinstance(raw_rows,list) else None,'extraction_status':'COMPLETE_REUSED' if reuse else es.get('status','NOT_COMPLETE'),'normalization_status':'COMPLETE_REUSED' if reuse else ns.get('status','NOT_COMPLETE'),'normalization_calls':u.get('actual_request_attempts',0),'llm_in_set_answers':legal,'llm_out_of_set_answers':illegal,'normalized_null_fields':sum(r[k] is None for r in nr for k in ('Task','Dataset','Metric')) if complete else None,'evaluated':complete,'pdf_path':row['pdf_path'],'preprocess_dir':str(pre),'extraction_dir':str(ex),'normalization_dir':str(norm)}
        summaries.append(s);row['status']='COMPLETE_REUSED' if reuse else ('COMPLETE' if complete else 'INCOMPLETE_'+s['extraction_status']);row['stage_summary']=s
        if not complete:errors[ident]={'extraction':es,'normalization':ns,'reason':'No complete compatible normalization output; excluded from official metrics with explicit coverage disclosure'}
        for stage,path in [('extract',ex/'api_usage.json'),('normalize',norm/'normalization_api_usage.json')]:
            if not path.exists():continue
            use=read(path);target=historical if reuse else new_totals
            target['requests']+=use.get('actual_request_attempts',use.get('actual_model_request_attempts',0))
            for k in ('prompt_tokens','completion_tokens','total_tokens'):target[k]+=use.get(k,0) or 0
            if not reuse:
                api_seconds+=sum(c.get('seconds',0) for c in use.get('calls',[]))
        if not reuse:process_seconds+=(0 if row.get('preprocess_reused') else (ps.get('seconds',0) or 0))+(es.get('seconds',0) or 0)+(ns.get('seconds',0) or 0)
    historical_completed=dict(historical)
    prior_accounting=read(SUB/'prior_accounting.json')['cumulative_selected']
    prior_failed={k:prior_accounting[k]-historical[k] for k in historical}
    assert prior_failed['requests']==1 and prior_failed['total_tokens']==55528
    historical=prior_accounting
    merged=SUB/'merged';evaluation=SUB/'evaluation';evaluation.mkdir(exist_ok=True)
    save(merged/'output.json',output);save(merged/'normalized_output.json',normalized)
    coverage={'selected_papers':len(manifest['papers']),'completed_papers':len(normalized),'coverage':len(normalized)/len(manifest['papers']),'selected_gold_tdmrs':sum(r['gold_count'] for r in manifest['papers']),'evaluated_gold_tdmrs':sum(len(gold[p]['TDMs']) for p in normalized),'evaluated_ids':list(normalized),'incomplete':errors,'metric_scope':f'{len(normalized)}/{len(manifest["papers"])} selected papers; no claim of full coverage when incomplete'}
    save(evaluation/'coverage.json',coverage)
    os.chdir(SUB/'work');os.environ.update({'HF_HOME':str(ROOT/'assets/huggingface'),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','LANGCHAIN_TRACING_V2':'false','LANGSMITH_TRACING':'false'})
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Evaluation is offline')
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(os.fsdecode(args[0]));s=str(p).replace('\\','/').lower()
            if p.name.startswith('.env') or '/.codex/' in s or '/.claude/' in s:raise RuntimeError('No sensitive config in evaluation')
    sys.addaudithook(guard);sys.path.insert(0,str(REPO))
    sys.argv=[str(REPO/'tdm_eval.py'),'--gold_data_path',manifest['gold_path'],'--normalized_tdm_output_path',str(merged/'normalized_output.json'),'--eval_results_path',str(evaluation/'eval_results.json'),'--eval_values_path',str(evaluation/'eval_values.json')]
    runpy.run_path(str(REPO/'tdm_eval.py'),run_name='__main__')
    results=read(evaluation/'eval_results.json');values=read(evaluation/'eval_values.json')
    aggregate={k+' IIM':metric(v['Precision'],v['Recall']) for k,v in results['Individual'].items()}
    aggregate['TDM Exact Match']=metric(results['Exact Match Precision wo Results'],results['Exact Match Recall wo Results']);aggregate['TDMR Exact Match']=metric(results['Exact Match Precision'],results['Exact Match Recall'])
    per_paper={};diagnostics={}
    for ident in normalized:
        m={k+' IIM':metric(v['Precision'][ident],v['Recall'][ident]) for k,v in values['Individual'].items()}
        m['TDM Exact Match']=metric(values['Exact Match Recall wo Precision'][ident],values['Exact Match Recall wo Results'][ident]);m['TDMR Exact Match']=metric(values['Exact Match Precision'][ident],values['Exact Match Recall'][ident]);per_paper[ident]=m
        pred=normalized[ident]['normalized_output'];g=gold[ident]['TDMs'];raw=json.loads(output[ident]['output']);pn={number(r['Result']) for r in pred};gn={number(r['Result']) for r in g};common=(pn&gn)-{None}
        strict_result=metric(len(common)/len(pn) if pn else 0,len(common)/len(gn) if gn else 0)
        mismatch=[{'prediction_index':i+1,'gold_index':j+1,'prediction':p['Result'],'gold':gg['Result']} for i,p in enumerate(pred) for j,gg in enumerate(g) if ((str(gg['Result']) in p['Result']) or (p['Result'] in str(gg['Result'])))!=strict(p['Result'],gg['Result'])]
        goldrows=[]
        for j,gg in enumerate(g):
            exact=[i+1 for i,p in enumerate(pred) if fields(p,gg) and strict(p['Result'],gg['Result'])]
            numeric=[i+1 for i,p in enumerate(pred) if strict(p['Result'],gg['Result'])]
            raw_numeric=[i+1 for i,p in enumerate(raw) if strict(p['Result'],gg['Result'])]
            category='correct' if exact else ('numeric_result_missing_or_changed' if not numeric else 'normalization_null' if any(any(pred[i-1][k] is None for k in ('Task','Dataset','Metric')) for i in numeric) else 'numeric_match_but_binding_or_label_mismatch')
            goldrows.append({'gold_index':j+1,'gold':gg,'strict_tdmr_prediction_indices':exact,'strict_numeric_prediction_indices':numeric,'raw_numeric_prediction_indices':raw_numeric,'category':category})
        diagnostics[ident]={'strict_result_iim':strict_result,'substring_vs_strict_discrepancies':mismatch,'gold_rows':goldrows,'extra_prediction_values':[{'index':i+1,'raw':raw[i],'normalized':p} for i,p in enumerate(pred) if not any(strict(p['Result'],gg['Result']) for gg in g)],'category_counts':dict(Counter(r['category'] for r in goldrows))}
    metrics={'scope':coverage,'aggregation':'Official macro-average per-paper Precision and Recall. Additional F1 = harmonic mean of these aggregate P/R; not arithmetic mean of per-paper F1.','aggregate':aggregate,'per_paper':per_paper,'mean_per_paper_f1_SEPARATE':{name:sum(p[name]['F1'] for p in per_paper.values())/len(per_paper) for name in aggregate}}
    save(evaluation/'metrics_with_f1.json',metrics)
    save(evaluation/'per_paper_metrics.json',{'scope':coverage,'papers':{row['id']:{'status':'EVALUATED' if row['id'] in per_paper else 'NOT_EVALUATED','gold_count':row['gold_count'],'metrics':per_paper.get(row['id']),'reason':None if row['id'] in per_paper else errors.get(row['id'])} for row in manifest['papers']}})
    save(evaluation/'error_analysis.json',diagnostics)
    accounting={'new_experiment':new_totals,'historical_completed_outputs':historical_completed,'historical_failed_attempts':prior_failed,'reused_historical':historical,'cumulative_selected':{k:new_totals[k]+historical[k] for k in new_totals},'new_stage_seconds_sum':round(process_seconds,3),'new_model_request_seconds_sum':round(api_seconds,3),'wall_seconds_since_selection':round(time.time()-env['started_epoch'],3),'billing_cost':'UNVERIFIED; provider bill unavailable','offline_mock_tests_excluded':True}
    save(SUB/'api_usage_summary.json',accounting);save(SUB/'stage_summary.json',summaries);save(SUB/'manifest.json',manifest)
    save(SUB/'output_index.json',{r['paper']:{k:r[k] for k in ('pdf_path','preprocess_dir','extraction_dir','normalization_dir','evaluated')} for r in summaries})
    git=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'status','--porcelain'],cwd=REPO,text=True,capture_output=True,check=True);assert not git.stdout.strip(),git.stdout
    for p,h in read(SUB/'preserved_existing_sha256.json').items():assert sha(Path(p))==h
    for p,h in env['source_sha256'].items():assert sha(Path(p))==h
    save(SUB/'verification.json',{'previous_baseline_all_files_unchanged':True,'official_sources_prompts_requirements_unchanged':True,'git_clean':True,'official_evaluation_executed':True,'coverage':coverage,'normalized_values_not_corrected':True})
    lines=[f'# SCILEAD {len(manifest["papers"])} 篇 Baseline 实验报告','','## 完成覆盖率', '',f'选定 {coverage["selected_papers"]} 篇，完整完成并进入官方评测 {coverage["completed_papers"]} 篇；Gold 总计 {coverage["selected_gold_tdmrs"]} 条，实际评测覆盖 {coverage["evaluated_gold_tdmrs"]} 条。未完成项不会被视为完整选定子集结果。','', '## 逐篇阶段结果','','| 论文 | Gold | 页数 | 文本块 | Table 区域 | 证据 | 抽取条数 | 标准化调用 | 集合内 / 集合外回答 | 状态 |','|---|---:|---:|---:|---:|---:|---:|---:|---|---|']
    for s in summaries:lines.append(f'| {s["paper"]} | {s["gold_count"]} | {s["pdf_pages"]} | {s["text_chunks"]} | {s["table_regions"]} | {s["evidence_count"]} | {s["extracted_records"]} | {s["normalization_calls"]} | {s["llm_in_set_answers"]} / {s["llm_out_of_set_answers"]} | {"复用" if s["reused"] else s["normalization_status"]} |')
    lines+=['','集合内回答只说明输出属于候选名称，不等于语义映射必然正确。Table 数量是检测区域，不能当作正确表格数。','',f'## 官方聚合指标（覆盖 {len(normalized)}/{len(manifest["papers"])} 篇）','','| 指标 | Precision | Recall | 额外 F1 |','|---|---:|---:|---:|']
    for k,v in aggregate.items():lines.append(f'| {k} | {v["Precision"]:.6f} | {v["Recall"]:.6f} | {v["F1"]:.6f} |')
    lines+=['','P/R 由未修改的官方脚本对已完成论文逐篇计算后取算术平均；此处 F1 由聚合 P/R 计算，**不是逐篇 F1 的平均**。后者单独保存在 metrics_with_f1.json。','', '## 逐篇 F1','','| 论文 | Result IIM | TDM | TDMR |','|---|---:|---:|---:|']
    for p,m in per_paper.items():lines.append(f'| {p} | {m["Result IIM"]["F1"]:.6f} | {m["TDM Exact Match"]["F1"]:.6f} | {m["TDMR Exact Match"]["F1"]:.6f} |')
    lines+=['','所有逐篇六类指标 P/R/F1 见 evaluation/metrics_with_f1.json；逐条 Gold 数值、字段匹配和额外预测见 evaluation/error_analysis.json。','', '## 未完成论文', '',json.dumps(errors,ensure_ascii=False,indent=2),'','## 用量与耗时','','```json',json.dumps(accounting,ensure_ascii=False,indent=2),'```','','API 次数按实际持久化请求计数；重复名称逐次收费调用，无名称缓存。中断恢复只重放同一位置已成功的历史响应，不产生新请求。未完成/不确定请求不自动重发。','', '## 复现边界', '', '- 旧论文所有文件逐一 SHA256 核对未变，其 Result=1、TDMR=0 的历史结果直接复用。', '- 固定种子 20261013，四个 Gold 数量分层，预先指定年代偏好及公开 PDF 获取优先级。所有候选顺序在下载前保存，无基于模型表现的换样。', '- 保留原始 hi_res、表格推理、2000/200 分块、MPNet、Chroma 默认检索、原始 Query 和两个 Prompt。', '- Extraction 固定 1024 输出 Tokens、temperature=0、seed=0；Normalization 15 Tokens、全 43 篇名称集合、原始逐字段循环。', '- 无手工改值、无规则标准化、无扩大输出窗口、无失败请求自动重试。模型响应中的快照名已保存；中转站后端身份和种子确定性未独立验证。', '- 官方 Result 包含匹配与额外 Decimal 严格相等检查分开保留；不得用数值命中代替完整 TDMR 正确率。']
    lines=[line.replace('旧论文所有文件逐一 SHA256 核对未变，其 Result=1、TDMR=0 的历史结果直接复用。','所有复用论文的历史文件逐一 SHA256 核对未变，预测、标准化、评价及用量直接复用。').replace('预先指定年代偏好及公开 PDF 获取优先级','层内洗牌、层间轮转，预先固定候选顺序') for line in lines]
    (SUB/'report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'coverage':coverage,'aggregate':aggregate,'per_paper':per_paper,'api':accounting},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
