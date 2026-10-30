"""Serial Fully LLM run using frozen messages and exact original per-field mapping."""
import os,sys,json,csv,time,ast,argparse,msvcrt,shutil
from pathlib import Path
import httpx,ctypes
sys.dont_write_bytecode=True
from transport import ROOT,MODEL,BASE,save,load,digest,now,payload,one_request,validate,load_credentials
from result_compat import convert
RUN=ROOT/'fully'

class ServiceStop(RuntimeError):pass
class FormatStop(ValueError):pass

def resources():
 class Mem(ctypes.Structure):
  _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('available_page',ctypes.c_ulonglong),('total_virtual',ctypes.c_ulonglong),('available_virtual',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
 class Proc(ctypes.Structure):
  _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong),('peak',ctypes.c_size_t),('working',ctypes.c_size_t),('pool_peak',ctypes.c_size_t),('pool',ctypes.c_size_t),('nonpaged_peak',ctypes.c_size_t),('nonpaged',ctypes.c_size_t),('pagefile',ctypes.c_size_t),('peak_pagefile',ctypes.c_size_t)]
 m=Mem();m.length=ctypes.sizeof(m);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
 p=Proc();p.cb=ctypes.sizeof(p);ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
 ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(Proc),ctypes.c_ulong]
 assert ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(p),p.cb)
 return {'available_memory_bytes':m.available,'rss_bytes':p.working,'peak_rss_bytes':p.peak,'free_disk_bytes':shutil.disk_usage(ROOT).free}

def request(client,folder,messages,key,extraction):
 req=payload(messages)
 if (folder/'attempt.lock').exists():
  if not (folder/'state.json').exists():raise ServiceStop('UNKNOWN_ATTEMPT_NO_RESEND')
  s=load(folder/'state.json')
  if s.get('status')!='RECEIVED' or s.get('http_status')!=200:raise ServiceStop('FAILED_OR_UNKNOWN_NO_RESEND')
  if load(folder/'request.json')!=req:raise ServiceStop('REPLAY_REQUEST_CHANGED')
  if not (folder/'response.json').exists():raise ServiceStop('MISSING_RESPONSE_NO_RESEND')
  body=load(folder/'response.json')
 else:
  mem=resources()
  if mem['available_memory_bytes']<256*2**20 or mem['free_disk_bytes']<2*2**30:raise ServiceStop('RESOURCE_LIMIT')
  save(folder/'resource_before.json',mem)
  try:body=one_request(client,folder,req,key,BASE+'/chat/completions')
  except Exception as e:raise ServiceStop(type(e).__name__+':'+str(e).replace(key,'[REDACTED]')[:150]) from None
  finally:save(folder/'resource_after.json',resources())
 try:result=validate(body,extraction)
 except Exception as e:
  save(folder/'validation.json',{'valid':False,'reason':str(e)[:200]})
  if str(e)=='RESPONSE_MODEL_MISMATCH':raise ServiceStop('RESPONSE_MODEL_MISMATCH') from None
  raise FormatStop(str(e)[:200]) from None
 save(folder/'validation.json',{'valid':True,'records':len(result) if extraction else None,'finish_reason':body['choices'][0]['finish_reason'],'response_model':body['model']})
 return body,result

