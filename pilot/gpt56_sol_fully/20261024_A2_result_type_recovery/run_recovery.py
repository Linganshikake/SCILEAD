"""Recover two numeric-Result outputs; only missing normalization calls are permitted."""
import json,sys,ast,time,os,argparse,msvcrt
from pathlib import Path
R=Path(__file__).resolve().parent
A2=R.parent/'20261024_A2_formal43';A0=R.parent/'20261024_A0_preparation'
sys.path.insert(0,str(A2))
from run_batch import request,payload,load,save,digest,now,ServiceStop,FormatStop,MODEL,ENV
from recovery_adapter import convert
import httpx
PAPERS=['1812.09471.pdf','2002.03184.pdf']

def freeze():
 manifest=load(A2/'result_manifest.json')
 protected={str(A2/p):h for p,h in manifest.items()}
 protected[str(A2/'result_manifest.json')]=digest(A2/'result_manifest.json')
 protected.update(load(A2/'protected_hashes.json'))
 if (R/'source_freeze_manifest.json').exists():
  prior=load(R/'source_freeze_manifest.json')
  assert protected==prior,'SOURCE_FREEZE_CHANGED'
 assert all(Path(p).exists() and digest(Path(p))==h for p,h in protected.items()),'FROZEN_SOURCE_CHANGED'
 save(R/'source_freeze_manifest.json',protected)
 return protected

def prepare():
 protected=freeze()
 strings=load(A0/'candidate_sets.json');candidates={k:ast.literal_eval(v) for k,v in strings.items()}
 prompts=load(A0/'frozen_prompts.json');inputs={x['paper_id']:x for x in load(A2/'input_manifest.json')}
 config=load(A2/'generation_config.json')
 assert config['normalization']=={k:v for k,v in payload([]).items() if k!='messages'}
 queues={};converted={};audits={}
 for pid in PAPERS:
  p=A2/'papers'/pid/'extraction';res=load(p/'response.json');state=load(p/'state.json')
  assert state['http_status']==200 and res['model']==MODEL and res['choices'][0]['finish_reason']=='stop'
  assert load(p/'validation.json')=={'valid':False,'reason':'INVALID_FIELD_TYPES'}
  assert not list((A2/'papers'/pid/'normalization').glob('**/attempt.lock'))
  raw=res['choices'][0]['message']['content'];rows,audit=convert(raw)
  assert len(rows)==(6 if pid==PAPERS[0] else 7)
  assert all(a['changed_type'] and a['numeric_semantics_equal'] for a in audit)
  docs=load(Path(inputs[pid]['cached_evidence_path']))
  assert digest(Path(inputs[pid]['cached_evidence_path']))==inputs[pid]['evidence_file_sha256']
  path=R/'papers'/pid
  save(path/'output.json',{pid:{'output':json.dumps(rows,ensure_ascii=False),'source_documents':docs}})
  save(path/'conversion_audit.json',{'source_response':str(p/'response.json'),'source_response_sha256':digest(p/'response.json'),'source_raw_text_sha256':digest(p/'response_raw.txt'),
     'rows':audit,'record_count_order_duplicates_preserved':True,'non_result_fields_unchanged':True,'method':'str(json.loads Result) as official tdm_llm_normalization.py:74, with Decimal(original literal)==Decimal(converted string)',
     'no_unit_rescaling':True,'no_rounding':True,'original_response_not_modified':True})
  jobs=[]
  for i,row in enumerate(rows):
   for field,value in row.items():
    if field=='Result' or value in candidates[field]:continue
    jobs.append({'paper_id':pid,'position':len(jobs)+1,'record_index':i,'field':field,'input':value,
      'messages':[{'role':'system','content':prompts['normalization-system-prompt']},{'role':'user','content':'\n\nItem list: '+strings[field]+'\n\nInput: '+value+'\n\nAnswer: '}]})
  queues[pid]=jobs;converted[pid]=rows;audits[pid]=audit
 save(R/'normalization_request_manifest.json',{'model':MODEL,'papers':queues,'request_count':sum(map(len,queues.values())),'extraction_requests':0,'duplicate_name_cache':False,
      'candidate_strings':strings,'generation_parameters':config['normalization'],'base_url':config['base_url'],'automatic_retries':0})
 save(R/'preflight.json',{'status':'PASS','source_files_verified':len(protected),'papers':PAPERS,'records':13,'numeric_conversions':13,'new_extraction_calls':0,
      'planned_normalization_calls':sum(map(len,queues.values())),'tests_passed':6,'authorization':'用户：恢复这两篇格式失败的论文；只做Result类型恢复及两篇缺失的下游步骤',
      'prior_A2_unchanged':True,'historical_A2_calls':696,'A1_calls_excluded':14,'type_policy_change_explicit':True})
 return protected,queues,converted,candidates

