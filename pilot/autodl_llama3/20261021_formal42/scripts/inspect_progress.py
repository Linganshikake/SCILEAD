from pathlib import Path
import json,datetime,subprocess,time
R=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_formal42')
s=json.loads((R/'batch_status.json').read_text());rows=s.get('papers',{})
done=[p for p,x in rows.items() if x.get('generation_status')=='COMPLETE'];valid=[p for p,x in rows.items() if x.get('parse_status')=='COMPLETE'];failed=[{'paper_id':p,'reason':x.get('reason'),'format':x.get('format_audit'),'generation':x.get('usage',{}).get('actual_generation')} for p,x in rows.items() if x.get('parse_status')=='FAILED']
info={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':s['status'],'complete_generations':len(done),'valid_papers':len(valid),'running_papers':[p for p,x in rows.items() if x.get('generation_status')=='RUNNING'],'failures':failed}
for f in ['partial_status.json','formal_remote_complete.json']:
 if (R/f).exists():info[f]=json.loads((R/f).read_text())
info['normalization_calls']={str(p.relative_to(R)):len(list(p.glob('*/complete.json'))) for p in (R/'normalization').rglob('calls')}
info['gpu']=subprocess.run(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout.strip()
info['own_processes']=subprocess.run(['ps','-eo','pid,etimes,args'],capture_output=True,text=True).stdout.splitlines()
info['own_processes']=[x for x in info['own_processes'] if str(R) in x or 'adapters/run_llama.py' in x]
for f in ['remote_batch.py.log','remote_followup.py.log']:
 p=R/f
 if p.exists() and p.stat().st_size:info[f+'_tail']=p.read_text(errors='replace')[-1500:]
info['failures']=[{'paper_id':x['paper_id'],'reason':x['reason'],'output_tokens':(x.get('generation') or {}).get('output_tokens')} for x in failed]
if s['status'] in ['EXTRACTION_RUNNING','FULLY_LLM_RUNNING']:
 info['own_process_count']=len(info.pop('own_processes'))
print(json.dumps(info))
