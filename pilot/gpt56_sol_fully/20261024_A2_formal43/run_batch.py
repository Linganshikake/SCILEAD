"""Approved A2 serial runner. Uses frozen A1 transport/validation; never resends attempts."""
import sys,os,json,ast,time,csv,shutil,ctypes,msvcrt,argparse
from pathlib import Path
R=Path(__file__).resolve().parent
A1=R.parent/'20261024_A1_single_paper'
A0=R.parent/'20261024_A0_preparation'
sys.path.insert(0,str(A1))
from run_trial import one_request,validate,payload,save,load,digest,MODEL,ENV,now
import httpx

class ServiceStop(RuntimeError):pass
class FormatStop(ValueError):pass

def secret_scan(root,key):
 # The sole excluded byte is our own fixed b'0' process-control lock.
 # Windows disallows a second handle from reading that locked byte.
 return all(key.encode() not in p.read_bytes() for p in root.rglob('*') if p.is_file() and p!=root/'batch_process.lock')

class MemoryStatus(ctypes.Structure):
 _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('available_page',ctypes.c_ulonglong),('total_virtual',ctypes.c_ulonglong),('available_virtual',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
class ProcessMemory(ctypes.Structure):
 _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong),('peak',ctypes.c_size_t),('working',ctypes.c_size_t),('pool_peak',ctypes.c_size_t),('pool',ctypes.c_size_t),('nonpaged_peak',ctypes.c_size_t),('nonpaged',ctypes.c_size_t),('pagefile',ctypes.c_size_t),('peak_pagefile',ctypes.c_size_t)]
def resources():
 m=MemoryStatus();m.length=ctypes.sizeof(m)
 if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):raise ServiceStop('MEMORY_PROBE_FAILED')
 p=ProcessMemory();p.cb=ctypes.sizeof(p)
 ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
 ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(ProcessMemory),ctypes.c_ulong]
 if not ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(p),p.cb):raise ServiceStop('PROCESS_MEMORY_PROBE_FAILED')
 return {'available_memory_bytes':m.available,'process_peak_rss_bytes':p.peak,'process_rss_bytes':p.working,'free_disk_bytes':shutil.disk_usage(R).free}

def request(client,folder,req,key,url,extraction):
 if (folder/'attempt.lock').exists():
  if not (folder/'state.json').exists():raise ServiceStop('UNKNOWN_EXISTING_ATTEMPT')
  s=load(folder/'state.json')
  if s.get('status')!='RECEIVED' or s.get('http_status')!=200:raise ServiceStop('FAILED_OR_UNKNOWN_ATTEMPT_NO_RESEND')
  if not (folder/'request.json').exists() or load(folder/'request.json')!=req:raise ServiceStop('REQUEST_HASH_CHANGED')
  if not (folder/'response.json').exists():raise ServiceStop('MISSING_RESPONSE_NO_RESEND')
  res=load(folder/'response.json')
 else:
  mem=resources()
  if mem['available_memory_bytes']<256*2**20 or mem['free_disk_bytes']<2*2**30:raise ServiceStop('RESOURCE_LIMIT')
  save(folder/'resource_before.json',mem)
  try:res=one_request(client,folder,req,key,url)
  except Exception as e:raise ServiceStop(type(e).__name__+':'+str(e).replace(key,'[REDACTED]')[:180]) from None
  finally:save(folder/'resource_after.json',resources())
 try:parsed=validate(res,extraction)
 except Exception as e:
  save(folder/'validation.json',{'valid':False,'reason':str(e)[:200]})
  if str(e)=='RESPONSE_MODEL_MISMATCH':raise ServiceStop('RESPONSE_MODEL_MISMATCH') from None
  raise FormatStop(str(e)[:200]) from None
 save(folder/'validation.json',{'valid':True,'finish_reason':'stop','model':MODEL,'records':len(parsed) if extraction else None})
 return res,parsed

def write_csv(path,rows,fields=None):
 if not rows and fields is None:return
 tmp=path.with_suffix('.tmp')
 with tmp.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
 os.replace(tmp,path)

