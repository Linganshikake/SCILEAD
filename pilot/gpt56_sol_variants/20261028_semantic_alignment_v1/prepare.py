"""Prepare isolated Sol rerun; offline only. Historical artifacts are read-only."""
import difflib,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent/'20261024'
PILOT=ROOT.parents[1];REFERENCE=PILOT/'deepseek_v41_flash/20261028_semantic_alignment_v1'
REPO=PILOT.parent/'emnlp2024-leaderboard-generation'
BRANCHES=['partially','cold_default','cold_0','cold_42']
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def copy(a,b):
 b.parent.mkdir(parents=True,exist_ok=True);assert not b.exists(),str(b);shutil.copyfile(a,b)
def main():
 assert not (ROOT/'experiment_manifest.json').exists(),'Inspect existing run; never overwrite'
 assert read(BASE/'experiment_manifest.json')['status']=='COMPLETE'
 assert read(REPO/'prompts.json')==read(REFERENCE/'prompts_original.json')
 for n in ['prompts_original.json','prompts_semantic_v1.json','prompt_additions.json','prompt_diff.txt']:
  copy(REFERENCE/n,ROOT/n)
 for n in ['generation_config.json','input_manifest.json']:
  copy(BASE/n,ROOT/n)
 for n in ['inputs/output.json','masking/initial_labels.json','masking/partially_masked_leaderboards.json','references/cold_initial_labels.json']:
  copy(BASE/n,ROOT/n)
 conf=read(BASE/'partially/config.json')
 copy(Path(conf['gold_path']),ROOT/'inputs/gold.json');copy(Path(conf['leaderboards_path']),ROOT/'inputs/leaderboards.json')
 changes=[
  ("TOP=Path(__file__).resolve().parent","TOP=Path(__file__).resolve().parent\nPROMPT_PATH=TOP/'prompts_semantic_v1.json'\nfrom runtime_policy import configure_paths\nconfigure_paths()"),
  ("origin=PILOT/('full43_cold_start' if cold else 'full43_partially')/'engine.py'","origin=(TOP/'cold_observer.py') if cold else PILOT/'full43_partially/engine.py'"),
  ("read(REPO/'prompts.json')","read(PROMPT_PATH)"),
  ("prompt_file=str(REPO/'prompts.json')","prompt_file=str(PROMPT_PATH)")]
 code=(BASE/'variant_runtime.py').read_text(encoding='utf8');exact=[]
 for before,after in changes:
  count=code.count(before);assert count>0,before;exact.append(dict(before=before,after=after,count=count));code=code.replace(before,after)
 (ROOT/'variant_runtime.py').write_text(code,encoding='utf8')
 observer_source=PILOT/'full43_cold_start/engine.py'
 observer=observer_source.read_text(encoding='utf8').split('class Transport:')[0].replace("read(REPO/'prompts.json')","read(PROMPT_PATH)")
 (ROOT/'cold_observer.py').write_text(observer,encoding='utf8')
 for n in ['runtime_policy.py','offline_entry.py','run_offline_tests.py']:
  s=(REFERENCE/'variants'/n).read_text(encoding='utf8')
  if n=='run_offline_tests.py':s=s.replace("str(v.TRANSPORT_PATH)","str(v.A1/'run_trial.py')").replace("v.sha(v.TRANSPORT_PATH)","v.sha(v.A1/'run_trial.py')")
  (ROOT/n).write_text(s,encoding='utf8')
 copy(BASE/'test_transport.py',ROOT/'test_transport.py')
 for n in ['test_original_partially.py','test_original_cold_start.py']:
  s=(BASE/n).read_text(encoding='utf8').replace("prompt_file=str(REPO/'prompts.json')","prompt_file=str(PROMPT_PATH)")
  s=s.replace("/'reproducibility'/'partially'","/'reproducibility'/('partially_'+str(time.time_ns()))").replace("/'reproducibility'/'cold_start'","/'reproducibility'/('cold_start_'+str(time.time_ns()))")
  (ROOT/n).write_text(s,encoding='utf8')
 protected={}
 def protect(p):protected[str(p)]=sha(p)
 for p in REPO.glob('*.py'):protect(p)
 protect(REPO/'prompts.json')
 transport=PILOT/'gpt56_sol_fully/20261024_A1_single_paper/run_trial.py'
 for p in [transport,observer_source,PILOT/'full43_partially/engine.py',BASE/'variant_runtime.py',BASE/'experiment_manifest.json',BASE/'verification.json',BASE/'report.md',BASE/'metrics_summary.json',BASE/'api_usage_summary.json',Path(conf['gold_path']),Path(conf['leaderboards_path'])]:protect(p)
 for b in BRANCHES:
  old=read(BASE/b/'config.json');new=dict(old)
  new.update(input_path=str(ROOT/'inputs/output.json'),gold_path=str(ROOT/'inputs/gold.json'),leaderboards_path=str(ROOT/'inputs/leaderboards.json'),experiment_type='PROMPT_SEMANTIC_ALIGNMENT_V1',prompt_path=str(ROOT/'prompts_semantic_v1.json'))
  save(ROOT/b/'config.json',new);copy(BASE/b/'official_config.json',ROOT/b/'official_config.json')
  save(ROOT/b/'paper_order.json',old['paper_order'])
  for stage in ['stage1','stage2']:(ROOT/b/stage).mkdir(exist_ok=True)
  for rel in ['config.json','official_config.json','stage1/normalized_output.json','stage2/leaderboard_normalized_output.json','stage1/summary.json','stage2/summary.json']:
   protect(BASE/b/rel)
 for base in [BASE,ROOT]:
  for rel in ['inputs/output.json','generation_config.json','input_manifest.json','masking/initial_labels.json','masking/partially_masked_leaderboards.json','references/cold_initial_labels.json']:protect(base/rel)
 for p in [ROOT/'variant_runtime.py',ROOT/'cold_observer.py',ROOT/'runtime_policy.py',ROOT/'prompts_semantic_v1.json',ROOT/'prompt_additions.json',ROOT/'inputs/gold.json',ROOT/'inputs/leaderboards.json',REFERENCE/'prompts_semantic_v1.json',REFERENCE/'prompt_additions.json']:protect(p)
 for b in BRANCHES:
  for n in ['config.json','official_config.json','paper_order.json']:protect(ROOT/b/n)
 save(ROOT/'protected_hashes.json',protected);save(ROOT/'critical_paths.json',list(protected))
 save(ROOT/'adapter_changes.json',{'source':str(BASE/'variant_runtime.py'),'source_sha256':sha(BASE/'variant_runtime.py'),'exact_replacements':exact,'transport_path':str(transport),'transport_sha256':sha(transport),'cold_observer_source':str(observer_source),'cold_observer_source_sha256':sha(observer_source),'observer_change':'prefix before class Transport; only Prompt validation binding replaced'})
 raw=read(ROOT/'inputs/output.json');n=sum(len(json.loads(x['output'])) for x in raw.values());assert len(raw)==43 and n==335
 save(ROOT/'experiment_manifest.json',{'status':'PREPARED','created_utc':datetime.now(timezone.utc).isoformat(),'baseline':str(BASE),'prompt_source':str(REFERENCE),'experiment_type':'PROMPT_SEMANTIC_ALIGNMENT_V1','model':'gpt-5.6-sol','generation':read(ROOT/'generation_config.json'),'papers':43,'prediction_records':n,'gold_records':295,'gold_boards':27,'branches':BRANCHES,'new_extraction_requests':0,'prompt_sha256':sha(ROOT/'prompts_semantic_v1.json'),'raw_extraction_sha256':sha(ROOT/'inputs/output.json'),'same_prompt_as_deepseek':True,'method_changes':'Two appended system Prompt requirements only','automatic_retries':0,'baseline_successful_requests':3048,'request_estimate':'About 3000, depends on new responses and dynamic candidate sets','max_method_positions':5360,'protected_file_count':len(protected)})
 print(json.dumps({'status':'PREPARED','papers':43,'predictions':n,'protected_files':len(protected)}))
if __name__=='__main__':main()
