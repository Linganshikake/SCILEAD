"""Execute only approved P4 requests, through original normalization main."""
import os,sys,json,hashlib,time,argparse,csv,ast
from pathlib import Path
from datetime import datetime,timezone
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;P4=OUT.parent/'20261022_stage4_preparation';ROOT=Path(r'D:\C++\SCILEAD');REPO=ROOT/'emnlp2024-leaderboard-generation'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
def verified_output(folder,copy_path,state):
    source=folder/'normalization/normalized_output.json'
    assert sha(source)==state['normalized_sha256'],'Original checkpoint output hash mismatch'
    original=read(source)
    assert read(copy_path)==original,'Delivery copy differs from verified official output'
    return original
def preflight():
    v=read(P4/'preparation_verification.json');assert sha(P4/'normalization_request_preview.json')==v['requests_sha256'];assert sha(P4/'normalization_input.json')==v['input_sha256']
    assert len(read(P4/'normalization_request_preview.json')['requests'])==123
    assert read(P4/'verification.json')['status']=='P4_PREPARED_AWAITING_EXPLICIT_APPROVAL'
    before=read(P4/'protected_files_before.json');before.update({str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in P4.rglob('*') if p.is_file()})
    for p,v in before.items():assert Path(p).stat().st_size==v['bytes'] and sha(Path(p))==v['sha256'],p
    if (OUT/'protected_files_before.json').exists():assert before==read(OUT/'protected_files_before.json')
    else:save(OUT/'protected_files_before.json',before)
    authorization={'user_approval':'同意，可以进入下一阶段','scope':'P5 after frozen P4:123 requests,37 completed papers,65 raw AxCell records;37-paper evaluation with9 VALID_EMPTY,author36unknown','max_new_requests':123,'model':'gpt-4.1-2025-04-14','prompt_or_method_changes':False,'retry_authorized':False,'preview_sha256':sha(P4/'normalization_request_preview.json'),'input_sha256':sha(P4/'normalization_input.json'),'provider_cost_unverified_accepted':True,'prepared_utc':datetime.now(timezone.utc).isoformat()}
    if not (OUT/'authorization.json').exists():save(OUT/'authorization.json',authorization)
    else:assert read(OUT/'authorization.json')['preview_sha256']==authorization['preview_sha256']
    save(OUT/'preflight.json',{'protected_files':len(before),'all_unchanged':True,'planned_requests':123,'actual_calls_before_run':len(list((OUT/'api_calls').glob('*/attempt.json'))),'approved':True})
    return read(P4/'normalization_request_preview.json')['requests'],read(P4/'normalization_input.json')
