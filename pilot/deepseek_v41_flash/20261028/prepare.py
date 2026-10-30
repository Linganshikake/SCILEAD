"""Offline evidence/config freeze; no credentials or network."""
import sys,os,json,ast,csv,shutil,importlib.metadata
from pathlib import Path
sys.dont_write_bytecode=True
from transport import ROOT,MODEL,DOCUMENTED_VERSION,payload,save,load,digest,now
PROJECT=Path(r'D:\C++\SCILEAD');PILOT=PROJECT/'pilot';REPO=PROJECT/'emnlp2024-leaderboard-generation'
A0=PILOT/'gpt56_sol_fully/20261024_A0_preparation';A2=PILOT/'gpt56_sol_fully/20261024_A2_formal43'

def main():
 assert not (ROOT/'experiment_manifest.json').exists(),'Already prepared; do not overwrite'
 run=ROOT/'fully';run.mkdir(exist_ok=True)
 old=load(A2/'input_manifest.json');prompts=load(A0/'frozen_prompts.json');scope=load(A0/'evaluation_scope.json')
 assert digest(scope['gold_path'])==scope['gold_sha256'] and digest(scope['leaderboard_path'])==scope['leaderboard_sha256']
 gold=load(scope['gold_path']);candidates=load(A0/'candidate_sets.json')
 assert len(gold)==43 and sum(len(v['TDMs']) for v in gold.values())==295
 assert [len(ast.literal_eval(candidates[k])) for k in ('Task','Dataset','Metric')]==[23,71,26]
 assert all(v==load(REPO/'prompts.json')[k] for k,v in prompts.items())
 protected={}
 for f in REPO.iterdir():
  if f.is_file() and (f.suffix in ('.py','.json','.yml') or f.name=='requirements.txt'):protected[str(f)]=digest(f)
 for f in (Path(scope['gold_path']),Path(scope['leaderboard_path']),A0/'candidate_sets.json',A0/'frozen_prompts.json'):protected[str(f)]=digest(f)
 for d in [PILOT/'full43_uncapped',PILOT/'full43_cs',PILOT/'full43_partially',PILOT/'full43_cold_start',PILOT/'gpt56_sol_fully/20261024_A2_result_type_recovery',PILOT/'gpt56_sol_variants/20261024']:
  for pat in ['merged/*.json','report.md','verification.json','generation_config.json','*/stage*/normalized_output.json','*/stage*/leaderboard_normalized_output.json']:
   for f in d.glob(pat):
    if f.is_file():protected[str(f)]=digest(f)
 rows=[]
 os.environ['TIKTOKEN_CACHE_DIR']=str(PROJECT/'assets/tiktoken')
 import tiktoken
 enc=tiktoken.get_encoding('o200k_base')
 for i,row in enumerate(old,1):
  pid=row['paper_id'];src=Path(row['cached_evidence_path']);msg=Path(row['messages_path'])
  assert digest(src)==row['evidence_file_sha256'] and digest(msg)==row['messages_file_sha256']
  docs=load(src);messages=load(msg)
  expected=[{'role':'system','content':prompts['tdm-extraction-system-prompt'].format()},{'role':'user','content':prompts['query']+'\n\nRetrieved document contents:\n\n'+'\n\n'.join(d['content'] for d in docs)+'.\n\n Output json:\n\n'}]
  assert messages==expected and row['text_blocks']==4 and len(docs)==4+row['table_documents']
  destination=ROOT/'inputs'/pid;destination.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(src,destination/'source_documents.json');shutil.copyfile(msg,destination/'extraction_messages.json')
  protected[str(src)]=digest(src);protected[str(msg)]=digest(msg)
  estimated=3+sum(3+sum(len(enc.encode(v)) for v in m.values()) for m in messages)
  byte_bound=sum(len(m['content'].encode('utf8')) for m in messages)+4096
  assert byte_bound+65536<1000000,'CONTEXT_FIT_NEEDS_REVIEW'
  rows.append({'queue_order':i,'paper_id':pid,'gold_count_audit_only':len(gold[pid]['TDMs']),
   'cached_evidence_path':str(destination/'source_documents.json'),'historical_evidence_path':str(src),
   'evidence_file_sha256':digest(src),'messages_path':str(destination/'extraction_messages.json'),'messages_file_sha256':digest(msg),
   'source_version':row['source_version'],'text_blocks':4,'table_documents':row['table_documents'],'evidence_count':len(docs),
   'o200k_proxy_input_tokens':estimated,'proxy_is_not_deepseek_tokenizer':True,'input_utf8_byte_plus_framing_bound':byte_bound,
   'documented_context_length':1000000,'exact_input_tokens':'API usage after execution','status':'PENDING','reuse_prediction':False})
 save(ROOT/'input_manifest.json',rows)
 with (ROOT/'input_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for name in ('frozen_prompts.json','candidate_sets.json','evaluation_scope.json'):shutil.copyfile(A0/name,ROOT/name)
 save(ROOT/'protected_hashes.json',protected)
 cfg=payload([]);cfg.pop('messages');save(ROOT/'generation_config.json',cfg)
 save(ROOT/'experiment_manifest.json',{'created_utc':now(),'requested_model':'deepseek-V4.1-Flash','api_model':MODEL,'documented_serving_model':DOCUMENTED_VERSION,
  'endpoint':'https://api.deepseek.com/chat/completions','scope':scope,'branches':['fully_llm','fully_cs','partially','cold_default','cold_0','cold_42'],
  'input_manifest':str(ROOT/'input_manifest.json'),'candidate_sets':str(ROOT/'candidate_sets.json'),'generation_config':cfg,
  'reasoning_rationale':'Official default high; medium is documented to map to high. No tuning runs.',
  'output_budget':'No client cap; official thinking/high server default 64K. Previous Sol requested 32768; this provider configuration difference is recorded.',
  'historical_source':str(A2),'original_source_root':str(REPO),'frozen_source_version':'b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25',
  'prediction_reuse':False,'evidence_reuse':True,'auto_retries':0,'credentials_stored':False,'normalization_cache':'Per-call checkpoint only; no repeated-field memoization',
  'versions':{k:importlib.metadata.version(k) for k in ('httpx','langchain','langchain-core','torch','transformers','sentence-transformers','numpy')},
  'request_estimate':'43 Extraction + output-dependent Fully/Partially/3xCold field calls; FullyCS=0 API calls',
  'format_policy':'Exact JSON array; unique four fields; T/D/M strings; approved numeric Result conversion only, raw immutable'})
 save(ROOT/'preparation_verification.json',{'status':'PASS','papers':43,'gold':295,'all_docs_match_frozen':True,'all_messages_match_official':True,
  'protected_files':len(protected),'max_proxy_input_tokens':max(r['o200k_proxy_input_tokens'] for r in rows),
  'max_utf8_plus_framing':max(r['input_utf8_byte_plus_framing_bound'] for r in rows),'model_calls':0})
 print(json.dumps(load(ROOT/'preparation_verification.json')))
if __name__=='__main__':main()
