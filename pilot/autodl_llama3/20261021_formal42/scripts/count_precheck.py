from pathlib import Path
import json,collections
ROOT=Path('/root/autodl-tmp/scilead');R=ROOT/'runs/llama3/20261021_formal42'
raw=json.loads((R/'extraction/prepared_output.json').read_text());gold=json.loads((ROOT/'data/gold/tdm_annotations.json').read_text())
labels={k:{x[k] for p in gold.values() for x in p['TDMs']} for k in ['Task','Dataset','Metric']};fields=collections.Counter();papers={}
for pid,entry in raw.items():
 rows=json.loads(entry['output']);n=0
 for row in rows:
  for k in labels:
   if row[k] not in labels[k]:fields[k]+=1;n+=1
 papers[pid]={'extraction_records':len(rows),'expected_fully_llm_calls':n}
out={'valid_papers':len(raw),'records':sum(x['extraction_records'] for x in papers.values()),'candidate_counts':{k:len(v) for k,v in labels.items()},'expected_fully_llm_calls':sum(fields.values()),'by_field':dict(fields),'per_paper':papers,'no_inference':True}
(R/'config/normalization_call_precheck.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='per_paper'}))
