"""P4 only: deterministic offline request planning, never constructs an API client."""
import os, sys, json, hashlib, csv, math, statistics, ast, traceback
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
sys.dont_write_bytecode=True
ROOT=Path(r'D:\C++\SCILEAD'); OUT=Path(__file__).resolve().parent
P3=OUT.parent/'20261022_stage3_resume'; FORMAL=OUT.parent/'20261022_formal'
REPO=ROOT/'emnlp2024-leaderboard-generation'; BASELINE=ROOT/'pilot/full43_uncapped'
assert os.environ.get('PYTHONHASHSEED')=='0'
os.environ.update(TIKTOKEN_CACHE_DIR=str(ROOT/'assets/tiktoken'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING='false',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false')
blocked=[]
def guard(event,args):
    if event in ('socket.connect','socket.getaddrinfo','socket.bind'):
        blocked.append({'event':event,'address':str(args[1]) if len(args)>1 else None,'stack':[{'file':Path(s.filename).name,'function':s.name,'line':s.lineno} for s in traceback.extract_stack(limit=9)]}); raise RuntimeError('P4 is strictly offline')
    if event=='open' and isinstance(args[0],(str,bytes)):
        name=Path(os.fsdecode(args[0])).name.lower()
        if name.endswith('.env') or name.startswith('.env') or name in ('id_rsa','id_ed25519'):
            raise RuntimeError('P4 cannot read credentials')
sys.addaudithook(guard)
import tiktoken
sys.path.insert(0,str(REPO))
from prompting import NormalizationPrompt
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def table(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def percentile(xs,q):
    v=sorted(xs);return v[max(0,math.ceil(q*len(v))-1)] if v else None
baseline=read(BASELINE/'manifest.json'); goldpath=Path(baseline['gold_path']); gold=read(goldpath)
assert sha(goldpath)==baseline['gold_sha256']
assert len(gold)==43 and sum(len(p['TDMs']) for p in gold.values())==295
labels={k:set() for k in ('Task','Dataset','Metric')}
for paper in gold.values():
    for row in paper['TDMs']:
        for key in labels: labels[key].add(row[key])
assert {k:len(v) for k,v in labels.items()}=={'Task':23,'Dataset':71,'Metric':26}
candidate={k:str(v) for k,v in labels.items()}
historical_candidate=BASELINE/'papers/wang19f/extraction/normalization/candidate_sets.json'
assert candidate==read(historical_candidate),'Candidate order differs from frozen Fully baseline'
prompts=read(REPO/'prompts.json'); prompt=prompts['normalization-system-prompt']
template=NormalizationPrompt(prompt,'gpt4-turbo-128k').prompt_template
MODEL='gpt-4.1-2025-04-14';ENC=tiktoken.encoding_for_model(MODEL)
def tokens(messages):return 3+sum(3+len(ENC.encode(m['role']))+len(ENC.encode(m['content'])) for m in messages)
settings=read(ROOT/'pilot/experiment_settings.json')
assert settings['model']==MODEL and settings['normalization_max_tokens'] is None
config={'experiment':'AxCell Extraction + GPT-4.1 Fully Normalization','model':MODEL,'base_url':'https://9527.codes/v1','temperature':0,'seed':0,'stream':False,'max_retries':0,'client_output_limit':'OMITTED','omitted_fields':['max_tokens','max_completion_tokens','max_output_tokens','response_format','tools'],'is_few_shot':False,'model_type_compatibility_branch':'gpt4-turbo-128k','python_hash_seed':0,'timeout_seconds':{'connect':20,'read':180,'write':30,'pool':20},'candidate_counts':{k:len(v) for k,v in labels.items()},'official_source_commit':'8bf74b0a830feb7035c6166dce3394dc344ae532','gold_sha256':sha(goldpath),'prompts_file_sha256':sha(REPO/'prompts.json'),'system_prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'candidate_serialization_sha256':digest(candidate),'official_cache':False,'checkpoint_reuse':'same AxCell paper, record index, field, source input hash and complete identical payload only; never reuse other experiments or deduplicate equal field names','response_handling':'exact response string membership; outside set maps to null; no strip/quote removal/manual mapping; non-stop finish or HTTP failure is incomplete and never auto-retried','authorization':'P4_PREPARATION_ONLY_ZERO_PAID_CALLS'}
save('config.json',config);save('candidate_sets.json',candidate)
save('candidate_order.json',{k:list(labels[k]) for k in labels})
save('prompt_snapshot.json',{'key':'normalization-system-prompt','system':prompt,'human_template':'\n\nItem list: {items}\n\nInput: {input}\n\nAnswer: ','sha256':config['system_prompt_sha256']})
p3=read(P3/'extraction_manifest.json');verify=read(P3/'stage3_verification.json')
assert verify['stage3_complete'] and verify['raw_record_count']==65 and verify['completed_papers']==37
known={'1511.08308v5/table_06.csv/6.2':'METRIC_CELL_BINDING_RECALL_AS_F1','1511.08308v5/table_11.csv/2.4':'ENTITY_COUNT_AS_SCORE','1603.01354v5/table_06.csv/3.1':'EMBEDDING_DIMENSION_AS_SCORE'}
output={};records=[];plans=[];checks=[];perpaper=[];input_files={};statusby={r['paper_id']:r for r in p3['rows']}
for row in p3['rows']:
    pid=row['paper_id'];assert pid in gold
    if row['status']=='FAILED':continue
    assert row['status'] in ('EXTRACTION_COMPLETE','VALID_EMPTY')
    folder=Path(row['local_output_directory']);rp=folder/'raw_outputs/records.json';pp=folder/'raw_outputs/provenance.json';op=folder/'scilead_compatible_outputs/output.json'
    for p in (rp,pp,op):
        relative=p.relative_to(folder).as_posix()
        assert sha(p)==row['output_hashes'][relative]
        input_files[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)}
    raw=read(rp);prov=read(pp);mapped=read(op)
    assert list(mapped)==[pid] and len(raw)==row['record_count']
    tdms=json.loads(mapped[pid]['output']);assert len(tdms)==len(raw)==len(prov)
    assert row['status']!='VALID_EMPTY' or not raw
    output[pid]=mapped[pid];start=len(plans)
    for idx,(r,t) in enumerate(zip(raw,tdms)):
        expected={'Task':r['task'],'Dataset':r['dataset'],'Metric':r['metric'],'Result':str(r['score'])}
        assert t==expected and all(isinstance(v,str) for v in t.values())
        cell=next(p['cell_ext_id'] for p in prov if p['output_index']==idx)
        paperdir,filename,coordinates=cell.split('/');tablepath=FORMAL/'stage2/parsed/papers'/paperdir/filename
        if pid=='1511.08308.pdf':
            assert paperdir=='1511.08308v5'
            tablepath=OUT.parent/'20261022_single_paper/parsed_paper'/filename
        assert tablepath.is_file(),str(tablepath)
        with tablepath.open(encoding='utf-8',newline='') as f: tab=list(csv.reader(f))
        ri,ci=map(int,coordinates.split('.'));assert ri<len(tab) and ci<len(tab[ri])
        trace={'paper_id':pid,'record_index':idx,'record_id':f'{pid}#{idx+1:03d}','raw_prediction':r,'tdmr':t,'cell_ext_id':cell,'source_table':str(tablepath),'source_table_sha256':sha(tablepath),'raw_source_cell':tab[ri][ci],'known_error':known.get(cell),'prediction_sha256':digest(r),'raw_file_sha256':sha(rp),'result_policy':'P3 string preserved; no scaling, units conversion, rounding or semantic repair'}
        records.append(trace)
        for field,value in t.items():
            if field=='Result':
                checks.append({'record_id':trace['record_id'],'field':field,'value':value,'decision':'PRESERVE_RESULT','request_id':None});continue
            exact=value in labels[field]
            check={'record_id':trace['record_id'],'field':field,'value':value,'decision':'EXACT_SKIP' if exact else 'NEEDS_LLM','request_id':None}
            if not exact:
                messages=[{'role':{'system':'system','human':'user'}[m.type],'content':m.content} for m in template.invoke({'items':candidate[field],'input':value}).to_messages()]
                payload={'model':MODEL,'messages':messages,'temperature':0,'seed':0,'stream':False,'n':1}
                assert set(payload)=={'model','messages','temperature','seed','stream','n'}
                identity={'experiment':config['experiment'],'paper_id':pid,'record_index':idx,'field':field,'input_record_sha256':digest(t),'raw_file_sha256':sha(rp),'cell_ext_id':cell,'payload':payload,'gold_sha256':config['gold_sha256'],'prompt_sha256':config['system_prompt_sha256']}
                item={'request_id':f'norm-{len(plans)+1:04d}','paper_id':pid,'record_index':idx,'record_id':trace['record_id'],'field':field,'original_value':value,'cell_ext_id':cell,'known_error':known.get(cell),'payload':payload,'payload_sha256':digest(payload),'checkpoint_cache_key':digest(identity),'cache_status':'MISS_NO_VERIFIED_AXCELL_CHECKPOINT','status':'PREPARED_NOT_SENT','estimated_prompt_tokens':tokens(messages)}
                plans.append(item);check['request_id']=item['request_id']
            checks.append(check)
    perpaper.append({'paper_id':pid,'extraction_status':row['status'],'records':len(raw),'gold_count':len(gold[pid]['TDMs']),'planned_requests':len(plans)-start,'exact_fields_skipped':3*len(raw)-(len(plans)-start),'author36_membership':'UNVERIFIED'})
assert len(output)==37 and len(records)==65 and sum(not json.loads(v['output']) for v in output.values())==9
assert sum(bool(r['known_error']) for r in records)==3
assert len({p['checkpoint_cache_key'] for p in plans})==len(plans)
save('normalization_input.json',output);save('record_provenance.json',records);save('field_checks.json',checks);table('per_paper_request_counts.csv',perpaper)
save('input_hashes.json',input_files)
# Look only in AxCell experiment/checkpoint locations, never credentials or model caches.
cache_roots=[ROOT/'pilot/axcell_aliyun',ROOT/'pilot/axcell_local',Path(r'E:\SCILEAD\axcell\runs'),Path(r'E:\SCILEAD\axcell\reports')]
cache_candidates=[]
for root in cache_roots:
    for p in root.rglob('*.json'):
        if p.is_relative_to(OUT) or p.name not in ('normalized_output.json','normalization_api_usage.json','normalization_usage.json','normalization_manifest.json'):continue
        cache_candidates.append({'path':str(p),'sha256':sha(p)})
assert not cache_candidates,'Existing AxCell normalization assets require review before assigning cache misses'
save('cache_audit.json',{'roots':[str(p) for p in cache_roots],'matching_existing_axcell_normalization_assets':cache_candidates,'verified_checkpoint_hits':0,'actual_api_calls':0,'cross_experiment_field_cache_used':False,'same_value_requests_not_deduplicated':True,'history_policy':'Historical GPT/Llama predictions or same-name mappings are not AxCell per-occurrence checkpoints.'})
# Historical Fully no-limit successful requests: statistics only, never answers substituted.
history=[];history_files={}
for paper in baseline['papers']:
    norm=Path(paper['normalization_dir'])
    for statepath in sorted((norm/'api_calls').glob('*/state.json')):
        reqpath=statepath.with_name('request.json');responsepath=statepath.with_name('response.json')
        if not reqpath.is_file() or not responsepath.is_file():continue
        s=read(statepath);req=read(reqpath);response=read(responsepath)
        if s.get('status')!='COMPLETE' or s.get('http_status')!=200 or s.get('finish_reason')!='stop':continue
        if req.get('model')!=MODEL or response.get('model')!=MODEL or any(k in req for k in ('max_tokens','max_completion_tokens','max_output_tokens')):continue
        field=s['expected'].get('field')
        if field not in labels:continue
        if req['messages'][0]['content']!=prompt:continue
        if not req['messages'][1]['content'].startswith('\n\nItem list: '+candidate[field]+'\n\nInput: '):continue
        usage=response.get('usage') or s.get('usage') or {}
        if not isinstance(usage.get('completion_tokens'),int) or not isinstance(s.get('seconds'),(int,float)):continue
        history.append({'field':field,'prompt_tokens':usage['prompt_tokens'],'estimated_prompt_tokens':tokens(req['messages']),'completion_tokens':usage['completion_tokens'],'seconds':s['seconds'],'state_path':str(statepath),'request_sha256':sha(reqpath),'response_sha256':sha(responsepath)})
        for p in (statepath,reqpath,responsepath):history_files[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)}
assert history,'No verified historical sample for estimate'
histstats={}
for field in labels:
    sample=[h for h in history if h['field']==field]
    if sample:histstats[field]={'n':len(sample),'mean_output_tokens':statistics.mean(h['completion_tokens'] for h in sample),'p95_output_tokens':percentile([h['completion_tokens'] for h in sample],.95),'mean_seconds':statistics.mean(h['seconds'] for h in sample),'p50_seconds':statistics.median(h['seconds'] for h in sample),'p95_seconds':percentile([h['seconds'] for h in sample],.95)}
save('historical_usage_reference.json',{'source':'Frozen fully zero-shot no-client-output-limit results; unique manifest paths','samples':history,'by_field':histstats,'reference_only_not_cached_answers':True});save('historical_files_read_sha256.json',history_files)
counts=Counter(p['field'] for p in plans);expected_out=math.ceil(sum(histstats[k]['mean_output_tokens']*n for k,n in counts.items()));p95_out=math.ceil(sum(histstats[k]['p95_output_tokens']*n for k,n in counts.items()));budget_out=128*len(plans)
prompt_tokens=sum(p['estimated_prompt_tokens'] for p in plans)
scenarios={}
for name,ot in [('historical_mean',expected_out),('historical_per_field_p95',p95_out),('planning_128_tokens_each_NOT_A_CAP',budget_out)]:scenarios[name]={'input_tokens':prompt_tokens,'output_tokens':ot,'total_tokens':prompt_tokens+ot,'openai_reference_usd':round((2*prompt_tokens+8*ot)/1e6,6)}
duration={measure:sum(histstats[k][measure]*n for k,n in counts.items()) for measure in ('mean_seconds','p50_seconds','p95_seconds')}
dups=Counter(p['payload_sha256'] for p in plans)
summary={'created_utc':datetime.now(timezone.utc).isoformat(),'stage':'P4_AWAITING_APPROVAL','model':MODEL,'processed_papers':37,'nonempty_papers':28,'valid_empty_papers':9,'upstream_parse_failed_papers':2,'raw_records':65,'planned_requests':len(plans),'requests_by_field':dict(counts),'exact_match_fields_skipped':195-len(plans),'verified_cache_hits':0,'new_requests_on_approval':len(plans),'actual_api_requests':0,'unique_payloads':len(dups),'repeated_occurrences_not_deduplicated':len(plans)-len(dups),'estimated_prompt_tokens':prompt_tokens,'max_single_prompt_tokens':max(p['estimated_prompt_tokens'] for p in plans),'encoding':ENC.name,'token_estimate_formula':'3 reply overhead + sum(3 message overhead + tokens(role) + tokens(content)); same as frozen scilead_api.py, actual provider usage may differ','historical_reference_calls':len(history),'cost_scenarios':scenarios,'serial_time_estimate_seconds':duration,'pricing':{'checked_utc':datetime.now(timezone.utc).isoformat(),'source':'https://developers.openai.com/api/docs/models/gpt-4.1','input_usd_per_million':2,'output_usd_per_million':8,'cached_input_discount_assumed':False,'provider':'https://9527.codes','provider_price':'UNVERIFIED','actual_provider_cost':None,'caveat':'OpenAI public reference only, not a provider quote; no fixed cost ceiling because no output token cap is transmitted'},'scope':{'author36':'UNVERIFIED','completed37_gold':sum(len(gold[p]['TDMs']) for p in output),'available_tex39_gold':sum(len(gold[p]['TDMs']) for p in statusby),'complete_scilead43_gold':295},'ready_for_paid_execution':False,'technical_request_preparation_ready':True,'blockers':['P4 explicit paid-call approval required','37-paper independent scope vs unknown author36 requires acceptance','Provider price/billing not independently verified']}
save('normalization_request_manifest.json',{'summary':summary,'config':config,'request_ids':[p['request_id'] for p in plans],'requests':[{k:v for k,v in p.items() if k!='payload'} for p in plans],'per_paper':perpaper,'payload_file':'normalization_request_preview.json','payload_file_policy':'contains every exact planned request, not illustrative snippets only'})
save('normalization_request_preview.json',{'actual_api_requests':0,'requests':plans})
save('estimation.json',summary)
with (FORMAL/'input_manifest.csv').open(encoding='utf-8-sig',newline='') as f: scope_inputs={r['paper_id']:r for r in csv.DictReader(f)}
scope=[]
for pid,g in gold.items():
    row=statusby.get(pid);old=scope_inputs[pid]
    status=row['status'] if row else 'TEX_UNAVAILABLE'
    scope.append({'paper_id':pid,'has_gold':True,'gold_count':len(g['TDMs']),'id_match':'EXACT','tex_version':old['tex_version'],'tex_path':old['tex_path'],'tex_sha256':old['sha256'],'status':status,'raw_records':row.get('record_count') if row else None,'author36_membership':'UNVERIFIED','author36_confirmed_complete':False,'normalization_candidate':status=='EXTRACTION_COMPLETE','evaluation_scope':'PROPOSED_LOCAL_COMPLETED_37' if status in ('EXTRACTION_COMPLETE','VALID_EMPTY') else 'EXCLUDED_FAILURE_OR_MISSING_INPUT_RETAINED_IN_COVERAGE','notes':'Original author36 membership and TeX version unknown; no performance-based selection'})
table('paper_scope_comparison.csv',scope)
save('scope_summary.json',{'all_scilead_papers':43,'confirmed_author36_and_completed':0,'completed_author36_unverified':37,'gold_missing_or_unmatched_ids':0,'parse_failed':[r['paper_id'] for r in scope if r['status']=='FAILED'],'tex_unavailable':[r['paper_id'] for r in scope if r['status']=='TEX_UNAVAILABLE'],'scope_decision':'37 completed papers including 9 VALID_EMPTY proposed; keep39 input/43 dataset coverage separate; author36 strict reproduction NOT established'})
protected=read(OUT/'protected_files_before.json');changed=[p for p,v in protected.items() if not Path(p).is_file() or Path(p).stat().st_size!=v['bytes'] or sha(Path(p))!=v['sha256']]
save('offline_guard_diagnostic.json',{'changed':changed,'blocked_network_events':blocked})
assert not changed,repr(changed)
assert all(v['event']=='socket.bind' and v['address'] in ("('127.0.0.1', 0)","('::1', 0)") for v in blocked),repr(blocked)
save('preparation_verification.json',{'stage':'P4_AWAITING_APPROVAL','protected_file_count':len(protected),'protected_files_unchanged':not changed,'changed':changed,'p3_raw_hash_checks':True,'official_candidate_set_and_order_match_frozen_fully':True,'source_provenance_valid_for_all_65':True,'known_error_records_preserved':3,'result_strings_unchanged':True,'no_max_output_parameters':all(not any(k in p['payload'] for k in config['omitted_fields']) for p in plans),'actual_api_calls':0,'api_client_created':False,'credentials_read':False,'network_attempts':blocked,'normalization_executed':False,'evaluation_executed':False,'cache_hits':0,'new_requests':len(plans),'requests_sha256':sha(OUT/'normalization_request_preview.json'),'input_sha256':sha(OUT/'normalization_input.json')})
print(json.dumps(summary,ensure_ascii=True))