def summarize():
    states=[read(p) for p in sorted((OUT/'api_calls').glob('*/state.json'))]
    attempts=len(list((OUT/'api_calls').glob('*/attempt.json')));assert attempts<=123
    total={k:sum((s.get('usage') or {}).get(k,0) or 0 for s in states) for k in ('prompt_tokens','completion_tokens','total_tokens')}
    result={'model':'gpt-4.1-2025-04-14','authorized_requests':123,'actual_attempts':attempts,'completed_calls':sum(s['status']=='COMPLETE' for s in states),'failed_calls':sum(s['status']=='FAILED' for s in states),'unreported_usage_attempts':sum(s.get('attempts',0)>0 and not bool(s.get('usage')) for s in states),'automatic_retries':0,'call_seconds_sum':sum(s.get('seconds',0) for s in states),'actual_provider_cost':None,'provider_price':'UNVERIFIED','openai_reference_usd':round((2*total['prompt_tokens']+8*total['completion_tokens'])/1e6,6),'calls':states,**total}
    save(OUT/'normalization_usage.json',result)
    papers=[read(p) for p in sorted((OUT/'papers').glob('*/state.json'))]
    if papers:
        with (OUT/'normalization_status.csv').open('w',encoding='utf-8-sig',newline='') as f:
            keys=['paper_id','status','records','planned_requests','completed_requests','null_fields','seconds','error_type'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(papers)
    return result,papers
def run(plan,inputs):
    assert os.environ.get('PYTHONHASHSEED')=='0'
    os.environ['SCILEAD_RUN_ROOT']=str(OUT);(OUT/'work').mkdir(exist_ok=True)
    sys.path.insert(0,str(ROOT/'pilot/scripts'));import scilead_api as api
    api.setup('normalize') # Reuse designated secret loader; never print/write credential.
    from ledger import FrozenLedger
    import tdm_llm_normalization as official
    goldpath=Path(read(ROOT/'pilot/full43_uncapped/manifest.json')['gold_path'])
    assert sha(goldpath)==read(P4/'config.json')['gold_sha256']
    labels={k:ast.literal_eval(v) for k,v in read(P4/'candidate_sets.json').items()}
    for pid,data in inputs.items():
        folder=OUT/'papers'/pid;folder.mkdir(parents=True,exist_ok=True)
        subset=[p for p in plan if p['paper_id']==pid];records=json.loads(data['output'])
        if (folder/'state.json').exists() and read(folder/'state.json')['status']=='COMPLETE':
            s=read(folder/'state.json');verified_output(folder,OUT/'normalized_outputs'/pid/'normalized_output.json',s);print('SKIP_COMPLETE',pid,flush=True);continue
        save(folder/'output.json',{pid:data})
        save(folder/'config.json',{'model_type':'gpt4-turbo-128k','model':'gpt-4.1-2025-04-14','is_few_shot':False,'temperature':0,'seed':0,'client_output_token_limit':'OMITTED','extraction_provenance':'Immutable AxCell P3'})
        state={'paper_id':pid,'status':'RUNNING','records':len(records),'planned_requests':len(subset),'completed_requests':0,'null_fields':None,'error_type':None};save(folder/'state.json',state)
        ledger=FrozenLedger(OUT/'api_calls',subset,api.KEY,network_switch=lambda value:setattr(api,'NETWORK',value));official.utils.llm_init_langchain=lambda config,max_new_tokens,seed:ledger
        start=time.monotonic()
        try:
            args=argparse.Namespace(seed=0,max_new_tokens=None,gold_tdm_path=str(goldpath),tdm_output_path=folder.as_posix()+'/',prompt_file=str(REPO/'prompts.json'))
            official.main(args);assert ledger.cursor==len(subset)
            normalized=read(folder/'normalization/normalized_output.json');nr=normalized[pid]['normalized_output'];assert len(nr)==len(records)
            assert normalized[pid]['source_documents']==data['source_documents']
            assert [r['Result'] for r in nr]==[r['Result'] for r in records]
            for idx,r in enumerate(nr):
                assert set(r)=={'Task','Dataset','Metric','Result'}
                for k in labels:
                    assert r[k] is None or r[k] in labels[k]
                    if records[idx][k] in labels[k]:assert r[k]==records[idx][k]
            save(OUT/'normalized_outputs'/pid/'normalized_output.json',normalized)
            state.update(status='COMPLETE',null_fields=sum(r[k] is None for r in nr for k in labels),normalized_sha256=sha(folder/'normalization/normalized_output.json'))
        except Exception as exc:
            state.update(status='FAILED',error_type=type(exc).__name__,error=api.scrub(str(exc)))
        finally:
            ledger.close();state['seconds']=round(time.monotonic()-start,3);state['completed_requests']=sum(read(OUT/'api_calls'/q['request_id']/'state.json').get('status')=='COMPLETE' for q in subset if (OUT/'api_calls'/q['request_id']/'state.json').exists());save(folder/'state.json',state);summarize();print(pid,state['status'],state['completed_requests'],'/',len(subset),flush=True)
    usage,papers=summarize();complete=[x for x in papers if x['status']=='COMPLETE']
    merged={}
    for s in complete:merged.update(verified_output(OUT/'papers'/s['paper_id'],OUT/'normalized_outputs'/s['paper_id']/'normalized_output.json',s))
    save(OUT/'normalization_manifest.json',{'papers':papers,'completed_papers':len(complete),'expected_papers':37,'failed_papers':[x['paper_id'] for x in papers if x['status']!='COMPLETE'],'actual_calls':usage['actual_attempts'],'predictions':sum(len(x['normalized_output']) for x in merged.values()),'raw_input_sha256':sha(P4/'normalization_input.json'),'request_manifest_sha256':sha(P4/'normalization_request_preview.json'),'official_main_unmodified':True,'response_null_policy':'Official exact membership; no cleanup'})
    if len(complete)==37:
        assert len(merged)==37 and sum(len(x['normalized_output']) for x in merged.values())==65 and usage['completed_calls']==123
        save(OUT/'merged/normalized_output.json',merged);save(OUT/'merged/output.json',inputs)
    save(OUT/'execution_finished.json',{'finished_utc':datetime.now(timezone.utc).isoformat(),'completed_papers':len(complete),'status':'COMPLETE' if len(complete)==37 else 'PARTIAL','actual_calls':usage['actual_attempts']})
    return 0 if len(complete)==37 else 2
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute-approved',action='store_true');args=parser.parse_args()
    plan,inputs=preflight()
    if not args.execute_approved:print('PREFLIGHT PASS; no model requests');sys.exit(0)
    lock=OUT/'execution.lock'
    with lock.open('x',encoding='utf-8') as f:json.dump({'pid':os.getpid(),'created_utc':datetime.now(timezone.utc).isoformat()},f)
    if not (OUT/'execution_started.json').exists():save(OUT/'execution_started.json',{'started_utc':datetime.now(timezone.utc).isoformat(),'started_epoch':time.time()})
    try:code=run(plan,inputs)
    finally:lock.unlink()
    sys.exit(code)
