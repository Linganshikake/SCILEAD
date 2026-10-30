"""Read-only experimental verification and usage summary; no API or model imports."""
import collections,csv,hashlib,json,re
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261028'
BRANCHES=['partially','cold_default','cold_0','cold_42']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def audit_attempts(folder,req,exp,branch,stage):
 """Count physical attempts, retaining an authorized ambiguous original attempt."""
 acc=read(folder/'accepted.json');relative=acc.get('response_relative_path','response.json')
 assert relative in ('response.json','retry_1/response.json')
 accepted_path=folder/relative;accepted=read(accepted_path)
 assert sha(accepted_path)==acc['response_sha256']
 assert accepted['model']=='deepseek-flash' and accepted['choices'][0]['finish_reason']=='stop'
 assert isinstance(accepted['choices'][0]['message']['content'],str) and accepted['choices'][0]['message']['content'].strip()
 attempts=[folder]+sorted(p.parent for p in folder.glob('retry_*/state.json'))
 if len(attempts)>1:
  assert (branch,stage,folder.name)==('cold_42','stage2','0182') and len(attempts)==2
  assert relative=='retry_1/response.json'
  auth=read(folder/'manual_recovery_authorization.json')
  assert auth['authorized'] and auth['max_additional_attempts']==1
  assert auth['request_sha256']==sha(folder/'request.json')
  assert auth['original_state_sha256']==sha(folder/'state.json')
  assert auth['helper_sha256']==sha(ROOT/'authorized_resume.py')
 rows=[]
 for attempt in attempts:
  state=read(attempt/'state.json');assert read(attempt/'request.json')==req
  assert state['post_calls']==1 and state['automatic_retries']==0
  response_path=attempt/'response.json';rsp=read(response_path) if response_path.exists() else None
  if rsp is None:
   assert len(attempts)==2 and attempt==folder and state['status']=='UNKNOWN_TRANSPORT_ERROR'
   assert state['error_type']=='RemoteProtocolError' and not state.get('usage')
  else:
   assert state['http_status']==200 and rsp['model']=='deepseek-flash'
   assert rsp['choices'][0]['finish_reason']=='stop'
   assert isinstance(rsp['choices'][0]['message']['content'],str)
   assert state['usage']==rsp['usage']
  assert not re.search(r'\bsk-[A-Za-z0-9_-]{24,}|Bearer\s+[A-Za-z0-9_-]{24,}',(attempt/'request.json').read_text()+(response_path.read_text() if rsp else ''))
  u=state.get('usage') or {};choice=rsp['choices'][0] if rsp else {}
  rows.append({'branch':branch,'stage':stage,'call':int(folder.name),'attempt':'original' if attempt==folder else attempt.name,
   'paper_id':exp['paper'],'record':exp['record'],'field':exp['field'],'status':state['status'],'error_type':state.get('error_type'),
   'request_model':req['model'],'response_model':rsp.get('model') if rsp else None,'finish_reason':choice.get('finish_reason'),
   'http_status':state.get('http_status'),'usage_known':bool(u),
   'prompt_tokens':u.get('prompt_tokens',0),'completion_tokens':u.get('completion_tokens',0),'total_tokens':u.get('total_tokens',0),
   'reasoning_tokens':(u.get('completion_tokens_details') or {}).get('reasoning_tokens',0),'seconds':state['elapsed_seconds'],
   'started_utc':state['started_utc'],'response_id':rsp.get('id') if rsp else None,'system_fingerprint':rsp.get('system_fingerprint') if rsp else None,
   'system_prompt_sha256':hashlib.sha256(req['messages'][0]['content'].encode()).hexdigest(),'request_sha256':sha(attempt/'request.json'),
   'response_sha256':sha(response_path) if rsp else None,'path':str(attempt)})
 return rows
