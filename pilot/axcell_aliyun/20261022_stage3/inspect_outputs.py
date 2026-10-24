from pathlib import Path
import json,csv
B=Path('/root/scilead/axcell/runs/20261022_stage3')
out=[]
for p in (B/'papers').glob('*/state.json'):
 s=json.loads(p.read_text())
 if s['status'] not in ['EXTRACTION_COMPLETE','VALID_EMPTY']:continue
 run=p.parent;raw=json.loads((run/'raw_outputs/records.json').read_text());prov=json.loads((run/'raw_outputs/provenance.json').read_text())
 rows=[]
 for r,v in zip(raw,prov):
  ext=v['cell_ext_id'];source,table,coords=ext.split('/')
  inp=run/'inputs'/source/table
  if s.get('reused'):inp=Path('/root/scilead/axcell/data/papers')/source/table
  data=list(csv.reader(inp.open())) if inp.exists() else []
  rowidx,colidx=map(int,coords.split('.'))
  rows.append({'prediction':r,'source':ext,'table_first_rows':data[:3],'raw_source_row':data[rowidx] if rowidx<len(data) else None})
 out.append({'paper_id':run.name,'record_count':len(raw),'records':rows})
print(json.dumps(out))
