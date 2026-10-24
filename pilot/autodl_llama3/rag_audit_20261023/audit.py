"""Offline read-only audit; writes only beside this script. No project imports."""
import ast, csv, hashlib, io, json, pickle, subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(r'D:\C++\SCILEAD'); P=ROOT/'pilot'; OUT=Path(__file__).resolve().parent
SETUP=P/'autodl_setup/20261021'; STAGE=SETUP/'stage'
FORM=P/'autodl_llama3/20261021_formal42'; FOLLOW=P/'autodl_llama3/20261021_format_followup'
OFFICIAL=ROOT/'emnlp2024-leaderboard-generation'; ARCHIVE=Path(r'D:\C++\SCILEAD-publish')
PIN='8bf74b0a830feb7035c6166dce3394dc344ae532'; ARCHPIN='b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25'
before={}; missing=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def rb(p):
    p=Path(p); b=p.read_bytes(); before.setdefault(str(p),sha(b)); return b
def read(p):return json.loads(rb(p).decode('utf-8-sig'))
def txt(p):return rb(p).decode('utf-8-sig')
def canon(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def dump(name,d): (OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def csvout(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def git(repo,*args):return subprocess.check_output(['git','-c','safe.directory='+repo.as_posix(),'-C',str(repo),*args])

class InertDocument:
    def __setstate__(self,state):self.__dict__.update(state['__dict__'])
class Restricted(pickle.Unpickler):
    def find_class(self,module,name):
        if (module,name)==('langchain_core.documents.base','Document'):return InertDocument
        raise ValueError('Unapproved pickle class: '+module+'.'+name)
def unpickle(p):
    raw=Restricted(io.BytesIO(rb(p))).load()
    return {pid:[{'content':d.page_content,'metadata':d.metadata} for d in docs] for pid,docs in raw.items()}
def export_docs(ds):
    # The first pilot's diagnostic JSON calls the same content field 'text'.
    return [{'content':d['content'] if 'content' in d else d['text'],'metadata':d['metadata']} for d in ds]

# Snapshot the official/adapter/source versions and compare actual archival objects.
expected=read(FORM/'config/remote_expected_hashes.json'); transfer=read(SETUP/'transfer_manifest.json')
versions=[]
for rel,expected_sha in expected.items():
    path=STAGE/rel; b=rb(path)
    row={'relative_path':rel,'local_snapshot':str(path),'actual_sha256':sha(b),'formal_expected_sha256':expected_sha,'formal_hash_matches':sha(b)==expected_sha}
    if rel.startswith('source/'):
        name=rel.removeprefix('source/')
        upstream=git(OFFICIAL,'show',PIN+':'+name)
        archived=git(ARCHIVE,'show',ARCHPIN+':emnlp2024-leaderboard-generation/'+name)
        local=rb(OFFICIAL/name)
        row.update(upstream_commit=PIN,archive_commit=ARCHPIN,upstream_blob_sha256=sha(upstream),archive_blob_sha256=sha(archived),upstream_equal=b==upstream,archive_equal_lf=b.replace(b'\r\n',b'\n')==archived.replace(b'\r\n',b'\n'),working_tree_equal_lf=local.replace(b'\r\n',b'\n')==upstream.replace(b'\r\n',b'\n'))
    versions.append(row)

fm=read(FORM/'experiment_manifest.json'); fidx={x['paper_id']:x for x in fm['papers'] if x['paper_id'] in fm['scope']['eligible_ids']}
base=read(P/'full43_uncapped/manifest.json'); merged=read(P/'full43_uncapped/merged/output.json')
index=read(STAGE/'data/paper_index.json'); idx={x['paper_id']:x for x in index}
audits=list(csv.DictReader(io.StringIO(txt(SETUP/'input_length_audit.csv'))))
aud={x['paper_id']:x for x in audits if x['model_type']=='llama-3-instruct-70b'}
preflight=read(FORM/'preflight.json'); preaud={x['paper_id']:x for x in preflight['audit']}
recounts=read(OUT/'tokenizer_recount.json')
prompts=read(STAGE/'source/prompts.json')
# Extract only the literal llama3 template expression from the frozen AST, not imports/code execution.
tree=ast.parse(txt(STAGE/'source/prompting.py'))
branch=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and any(isinstance(c,ast.Constant) and c.value=='llama-3-instruct-70b' for c in n.test.comparators))
expr=next(n.value for n in branch.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='initial_template' for t in n.targets))
def literal_expr(n):
    if isinstance(n,ast.Constant) and isinstance(n.value,str):return n.value
    if isinstance(n,ast.Name) and n.id=='system_prompt':return prompts['tdm-extraction-system-prompt']
    if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Add):return literal_expr(n.left)+literal_expr(n.right)
    raise ValueError('Unexpected template AST')
