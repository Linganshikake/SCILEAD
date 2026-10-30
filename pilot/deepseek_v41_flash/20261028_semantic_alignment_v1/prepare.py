"""Prepare one isolated Prompt variant; no network, credentials or model loading."""
import difflib,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261028'
REPO=Path(r'D:\C++\SCILEAD\emnlp2024-leaderboard-generation')
V=ROOT/'variants'
BRANCHES=['partially','cold_default','cold_0','cold_42']
ADDITIONS={
'masked-normalization-system-prompt': '''\n\nSemantic matching requirements:
Match by meaning and entity identity, not by literal string equality. Recognize unambiguous abbreviations, acronyms, aliases, paraphrases, capitalization, punctuation and superficial spelling differences. Different wording alone is not a reason to reject a match. Compare the input against the supplied candidates before deciding that it is a new entity.
For task names, a more specific wording may match an existing standard task when both denote the same underlying task. Preserve meaningful differences in dataset identity, language, version, split and metric definition; do not merge distinct entities merely because their names are similar. Do not guess an ambiguous abbreviation or missing experimental condition.
If one candidate is a clear semantic match, output that candidate exactly as written in the item list. If the list is empty, no candidate matches, or the match remains ambiguous, output the original input entity exactly unchanged. Do not invent a new canonical name. Output only the selected item or unchanged input, without quotes, explanation or extra formatting.''',
'leaderboard-normalization-system-prompt': '''\n\nSemantic matching requirements:
Here, a tuple matches a listed tuple when its Task, Dataset and Metric denote the same underlying benchmark, even if their strings differ. This is semantic alignment, not an exact-string membership test. Compare all three fields jointly. Recognize unambiguous abbreviations, acronyms, aliases, paraphrases, capitalization, punctuation and superficial spelling differences, using the information in the input tuple and candidate tuples to disambiguate.
A more specific task wording may match a broader standard task label when they describe the same underlying benchmark and the Dataset and Metric remain compatible. Do not merge different dataset identities, languages, versions, splits or metric definitions. Missing details must not be guessed when multiple candidates remain plausible. Similar names alone do not establish equivalence.
If one listed tuple is a clear semantic match, return the entire listed tuple verbatim, with its exact spelling, punctuation and spacing. Never mix fields from different candidates. If no candidate matches or the match remains ambiguous, return the original input tuple verbatim. Output only that one tuple, without quotes, explanation, code fences or extra formatting.'''
}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def copy(a,b):
 b=Path(b);b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)
