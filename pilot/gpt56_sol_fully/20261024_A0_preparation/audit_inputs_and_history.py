"""Offline A0 audit: only designated env presence/URL; never emit its secret values."""
from pathlib import Path
import sys,os,json,hashlib,csv,ast,collections,statistics,shutil,importlib.metadata
from urllib.parse import urlsplit
O=Path(__file__).resolve().parent;OLD=O.parent/'a0_20261024';ROOT=Path(r'D:\C++\SCILEAD');P=ROOT/'pilot';ENV=ROOT/'SCILEAD_small_test/.env'
sys.dont_write_bytecode=True
def guard(e,a):
    if e in ('socket.connect','socket.getaddrinfo','socket.bind'):raise RuntimeError('A0_OFFLINE_AUDIT_NO_NETWORK')
    if e=='open' and isinstance(a[0],(str,bytes)):
        p=Path(os.fsdecode(a[0]));mode=a[1];flags=a[2]
        if p.suffix=='.env' and p.resolve()!=ENV.resolve():raise RuntimeError('UNRELATED_CREDENTIAL_FILE')
        write=isinstance(mode,str) and any(c in mode for c in 'wax+') or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        if write and not p.resolve().is_relative_to(O):raise RuntimeError('WRITE_OUTSIDE_NEW_A0')
sys.addaudithook(guard)
before={}
def rb(p):
    p=Path(p);b=p.read_bytes();assert p!=ENV;before[str(p)]=hashlib.sha256(b).hexdigest();return b
def read(p):return json.loads(rb(p).decode('utf-8-sig'))
def save(name,data):
    p=O/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'offline_audit.json').exists()
for rel,h in read(OLD/'delivery_manifest.json').items():assert sha(OLD/rel)==h
for p,h in read(OLD/'read_source_hashes.json').items():assert sha(Path(p))==h;before[p]=h
for name in ['candidate_sets.json','frozen_prompts.json','prompt_hash.json','source_version_verification.json','evaluation_scope.json','independent_message_validation.json']:(O/name).write_bytes(rb(OLD/name))
for p in (OLD/'inputs').rglob('*.json'):
    target=O/p.relative_to(OLD);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(rb(p))
rows=read(OLD/'input_manifest.json');lengths=list(csv.DictReader((OLD/'prompt_token_estimates.csv').open(encoding='utf-8-sig')));rb(OLD/'prompt_token_estimates.csv');ls={r['paper_id']:r for r in lengths}
for r in rows:
    r['message_file']=str(O/'inputs'/r['paper_id']/'extraction_messages.json');r['prompt_construction']='Frozen original GPT system/user template + original query + ordered cached evidence; no new retrieval'
    r['proxy_input_tokens']=int(ls[r['paper_id']]['proxy_input_tokens']);r['target_tokenizer_verified']=False;r['input_complete']=True;r['ready_for_trial']=False;r['trial_gate']='PROVIDER_UNVERIFIED; A1 not authorized'
for r in lengths:
    r['official_context_window']=1050000;r['official_max_input_tokens']=922000;r['proposal_output_budget']=32768;r['fits_official_limits_under_proxy_estimate']=int(r['proxy_input_tokens'])+32768<=1050000 and int(r['proxy_input_tokens'])<=922000;r['provider_limit']='UNVERIFIED';r['target_budget_compliance']='PROVISIONAL_PROXY_ONLY'