template=literal_expr(expr)
trace=[]; lengths=[]; failures=[]
for paper in base['papers']:
    pid=paper['id']; src=STAGE/idx[pid]['evidence_file']; docs=read(src)[pid]
    pre=Path(paper['source_preprocess_dir']); pkl=pre/'processed_docs.pkl'
    saved=unpickle(pkl)[pid]
    hist=export_docs(read(pre/'retrieval-evidence.json')[pid])
    chunks=export_docs(read(pre/'text-chunks.json'))
    tablep=pre/'table-documents.json'
    if not tablep.exists():tablep=pre/'official-table-documents.json'
    tables=read(tablep)
    if isinstance(tables,dict):tables=tables.get(pid,tables)
    tables=export_docs(tables)
    summaryp=pre/'summary.json'
    if not summaryp.exists():summaryp=pre/'pilot-summary.json'
    summary=read(summaryp); config=read(pre/'config.json')
    logp=pre/'run.log'; log=None
    if logp.exists(): log=txt(logp)
    startedp=pre/'started.json'; started=read(startedp) if startedp.exists() else None
    prompt=template.format(question=prompts['query'],context='\n\n'.join(d['content'] for d in docs))
    counts=Counter(d['metadata'].get('type') for d in docs)
    textdocs=[d for d in docs if d['metadata'].get('type')=='Text']; tabledocs=[d for d in docs if d['metadata'].get('type')=='Table']
    checks={'staged_equals_gpt_source_documents':docs==merged[pid]['source_documents'],
      'staged_equals_historical_pickle':docs==saved,'staged_equals_retrieval_export':docs==hist,
      'pickle_hash_matches_frozen_manifest':sha(rb(pkl))==paper['evidence_sha256'],
      'canonical_hash_matches_transfer_index':canon(docs)==idx[pid]['evidence_canonical_sha256'],
      'all_tables_in_original_order':tabledocs==tables,
      'selected_texts_are_original_chunks':all(d in chunks for d in textdocs),
      'prompt_hash_matches_length_audit':sha(prompt.encode())==aud[pid]['prompt_sha256'],
      'prompt_hash_matches_formal_preflight':sha(prompt.encode())==preaud[pid]['prompt_sha256'],
      'query_matches_preprocessing':config.get('query')==prompts['query'],
      'offline_tokenizer_recount_equals_audit':recounts['papers'][pid]['before_author_pad']==int(aud[pid]['input_tokens'])}
    order=[{'index':i,'type':d['metadata'].get('type'),'metadata':d['metadata'],'characters':len(d['content']),'content_sha256':sha(d['content'].encode()),'original_text_chunk_indices':[j for j,c in enumerate(chunks) if c==d] if d['metadata'].get('type')=='Text' else [],'original_table_indices':[j for j,c in enumerate(tables) if c==d] if d['metadata'].get('type')=='Table' else []} for i,d in enumerate(docs)]
    row={'paper_id':pid,'classification':'REUSED_PREPROCESSED_RAG_EVIDENCE','formal_generated':pid in fidx,'staged_evidence_file':str(src),'historical_preprocess_dir':str(pre),'historical_pickle':str(pkl),'historical_pickle_sha256':sha(rb(pkl)),'gpt_source_file':str(P/'full43_uncapped/merged/output.json'),'evidence_canonical_sha256':canon(docs),'preprocess_started_record':started,'preprocess_summary':summary,'historical_log':str(logp) if log is not None else None,'all_text_chunks':len(chunks),'selected_text_chunks':len(textdocs),'all_table_documents':len(tables),'selected_table_documents':len(tabledocs),'text_characters':sum(len(d['content']) for d in textdocs),'table_characters':sum(len(d['content']) for d in tabledocs),'prompt_characters':len(prompt),'query':prompts['query'],'prompt_sha256':sha(prompt.encode()),'input_tokens_recorded':int(aud[pid]['input_tokens']),'evidence_order':order,'checks':checks}
    actual=None
    if pid in fidx:
        ext=FORM/fidx[pid]['raw_output_path']; output=read(ext)[pid]; call=ext.parent/'calls/000000'
        req=read(call/'request.json'); comp=read(call/'complete.json'); cfg=read(ext.parent/'config.json'); pipeline=read(call/'pipeline_raw_response.json'); response=txt(call/'response.txt')
        pipeline_text=pipeline
        while isinstance(pipeline_text,list):
            assert len(pipeline_text)==1
            pipeline_text=pipeline_text[0]
        actual=comp['actual_generation']; checks.update(actual_prompt_exact_match=req['prompt']==prompt,actual_prompt_hash_matches=req['prompt_sha256']==sha(prompt.encode()),actual_output_source_documents_match=output['source_documents']==docs,actual_tokens_match_audit=actual['input_tokens']==int(aud[pid]['input_tokens']),raw_pipeline_is_prompt_plus_response=pipeline_text['generated_text']==prompt+response,original_response_preserved=output['output']==response,actual_system_prompt_matches=cfg['system_prompt']==prompts['tdm-extraction-system-prompt'],actual_query_matches=cfg['query_prompt']==prompts['query'],preprocessed_flag_true=cfg['is_preprocessed_doc'] is True)
        checks['offline_tokenizer_after_author_pad_equals_actual']=recounts['papers'][pid]['after_author_pad']==actual['input_tokens']
        row.update(request_path=str(call/'request.json'),complete_path=str(call/'complete.json'),actual_is_preprocessed_doc=cfg.get('is_preprocessed_doc'),actual_processed_docs_path=cfg.get('processed_docs_path'),actual_evidence_loader='/root/autodl-tmp/scilead/data/evidence/'+pid+'.json',actual_generation=actual,reused_generation=fidx[pid]['reused_generation'])
        command=ext.parent.parent/'command.json'
        if command.exists():row['formal_command']=read(command)
    if actual and actual['input_tokens']!=int(aud[pid]['input_tokens']):
        tokencheck=read(OUT/'tokenizer_recount.json')['papers'][pid]
        checks['actual_token_difference_explained_by_author_pad_token']=tokencheck['before_author_pad']==int(aud[pid]['input_tokens']) and tokencheck['after_author_pad']==actual['input_tokens']
    for name,ok in checks.items():
        if name=='actual_tokens_match_audit' and checks.get('actual_token_difference_explained_by_author_pad_token'):continue
        if not ok:failures.append({'paper_id':pid,'check':name})
    trace.append(row)
    lengths.append({'paper_id':pid,'selected_text_chunks':len(textdocs),'original_text_chunks':len(chunks),'selected_tables':len(tabledocs),'evidence_count':len(docs),'text_characters':row['text_characters'],'table_characters':row['table_characters'],'prompt_sha256':row['prompt_sha256'],'audit_input_tokens':int(aud[pid]['input_tokens']),'actual_generation_input_tokens':actual['input_tokens'] if actual else '', 'context_limit':8192,'reserved_output_tokens':1024,'input_plus_budget':int(aud[pid]['input_tokens'])+1024,'formal_generated':actual is not None,'finish_reason':actual['finish_reason'] if actual else 'BLOCKED_BEFORE_GENERATION','request_path':row.get('request_path',''),'historical_preprocess_dir':str(pre)})