def main():
 assert not (ROOT/'experiment_manifest.json').exists(),'Already prepared; inspect existing manifest rather than overwrite'
 assert load(BASE/'verification.json')['completion_status']=='COMPLETE'
 before=load(REPO/'prompts.json');after=dict(before)
 for key,suffix in ADDITIONS.items():after[key]+=suffix
 save(ROOT/'prompt_additions.json',ADDITIONS);save(ROOT/'prompts_semantic_v1.json',after)
 copy(REPO/'prompts.json',ROOT/'prompts_original.json')
 (ROOT/'prompt_diff.txt').write_text(''.join(difflib.unified_diff(json.dumps(before,indent=2,ensure_ascii=False).splitlines(True),json.dumps(after,indent=2,ensure_ascii=False).splitlines(True),fromfile='original/prompts.json',tofile='semantic_v1/prompts.json')),encoding='utf-8')
 for n in ['transport.py','generation_config.json','evaluation_scope.json','input_manifest.json']:
  copy(BASE/n,ROOT/n)
 files=['runtime_policy.py','offline_entry.py','run_offline_tests.py','test_transport.py','test_original_partially.py','test_original_cold_start.py']
 for n in files:copy(BASE/'variants'/n,V/n)
 code=(BASE/'variants/variant_runtime.py').read_text(encoding='utf-8')
 code=code.replace("TRANSPORT_PATH=TOP.parent/'transport.py'","TRANSPORT_PATH=TOP.parent/'transport.py'\nPROMPT_PATH=TOP.parent/'prompts_semantic_v1.json'")
 code=code.replace("read(REPO/'prompts.json')","read(PROMPT_PATH)").replace("prompt_file=str(REPO/'prompts.json')","prompt_file=str(PROMPT_PATH)")
 code=code.replace("origin=PILOT/('full43_cold_start' if cold else 'full43_partially')/'engine.py'","origin=(ADAPTER_ROOT/'cold_observer.py') if cold else PILOT/'full43_partially'/'engine.py'")
 observer=(BASE.parent.parent/'full43_cold_start/engine.py').read_text(encoding='utf-8').split('class Transport:')[0].replace("read(REPO/'prompts.json')","read(PROMPT_PATH)")
 (V/'cold_observer.py').write_text(observer,encoding='utf-8')
 # Only the Prompt-file binding changes; original main and acceptance observer remain intact.
 (V/'variant_runtime.py').write_text(code,encoding='utf-8')
 for n in ['test_original_partially.py','test_original_cold_start.py']:
  p=V/n;p.write_text(p.read_text(encoding='utf-8').replace("prompt_file=str(REPO/'prompts.json')","prompt_file=str(PROMPT_PATH)"),encoding='utf-8')
 p=V/'run_offline_tests.py';s=p.read_text(encoding='utf-8').replace("('test_adapters', 'test_transport', 'test_original_partially',\n          'test_original_cold_start', 'test_frozen_protocol')","('test_prompt_variant', 'test_transport', 'test_original_partially',\n          'test_original_cold_start')");p.write_text(s,encoding='utf-8')
 p=V/'offline_entry.py';s=p.read_text(encoding='utf-8').replace("('test_adapters', 'test_transport', 'test_original_partially',\n                     'test_original_cold_start', 'test_frozen_protocol')","('test_prompt_variant', 'test_transport', 'test_original_partially',\n                     'test_original_cold_start')");p.write_text(s,encoding='utf-8')
 for name in ['inputs/output.json','inputs/gold.json','inputs/leaderboards.json','masking/initial_labels.json','masking/partially_masked_leaderboards.json','references/cold_initial_labels.json']:
  copy(BASE/'variants'/name,V/name)
 for b in BRANCHES:
  conf=load(BASE/'variants'/b/'config.json')
  for k in ['input_path','gold_path','leaderboards_path']:conf[k]=conf[k].replace(str(BASE/'variants'),str(V))
  conf['experiment_type']='PROMPT_SEMANTIC_ALIGNMENT_V1';conf['prompt_path']=str(ROOT/'prompts_semantic_v1.json')
  save(V/b/'config.json',conf)
  copy(BASE/'variants'/b/'official_config.json',V/b/'official_config.json')
  copy(BASE/'variants'/b/'paper_order.json',V/b/'paper_order.json')
  for stage in ['stage1','stage2']:(V/b/stage).mkdir(exist_ok=True)
 protected=load(BASE/'protected_hashes.json')
 for p in [BASE/'fully/merged/output.json', BASE/'fully/merged/normalized_output.json',BASE/'verification.json',BASE/'report.md',BASE/'results_summary.json',REPO/'prompts.json']:
  protected[str(p)]=sha(p)
 for b in BRANCHES:
  for rel in ['config.json','paper_order.json','stage1/normalized_output.json','stage2/leaderboard_normalized_output.json','stage1/summary.json','stage2/summary.json']:
   p=BASE/'variants'/b/rel;protected[str(p)]=sha(p)
 for p in [ROOT/'prompts_semantic_v1.json',ROOT/'prompt_additions.json',ROOT/'transport.py',ROOT/'generation_config.json',V/'variant_runtime.py',V/'cold_observer.py',V/'runtime_policy.py',*list((V/'inputs').glob('*.json')),*list((V/'masking').glob('*.json')),*list((V/'references').glob('*.json'))]:protected[str(p)]=sha(p)
 for b in BRANCHES:
  for n in ['config.json','paper_order.json','official_config.json']:
   p=V/b/n;protected[str(p)]=sha(p)
 save(V/'protected_hashes.json',protected);save(V/'critical_paths.json',list(protected))
 save(ROOT/'protected_hashes.json',protected)
 raw=load(V/'inputs/output.json');assert len(raw)==43 and sum(len(json.loads(x['output'])) for x in raw.values())==295
 save(ROOT/'experiment_manifest.json',{'status':'PREPARED','created_utc':datetime.now(timezone.utc).isoformat(),'experiment_type':'PROMPT_SEMANTIC_ALIGNMENT_V1','baseline':str(BASE),'model':'deepseek-flash','generation':load(ROOT/'generation_config.json'),'branches':BRANCHES,'papers':43,'gold_records':295,'prediction_records':295,'gold_leaderboards':27,'extraction_reused':True,'new_extraction_requests':0,'changed_prompt_keys':list(ADDITIONS),'prompt_sha256':sha(ROOT/'prompts_semantic_v1.json'),'original_prompt_sha256':sha(REPO/'prompts.json'),'raw_extraction_sha256':sha(V/'inputs/output.json'),'initial_labels_and_paper_orders':'byte-identical to baseline','stage1_dynamic_labels':'original algorithm; subsequent candidate membership may change with new model answers','normalization_acceptance':'unchanged official code','automatic_retries':0,'request_estimate_baseline':2339,'max_method_positions':4720,'protected_files':len(protected)})
 save(ROOT/'adapter_changes.json',{'source':str(BASE/'variants/variant_runtime.py'),'source_sha256':sha(BASE/'variants/variant_runtime.py'),'adapted_sha256':sha(V/'variant_runtime.py'),'changes':['Independent PROMPT_PATH constant','System Prompt validation reads PROMPT_PATH','Both official mains receive PROMPT_PATH'],'transport_byte_identical':sha(ROOT/'transport.py')==sha(BASE/'transport.py')})
 print(json.dumps({'status':'PREPARED','papers':43,'predictions':295,'changed_prompt_keys':list(ADDITIONS),'protected':len(protected)}))
if __name__=='__main__':main()