def summarize(checkpoint):
 records=[];usages=[]
 for p in sorted((R/'papers').glob('*/**/state.json')):
  s=load(p);rel=p.relative_to(R/'papers');folder=p.parent
  resp=load(folder/'response.json') if (folder/'response.json').exists() else {}
  choices=resp.get('choices') or []
  u=s.get('usage') or {};v=load(folder/'validation.json') if (folder/'validation.json').exists() else {}
  memory=load(folder/'resource_after.json') if (folder/'resource_after.json').exists() else {}
  item={'paper_id':rel.parts[0],'stage':rel.parts[1],'request_position':folder.name,'request_model':MODEL,'response_model':s.get('response_model'),
        'http_status':s.get('http_status'),'finish_reason':choices[0].get('finish_reason') if choices else None,'state':s['status'],'valid':v.get('valid'),
        'input_tokens':u.get('prompt_tokens'),'output_tokens':u.get('completion_tokens'),'total_tokens':u.get('total_tokens'),
        'response_id':s.get('response_id'),'started_utc':s.get('started_utc'),'elapsed_seconds':s.get('elapsed_seconds'),
        'raw_response_path':str(folder/'response_raw.txt'),'request_sha256':digest(folder/'request.json'),
        'normalized_mapping_path':str(folder/'mapping.json') if (folder/'mapping.json').exists() else '',
        'failure_reason':v.get('reason') or s.get('error_type'),'process_peak_rss_bytes':memory.get('process_peak_rss_bytes'),
        'available_memory_bytes':memory.get('available_memory_bytes'),'free_disk_bytes':memory.get('free_disk_bytes')}
  records.append(item);usages.append(u)
 total={k:sum(u.get(k,0) or 0 for u in usages) for k in ['prompt_tokens','completion_tokens','total_tokens']}
 total.update(request_attempts=len(records),extraction_attempts=sum(r['stage']=='extraction' for r in records),normalization_attempts=sum(r['stage']=='normalization' for r in records),
              http_200=sum(r['http_status']==200 for r in records),unknown_usage_requests=sum(not u for u in usages),
              request_latency_seconds=sum(r['elapsed_seconds'] or 0 for r in records),process_peak_rss_bytes=max([r['process_peak_rss_bytes'] or 0 for r in records]+[0]),
              A1_calls_excluded=14)
 save(R/'api_usage_summary.json',total)
 write_csv(R/'request_status.csv',records)
 write_csv(R/'paper_status.csv',[{'paper_id':p,**s} for p,s in checkpoint['papers'].items()])
 save(R/'runtime_checkpoint.json',checkpoint)
 return total

