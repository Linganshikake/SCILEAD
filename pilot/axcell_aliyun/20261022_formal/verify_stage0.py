"""Final offline integrity gate; never starts a remote stage or reads credentials."""
from pathlib import Path
import csv,hashlib,json
P=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
required=['input_manifest.csv','experiment_manifest.json','environment_preflight.md','resource_preflight.md','scope_and_gold_audit.md']
assert all((P/n).is_file() and (P/n).stat().st_size for n in required)
rows=list(csv.DictReader((P/'input_manifest.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==43 and len({x['paper_id'] for x in rows})==43
ready=[x for x in rows if x['input_eligible']=='True']
assert len(ready)==39 and sum(int(x['gold_tdmr_count']) for x in ready)==283
assert sum(int(x['gold_tdmr_count']) for x in rows)==295
assert all(x['author_36_membership']=='UNVERIFIED' and x['formal_evaluation_allowed']=='False' for x in rows)
assert all(x['file_integrity_verified']=='True' and x['hash_match']=='True' for x in ready)
assert all(x['remote_status']=='MISSING_SOURCE_NOT_QUEUED' for x in rows if x['input_eligible']=='False')
manifest=read(P/'experiment_manifest.json');gate=read(P/'stage_gate.json');remote=read(P/'remote_preflight.json')
assert manifest['input_manifest']['sha256']==sha(P/'input_manifest.csv')
assert manifest['status']==gate['state']=='P0_AWAITING_USER_CONFIRMATION'
assert all(gate[x] is False for x in ['phase1_authorized','batch_parse_authorized','batch_extraction_authorized','paid_api_authorized'])
assert manifest['time']['experiment_start_utc'] is None and manifest['time']['new_api_calls']==0
assert remote['read_only'] and remote['containers_started']==remote['model_loads']==remote['api_calls']==0
assert remote['original_assets_match'] and remote['single_paper_run_unchanged'] and remote['single_paper_script_and_parsed_match']
assert remote['pip_check']['exit_code']==0 and not remote['package_diff_from_single_paper']
checks=[]
for e in read(P/'protected_inputs_before.json'):
 p=Path(e['path']);match=p.is_file() and p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
 checks.append({'path':str(p),'unchanged':match})
assert all(x['unchanged'] for x in checks)
for x in read(P/'comparison_input_index.json'):assert sha(Path(x['path']))==x['sha256']
inspection=read(P/'single_paper_error_baseline.json')
assert inspection['records'][0]['source_value']=='91.85'
assert inspection['records'][0]['first_two_rows'][1][2]=='Recall'
assert inspection['records'][1]['source_value']=='4,696'
assert inspection['records'][1]['source_row'][0]=='Test set size (# entities)'
plan=P/'stage0_plan.md';plan.write_text(plan.read_text(encoding='utf-8').replace('- [ ]','- [x]')+'\nPhase 0 completed. Evidence gates passed; scope author-36 remains UNVERIFIED. STOP AT P0. No P1/batch/model/API authorization inferred.\n',encoding='utf-8')
result={'status':'P0_AUDIT_COMPLETE_AWAITING_CONFIRMATION','stage':0,'required_files_complete':True,'manifest_rows':43,'eligible_inputs':39,'eligible_gold':283,'author36_verified':False,'official_live_metadata_requests':'4 ReadTimeout; no inference of publication absence','protected_local_files_checked':len(checks),'all_protected_local_files_unchanged':True,'protected_local_checks':checks,'remote_original_assets_match':True,'remote_single_run_unchanged':True,'no_system_or_dependency_change':True,'phase1_started':False,'batch_started':False,'model_generations':0,'paid_api_calls':0,'final_p0_review':'Offline schema/count/hash checks; no runtime or score claims beyond measured phase0 evidence'}
(P/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
outputs=[]
for p in sorted(P.rglob('*')):
 if p.is_file() and p.name!='stage0_delivery_manifest.json' and '__pycache__' not in p.parts:
  assert not p.name.endswith('.env')
  outputs.append({'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':sha(p)})
(P/'stage0_delivery_manifest.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='protected_local_checks'}))
print('DELIVERY_FILES',len(outputs))
