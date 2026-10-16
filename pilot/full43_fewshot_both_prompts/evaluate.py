from common import *
import argparse,collections,shutil
from scoring import score

def main():
    setup();verify();m=read(RUN/'input_manifest.json');raw=read(RUN/'input/output.json');gold=read(m['gold_path'])
    assert sha(RUN/'input/output.json')==m['frozen_raw_sha256']
    norm={};failed=[];summaries=[];calls=[]
    for row in m['papers']:
        out=Path(row['normalization_dir']);summary=read(out/'summary.json') if (out/'summary.json').exists() else {'status':'NOT_EXECUTED'}
        summaries.append({'paper':row['id'],'gold_count':row['gold_count'],**summary})
        if summary['status']=='COMPLETE':
            value=read(out/'normalized_output.json');p=row['id'];assert list(value)==[p]
            assert value[p]['source_documents']==raw[p]['source_documents']
            assert [x['Result'] for x in value[p]['normalized_output']]==[x['Result'] for x in json.loads(raw[p]['output'])]
            norm.update(value)
        else:failed.append({'paper':row['id'],**summary})
        for f in sorted(Path(row['calls_dir']).glob('*/attempt.json')):
            s=read(f.parent/'state.json');calls.append({'paper':row['id'],'path':str(f.parent),**s})
    usage={'extraction_requests':0,'normalization_attempts':len(calls),'successful_responses':sum(s['status']=='COMPLETE' for s in calls),'failed_or_uncertain':sum(s['status']!='COMPLETE' for s in calls),'unknown_usage_attempts':sum(not s.get('usage') for s in calls),'automatic_retries':0,'request_seconds':sum(s.get('seconds',0) for s in calls),'wall_seconds':read(RUN/'execution_finished.json')['epoch']-read(RUN/'execution_started.json')['epoch'] if (RUN/'execution_finished.json').exists() else None,'billing_cost':'UNVERIFIED; use returned tokens, not LangChain dollar cost','history_extraction_reused_not_billed_again':read(PREVIOUS/'api_usage_summary.json')['stages']['extract'],'calls':calls}
    for k in ('prompt_tokens','completion_tokens','total_tokens'):usage[k]=sum((s.get('usage') or {}).get(k,0) or 0 for s in calls)
    save(RUN/'api_usage_summary.json',usage)
    save(RUN/'normalization/normalized_output.json',norm);save(RUN/'merged/normalized_output.json',norm);save(RUN/'stage_summary.json',summaries)
    coverage={'completed_papers':len(norm),'selected_papers':43,'records':sum(len(x['normalized_output']) for x in norm.values()),'evaluated_gold':sum(len(gold[p]['TDMs']) for p in norm),'selected_gold':295,'failed':failed}
    save(RUN/'evaluation/coverage.json',coverage)
    assert norm,'No completed normalization'
    import tdm_eval as official
    out=RUN/'evaluation';args=argparse.Namespace(gold_data_path=m['gold_path'],normalized_tdm_output_path=str(RUN/'normalization/normalized_output.json'),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json'))
    save(out/'invocation.json',vars(args));official.main(args)
    agg,per,strict,analysis=score(norm,raw,gold,coverage,out)
    B=read(PREVIOUS/'evaluation/metrics_with_f1.json');A=read(BASE/'evaluation/metrics_with_f1.json')
    # A stores this auxiliary metric separately; adapt storage, not mathematics.
    A=dict(A,strict_result_iim_auxiliary=read(BASE/'evaluation/strict_result_metrics.json')['aggregate'])
    if len(norm)==43:
        assert coverage['records']==293 and coverage['evaluated_gold']==295
        assert agg['Result IIM']==B['aggregate']['Result IIM'] and strict==B['strict_result_iim_auxiliary']
        assert read(out/'eval_values.json')['Individual']['Result']==read(PREVIOUS/'evaluation/eval_values.json')['Individual']['Result']
    bn=read(PREVIOUS/'fewshot_normalized_output.json');an=read(BASE/'merged/normalized_output.json')
    changes=[];counts=collections.Counter();nullcounts={s:collections.Counter() for s in 'ABC'};perchanges=[]
    for setting,values in [('A',an),('B',bn),('C',norm)]:
        for p,x in values.items():
            for row in x['normalized_output']:
                for field in ('Task','Dataset','Metric'):nullcounts[setting][field]+=row[field] is None
    for p,x in norm.items():
        rr=json.loads(raw[p]['output']);assert len(rr)==len(x['normalized_output'])==len(bn[p]['normalized_output'])
        for i,(r,b,c) in enumerate(zip(rr,bn[p]['normalized_output'],x['normalized_output']),1):
            for k in ('Task','Dataset','Metric'):
                if b[k]!=c[k]:
                    category='null_to_label' if b[k] is None else 'label_to_null' if c[k] is None else 'label_to_different_label'
                    counts[category]+=1;changes.append({'paper':p,'record':i,'field':k,'original_name':r[k],'B':b[k],'C':c[k],'category':category,'Result':r['Result']})
        perchanges.append({'paper':p,'A':A['per_paper'][p],'B':B['per_paper'][p],'C':per[p],'C_minus_B_TDMR_F1':per[p]['TDMR Exact Match']['F1']-B['per_paper'][p]['TDMR Exact Match']['F1'],'records':len(rr)})
    comparison={'scope':coverage,'A':{'name':'Zero-shot Extraction + Zero-shot Normalization','source':str(BASE),'aggregate':A['aggregate'],'strict_result':A['strict_result_iim_auxiliary']},'B':{'name':'Few-shot Extraction + Zero-shot Normalization','source':str(PREVIOUS),'aggregate':B['aggregate'],'strict_result':B['strict_result_iim_auxiliary']},'C':{'name':'Few-shot Extraction + Few-shot Normalization','source':str(RUN),'aggregate':agg,'strict_result':strict},'null_fields':{k:dict(v) for k,v in nullcounts.items()},'mapping_change_counts':dict(counts),'mapping_changes':changes,'per_paper':perchanges,'result_and_extraction_identical_B_C':True,'note':'A/B full43 reference; compare to C only if C coverage is43. Table7 prompt-branch comparison should use C. Leaderboard evaluation is supplemental.'}
    save(out/'comparison_of_three_settings.json',comparison)
    lines=['# Gold / Few-shot + Few-shot 逐条对照','辅助严格数值匹配不替代官方字符串包含匹配。所有变化按论文 ID 和原始记录序号关联。','']
    for p,rows in analysis.items():
        lines+=['## '+p,'','| Gold # | Gold TDMR | 原始 / 新标准化预测 | 分类 |','| --- | --- | --- | --- |']
        for x in rows['gold_rows']:lines.append('| '+str(x['gold_index'])+' | '+json.dumps(x['gold'],ensure_ascii=False)+' | '+json.dumps(x['matching_predictions'],ensure_ascii=False).replace('|','\\|')+' | '+x['category']+' |')
    (out/'tdmr_comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    if len(norm)==43:
        lb=RUN/'leaderboard_evaluation';lb.mkdir(exist_ok=True)
        for name in ('run_official_leaderboard_eval.py','evaluate_paper_metrics.py'):
            if not (lb/name).exists():shutil.copyfile(PREVIOUS/'leaderboard'/name,lb/name)
        for d in ('official','paper_metrics','leaderboards','reference'):(lb/d).mkdir(exist_ok=True)
        common=(PREVIOUS/'leaderboard/common.py').read_text(encoding='utf-8').replace("NORMALIZED=BASE/'fewshot_normalized_output.json'","NORMALIZED=BASE/'normalization/normalized_output.json'").replace("BASE/'manifest.json'","BASE/'input_manifest.json'")
        (lb/'common.py').write_text(common,encoding='utf-8')
    print(json.dumps({'coverage':coverage,'aggregate':agg,'strict_result':strict,'usage':{k:v for k,v in usage.items() if k not in ('calls','history_extraction_reused_not_billed_again')},'mapping_changes':dict(counts),'null_fields_C':dict(nullcounts['C'])}),flush=True)

if __name__=='__main__':main()