# Follow-up recovered formatting changes only; diagnostic generation gets a separate check.
v2=read(FOLLOW/'format_v2/extraction/prepared_output.json')
v2checks={pid:entry['source_documents']==merged[pid]['source_documents'] for pid,entry in v2.items()}
diagdir=FOLLOW/'token2048_diagnostic/extraction'; diag=read(diagdir/'output.json'); did=next(iter(diag)); dreq=read(diagdir/'calls/000000/request.json')
orig=next(x for x in trace if x['paper_id']==did)
follow={'v2_papers':len(v2),'v2_source_documents_equal_frozen':v2checks,'v2_verification':read(FOLLOW/'reports/verification.json'),'diagnostic_paper':did,'diagnostic_evidence_equal':diag[did]['source_documents']==merged[did]['source_documents'],'diagnostic_prompt_hash_equal':dreq['prompt_sha256']==orig['prompt_sha256'],'diagnostic_max_new_tokens':dreq['max_new_tokens'],'not_part_of_formal_v2':True}

additional=[SETUP/'scripts/prepare_bundle.py',P/'scripts/subset5_preprocess.py',SETUP/'references/scilead_emnlp_2024.txt',FORM/'remote_snapshot/scripts/remote_batch.py',FORM/'verification.json',FORM/'run_report.md',FORM/'generation_config.json',SETUP/'model_manifest.json',SETUP/'context_blockers.md',SETUP/'pipeline_exact_token_audit.json',FORM/'remote_snapshot/launch.json']
for path in additional:rb(path)
l2=P/'autodl_llama2/stage5_original_20261023/remote/single_paper/extraction'
l2data=read(l2/'output.json');l2comp=read(l2/'calls/000000/complete.json')
cross={'paper_id':'2020.emnlp-main.152.pdf','llama2_output':str(l2/'output.json'),'same_evidence_as_llama3':l2data['2020.emnlp-main.152.pdf']['source_documents']==merged['2020.emnlp-main.152.pdf']['source_documents'],'llama2_actual_generation':l2comp['actual_generation']}
remote_manifest=read(FORM/'remote_snapshot/artifact_manifest_remote.json');remote_checks=[]
for ent in remote_manifest:
    path=FORM/'remote_snapshot'/ent['path']
    if str(path) in before:remote_checks.append({'path':str(path),'matches_recorded_remote_sha256':before[str(path)]==ent['sha256']})
