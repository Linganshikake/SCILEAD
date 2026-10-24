from pathlib import Path
import json,collections
B=Path('/root/scilead/axcell/runs/20261022_stage3_resume');out=[]
for path in (B/'papers').glob('*/state.json'):
 s=json.loads(path.read_text())
 if s['status']!='VALID_EMPTY':continue
 events=json.loads((path.parent/'raw_outputs/pipeline_events.json').read_text())
 out.append({'paper_id':path.parent.name,'seconds':s.get('seconds'),
 'type_counts':dict(collections.Counter(t['prediction'] for e in events for t in e.get('tables',[]))),
 'filters':[{'step':e['step'],'proposals':e.get('proposal_count'),'kept':len(e['kept_ids']) if 'kept_ids' in e else None,'removal_reason_counts':dict(collections.Counter(str(x) for x in e.get('removed_reasons',{}).values()))} for e in events if 'proposal_count' in e]})
print(json.dumps(out))
