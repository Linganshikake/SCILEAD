"""A1 offline acceptance and A2 preparation. No credential access or API executor."""
import os,sys,socket,json,hashlib,csv,ast,runpy,io,contextlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

R=Path(__file__).resolve().parent
PROJECT=Path(r'D:\C++\SCILEAD')
A0=R.parent/'20261024_A0_preparation'
A1=R.parent/'20261024_A1_single_paper'
SOURCE=PROJECT/'emnlp2024-leaderboard-generation'
PAPER='2020.emnlp-main.152.pdf'
MODEL='gpt-5.6-sol'
ATTEMPTS=[]
def deny(*args,**kwargs):
    ATTEMPTS.append('blocked network attempt')
    raise RuntimeError('OFFLINE_ONLY_NETWORK_FORBIDDEN')
socket.socket.connect=deny
socket.socket.connect_ex=deny
socket.create_connection=deny
os.environ.update(TIKTOKEN_CACHE_DIR=str(PROJECT/'assets/tiktoken'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false',HF_HUB_DISABLE_TELEMETRY='1',PYTHONDONTWRITEBYTECODE='1')
sys.dont_write_bytecode=True
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(name,x):
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def md(name,x):(R/name).write_text(x,encoding='utf-8')
def csvsave(name,rows):
    with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

assert not (R/'verification.json').exists(),'Existing preparation must not be overwritten'
protected=read(A0/'read_source_hashes.json')
protected.update({str(A0/p):h for p,h in read(A0/'delivery_manifest.json').items()})
protected.update({str(p):sha(p) for p in A1.rglob('*') if p.is_file()})
assert all(Path(p).exists() and sha(Path(p))==h for p,h in protected.items()),'FROZEN_INPUT_HASH_MISMATCH'
assert all(sha(A1/p)==h for p,h in read(A1/'delivery_manifest.json').items()),'A1_DELIVERY_HASH_MISMATCH'
scope=read(A0/'evaluation_scope.json');gold_path=Path(scope['gold_path']);gold=read(gold_path)
assert sha(gold_path)==scope['gold_sha256']
assert len(gold)==43 and sum(len(v['TDMs']) for v in gold.values())==295
prompts=read(A0/'frozen_prompts.json');candidate_strings=read(A0/'candidate_sets.json')
candidates={k:ast.literal_eval(v) for k,v in candidate_strings.items()}
assert [len(candidates[k]) for k in ['Task','Dataset','Metric']]==[23,71,26]
for k in candidates:assert candidates[k]=={row[k] for p in gold.values() for row in p['TDMs']}

# Audit actual A1 responses and exact per-position normalization, no re-generation.
out=read(A1/'output.json')[PAPER];raw=json.loads(out['output'])
norm=read(A1/'normalization/normalized_output.json')[PAPER]
assert len(raw)==len(norm['normalized_output'])==6
assert out['source_documents']==norm['source_documents']==read(A0/'inputs'/PAPER/'source_documents.json')
folders=[p.parent for p in sorted((A1/'normalization/requests').glob('*/request.json'))]
trace=[];ix=0
for i,row in enumerate(raw):
    assert set(row)=={'Task','Dataset','Metric','Result'} and all(isinstance(v,str) for v in row.values())
    for k,v in row.items():
        folder=None
        if k=='Result' or v in candidates[k]:expected=str(v);mode='DIRECT'
        else:
            folder=folders[ix];ix+=1;req=read(folder/'request.json');resp=read(folder/'response.json')
            expected_messages=[{'role':'system','content':prompts['normalization-system-prompt']},{'role':'user','content':'\n\nItem list: '+candidate_strings[k]+'\n\nInput: '+v+'\n\nAnswer: '}]
            assert req['messages']==expected_messages
            answer=resp['choices'][0]['message']['content'];expected=answer if answer in candidates[k] else None;mode='LLM'
        assert norm['normalized_output'][i][k]==expected
        trace.append({'record_index':i,'field':k,'raw_value':v,'normalized_value':expected,'mode':mode,'request_directory':str(folder) if folder else ''})
assert ix==13==len(folders)
csvsave('A1_field_mapping_audit.csv',trace)
params=None
for folder in [A1/'extraction']+folders:
    req=read(folder/'request.json');res=read(folder/'response.json');state=read(folder/'state.json')
    assert state['http_status']==200 and res['model']==MODEL and res['choices'][0]['finish_reason']=='stop'
    current={k:v for k,v in req.items() if k!='messages'}
    if params is None:params=current
    assert current==params
assert params=={'model':MODEL,'reasoning_effort':'medium','max_completion_tokens':32768,'stream':False}

# Execute unmodified official CLI in this network-blocked process; normal utils imports.
evaluation=R/'A1_evaluation';evaluation.mkdir(exist_ok=True)
argv=[str(SOURCE/'tdm_eval.py'),'--gold_data_path',str(gold_path),'--normalized_tdm_output_path',str(A1/'normalization/normalized_output.json'),
      '--eval_results_path',str(evaluation/'eval_results.json'),'--eval_values_path',str(evaluation/'eval_values.json')]
save('A1_evaluation/invocation.json',{'argv':argv,'script_sha256':sha(SOURCE/'tdm_eval.py'),'unmodified_official_cli':True,'network_blocked':True,'gold_full_dataset_only_prediction_scope_one_paper':True})
sys.path.insert(0,str(SOURCE));sys.argv=argv
buf=io.StringIO()
with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):runpy.run_path(str(SOURCE/'tdm_eval.py'),run_name='__main__')
(evaluation/'official_eval.log').write_text(buf.getvalue(),encoding='utf-8')
ev=read(evaluation/'eval_results.json')
metrics={k:{'Precision':v['Precision'],'Recall':v['Recall']} for k,v in ev['Individual'].items()}
metrics['TDM']={'Precision':ev['Exact Match Precision wo Results'],'Recall':ev['Exact Match Recall wo Results']}
metrics['TDMR']={'Precision':ev['Exact Match Precision'],'Recall':ev['Exact Match Recall']}
for v in metrics.values():v['F1']=2*v['Precision']*v['Recall']/(v['Precision']+v['Recall']) if v['Precision']+v['Recall'] else 0
save('A1_evaluation/metrics_with_f1.json',{'metrics':metrics,'precision_recall':'Unmodified official tdm_eval.py','f1':'Additional 2PR/(P+R), not mean of per-paper F1'})
strict=[];used=set()
for gi,g in enumerate(gold[PAPER]['TDMs']):
    match=[i for i,p in enumerate(norm['normalized_output']) if i not in used and all(p[k]==g[k] for k in ['Task','Dataset','Metric']) and Decimal(p['Result'])==Decimal(str(g['Result']))]
    assert len(match)==1,'UNEXPECTED_GOLD_MAPPING'
    used.add(match[0]);strict.append({'gold_index':gi,'prediction_index':match[0],'strict_tdmr_match':True})
assert len(used)==6 and all(v==1 for m in metrics.values() for v in m.values())
save('A1_evaluation/strict_numeric_check.json',{'matches':strict,'matching':'one-to-one Decimal numeric equality plus exact TDM','matches_official_on_this_paper':True})
evidence=out['source_documents'];table=evidence[7]
assert table['metadata']['page_number']==5 and table['metadata']['type']=='Table' and 'Table 3:' in table['content']
assert all(r['Result'] in table['content'] for r in raw)
save('A1_evaluation/evidence_excerpt.json',{'document_index':7,'source':str(A1/'source_documents.json'),'sha256':canonical(table),'document':table,'scope':'Frozen parsed evidence, no new PDF parsing or retrieval'})
report='# A1离线验收\n\n仅离线操作，本轮API调用0次。原始A1文件保持不变，报告与评价写入A2独立目录。\n\n'
report+='对2020.emnlp-main.152.pdf的6条Extraction、13次Normalization逐字段追溯：6个Task、3个Dataset、4个Metric发起请求；其余直接保留。Result字符串原样保留，无缓存合并、修正、删项或重生成。14次历史请求均HTTP200、stop且响应模型标识匹配。\n\n'
report+='## 官方评价\n\n使用完整43篇Gold，未经修改的tdm_eval.py只遍历该篇预测，评价分母为1篇/6条Gold。P/R由官方生成；F1额外按2PR/(P+R)计算。\n\n|指标|P|R|F1|\n|---|---:|---:|---:|\n'
report+=''.join(f'|{k}|{v["Precision"]:.6f}|{v["Recall"]:.6f}|{v["F1"]:.6f}|\n' for k,v in metrics.items())
report+='\n严格Decimal数值相等及TDM一对一匹配为6/6；本篇未发现官方包含关系产生的虚假匹配、重复记录或额外结果。\n\n## 原始缓存证据抽查\n\n6条均来自第5页Table 3。第4页Metrics正文明确Slot用F1、Intent用Accuracy、联合结果用Sentence accuracy。\n\n|Dataset|Metric|Result|Table 3方法行|\n|---|---|---|---|\n'
for i,r in enumerate(norm['normalized_output']):report+=f'|{r["Dataset"]}|{r["Metric"]}|{r["Result"]}|'+('SlotRefine with GloVe' if i==0 else 'SlotRefine with BERT')+'|\n'
report+='\nATIS Slot最佳96.24来自GloVe而非BERT（96.16），抽取保留了逐指标最佳结果。6条均与Gold对应，未确认Baseline混入或字段错误。表格转换文本存在列顺序混排；上述判断基于冻结表格与Metrics正文，未重新渲染PDF，不代表全量解析质量已验证。\n\n原始Task的细分名称经官方候选映射统一为Intent Detection and Slot Filling；Snips→SNIPS、F1-score→F1、Sentence accuracy→Sent-Accuracy均正确。\n\n单篇满分只验证这篇与管线，不用于调整Prompt、参数、排序、抽取规则或推广全量性能结论。\n'
md('A1_offline_evaluation.md',report)
save('A1_verification.json',{'status':'PASS','paper_id':PAPER,'records':6,'normalization_requests':13,'official_eval_passed':True,'strict_tdmr_matches':6,'api_calls_this_task':0,'semantic_audit':'All six match frozen Gold and Table3 cached evidence','evaluation_scope':'one paper six gold','original_files_unchanged':True})

# Recount each actual serialized message using cached local target-prefix encoding.
# This is an estimate: the provider has not published tokenizer/framing/context limits.
import tiktoken
encoding=tiktoken.encoding_for_model(MODEL)
def tokens(messages):return 3+sum(3+len(encoding.encode(m['role'],disallowed_special=()))+len(encoding.encode(m['content'],disallowed_special=())) for m in messages)
inputs=read(A0/'input_manifest.json');assert len(inputs)==43 and {r['paper_id'] for r in inputs}==set(gold)
manifest=[];queue=[];status=[];checkpoint={}
for order,r in enumerate(inputs,1):
    pid=r['paper_id'];src=A0/'inputs'/pid
    docs=read(src/'source_documents.json');messages=read(src/'extraction_messages.json')
    historical=read(Path(r['source_evidence_path']))
    assert sha(Path(r['source_evidence_path']))==r['source_file_sha256']
    assert docs==historical[pid] and canonical(docs)==r['ordered_evidence_sha256']
    assert messages==[{'role':'system','content':prompts['tdm-extraction-system-prompt'].format()},{'role':'user','content':prompts['query']+'\n\nRetrieved document contents:\n\n'+'\n\n'.join(d['content'] for d in docs)+'.\n\n Output json:\n\n'}]
    assert all(d['metadata']['filename']==pid for d in docs)
    text_count=sum(d['metadata']['type']=='Text' for d in docs);table_count=sum(d['metadata']['type']=='Table' for d in docs)
    assert text_count==4 and text_count+table_count==len(docs)
    estimate=tokens(messages)
    fit=estimate<=922000 and estimate+32768<=1050000
    assert fit
    entry={'queue_order':order,'paper_id':pid,'gold_count_audit_only':len(gold[pid]['TDMs']),
           'cached_evidence_path':str(src/'source_documents.json'),'historical_evidence_path':r['source_evidence_path'],
           'source_version':r['source_archive_commit'],'evidence_file_sha256':sha(src/'source_documents.json'),'ordered_evidence_sha256':canonical(docs),
           'text_blocks':text_count,'table_documents':table_count,'evidence_count':len(docs),'messages_path':str(src/'extraction_messages.json'),
           'messages_file_sha256':sha(src/'extraction_messages.json'),'messages_canonical_sha256':canonical(messages),
           'recomputed_input_tokens_estimate':estimate,'tokenizer':encoding.name,'exact_provider_prompt_tokens':None,
           'token_count_status':'LOCAL_PREFIX_ENCODING_PROXY_NOT_EXACT','official_context_provisional_fit':fit,
           'provider_context_limit':None,'provider_context_status':'UNVERIFIED','a1_same_input_exists':pid==PAPER,
           'formal_result_reuse':False,'formal_status':'PENDING_APPROVAL','output_directory':str(R/'papers'/pid)}
    manifest.append(entry)
    queue.append({'paper_id':pid,'order':order,'extraction':{'state':'PENDING_APPROVAL','planned_calls':1,'messages_path':entry['messages_path'],'messages_sha256':entry['messages_file_sha256']},
                  'normalization':{'state':'DEFERRED_UNTIL_VALID_EXTRACTION','planned_calls':None,'expand':'one per non-Result field not exactly in candidate set; preserve record/key order; no duplicate cache'},
                  'formal_result_reuse':False,'output_directory':entry['output_directory']})
    checkpoint[pid]={'extraction':'PENDING_APPROVAL','normalization':'NOT_PLANNED','attempts':[],'successful_request_ids':[]}
    status.append({'paper_id':pid,'status':'PENDING_APPROVAL','request_stage':'NOT_STARTED','sequence':'','request_model':MODEL,'response_model':'','input_tokens':'','output_tokens':'','http_status':'','finish_reason':'','raw_response_path':'','normalized_output_path':'','success':'','failure_reason':'','elapsed_seconds':'','process_peak_rss_bytes':'','available_memory_bytes':'','free_disk_bytes':''})
csvsave('input_manifest.csv',manifest);save('input_manifest.json',manifest)
save('request_queue.json',{'scope':'43 papers; A1 excluded from formal result reuse','execution_authorized':False,'papers':queue,
                         'extraction_calls':43,'normalization_calls_historical_estimate':542,'total_calls_historical_estimate':585,'normalization_jobs_materialized':0})
csvsave('resource_and_request_status.csv',status)
save('checkpoint.json',{'state':'PREPARED_NOT_AUTHORIZED','papers':checkpoint,'api_attempts_this_task':0})
save('generation_config.json',{'model':MODEL,'extraction':params,'normalization':params,'api':'Chat Completions','base_url':'https://9527.codes/v1','path':'/chat/completions',
     'message_source':'Exact frozen official system/user messages','candidate_sets_path':str(A0/'candidate_sets.json'),'candidate_sets_sha256':sha(A0/'candidate_sets.json'),
     'normalization_acceptance':'Raw exact candidate string accepted; otherwise null; Result unchanged string; repeated inputs remain independent calls',
     'timeout_seconds':{'connect':20,'read':600,'write':30,'pool':20},'automatic_retries':0,'stream':False,
     'omitted_fields':['temperature','seed','do_sample','tools','response_format','previous_response_id'],
     'input_truncation':False,'transport':'Direct TLS verified, no environment proxy, no redirects',
     'observed_support':'All A1 requests accepted these exact fields; upstream enforcement not independently confirmed',
     'frozen_from_A1_request':str(A1/'extraction/request.json'),'execution_authorized':False})
provider={'historical_successes':14,'historical_model':MODEL,'historical_parameters_accepted':True,'last_success_utc':read(folders[-1]/'state.json')['started_utc'],
          'current_live_availability':'UNVERIFIED_NO_PROBE','public_provider_context_limit':None,'context_fit_confirmed_papers':0,'context_fit_unknown_papers':43,
          'observed_single_paper_actual_input_tokens':2345,'observed_single_paper_is_capacity_limit':False,
          'fixed_upstream_snapshot_attestation':'UNVERIFIED','reasoning_enforcement':'UNVERIFIED','historical_channel_issue_resolved':'NOT_ESTABLISHED',
          'normal_model_api_probe_calls':0,'current_status_confirmation_needed_before_launch':'Provider console/support or user report, without extra probe requests'}
save('provider_status.json',provider)
save('token_length_audit.json',{'recomputed_papers':43,'encoding':encoding.name,'exact_mapping':False,'model_prefix_mapping':True,
      'total_estimated_input_tokens':sum(r['recomputed_input_tokens_estimate'] for r in manifest),'maximum_estimated_input_tokens':max(r['recomputed_input_tokens_estimate'] for r in manifest),
      'A1_estimated_vs_actual':[tokens(read(A0/'inputs'/PAPER/'extraction_messages.json')),2345],
      'actual_counts_all_43_available':False,'reason':'No documented provider tokenizer/framing; API token-count/probe prohibited. Estimates recalculated, not copied.',
      'official_limit_provisional_fit':43,'provider_limit_confirmed_fit':0,'provider_limit_unknown':43,'confirmed_excess_context_blocked':0})
save('experiment_manifest.json',{'experiment':'GPT-5.6 Sol Fully LLM','stage':'A2 PREPARATION ONLY','created_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
      'execution_environment':'Local Windows, Python D:\\miniconda3\\envs\\scilead\\python.exe','remote_execution_directory':None,'output_directory':str(R),
      'model':MODEL,'paper_count':43,'gold_tdmrs':295,'leaderboards':27,'gold_path':str(gold_path),'gold_sha256':sha(gold_path),
      'gold_in_model_inputs':False,'source_archive_commit':'b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25','upstream_commit':'8bf74b0a830feb7035c6166dce3394dc344ae532',
      'evaluation_script':str(SOURCE/'tdm_eval.py'),'evaluation_script_sha256':sha(SOURCE/'tdm_eval.py'),'candidate_counts':{k:len(v) for k,v in candidates.items()},
      'candidate_sets_hash':sha(A0/'candidate_sets.json'),'prompt_hash_file':str(A0/'prompt_hash.json'),
      'A1_reuse':False,'A1_reason':'Validation-only run; not explicitly designated formal, all43 queued for future fresh extraction',
      'input_total':{'text':172,'tables':301},'planned_serial':True,'api_requests_this_task':0,'launch_authorized':False})
md('run_plan.md','''# A2正式批量运行准备（未启动）

43篇固定顺序采用A0清单原顺序；不得依据单篇表现重排、删样或修改方法。A1只作验证，不复用为正式结果，因此计划43次新Extraction；标准化约542次、总约585次仅历史参照，真实请求清单待新预测产生后逐字段展开。

启动门槛：用户明确批准A2；从服务商控制台/客服或用户确认获得当前可用状态，不发送额外探测。A1的14次成功只能证明当时该接口接受参数；不能证明通道已永久恢复、隐藏预算或固定上游快照。43篇实际服务商上下文是否合规目前均未知，不虚构上限；应先确认限制或由用户明确接受按服务端结果判定。已知超过限制的样本标BLOCKED_CONTEXT，不截断。不要套用Llama或旧30k规则。

执行前核验输入/配置哈希、目录独立性、Python依赖、可用内存和磁盘；一次一篇，无模型本地加载。输入Token离线重算为o200k_base代理值，正式API返回后逐请求补充真实usage；不得把代理数称为精确目标模型Token。

每篇Extraction先将不含凭据的请求正文和唯一attempt编号落盘，再标SENDING并只发一次。保留HTTP、原始响应、response model、finish_reason、request ID、usage及耗时，原始响应保存成功后再更新checkpoint。验证完整JSON数组、四字段、字符串Result和stop；空数组可为VALID_EMPTY，异常JSON不得修复或部分接受。

只有完整有效Extraction才展开该篇Normalization。使用A0冻结候选字符串及顺序、官方逐字段/逐记录顺序和Prompt；精确命中跳过；重复待映射字段独立请求，不缓存合并；Result原样保留；候选外返回null。记录每条映射及原始返回，不能因为低分、null或内容错误重跑。

HTTP500/get_channel_failed、429、超时或UNKNOWN：保存状态，停止调度以排查共享服务状态；不重发、不换模型、不改Prompt。格式失败仅停止该篇下游，保留其他结果。断点恢复只跳过哈希一致的成功阶段；SENDING/UNKNOWN/FAILED不能自动重发，须明确有限恢复授权。未开始的位置保持PENDING。恢复按请求位置而非内容缓存。

请求日志字段由resource_and_request_status.csv给出；未来每次请求扩展一行，绝不能将当前43篇占位行当成43次已发送请求。checkpoint当前全部待授权，normalization_jobs_materialized为0。

每篇输出目录papers/<paper_id>/，保存extraction/request.json、response_raw.txt、response.json、state.json、output.json及normalization/requests/<position>/、normalized_output.json。合并和正式评价仅在已批准运行完成后执行；失败覆盖率明示，原Gold、官方评价重复处理和Macro口径不变。

本轮没有API执行器或自动启动任务，没有读凭据、联网、模型生成、重新检索、PDF解析或配置升级。准备结束暂停。
''')
changed=[p for p,h in protected.items() if sha(Path(p))!=h]
assert not changed and not ATTEMPTS
save('verification.json',{'status':'PREPARATION_COMPLETE_PENDING_APPROVAL_AND_PROVIDER_CONFIRMATION','A1_official_evaluation':'PASS',
      'paper_count':43,'gold_tdmrs':295,'text_blocks':172,'table_documents':301,'evidence_complete':True,'source_order_and_hashes_verified':True,
      'prompt_tokens_recomputed':43,'token_count_precision':'PROXY_NOT_ACTUAL','provider_context_confirmed_fit':0,'provider_context_unknown':43,
      'official_limit_provisional_fit':43,'known_context_failures':0,'A1_formal_reuse':False,'planned_extractions':43,'estimated_normalizations':542,
      'estimated_total_requests':585,'materialized_normalization_requests':0,'model_api_calls_this_task':0,'network_attempts_blocked':ATTEMPTS,
      'credentials_read':False,'protected_files_checked':len(protected),'changed_frozen_files':changed,'launch_authorized':False,
      'blockers':['A2 explicit authorization pending','Provider current availability not independently confirmed','Provider context limit and precise tokenizer/framing unknown']})
save('protected_hashes.json',protected)
save('delivery_manifest.json',{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and p.name!='delivery_manifest.json'})
print(json.dumps({'A1_metrics':metrics,'A2_papers':43,'Gold':295,'estimated_tokens':sum(r['recomputed_input_tokens_estimate'] for r in manifest),'provider_context_unknown':43,'api_calls':0,'protected_files_unchanged':len(protected)},ensure_ascii=False))