def csvsave(p,rows):
 if not rows:return
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def summarize(cp):
 states=[]
 for p in sorted((RUN/'papers').glob('*/**/state.json')):
  s=load(p);r=p.relative_to(RUN/'papers');u=s.get('usage') or {}
  states.append({'paper_id':r.parts[0],'stage':r.parts[1],'request_directory':str(p.parent),
   'status':s['status'],'http_status':s.get('http_status'),'request_model':MODEL,'response_model':s.get('response_model'),
   'finish_reason':s.get('finish_reason'),'prompt_tokens':u.get('prompt_tokens'),'completion_tokens':u.get('completion_tokens'),
   'total_tokens':u.get('total_tokens'),'reasoning_tokens':(u.get('completion_tokens_details') or {}).get('reasoning_tokens'),
   'cache_hit_tokens':u.get('prompt_cache_hit_tokens'),'cache_miss_tokens':u.get('prompt_cache_miss_tokens'),
   'elapsed_seconds':s.get('elapsed_seconds'),'request_id':s.get('response_id')})
 usage={k:sum(r.get(k) or 0 for r in states) for k in ('prompt_tokens','completion_tokens','total_tokens','reasoning_tokens','cache_hit_tokens','cache_miss_tokens','elapsed_seconds')}
 usage.update(request_attempts=len(states),extraction_attempts=sum(x['stage']=='extraction' for x in states),normalization_attempts=sum(x['stage']=='normalization' for x in states),http_200=sum(x['http_status']==200 for x in states),unknown_usage=sum(x['total_tokens'] is None for x in states),automatic_retries=0)
 save(RUN/'api_usage_summary.json',usage);csvsave(RUN/'request_status.csv',states)
 csvsave(RUN/'paper_status.csv',[{'paper_id':p,**v} for p,v in cp['papers'].items()]);save(RUN/'checkpoint.json',cp)
 raw={};compatible={};norm={}
 for pid in cp['papers']:
  d=RUN/'papers'/pid
  if (d/'raw_output.json').exists():raw.update(load(d/'raw_output.json'))
  if (d/'output.json').exists():compatible.update(load(d/'output.json'))
  if cp['papers'][pid]['normalization']=='COMPLETE':norm.update(load(d/'normalization/normalized_output.json'))
 save(RUN/'merged/raw_output.json',raw);save(RUN/'merged/output.json',compatible);save(RUN/'merged/normalized_output.json',norm)
 return usage

def verify_inputs():
 protected=load(ROOT/'protected_hashes.json');changed=[p for p,h in protected.items() if not Path(p).exists() or digest(p)!=h]
 assert not changed,'PROTECTED_FILE_CHANGED'
 inputs=load(ROOT/'input_manifest.json')
 for r in inputs:
  assert digest(r['cached_evidence_path'])==r['evidence_file_sha256'] and digest(r['messages_path'])==r['messages_file_sha256']
 return inputs,len(protected)

