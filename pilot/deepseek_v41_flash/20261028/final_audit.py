"""Audit actual calls and protected sources without inference or evaluation."""
import json,csv,sys,ast
from pathlib import Path
from collections import Counter
from datetime import datetime,timedelta
from transport import ROOT,MODEL,ACCEPTED_MODELS,payload,load,save,digest,now

def main():
 files=list((ROOT/'fully/papers').glob('*/**/state.json'))
 for branch in ('partially','cold_default','cold_0','cold_42'):
  files.extend((ROOT/'variants'/branch).glob('stage*/api_calls/**/state.json'))
 assert len(set(files))==len(files)
 requests=[];issues=[];branch_usage={}
 for p in sorted(files):
  s=load(p);folder=p.parent;req=load(folder/'request.json');resp=load(folder/'response.json') if (folder/'response.json').exists() else {}
  rel=p.relative_to(ROOT);branch='fully' if rel.parts[0]=='fully' else rel.parts[1]
  u=s.get('usage') or {};choices=resp.get('choices') or [];finish=choices[0].get('finish_reason') if choices else None
  actual={k:v for k,v in req.items() if k!='messages'};expected=payload([]);expected.pop('messages')
  if actual!=expected:issues.append({'path':str(folder),'error':'PARAMETER_MISMATCH'})
  if resp and resp.get('model') not in ACCEPTED_MODELS:issues.append({'path':str(folder),'error':'MODEL_MISMATCH'})
  row={'branch':branch,'path':str(folder),'http':s.get('http_status'),'request_model':req['model'],'response_model':resp.get('model'),
   'finish_reason':finish,'prompt_tokens':u.get('prompt_tokens'),'completion_tokens':u.get('completion_tokens'),'total_tokens':u.get('total_tokens'),
   'reasoning_tokens':(u.get('completion_tokens_details') or {}).get('reasoning_tokens'),'prompt_cache_hit_tokens':u.get('prompt_cache_hit_tokens'),
   'seconds':s.get('elapsed_seconds'),'started_utc':s.get('started_utc'),'response_id':s.get('response_id'),'system_fingerprint':resp.get('system_fingerprint'),
   'request_sha256':digest(folder/'request.json'),'response_sha256':digest(folder/'response.json') if resp else '',
   'output_cap_sent':any(k in req for k in ('max_tokens','max_output_tokens','max_completion_tokens'))}
  requests.append(row)
 for branch in sorted({r['branch'] for r in requests}):
  selected=[r for r in requests if r['branch']==branch]
  branch_usage[branch]={'attempts':len(selected),'http_200':sum(r['http']==200 for r in selected),'stop':sum(r['finish_reason']=='stop' for r in selected),
   **{k:sum(r[k] or 0 for r in selected) for k in ('prompt_tokens','completion_tokens','total_tokens','reasoning_tokens','prompt_cache_hit_tokens','seconds')}}
 usage={'branches':branch_usage,'total':{k:sum(r[k] or 0 for r in requests) for k in ('prompt_tokens','completion_tokens','total_tokens','reasoning_tokens','prompt_cache_hit_tokens','seconds')},
  'actual_model_requests':len(requests),'http_status_counts':dict(Counter(str(r['http']) for r in requests)),'finish_reason_counts':dict(Counter(str(r['finish_reason']) for r in requests)),
  'unknown_usage_requests':sum(r['total_tokens'] is None for r in requests),'automatic_retries':0,'model_list_gets_excluded':1,
  'latency_definition':'Sum of request durations; independent branches may overlap','recorded_utc':now()}
 if requests:
  usage['first_request_utc']=min(r['started_utc'] for r in requests if r['started_utc'])
  end=max(datetime.fromisoformat(r['started_utc'])+timedelta(seconds=r['seconds'] or 0) for r in requests if r['started_utc'])
  usage['last_response_utc']=end.isoformat();usage['wall_seconds_including_between_phase_gaps']=(end-datetime.fromisoformat(usage['first_request_utc'])).total_seconds()
  usage['response_system_fingerprints']=sorted({r['system_fingerprint'] for r in requests if r['system_fingerprint']})
 save(ROOT/'api_usage_summary.json',usage)
 if requests:
  with (ROOT/'request_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(requests[0]));w.writeheader();w.writerows(requests)
 protected=load(ROOT/'protected_hashes.json');changed=[p for p,h in protected.items() if not Path(p).exists() or digest(p)!=h]
 original=load(ROOT/'input_manifest.json');raw=load(ROOT/'fully/merged/output.json');norm=load(ROOT/'fully/merged/normalized_output.json')
 evidence=[]
 for r in original:
  p=r['paper_id'];ok=p in raw and raw[p]['source_documents']==load(r['cached_evidence_path'])
  evidence.append({'paper_id':p,'evidence_unchanged':ok,'evidence_sha256':digest(r['cached_evidence_path'])})
  q=ROOT/'fully/papers'/p/'extraction/request.json'
  if q.exists() and load(q)['messages']!=load(r['messages_path']):issues.append({'paper':p,'error':'EXTRACTION_MESSAGES_CHANGED'})
  if p in norm and (len(norm[p]['normalized_output'])!=len(json.loads(raw[p]['output'])) or [x['Result'] for x in norm[p]['normalized_output']]!=[x['Result'] for x in json.loads(raw[p]['output'])]):issues.append({'paper':p,'error':'NORMALIZATION_RESULTS_CHANGED'})
 verification={'utc':now(),'protected_file_count':len(protected),'protected_files_changed':changed,'parameter_or_input_issues':issues,
  'fully_extracted_papers':len(raw),'fully_normalized_papers':len(norm),'gold_covered':sum(r['gold_count_audit_only'] for r in original if r['paper_id'] in norm),
  'extraction_records':sum(len(json.loads(x['output'])) for x in raw.values()),'evidence_checks':evidence,
  'request_output_cap_count':sum(r['output_cap_sent'] for r in requests),'all_received_finish_stop':all(r['finish_reason']=='stop' for r in requests),
  'all_request_parameters_match':not any(x['error']=='PARAMETER_MISMATCH' for x in issues),'actual_response_models':sorted({r['response_model'] for r in requests if r['response_model']}),
  'audit_status':'PASS' if not changed and not issues and len(norm)==43 and all(e['evidence_unchanged'] for e in evidence) else 'INCOMPLETE_OR_FAILED',
  'meaning':'Request/input/source audit; branch completion and evaluation are separately recorded in report.'}
 save(ROOT/'verification.json',verification)
 print(json.dumps({'audit_status':verification['audit_status'],'fully_papers':len(norm),'requests':len(requests),'tokens':usage['total']['total_tokens'],'changed':len(changed),'issues':issues},ensure_ascii=False))
if __name__=='__main__':main()
