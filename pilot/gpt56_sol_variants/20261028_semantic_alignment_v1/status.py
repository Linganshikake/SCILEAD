import json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf8'))
result={};states=[]
for b in ['partially','cold_default','cold_0','cold_42']:
 result[b]={}
 for stage in ['stage1','stage2']:
  d=ROOT/b/stage;p=d/'summary.json'
  fs=list((d/'api_calls').glob('*/state.json'));attempts=fs+list((d/'api_calls').glob('*/retry_*/state.json'));s=[load(f) for f in attempts];states.extend(s)
  result[b][stage]={'status':load(p)['status'] if p.exists() else ('RUNNING' if fs else 'PENDING'),'logical_calls':len(fs),'attempts':len(s),'http200':sum(x.get('http_status')==200 for x in s),'accepted_calls':sum((f.parent/'accepted.json').exists() for f in fs)}
  if p.exists() and load(p)['status']!='COMPLETE':result[b][stage]['failure']=load(p)
result['api']={'attempts':len(states),'http':dict(collections.Counter(str(x.get('http_status')) for x in states)),'tokens':sum((x.get('usage') or {}).get('total_tokens',0) for x in states)}
print(json.dumps(result,ensure_ascii=False))
