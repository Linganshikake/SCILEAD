"""Read-only progress monitor; never sends API requests or restarts workers."""
import argparse,collections,json,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def snapshot():
 rows={};states=[];accepted=0;terminal=0
 for branch in ['partially','cold_default','cold_0','cold_42']:
  rows[branch]={}
  for stage in ['stage1','stage2']:
   d=ROOT/branch/stage;summary=read(d/'summary.json') if (d/'summary.json').exists() else {}
   ss=[read(p) for p in (d/'api_calls').rglob('state.json')];states+=ss
   n=len(list((d/'api_calls').glob('*/accepted.json')));accepted+=n
   status=summary.get('status','RUNNING' if ss else 'PENDING')
   rows[branch][stage]={'status':status,'accepted':n,'attempts':len(ss)}
  if rows[branch]['stage2']['status']=='COMPLETE' or any(v['status'].startswith('PAUSED') for v in rows[branch].values()):terminal+=1
 return {'utc':datetime.now(timezone.utc).isoformat(),'branches':rows,'attempts':len(states),'accepted':accepted,
  'states':dict(collections.Counter(s['status'] for s in states)),
  'known_tokens':sum((s.get('usage') or {}).get('total_tokens',0) for s in states),'terminal_branches':terminal}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,default=3600);a=parser.parse_args();end=time.monotonic()+a.seconds
 while True:
  s=snapshot();print(json.dumps(s),flush=True)
  if s['terminal_branches']==4 or time.monotonic()>=end:break
  time.sleep(45)