dump('source_traceability.json',{'audit_time':datetime.now(timezone.utc).isoformat(),'scope':'local archived execution evidence; no remote login','source_versions':versions,'official_commit':PIN,'archive_commit':ARCHPIN,'transfer_status':transfer['status'],'papers':trace,'format_followup':follow,'llama2_crosscheck':cross,'archived_remote_hash_checks':remote_checks,'failures':failures})
csvout('prompt_length_reconciliation.csv',lengths)
csvout('rag_execution_evidence.csv',[{'paper_id':x['paper_id'],'classification':x['classification'],'formal_generated':x['formal_generated'],'runtime_similarity_search':False,'runtime_chain':'RetrievalQA(stuff) + FrozenRetriever returns saved list' if x['formal_generated'] else 'NOT_GENERATED','query':x['query'],'all_text_chunks':x['all_text_chunks'],'selected_text_chunks':x['selected_text_chunks'],'all_tables':x['all_table_documents'],'selected_tables':x['selected_table_documents'],'source_documents_file':x['staged_evidence_file'],'historical_retrieval_export':str(Path(x['historical_preprocess_dir'])/'retrieval-evidence.json'),'request_file':x.get('request_path',''),'prompt_sha256':x['prompt_sha256'],'traceability_checks_reconciled':not any(f['paper_id']==x['paper_id'] for f in failures)} for x in trace])
changed=[p for p,h in before.items() if sha(Path(p).read_bytes())!=h]
verification={'status':'PASS' if not failures and not changed and all(v['formal_hash_matches'] for v in versions) else 'REVIEW','read_only_inputs_checked':len(before),'changed_inputs':changed,'source_hash_checks':versions,'traceability_failures':failures,'43_evidence_sets_equal_historical_pickle':sum(x['checks']['staged_equals_historical_pickle'] for x in trace),'42_actual_prompts_equal_reconstructed':sum(x['checks'].get('actual_prompt_exact_match',False) for x in trace),'42_pipeline_inputs_confirmed':sum(x['checks'].get('raw_pipeline_is_prompt_plus_response',False) for x in trace),'token_counts_recomputed_this_audit':True,'token_count_evidence':'tokenizer_recount.json: local tokenizers only, no models/imports from project; historical tokenizer audit + formal preflight + 42 actual generate input tensor lengths; exact prompt hashes recomputed','remote_live_access':False,'new_model_generations':0,'new_paid_api_calls':0,'credentials_read':False,'file_sha256_before_after':before}
dump('verification.json',verification)
verification.update(archived_remote_files_compared=len(remote_checks),archived_remote_hash_mismatches=[x for x in remote_checks if not x['matches_recorded_remote_sha256']],llama2_crosscheck=cross)
if verification['archived_remote_hash_mismatches']:verification['status']='REVIEW'
dump('verification.json',verification)
print(json.dumps({'status':verification['status'],'files':len(before),'failures':failures,'longest_eligible':max([x for x in lengths if x['formal_generated']],key=lambda x:x['audit_input_tokens']),'samples':[ {k:v for k,v in x.items() if k not in ('evidence_order','preprocess_summary','checks')} for x in trace if x['paper_id'] in ['1912.08777.pdf','1511.08308.pdf','2020.emnlp-main.152.pdf']]},ensure_ascii=False,indent=2))