def main(execute):
 # Preserve preparation artifacts; runtime state is separate and resumable.
 baseline=load(R/'delivery_manifest.json')
 assert all(digest(R/p)==h for p,h in baseline.items()),'PREPARATION_CHANGED'
 protected=load(R/'protected_hashes.json')
 assert all(Path(p).exists() and digest(Path(p))==h for p,h in protected.items()),'FROZEN_RESULTS_CHANGED'
 inputs=load(R/'input_manifest.json');cfg=load(R/'generation_config.json')
 assert len(inputs)==43 and sum(r['gold_count_audit_only'] for r in inputs)==295
 assert cfg['extraction']==cfg['normalization']=={k:v for k,v in payload([]).items() if k!='messages'}
 for r in inputs:
  assert digest(Path(r['messages_path']))==r['messages_file_sha256']
  assert digest(Path(r['cached_evidence_path']))==r['evidence_file_sha256']
 mem=resources();save(R/'launch_preflight.json',{'time':now(),'resources':mem,'papers':43,'protected_files':len(protected),'new_calls':0,'A1_reuse':False})
 if not execute:print(json.dumps({'preflight':'PASS','resources':mem,'papers':43}));return
 from dotenv import dotenv_values
 env=dotenv_values(ENV,interpolate=False,encoding='utf-8-sig')
 key=next((env[k] for k in ['OPENAI_API_KEY','API_KEY','SK'] if env.get(k)),None)
 base=next((env[k] for k in ['BASE_URL','OPENAI_BASE_URL','API_BASE','OPENAI_API_BASE','API_BASE_URL'] if env.get(k)),None)
 assert key and base and base.rstrip('/') in ['https://9527.codes','https://9527.codes/v1'],'UNEXPECTED_CREDENTIAL_CONFIG'
 url=base.rstrip('/')
 if not url.endswith('/v1'):url+='/v1'
 url+='/chat/completions'
 lock=(R/'batch_process.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
 msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 if not (R/'runtime_authorization.json').exists():
  save(R/'runtime_authorization.json',{'authorized_at':now(),'user_instruction':'批准，可以进行A2','papers':43,'A1_formal_reuse':False,
       'parameters':cfg['extraction'],'auto_retries':0,'provider_unknowns':'User approved proceeding; enforce server responses, no extra probe or input truncation',
       'supersedes_preparation_authorization_false':True,'generation_config_sha256':digest(R/'generation_config.json'),
       'runner_sha256':digest(Path(__file__)),'a1_transport_sha256':digest(A1/'run_trial.py')})
 checkpoint=load(R/'runtime_checkpoint.json') if (R/'runtime_checkpoint.json').exists() else {'state':'RUNNING','started_utc':now(),
        'papers':{r['paper_id']:{'extraction':'PENDING','normalization':'PENDING','records':0,'normalization_requests_planned':None,'normalization_requests_complete':0,'null_fields':None,'error':''} for r in inputs}}
 prompts=load(A0/'frozen_prompts.json');strings=load(A0/'candidate_sets.json');candidates={k:ast.literal_eval(v) for k,v in strings.items()}
 stop=None;checkpoint['state']='RUNNING';save(R/'runtime_checkpoint.json',checkpoint)
 try:
  with httpx.Client(transport=httpx.HTTPTransport(retries=0),trust_env=False,follow_redirects=False,timeout=httpx.Timeout(connect=20,read=600,write=30,pool=20)) as client:
   for index,r in enumerate(inputs,1):
    pid=r['paper_id'];paper=R/'papers'/pid;s=checkpoint['papers'][pid]
    if s['normalization']=='COMPLETE':
     verified=load(paper/'completion_hashes.json')
     assert all(digest(paper/f)==h for f,h in verified.items()),'COMPLETED_PAPER_CHANGED'
     continue
    if s['extraction']=='FORMAT_FAILED' or s['normalization']=='FORMAT_FAILED':continue
    docs=load(Path(r['cached_evidence_path']));messages=load(Path(r['messages_path']))
    save(paper/'input_manifest.json',r)
    phase='extraction'
    try:
     s['extraction']='RUNNING';save(R/'runtime_checkpoint.json',checkpoint)
     print(json.dumps({'paper':pid,'index':index,'stage':'EXTRACTION'}),flush=True)
     res,rows=request(client,paper/'extraction',payload(messages),key,url,True)
     save(paper/'output.json',{pid:{'output':res['choices'][0]['message']['content'],'source_documents':docs}})
     s.update(extraction='VALID_EMPTY' if not rows else 'COMPLETE',records=len(rows),error='')
     planned=[{'record_index':i,'field':k,'input':v} for i,row in enumerate(rows) for k,v in row.items() if k!='Result' and v not in candidates[k]]
     s['normalization_requests_planned']=len(planned)
     save(paper/'normalization_request_manifest.json',{'requests':planned,'candidate_strings':strings,'no_duplicate_cache':True})
     phase='normalization';s['normalization']='RUNNING';summarize(checkpoint)
     print(json.dumps({'paper':pid,'records':len(rows),'normalization_requests':len(planned)}),flush=True)
     normalized=[];count=0
     for i,row in enumerate(rows):
      nr={}
      for k,v in row.items():
       if k=='Result' or v in candidates[k]:nr[k]=str(v);continue
       count+=1;folder=paper/'normalization'/'requests'/f'{count:03d}_record{i}_{k}'
       nm=[{'role':'system','content':prompts['normalization-system-prompt']},{'role':'user','content':'\n\nItem list: '+strings[k]+'\n\nInput: '+v+'\n\nAnswer: '}]
       result,answer=request(client,folder,payload(nm),key,url,False)
       nr[k]=answer if answer in candidates[k] else None
       save(folder/'mapping.json',{'record':i,'field':k,'input':v,'raw_answer':answer,'accepted':nr[k],'reason':'EXACT_CANDIDATE' if nr[k] is not None else 'OUTSIDE_CANDIDATES'})
       s['normalization_requests_complete']=count;save(R/'runtime_checkpoint.json',checkpoint)
       print(json.dumps({'paper':pid,'normalization_done':count,'planned':len(planned)}),flush=True)
      normalized.append(nr);save(paper/'normalization/partial_output.json',normalized)
     save(paper/'normalization/normalized_output.json',{pid:{'normalized_output':normalized,'source_documents':docs}})
     s.update(normalization='COMPLETE',null_fields=sum(v is None for row in normalized for v in row.values()),error='')
     save(paper/'completion_hashes.json',{str(f.relative_to(paper)):digest(f) for f in paper.rglob('*') if f.is_file() and f.name!='completion_hashes.json'})
     total=summarize(checkpoint)
     print(json.dumps({'paper_complete':pid,'completed':sum(x['normalization']=='COMPLETE' for x in checkpoint['papers'].values()),'requests':total['request_attempts'],'total_tokens':total['total_tokens']}),flush=True)
    except FormatStop as e:
     s[phase]='FORMAT_FAILED';s['error']=str(e);save(paper/'failure.json',{'phase':phase,'type':'FORMAT_FAILED','reason':str(e)})
     summarize(checkpoint)
     print(json.dumps({'paper_failed':pid,'reason':str(e),'continue_other_papers':True}),flush=True)
    except ServiceStop as e:
     s[phase]='STOPPED_SERVICE_OR_UNKNOWN';s['error']=str(e)
     save(paper/'failure.json',{'phase':phase,'type':'STOPPED_SERVICE_OR_UNKNOWN','reason':str(e)})
     stop={'paper_id':pid,'phase':phase,'reason':str(e)};break
  checkpoint['state']='STOPPED' if stop else 'QUEUE_FINISHED'
 except Exception as e:
  stop={'type':type(e).__name__,'reason':str(e).replace(key,'[REDACTED]')[:200]};checkpoint['state']='ENGINEERING_STOP'
 finally:
  checkpoint['stop_reason']=stop;checkpoint['updated_utc']=now();total=summarize(checkpoint)
  changed=[p for p,h in protected.items() if not Path(p).exists() or digest(Path(p))!=h]
  secret_free=secret_scan(R,key)
  complete=[p for p,s in checkpoint['papers'].items() if s['normalization']=='COMPLETE']
  extracted={};normed={}
  for r in inputs:
   p=R/'papers'/r['paper_id']
   if (p/'output.json').exists():extracted.update(load(p/'output.json'))
   if r['paper_id'] in complete:normed.update(load(p/'normalization/normalized_output.json'))
  save(R/'merged/output.json',extracted);save(R/'merged/normalized_output.json',normed)
  save(R/'runtime_verification.json',{'status':checkpoint['state'],'completed_papers':len(complete),'target_papers':43,'gold_covered':sum(r['gold_count_audit_only'] for r in inputs if r['paper_id'] in complete),
       'extracted_papers':len(extracted),'records':sum(s['records'] for s in checkpoint['papers'].values()),'protected_hashes_checked':len(protected),
       'frozen_files_changed':changed,'secret_scan_passed':secret_free,'stop_reason':stop,'api_usage':total,'A1_reused':False})
  print(json.dumps({'final_state':checkpoint['state'],'complete_papers':len(complete),'requests':total['request_attempts'],'tokens':total['total_tokens'],'stop':stop},ensure_ascii=False),flush=True)
  lock.close()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');main(p.parse_args().execute)
