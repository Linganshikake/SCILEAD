"""Evaluate only durably completed stages; preserve existing successful evaluations."""
import sys,subprocess,json
from pathlib import Path
from transport import ROOT,load,digest,save,now

def main():
 output=[]
 raw=ROOT/'fully/merged/output.json';analysis=ROOT/'analysis'
 for branch in ('partially','cold_default','cold_0','cold_42'):
  for stage,name in (('stage1','normalized_output.json'),('stage2','leaderboard_normalized_output.json')):
   run=ROOT/'variants'/branch/stage;summary=run/'summary.json';target=analysis/'evaluations'/(branch+'_'+stage)
   if not summary.exists() or load(summary).get('status')!='COMPLETE':
    output.append({'case':branch+'_'+stage,'status':'WAITING'});continue
   source=run/name;meta=load(summary)
   assert digest(source)==meta['output_sha256'],'COMPLETED_NORMALIZATION_HASH_CHANGED'
   if (target/'status.json').exists():
    previous=load(target/'status.json')
    output.append({'case':branch+'_'+stage,'status':previous['status'],'reused_evaluation':True});continue
   assert not target.exists(),'Inspect unfinished evaluator output; never overwrite'
   p=subprocess.run([sys.executable,'-B','-X','utf8',str(analysis/'evaluate_offline.py'),'--raw',str(raw),'--normalized',str(source),'--out',str(target)],capture_output=True,text=True,encoding='utf8')
   if p.returncode!=0:
    output.append({'case':branch+'_'+stage,'status':'EVALUATION_ERROR','exit_code':p.returncode,'error':p.stderr[-800:]})
   else:output.append({'case':branch+'_'+stage,'status':load(target/'status.json')['status']})
 save(ROOT/'evaluation_progress.json',{'utc':now(),'cases':output,'new_model_calls':0})
 print(json.dumps(output,ensure_ascii=False))
if __name__=='__main__':main()
