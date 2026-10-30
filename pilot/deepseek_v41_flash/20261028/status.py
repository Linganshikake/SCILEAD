"""Safe local progress only; excludes offline test requests."""
import json
from pathlib import Path
from collections import Counter
from transport import ROOT,load

def status():
 out={};requests=[]
 p=ROOT/'fully/checkpoint.json'
 if p.exists():
  c=load(p);out['fully']={'state':c['state'],'papers_complete':sum(x['normalization']=='COMPLETE' for x in c['papers'].values()),'predictions':sum(x['records'] for x in c['papers'].values()),'stop':c.get('stop_reason')}
  requests.extend((ROOT/'fully/papers').glob('*/**/state.json'))
 for branch in ('partially','cold_default','cold_0','cold_42'):
  b=ROOT/'variants'/branch;out[branch]={}
  for stage in ('stage1','stage2'):
   p=b/stage/'summary.json';d=b/stage/'api_calls'
   sts=[load(s) for s in d.glob('*/state.json')];requests.extend(d.glob('*/state.json'))
   out[branch][stage]={'status':load(p).get('status') if p.exists() else ('RUNNING' if sts else 'NOT_STARTED'),'calls':len(sts),'received':sum(s.get('http_status')==200 for s in sts)}
 states=[load(p) for p in requests];out['api']={'attempts':len(states),'http':dict(Counter(str(s.get('http_status')) for s in states)),'total_tokens_reported':sum((s.get('usage') or {}).get('total_tokens',0) for s in states)}
 return out
if __name__=='__main__':print(json.dumps(status(),ensure_ascii=False))
