"""Offline before/after event comparison; no new predictions or semantic edits."""
import collections,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent/'20261028'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 summaries={};examples=[];raw=read(ROOT/'variants/inputs/output.json');gold=read(ROOT/'variants/inputs/gold.json')
 for b in ['partially','cold_default','cold_0','cold_42']:
  for stage in ['stage1','stage2']:
   d=ROOT/'variants'/b/stage;old=BASE/'variants'/b/stage
   assert read(d/'summary.json')['status']=='COMPLETE'
   olde={ (e['paper'],e['record'],e.get('field','TDM')):e for e in map(read,sorted((old/'events').glob('*.json'))) }
   newe=[read(p) for p in sorted((d/'events').glob('*.json'))]
   changes=[]
   for e in newe:
    k=(e['paper'],e['record'],e.get('field','TDM'));o=olde[k]
    if e['normalized']!=o['normalized']:
     changes.append({'paper':k[0],'record':k[1],'field':k[2],'before':o['normalized'],'after':e['normalized'],'before_branch':o['branch'],'after_branch':e['branch']})
   summary={'before_events':dict(collections.Counter(e['branch'] for e in olde.values())),
            'after_events':dict(collections.Counter(e['branch'] for e in newe)),
            'changed_event_count':len(changes),'changes':changes}
   summaries[b+'_'+stage]=summary
   chosen=[]
   if stage=='stage2':
    chosen=[e for e in newe if e['paper']=='2020.findings-emnlp.378.pdf' and e['record'] in [1,2,3]]
   else:
    chosen=[e for e in newe if (e['paper']=='1811.09242.pdf' and e.get('original')=='Arnet') or
            (e['paper']=='C18-1139.pdf' and e.get('field')=='Dataset' and e['record']==2)]
   for e in chosen:
    k=(e['paper'],e['record'],e.get('field','TDM'));o=olde[k]
    ex={'branch':b,'stage':stage,'paper':k[0],'record':k[1],'field':k[2],
        'raw_extraction':json.loads(raw[k[0]]['output'])[k[1]-1],
        'baseline_event':o,'variant_event':e,'gold_offline_analysis_only':gold[k[0]]['TDMs']}
    for label,event,directory in [('baseline',o,old),('variant',e,d)]:
     if 'call' in event:
      p=directory/'api_calls'/f"{event['call']:04d}"/'response.json'
      response=read(p)
      ex[label+'_response']={'path':str(p),'sha256':sha(p),'content':response['choices'][0]['message']['content'],
                           'provider_reasoning_content':response['choices'][0]['message'].get('reasoning_content')}
    examples.append(ex)
 save(ROOT/'inspection/alignment_events_comparison.json',summaries)
 save(ROOT/'inspection/examples_before_after.json',examples)
 print(json.dumps({'cases':len(summaries),'examples':len(examples),'changed_events':{k:v['changed_event_count'] for k,v in summaries.items()}}))
if __name__=='__main__':main()