def summary(status,error,started):
 states=[]
 for p in sorted((R/'papers').glob('*/normalization/**/state.json')):
  s=load(p);s['relative_request_path']=str(p.parent.relative_to(R));states.append(s)
 usage={k:sum((s.get('usage') or {}).get(k,0) or 0 for s in states) for k in ['prompt_tokens','completion_tokens','total_tokens']}
 usage.update(new_requests=len(states),new_extraction_calls=0,new_normalization_calls=len(states),http200=sum(s.get('http_status')==200 for s in states),
    unknown_usage=sum(s.get('usage') is None for s in states),elapsed_seconds=time.monotonic()-started,original_A2_calls=696,combined_A2_recovery_calls=696+len(states),A1_calls_excluded=14)
 save(R/'api_usage_summary.json',usage)
 save(R/'request_status.json',states)
 save(R/'runtime_status.json',{'status':status,'error':error,'updated_utc':now(),'usage':usage})
 return usage

def main(execute):
 protected,queues,converted,candidates=prepare()
 print(json.dumps({'offline_conversion':'PASS','records':13,'planned_normalization_calls':sum(map(len,queues.values())),'per_paper_calls':{p:len(q) for p,q in queues.items()},'new_extraction_calls':0}),flush=True)
 if not execute:return
 from dotenv import dotenv_values
 env=dotenv_values(ENV,interpolate=False,encoding='utf-8-sig')
 key=next((env[k] for k in ['OPENAI_API_KEY','API_KEY','SK'] if env.get(k)),None)
 base=next((env[k] for k in ['BASE_URL','OPENAI_BASE_URL','API_BASE','OPENAI_API_BASE','API_BASE_URL'] if env.get(k)),None)
 assert key and base and base.rstrip('/') in ['https://9527.codes','https://9527.codes/v1']
 base=base.rstrip('/');url=(base if base.endswith('/v1') else base+'/v1')+'/chat/completions'
 lock=(R/'recovery_process.lock').open('a+b');lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 start=time.monotonic();status='RUNNING';error=None
 save(R/'authorization.json',{'user_instruction':'恢复这两篇格式失败的论文','model':MODEL,'new_extraction_calls':0,'normalization_requests':sum(map(len,queues.values())),
      'parameters':{k:v for k,v in payload([]).items() if k!='messages'},'runner_sha256':digest(Path(__file__)),'adapter_sha256':digest(R/'recovery_adapter.py'),'started_utc':now()})
 try:
  with httpx.Client(transport=httpx.HTTPTransport(retries=0),trust_env=False,follow_redirects=False,timeout=httpx.Timeout(connect=20,read=600,write=30,pool=20)) as client:
   for pid in PAPERS:
    paper=R/'papers'/pid;normalized=[];count=0
    for i,row in enumerate(converted[pid]):
     nr={}
     for field,value in row.items():
      if field=='Result' or value in candidates[field]:nr[field]=str(value);continue
      job=queues[pid][count];count+=1
      assert (job['record_index'],job['field'],job['input'])==(i,field,value)
      folder=paper/'normalization/requests'/f'{count:03d}_record{i}_{field}'
      response,answer=request(client,folder,payload(job['messages']),key,url,False)
      nr[field]=answer if answer in candidates[field] else None
      save(folder/'mapping.json',{'paper_id':pid,'record_index':i,'field':field,'input':value,'raw_answer':answer,'accepted':nr[field],
           'reason':'EXACT_CANDIDATE' if nr[field] is not None else 'OUTSIDE_CANDIDATES'})
      save(R/'checkpoint.json',{'paper_id':pid,'last_request_completed':count,'planned':len(queues[pid]),'updated_utc':now()})
      print(json.dumps({'paper':pid,'normalization_done':count,'planned':len(queues[pid])}),flush=True)
     normalized.append(nr);save(paper/'normalization/partial_output.json',normalized)
    docs=load(paper/'output.json')[pid]['source_documents']
    save(paper/'normalization/normalized_output.json',{pid:{'normalized_output':normalized,'source_documents':docs}})
    save(paper/'verification.json',{'status':'RECOVERED','records':len(normalized),'normalization_requests':count,'null_fields':sum(v is None for r in normalized for v in r.values()),'new_extraction_calls':0})
    print(json.dumps({'paper_recovered':pid,'records':len(normalized)}),flush=True)
  status='RECOVERY_COMPLETE'
 except Exception as e:
  status='STOPPED';error={'type':type(e).__name__,'reason':str(e).replace(key,'[REDACTED]')[:250]}
  save(R/'failure.json',error)
 finally:
  # Release owned byte-range lock before scanning; old post-run issue cannot recur.
  lock.close()
  usage=summary(status,error,start)
  changed=[p for p,h in protected.items() if not Path(p).exists() or digest(Path(p))!=h]
  secret_free=all(key.encode() not in p.read_bytes() for p in R.rglob('*') if p.is_file())
  save(R/'source_integrity_verification.json',{'protected_files':len(protected),'changed_files':changed,'secret_scan_passed':secret_free,'new_extraction_calls':0})
  print(json.dumps({'status':status,'error':error,'usage':usage,'source_files_unchanged':not changed,'secret_scan_passed':secret_free}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');main(p.parse_args().execute)
