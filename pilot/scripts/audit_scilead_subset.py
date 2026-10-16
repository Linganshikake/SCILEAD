"""Offline audit and baseline comparison; never calls a model or parses a PDF."""
import argparse
import ast
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT/'emnlp2024-leaderboard-generation'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def offline():
    sys.dont_write_bytecode=True
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Offline audit')
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(os.fsdecode(args[0]));s=p.as_posix().lower()
            if p.name.startswith('.env') or '/.codex/' in s or '/.claude/' in s:raise RuntimeError('Sensitive config forbidden')
    sys.addaudithook(guard)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True);ap.add_argument('--official-prior',action='store_true');a=ap.parse_args()
    run=a.run_root.resolve();assert run.is_relative_to((ROOT/'pilot').resolve())
    m=read(run/'manifest.json');prior=Path(m['source_run']);pm=read(prior/'manifest.json')
    offline();os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false')
    os.chdir(run/'work')
    if a.official_prior:
        dest=run/'evaluation/prior5_recomputed';dest.mkdir(parents=True,exist_ok=True)
        current=read(run/'merged/normalized_output.json')
        selected={r['id']:current[r['id']] for r in pm['papers']}
        save(dest/'normalized_output.json',selected)
        sys.path.insert(0,str(REPO))
        sys.argv=[str(REPO/'tdm_eval.py'),'--gold_data_path',m['gold_path'],'--normalized_tdm_output_path',str(dest/'normalized_output.json'),'--eval_results_path',str(dest/'eval_results.json'),'--eval_values_path',str(dest/'eval_values.json')]
        runpy.run_path(str(REPO/'tdm_eval.py'),run_name='__main__');return
    old_hashes=read(run/'preserved_existing_sha256.json')
    assert all(sha(Path(p))==h for p,h in old_hashes.items()),'Previous baseline file changed'
    env=read(run/'environment.json');assert all(sha(Path(p))==h for p,h in env['source_sha256'].items())
    old_env=read(prior/'environment.json');current_dependencies={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    assert current_dependencies==old_env['dependencies'],'Dependencies changed'
    prior_verification=read(prior/'verification.json')
    for name in ('subset5_preprocess.py','subset5_api.py'):
        assert sha(ROOT/'pilot/scripts'/name)==prior_verification['orchestration_scripts_sha256'][name],'Validated execution adapter changed'
    fixed=read(run/'selection_fixed.json')['papers'];assert [p['id'] for p in fixed]==[p['id'] for p in m['papers']]
    assert sum(r['reused'] for r in m['papers'])==len(pm['papers'])
    gold=read(Path(m['gold_path']));labels={k:{r[k] for v in gold.values() for r in v['TDMs']} for k in ('Task','Dataset','Metric')}
    assert [len(labels[k]) for k in labels]==[23,71,26]
    count=Counter();token=Counter();response_ids=[];requests_by_paper={};truncated=[];failures=[];dupes={};input_tokens={}
    for row in m['papers']:
        if row['reused']:continue
        per=Counter()
        for stage,key in [('extract','extraction_dir'),('normalize','normalization_dir')]:
            folder=Path(row[key]);plan=read(folder/'request_plan.json') if (folder/'request_plan.json').exists() else []
            if stage=='normalize' and (folder/'candidate_sets.json').exists():
                candidates=read(folder/'candidate_sets.json');assert {k:ast.literal_eval(v) for k,v in candidates.items()}==labels
            if stage=='extract' and (folder/'dry_run.json').exists():input_tokens[row['id']]=read(folder/'dry_run.json')['tokens']
            for attempt in sorted(folder.glob('api_calls/*/attempt.json')):
                call=attempt.parent;state=read(call/'state.json');request=read(call/'request.json')
                count['attempts']+=1;per[stage]+=1
                assert read(attempt)['attempt']==1
                assert request['model']=='gpt-4.1-2025-04-14' and request['temperature']==0 and request['seed']==0
                assert request['max_tokens']==(1024 if stage=='extract' else 15)
                assert request['messages']==plan[int(call.name)-1]['messages']==state['expected']['messages']
                if state['status']!='COMPLETE':failures.append({'paper':row['id'],'stage':stage,'call':int(call.name),'state':state['status']})
                else:
                    count['complete']+=1;assert state['attempts']==1 and state['http_status']==200
                    response=read(call/'response.json');assert response['choices'][0]['message']['content']==state['raw_answer']
                    response_ids.append(response['id']);count['returned_model:'+response['model']]+=1
                    count['finish:'+state['finish_reason']]+=1
                    if state['finish_reason']=='length':truncated.append({'paper':row['id'],'stage':stage,'call':int(call.name)})
                token.update({k:state.get('usage',{}).get(k,0) or 0 for k in ('prompt_tokens','completion_tokens','total_tokens')})
            if stage=='extract' and (folder/'validation.json').exists():dupes[row['id']]=read(folder/'validation.json').get('duplicates')
        requests_by_paper[row['id']]=dict(per)
    assert len(response_ids)==len(set(response_ids))
    exception_path=run/'context_limit_exception.json'
    if exception_path.exists():
        approval=read(exception_path);row=next(p for p in m['papers'] if p['id']==approval['paper'])
        blocked=Path(approval['blocked_extraction_dir']);actual=Path(row['extraction_dir'])
        assert approval['approved'] is True and not list(blocked.glob('api_calls/*/attempt.json'))
        assert sha(blocked/'request_plan.json')==approval['blocked_plan_sha256']
        assert read(actual/'request_plan.json')==read(blocked/'request_plan.json')
        assert sha(Path(row['preprocess_dir'])/'processed_docs.pkl')==approval['processed_docs_sha256']
        assert input_tokens[row['id']]==approval['authorized_input_tokens']==54504
        assert requests_by_paper[row['id']].get('extract',0)<=1
    usage=read(run/'api_usage_summary.json');assert usage['new_experiment']['requests']==count['attempts']
    assert all(usage['new_experiment'][k]==token[k] for k in ('prompt_tokens','completion_tokens','total_tokens'))
    prevusage=read(prior/'api_usage_summary.json');history=prevusage.get('cumulative_selected',prevusage.get('cumulative_five_selected'))
    assert usage['reused_historical']==history
    assert all(usage['cumulative_selected'][k]==history[k]+usage['new_experiment'][k] for k in history)
    metrics=read(run/'evaluation/metrics_with_f1.json');previous=read(prior/'evaluation/metrics_with_f1.json')
    assert all(metrics['per_paper'][k]==v for k,v in previous['per_paper'].items())
    for name,v in metrics['aggregate'].items():
        n=len(metrics['per_paper']);p=sum(x[name]['Precision'] for x in metrics['per_paper'].values())/n;r=sum(x[name]['Recall'] for x in metrics['per_paper'].values())/n
        assert v['Precision']==p and v['Recall']==r and abs(v['F1']-(2*p*r/(p+r) if p+r else 0))<1e-12
    proc=subprocess.run([sys.executable,'-X','utf8',__file__,'--run-root',str(run),'--official-prior'],capture_output=True,text=True,encoding='utf-8',env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    (run/'evaluation/prior5-recompute.log').write_text(proc.stdout+proc.stderr,encoding='utf-8');assert proc.returncode==0,'Prior-five evaluation failed'
    for filename in ('eval_results.json','eval_values.json'):
        assert read(run/'evaluation/prior5_recomputed'/filename)==read(prior/'evaluation'/filename),filename
    comparison={'prior_papers':len(pm['papers']),'prior_gold':sum(x['gold_count'] for x in pm['papers']),'current_papers_evaluated':len(metrics['per_paper']),'previous_per_paper_metrics_identical':True,'official_prior_recompute_identical':True,'metrics':{k:{'prior':previous['aggregate'][k],'current':v,'F1_delta':v['F1']-previous['aggregate'][k]['F1']} for k,v in metrics['aggregate'].items()},'interpretation':'Sample composition changed; no causal performance improvement claim.'}
    save(run/'evaluation/comparison_with_subset5.json',comparison)
    verification=read(run/'verification.json');verification.update(preserved_files_checked=len(old_hashes),dependencies_unchanged=True,fixed_selection_unchanged=True,candidate_set_counts={k:len(v) for k,v in labels.items()},request_audit=dict(count),new_tokens=dict(token),requests_by_paper=requests_by_paper,unique_response_ids=True,no_retries=True,truncations=truncated,failed_requests=failures,extraction_duplicate_counts=dupes,extraction_input_tokens=input_tokens,prior5_recomputed_identical=True,cumulative_usage_no_double_count=True,aggregate_recalculation_verified=True,adapter_sha256={p.name:sha(p) for p in (ROOT/'pilot/scripts').glob('*.py') if p.name in ('subset5_preprocess.py','subset5_api.py','subset15_evaluate.py','run_scilead_subset.py','extend_scilead_manifest.py','audit_scilead_subset.py')})
    save(run/'verification.json',verification)
    print(json.dumps({'requests':dict(count),'tokens':dict(token),'coverage':metrics['scope'],'prior5_recomputed_identical':True,'history':history},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