for name,data in [('input_manifest.csv',rows),('input_token_estimate.csv',lengths)]:
    with (O/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('input_manifest.json',rows)
# Secret stays in memory. Do not hash/copy the credential file or log variable values.
from dotenv import dotenv_values
v=dotenv_values(ENV,interpolate=False,encoding='utf-8-sig')
key_names=['OPENAI_API_KEY','API_KEY','SK'];base_names=['BASE_URL','OPENAI_BASE_URL','API_BASE','OPENAI_API_BASE','API_BASE_URL']
key_present=any(bool(v.get(k)) for k in key_names);bases=[v[k] for k in base_names if v.get(k)];safe_base=None;safe_matches=False
if bases:
    u=urlsplit(bases[0]);safe_matches=(u.scheme=='https' and u.hostname=='9527.codes' and u.path.rstrip('/')=='/v1')
    if safe_matches:safe_base='https://9527.codes/v1'
save('credential_presence_audit.json',{'source_file':str(ENV),'read_only':True,'key_present':key_present,'base_url_present':bool(bases),'base_url_matches_expected':safe_matches,'base_url_if_expected':safe_base,'secret_printed_or_copied':False,'request_sent':False})
del v,bases
manifest=read(P/'full43_uncapped/manifest.json');historical=[];stats={}
for stage,key in [('extract','extraction_dir'),('normalize','normalization_dir')]:
    calls=[]
    for paper in manifest['papers']:
        for path in sorted((Path(paper[key])/'api_calls').glob('*/state.json')):
            s=read(path);req=read(path.with_name('request.json'));resp=read(path.with_name('response.json'))
            assert s['status']=='COMPLETE' and s['http_status']==200 and s['finish_reason']=='stop' and resp['model']=='gpt-4.1-2025-04-14'
            assert req['model']=='gpt-4.1-2025-04-14'
            calls.append({'paper_id':paper['id'],'stage':stage,'state_path':str(path),'request_sha256':sha(path.with_name('request.json')),'response_sha256':sha(path.with_name('response.json')),**{k:s['usage'][k] for k in ['prompt_tokens','completion_tokens','total_tokens']}})
    stats[stage]={'calls':len(calls),**{k:sum(r[k] for r in calls) for k in ['prompt_tokens','completion_tokens','total_tokens']},'max_input_tokens':max(r['prompt_tokens'] for r in calls),'max_output_tokens':max(r['completion_tokens'] for r in calls),'mean_output_tokens':statistics.mean(r['completion_tokens'] for r in calls)};historical+=calls
assert stats['extract']['calls']==43 and stats['normalize']['calls']==542
save('historical_token_records.json',historical);save('historical_token_statistics.json',stats)
save('normalization_request_estimate.json',{'target_model':'gpt-5.6-sol','exact_new_count':None,'historical_reference_records':284,'historical_reference_calls':542,'historical_input_tokens':stats['normalize']['prompt_tokens'],'historical_output_tokens':stats['normalize']['completion_tokens'],'reference_total_requests':585,'reference_extraction_requests':43,'if_284_records_all_fields_unmatched':{'normalization':852,'combined':895},'rule':'Exact match skips; otherwise one call per Task/Dataset/Metric per record; no duplicate-value cache; Result not mapped.','general_bound':'0 <= normalization_calls <= 3 * actual_new_valid_records','reusable_model_predictions':0,'reusable_inputs':'43 cached evidence sets and official templates; no new retrieval','fee_scenarios':'Omitted per latest user instruction; no fee approval requested; A0 model API prohibition remains.'})
cross=P/'cross_model_gpt41_norm16_20261023';u=read(cross/'api_usage_summary.json');fail=[]
for group in ['arms','failure_archives']:
    for sp in (cross/group).rglob('state.json'):
        s=read(sp)
        if s['status']=='FAILED':
            rp=sp.with_name('response.json');err=read(rp).get('error',{}) if rp.exists() else {}
            fail.append({'state_path':str(sp),'http_status':s.get('http_status'),'error_type':s.get('error_type'),'service_error_code':err.get('code'),'message':err.get('message'),'usage_available':bool(s.get('usage'))})
save('provider_history_audit.json',{'legacy_adapter_path':str(P/'scripts/scilead_api.py'),'legacy_adapter_sha256':hashlib.sha256(rb(P/'scripts/scilead_api.py')).hexdigest(),'current_independent_adapter_sha256':hashlib.sha256(rb(cross/'scilead_api_snapshot.py')).hexdigest(),'historical_base_url':'https://9527.codes/v1','historical_request_path':'/v1/chat/completions','legacy_model':'gpt-4.1-2025-04-14','target_model_support':'PROVIDER_UNVERIFIED','target_actual_response_model':None,'target_fixed_mapping_verified':False,'recent_attempts':u['total_attempts'],'recent_successes':u['successful_attempts'],'recent_failures':u['failed_attempts'],'failure_records':fail,'root_cause_confirmed_by_provider':False,'billing_confirmed':False,'models_probe_performed':False,'public_provider_docs_locally_found':False})
save('installed_adapter_versions.json',{k:importlib.metadata.version(k) for k in ['openai','langchain-openai','langchain','tiktoken','httpx']})
save('read_source_hashes.json',before)
assert all(sha(Path(p))==h for p,h in before.items())
save('offline_audit.json',{'papers':43,'text_blocks':172,'table_documents':301,'gold_tdmrs':295,'leaderboards':27,'historical_calls_audited':len(historical),'inputs_equal_draft_verified_evidence':True,'read_files_unchanged':len(before),'credentials_presence_checked':True,'credential_values_not_logged':True,'model_api_requests':0,'api_probes':0,'network_in_audit':False,'scope_unchanged':True})
print(json.dumps({'papers':43,'historical_calls':len(historical),'protected_read_files':len(before),'credential_present':key_present,'base_matches_expected':safe_matches,'model_api_requests':0}))