def main():
 protected=read(ROOT/'protected_hashes.json');changed=[p for p,h in protected.items() if not Path(p).is_file() or sha(p)!=h]
 raw=read(ROOT/'variants/inputs/output.json');assert raw==read(BASE/'fully/merged/output.json')
 prompt=read(ROOT/'prompts_semantic_v1.json');oldprompt=read(ROOT/'prompts_original.json');add=read(ROOT/'prompt_additions.json')
 assert {k for k in prompt if prompt[k]!=oldprompt[k]}==set(add)
 for k in add:assert prompt[k]==oldprompt[k]+add[k]
 generation=read(ROOT/'generation_config.json');requests=[];stage_checks={};event_counts={};issues=[];path_index=[];original_files=[]
 for branch in BRANCHES:
  bc=read(ROOT/'variants'/branch/'config.json');oldbc=read(BASE/'variants'/branch/'config.json')
  for key in ['paper_order','cold_start','cold_start_seed','masking_seed','python_hash_seed','input_sha256']:assert bc[key]==oldbc[key]
  for stage in ['stage1','stage2']:
   d=ROOT/'variants'/branch/stage;key=branch+'_'+stage
   if not (d/'summary.json').exists() or read(d/'summary.json')['status']!='COMPLETE':
    stage_checks[key]={'status':'INCOMPLETE'};issues.append(key+': INCOMPLETE');continue
   s=read(d/'summary.json');assert sha(s['output_path'])==s['output_sha256']
   output=read(s['output_path']);assert list(output)==bc['paper_order'] and set(output)==set(raw)
   for p in raw:
    rr=json.loads(raw[p]['output']);nr=output[p]['normalized_output']
    assert len(nr)==len(rr) and output[p]['source_documents']==raw[p]['source_documents']
    assert [r['Result'] for r in nr]==[r['Result'] for r in rr]
   events=[read(p) for p in sorted((d/'events').glob('*.json'))]
   count=dict(collections.Counter(e['branch'] for e in events));event_counts[key]=count
   if stage=='stage1':assert read(d/'initial_labels.json')==read(BASE/'variants'/branch/stage/'initial_labels.json')
   else:assert read(d/'candidates.json')==read(BASE/'variants'/branch/stage/'candidates.json')
   calls=list((d/'api_calls').glob('*/state.json'));assert len(calls)==s['api_calls']
   for fp in calls:
    folder=fp.parent;req=read(folder/'request.json');exp=read(folder/'expected.json')
    assert {k:v for k,v in req.items() if k!='messages'}==generation
    assert req['messages']==exp['messages'] and len(req['messages'])==2
    pk='leaderboard-normalization-system-prompt' if stage=='stage2' else ('masked-normalization-system-prompt' if bc['cold_start'] or exp['field'] in ('Task','Dataset') else 'normalization-system-prompt')
    assert req['messages'][0]=={'role':'system','content':prompt[pk]}
    assert req['messages'][1]=={'role':'user','content':'\n\nItem list: '+exp['candidate_serialized']+'\n\nInput: '+exp['original']+'\n\nAnswer: '}
    requests.extend(audit_attempts(folder,req,exp,branch,stage))
   stage_checks[key]={'status':'COMPLETE','papers':len(output),'records':sum(len(x['normalized_output']) for x in output.values()),'calls':len(calls),'output_sha256':sha(s['output_path']),'null_fields':s['null_fields']}
   path_index.append({'branch':branch,'stage':stage,'output':s['output_path'],'sha256':sha(s['output_path']),'records':s['records'],'papers':s['papers']})
   original_files.append(Path(s['output_path']))
 grouped={}
 for branch in BRANCHES:
  ss=[r for r in requests if r['branch']==branch]
  grouped[branch]={'requests':len(ss),'successful_responses':sum(r['http_status']==200 for r in ss),'unknown_usage_requests':sum(not r['usage_known'] for r in ss),**{k:sum(r[k] for r in ss) for k in ['prompt_tokens','completion_tokens','total_tokens','reasoning_tokens','seconds']}}
 usage={'new_extraction_requests':0,'actual_model_requests':len(requests),'branches':grouped,
        'logical_normalization_requests':sum(v.get('calls',0) for v in stage_checks.values()),
        'totals':{k:sum(r[k] for r in requests) for k in ['prompt_tokens','completion_tokens','total_tokens','reasoning_tokens','seconds']},
        'http_counts':dict(collections.Counter(str(r['http_status']) for r in requests)),
        'finish_reason_counts':dict(collections.Counter(r['finish_reason'] for r in requests)),
        'automatic_retries':0,'authorized_additional_attempts':sum(r['attempt']!='original' for r in requests),
        'unknown_usage_requests':sum(not r['usage_known'] for r in requests),'token_totals_are_known_response_usage_only':True,'normalization_only':True}
 if requests:
  start=min(datetime.fromisoformat(r['started_utc']) for r in requests)
  end=max(datetime.fromisoformat(r['started_utc'])+timedelta(seconds=r['seconds']) for r in requests)
  usage.update(first_request_utc=start.isoformat(),last_response_utc=end.isoformat(),wall_seconds=(end-start).total_seconds())
  with (ROOT/'request_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(requests[0]));w.writeheader();w.writerows(requests)
 save(ROOT/'api_usage_summary.json',usage);save(ROOT/'output_index.json',path_index)
 save(ROOT/'normalization_event_summary.json',event_counts)
 verification={'status':'PASS' if not changed and not issues else 'INCOMPLETE_OR_FAILED','checked_utc':datetime.now(timezone.utc).isoformat(),
   'protected_file_count':len(protected),'protected_changes':changed,'stage_checks':stage_checks,'issues':issues,'new_extraction_requests':0,
   'old_extraction_unchanged':True,'Results_and_evidence_unchanged':True,'prompt_changes_only':list(add),'no_output_caps':True,
   'all_actual_system_prompts_and_user_templates_verified':True,'initial_sets_orders_and_stage2_candidate_order_match_baseline':True,
   'calls':len(requests),'all_accepted_logical_responses_http200_and_stop':True,
   'unknown_original_attempts':usage['unknown_usage_requests'],'authorized_additional_attempts':usage['authorized_additional_attempts'],
   'source_hashes':{str(p):sha(p) for p in original_files}}
 save(ROOT/'verification.json',verification)
 print(json.dumps({'status':verification['status'],'requests':len(requests),'tokens':usage['totals']['total_tokens'],'protected_changes':len(changed),'issues':issues}))
if __name__=='__main__':main()
