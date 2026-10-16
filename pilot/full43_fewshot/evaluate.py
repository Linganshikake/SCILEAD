from common import *
import argparse, collections, decimal, shutil
def metric(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0.0}
def number(x):
    try:
        n=decimal.Decimal(str(x));return n if n.is_finite() else None
    except decimal.InvalidOperation:return None
def numeric(a,b):return number(a) is not None and number(a)==number(b)
def same_tdm(a,b):return all(a[k]==b[k] for k in ('Task','Dataset','Metric'))
def main():
    setup();verify();m=read(RUN/'manifest.json');gold=read(m['gold_path']);raw={};norm={};failed=[];usage={};summaries=[]
    for stage in ('extract','normalize'):
        usage[stage]={'requests':0,'successful_responses':0,'failed_or_uncertain':0,'unknown_usage_attempts':0,'prompt_tokens':0,'completion_tokens':0,'total_tokens':0,'request_seconds':0}
    for row in m['papers']:
        paper=row['id'];ex=Path(row['extraction_dir']);no=Path(row['normalization_dir']);es=read(ex/'summary.json') if (ex/'summary.json').exists() else {};ns=read(no/'summary.json') if (no/'summary.json').exists() else {}
        if (ex/'output.json').exists():raw.update(read(ex/'output.json'))
        if es.get('status')==ns.get('status')=='COMPLETE':
            norm.update(read(no/'normalized_output.json'));assert digest(raw[paper]['source_documents'])==row['source_documents_sha256'];assert norm[paper]['source_documents']==raw[paper]['source_documents'];assert [r['Result'] for r in norm[paper]['normalized_output']]==[r['Result'] for r in json.loads(raw[paper]['output'])]
        else:failed.append({'paper':paper,'extraction':es,'normalization':ns})
        for stage,out,archived in stage_directories(row,m):
            if (out/'api_usage.json').exists():
                u=read(out/'api_usage.json');assert not u['mock']
                for k in usage[stage]:usage[stage][k]+=u['attempts' if k=='requests' else k]
        summary={'paper':paper,'gold':row['gold_count'],'evidence_count':row['evidence_count'],'extraction':es,'normalization':ns};summaries.append(summary);row['status']='COMPLETE' if paper in norm else 'INCOMPLETE'
    save(RUN/'manifest.json',m);save(RUN/'stage_summary.json',summaries);save(RUN/'fewshot_output.json',raw);save(RUN/'fewshot_normalized_output.json',norm);save(RUN/'merged/output.json',raw);save(RUN/'merged/normalized_output.json',norm)
    save(RUN/'normalization_statistics.json',{'completed_papers':len(norm),'planned_requests':read(RUN/'normalization_precheck.json')['expected_requests'],'completed_stage_requests':sum(s['normalization'].get('requests',0) for s in summaries),'exact_fields_skipped':sum(s['normalization'].get('exact_fields_skipped',0) for s in summaries),'llm_answers_in_candidate_set':sum(s['normalization'].get('returned_candidate',0) for s in summaries),'null_fields':sum(s['normalization'].get('null_fields',0) for s in summaries),'result_strings_unchanged':True,'note':'Semantic null is an official mapping outcome, not an HTTP failure.'})
    coverage={'completed_papers':len(norm),'selected_papers':43,'evaluated_gold':sum(len(gold[p]['TDMs']) for p in norm),'selected_gold':295,'failed':failed};save(RUN/'evaluation/coverage.json',coverage)
    recovery=read(RUN/'recovery_results.json') if (RUN/'recovery_results.json').exists() else {'outcomes':[]}
    save(RUN/'api_usage_summary.json',{'stages':usage,'total':{k:sum(v[k] for v in usage.values()) for k in usage['extract']},'wall_seconds_since_api_start':time.time()-read(RUN/'execution_started.json')['epoch'],'wall_time_note':'Includes waiting for explicit retry authorization and offline analysis; request_seconds sums observed HTTP durations.','baseline_selected_usage':read(BASE/'api_usage_summary.json')['current_baseline_selected_requests'],'billing_cost':'UNVERIFIED; only returned token usage reported; mock tests excluded; three original HTTP 502 attempts retain unknown billed usage','automatic_retries':0,'authorized_manual_retries':sum(x['requests']>0 for x in recovery['outcomes']),'authorized_recovery_new_attempts':sum(x['requests'] for x in recovery['outcomes']),'archived_attempt_stages':m.get('archived_attempt_stages',[])})
    assert norm,'No eligible predictions'
    import tdm_eval as official
    out=RUN/'evaluation';args=argparse.Namespace(gold_data_path=m['gold_path'],normalized_tdm_output_path=str(RUN/'fewshot_normalized_output.json'),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json'));save(out/'invocation.json',vars(args));official.main(args)
    res=read(out/'eval_results.json');vals=read(out/'eval_values.json');agg={k+' IIM':metric(v['Precision'],v['Recall']) for k,v in res['Individual'].items()};agg['TDM Exact Match']=metric(res['Exact Match Precision wo Results'],res['Exact Match Recall wo Results']);agg['TDMR Exact Match']=metric(res['Exact Match Precision'],res['Exact Match Recall'])
    per={};analysis={}
    for p in norm:
        pm={k+' IIM':metric(v['Precision'][p],v['Recall'][p]) for k,v in vals['Individual'].items()};pm['TDM Exact Match']=metric(vals['Exact Match Recall wo Precision'][p],vals['Exact Match Recall wo Results'][p]);pm['TDMR Exact Match']=metric(vals['Exact Match Precision'][p],vals['Exact Match Recall'][p]);per[p]=pm
        predictions=norm[p]['normalized_output'];original=json.loads(raw[p]['output']);gg=gold[p]['TDMs'];pn={number(x['Result']) for x in predictions};gn={number(x['Result']) for x in gg};intersection=(pn&gn)-{None};pd=len(pn-{None})+len({x['Result'] for x in predictions if number(x['Result']) is None});gd=len(gn-{None})+len({str(x['Result']) for x in gg if number(x['Result']) is None})
        rows=[]
        for i,g in enumerate(gg,1):
            numeric_idx=[j+1 for j,r in enumerate(predictions) if numeric(r['Result'],g['Result'])];exact=[j+1 for j,r in enumerate(predictions) if numeric(r['Result'],g['Result']) and same_tdm(r,g)]
            cat='correct' if exact else ('numeric_result_missing_or_changed' if not numeric_idx else 'normalization_null' if any(any(predictions[j-1][k] is None for k in ('Task','Dataset','Metric')) for j in numeric_idx) else 'numeric_match_but_binding_or_label_mismatch')
            rows.append({'gold_index':i,'gold':g,'strict_numeric_indices':numeric_idx,'strict_tdmr_indices':exact,'category':cat,'matching_predictions':[{'index':j,'raw':original[j-1],'normalized':predictions[j-1]} for j in numeric_idx]})
        discrepancies=[{'prediction':i+1,'gold':j+1,'predicted_result':a['Result'],'gold_result':b['Result']} for i,a in enumerate(predictions) for j,b in enumerate(gg) if ((str(b['Result']) in a['Result']) or (a['Result'] in str(b['Result'])))!=numeric(a['Result'],b['Result'])]
        analysis[p]={'strict_result_iim':metric(len(intersection)/pd if pd else 0,len(intersection)/gd if gd else 0),'gold_rows':rows,'category_counts':dict(collections.Counter(x['category'] for x in rows)),'substring_vs_strict_discrepancies':discrepancies,'extra_numeric_values':[{'index':i+1,'raw':original[i],'normalized':x} for i,x in enumerate(predictions) if not any(numeric(x['Result'],g['Result']) for g in gg)]}
    for k,v in agg.items():
        for score in ('Precision','Recall'):assert abs(v[score]-sum(x[k][score] for x in per.values())/len(per))<1e-12
    strict=metric(sum(x['strict_result_iim']['Precision'] for x in analysis.values())/len(analysis),sum(x['strict_result_iim']['Recall'] for x in analysis.values())/len(analysis))
    save(out/'metrics_with_f1.json',{'scope':coverage,'aggregate':agg,'per_paper':per,'strict_result_iim_auxiliary':strict,'aggregation':'Official per-paper macro P/R; F1=2PR/(P+R), not mean per-paper F1','official_source_sha256':sha(REPO/'tdm_eval.py')});save(out/'per_paper_metrics.json',per);save(out/'error_analysis.json',analysis)
    old=read(BASE/'evaluation/metrics_with_f1.json');oldraw=read(BASE/'merged/output.json');oldnorm=read(BASE/'merged/normalized_output.json');compare=[]
    cohort=out/'zero_shot_same_cohort';cohort.mkdir(exist_ok=True);save(cohort/'normalized_output.json',{p:oldnorm[p] for p in norm})
    official.main(argparse.Namespace(gold_data_path=m['gold_path'],normalized_tdm_output_path=str(cohort/'normalized_output.json'),eval_results_path=str(cohort/'eval_results.json'),eval_values_path=str(cohort/'eval_values.json')))
    cr=read(cohort/'eval_results.json');ca={k+' IIM':metric(v['Precision'],v['Recall']) for k,v in cr['Individual'].items()};ca['TDM Exact Match']=metric(cr['Exact Match Precision wo Results'],cr['Exact Match Recall wo Results']);ca['TDMR Exact Match']=metric(cr['Exact Match Precision'],cr['Exact Match Recall']);save(cohort/'metrics_with_f1.json',{'aggregate':ca,'papers':list(norm),'scope':'Frozen Zero-shot restricted to exactly the completed Few-shot papers'})
    for p in norm:
        a=json.loads(oldraw[p]['output']);b=json.loads(raw[p]['output']);oldnull=sum(r[k] is None for r in oldnorm[p]['normalized_output'] for k in ('Task','Dataset','Metric'));newnull=sum(r[k] is None for r in norm[p]['normalized_output'] for k in ('Task','Dataset','Metric'))
        compare.append({'paper':p,'old_records':len(a),'new_records':len(b),'old_null_fields':oldnull,'new_null_fields':newnull,'zero_shot':old['per_paper'][p],'few_shot':per[p],'tdmr_f1_delta':per[p]['TDMR Exact Match']['F1']-old['per_paper'][p]['TDMR Exact Match']['F1'],'added_raw_records':[r for r in b if r not in a],'removed_raw_records':[r for r in a if r not in b]})
    save(out/'comparison.json',{'papers':compare,'aggregate_zero':ca,'aggregate_zero_full43_reference':old['aggregate'],'aggregate_few':agg,'comparison_cohort':list(norm),'record_count_zero':284,'record_count_few':sum(validate(v['output'])['records'] or 0 for v in raw.values() if validate(v['output'])['schema_valid']),'invalid_extraction_papers':[p for p,v in raw.items() if not validate(v['output'])['schema_valid']],'warning':'Metrics compare exactly the completed paper cohort; full43 Zero-shot reference is separate if coverage is incomplete. No causal attribution solely to prompting.'})
    lines=['# 逐条 Gold / Few-shot 对照','辅助严格数值匹配不替代官方字符串包含匹配。null 说明标准化输出，不能仅据数值相同证明字段语义绑定正确。','']
    for p,an in analysis.items():
        lines+=['## '+p,'','| Gold # | Gold TDMR | 原始 / 标准化预测（数值对应） | 分类 |','| --- | --- | --- | --- |']
        for x in an['gold_rows']:lines.append('| '+str(x['gold_index'])+' | '+json.dumps(x['gold'],ensure_ascii=False)+' | '+json.dumps(x['matching_predictions'],ensure_ascii=False).replace('|','\\|')+' | '+x['category']+' |')
    (out/'tdmr_comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    # Reuse audited scoreboard wrappers without changing mathematical functions.
    if len(norm)==43:
        lb=RUN/'leaderboard';lb.mkdir(exist_ok=True)
        for name in ('run_official_leaderboard_eval.py','evaluate_paper_metrics.py'):
            shutil.copyfile(RUN.parent/'full43_cs/leaderboard_evaluation'/name,lb/name)
        for d in ('official','paper_metrics','leaderboards','reference'):(lb/d).mkdir(exist_ok=True)
    print(json.dumps({'coverage':coverage,'aggregate':agg,'strict':strict,'usage':usage},ensure_ascii=False))
if __name__=='__main__':main()