def main(execute=False,max_papers=None):
 inputs,protected_count=verify_inputs();mem=resources()
 save(RUN/'preflight.json',{'utc':now(),'inputs':len(inputs),'protected_files':protected_count,'resources':mem,'parameters':load(ROOT/'generation_config.json')})
 if not execute:print(json.dumps({'preflight':'PASS','papers':len(inputs),'resources':mem}));return 0
 key,base=load_credentials();assert base==BASE
 lock=(RUN/'process.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 cp=load(RUN/'checkpoint.json') if (RUN/'checkpoint.json').exists() else {'state':'PENDING','started_utc':now(),'papers':{r['paper_id']:{'extraction':'PENDING','normalization':'PENDING','records':0,'normalization_planned':None,'normalization_complete':0,'null_fields':None,'error':''} for r in inputs}}
 prompts=load(ROOT/'frozen_prompts.json');strings=load(ROOT/'candidate_sets.json');sets={k:ast.literal_eval(v) for k,v in strings.items()}
 cp['state']='RUNNING';stop=None;performed=0
 try:
  with httpx.Client(transport=httpx.HTTPTransport(retries=0),trust_env=False,follow_redirects=False,timeout=httpx.Timeout(connect=20,read=600,write=30,pool=20)) as client:
   for index,r in enumerate(inputs,1):
    pid=r['paper_id'];paper=RUN/'papers'/pid;s=cp['papers'][pid]
    if s['normalization']=='COMPLETE':
     assert all(digest(paper/f)==h for f,h in load(paper/'completion_hashes.json').items()),'COMPLETE_OUTPUT_CHANGED'
     continue
    if s['extraction']=='FORMAT_FAILED' or s['normalization']=='FORMAT_FAILED':continue
    phase='extraction';docs=load(r['cached_evidence_path']);messages=load(r['messages_path'])
    save(paper/'input_manifest.json',r)
    try:
     s['extraction']='RUNNING';save(RUN/'checkpoint.json',cp)
     print(json.dumps({'index':index,'paper':pid,'stage':phase}),flush=True)
     body,rows=request(client,paper/'extraction',messages,key,True)
     text=body['choices'][0]['message']['content'];rows,audit=convert(text)
     save(paper/'raw_output.json',{pid:{'output':text,'source_documents':docs}})
     save(paper/'result_conversion.json',{'raw_response_sha256':digest(paper/'extraction/response.json'),'records':audit,'numeric_semantics_unchanged':True})
     compatible=text if not any(a['changed_type'] for a in audit) else json.dumps(rows,ensure_ascii=False)
     save(paper/'output.json',{pid:{'output':compatible,'source_documents':docs}})
     s.update(extraction='COMPLETE' if rows else 'VALID_EMPTY',records=len(rows),error='')
     planned=[{'record':i,'field':k,'input':v} for i,row in enumerate(rows) for k,v in row.items() if k!='Result' and v not in sets[k]]
     save(paper/'normalization_request_manifest.json',{'requests':planned,'candidate_strings':strings,'cache':'none across positions'})
     s['normalization_planned']=len(planned);s['normalization']='RUNNING';phase='normalization';summarize(cp)
     normalized=[];count=0
     for i,row in enumerate(rows):
      nr={}
      for k,v in row.items():
       if k=='Result' or v in sets[k]:nr[k]=str(v);continue
       count+=1;folder=paper/'normalization/requests'/f'{count:03d}_record{i}_{k}'
       nm=[{'role':'system','content':prompts['normalization-system-prompt']},{'role':'user','content':'\n\nItem list: '+strings[k]+'\n\nInput: '+v+'\n\nAnswer: '}]
       response,answer=request(client,folder,nm,key,False)
       nr[k]=answer if answer in sets[k] else None
       save(folder/'mapping.json',{'record':i,'field':k,'input':v,'raw_answer':answer,'accepted':nr[k],'reason':'EXACT_CANDIDATE' if nr[k] is not None else 'OUTSIDE_CANDIDATES'})
       s['normalization_complete']=count;save(RUN/'checkpoint.json',cp)
       print(json.dumps({'paper':pid,'normalization':count,'planned':len(planned),'accepted':nr[k] is not None}),flush=True)
      normalized.append(nr);save(paper/'normalization/partial_output.json',normalized)
     save(paper/'normalization/normalized_output.json',{pid:{'normalized_output':normalized,'source_documents':docs}})
     s.update(normalization='COMPLETE',null_fields=sum(v is None for n in normalized for v in n.values()),error='')
     save(paper/'completion_hashes.json',{str(f.relative_to(paper)):digest(f) for f in paper.rglob('*') if f.is_file() and f.name!='completion_hashes.json'})
     performed+=1;u=summarize(cp)
     print(json.dumps({'paper_complete':pid,'completed':sum(x['normalization']=='COMPLETE' for x in cp['papers'].values()),'requests':u['request_attempts'],'tokens':u['total_tokens']}),flush=True)
     if max_papers is not None and performed>=max_papers:cp['state']='CHECKPOINT';break
    except FormatStop as e:
     s[phase]='FORMAT_FAILED';s['error']=str(e)
     save(paper/'failure.json',{'stage':phase,'reason':str(e),'raw_preserved':True});summarize(cp)
     print(json.dumps({'paper_failed':pid,'stage':phase,'reason':str(e)}),flush=True)
    except ServiceStop as e:
     s[phase]='BLOCKED';s['error']=str(e);stop={'paper':pid,'phase':phase,'reason':str(e)};break
  if stop:cp['state']='BLOCKED'
  elif cp['state']!='CHECKPOINT':cp['state']='QUEUE_FINISHED'
 except Exception as e:
  cp['state']='ENGINEERING_STOP';stop={'type':type(e).__name__,'reason':str(e).replace(key,'[REDACTED]')[:250]}
 finally:
  cp['stop_reason']=stop;cp['updated_utc']=now();u=summarize(cp)
  protected=load(ROOT/'protected_hashes.json');changed=[p for p,h in protected.items() if not Path(p).exists() or digest(p)!=h]
  complete=[p for p,s in cp['papers'].items() if s['normalization']=='COMPLETE']
  secret_free=all(key.encode() not in p.read_bytes() for p in RUN.rglob('*') if p.is_file() and p.name!='process.lock')
  save(RUN/'verification.json',{'state':cp['state'],'complete_papers':len(complete),'gold_covered':sum(r['gold_count_audit_only'] for r in inputs if r['paper_id'] in complete),'records':sum(s['records'] for s in cp['papers'].values()),'protected_files_changed':changed,'secret_scan_passed':secret_free,'usage':u,'stop':stop})
  print(json.dumps({'state':cp['state'],'complete':len(complete),'requests':u['request_attempts'],'tokens':u['total_tokens'],'stop':stop}),flush=True)
  lock.close()
 return 2 if stop else 0
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--max-papers',type=int);a=ap.parse_args();sys.exit(main(a.execute,a.max_papers))
