"""Offline merge, replay verification and unchanged official evaluation for recovered43."""
import os,sys,socket,runpy,json,ast,io,contextlib,copy,hashlib
from pathlib import Path
from types import SimpleNamespace
from decimal import Decimal,InvalidOperation
R=Path(__file__).resolve().parent;A2=R.parent/'20261024_A2_formal43';A0=R.parent/'20261024_A0_preparation'
PROJECT=Path(r'D:\C++\SCILEAD');SOURCE=PROJECT/'emnlp2024-leaderboard-generation'
def deny(*a,**kw):raise RuntimeError('OFFLINE_NETWORK_FORBIDDEN')
socket.socket.connect=deny;socket.create_connection=deny
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false');sys.dont_write_bytecode=True
sys.path.insert(0,str(R.parent/'20261024_A1_single_paper'))
from run_trial import load,save,digest,MODEL
from recovery_adapter import convert
assert load(R/'runtime_status.json')['status']=='RECOVERY_COMPLETE'
protected=load(R/'source_freeze_manifest.json')
original_out=load(A2/'merged/output.json');original_norm=load(A2/'merged/normalized_output.json')
assert len(original_out)==len(original_norm)==41
merged_out=copy.deepcopy(original_out);merged_norm=copy.deepcopy(original_norm)
requests=load(R/'normalization_request_manifest.json');candidate_strings=requests['candidate_strings'];candidates={k:ast.literal_eval(v) for k,v in candidate_strings.items()}
params=load(A2/'generation_config.json')['normalization']
source_index=[];call_details=[];conversion_records=[]
for pid,jobs in requests['papers'].items():
 p=R/'papers'/pid;o=load(p/'output.json')[pid];n=load(p/'normalization/normalized_output.json')[pid]
 original_response=load(A2/'papers'/pid/'extraction/response.json');reconstructed,audit=convert(original_response['choices'][0]['message']['content'])
 assert json.loads(o['output'])==reconstructed and o['source_documents']==n['source_documents']
 nr=n['normalized_output'];assert len(nr)==len(reconstructed)
 count=0
 for i,row in enumerate(reconstructed):
  for key,value in row.items():
   if key=='Result' or value in candidates[key]:expected=str(value)
   else:
    job=jobs[count];count+=1;folder=p/'normalization/requests'/f'{count:03d}_record{i}_{key}'
    req=load(folder/'request.json');response=load(folder/'response.json');state=load(folder/'state.json')
    assert req=={**params,'messages':job['messages']} and (job['record_index'],job['field'],job['input'])==(i,key,value)
    assert state['http_status']==200 and response['model']==MODEL and response['choices'][0]['finish_reason']=='stop'
    answer=response['choices'][0]['message']['content'];expected=answer if answer in candidates[key] else None
    call_details.append({'paper_id':pid,'position':count,'record_index':i,'field':key,'raw_answer':answer,'accepted':expected,'http_status':200,
       'model':response['model'],'finish_reason':'stop','response_id':response.get('id'),'usage':response.get('usage'),'latency':state['elapsed_seconds']})
   assert nr[i][key]==expected
 assert count==len(jobs)
 merged_out[pid]={**o};merged_norm[pid]={**n}
 conversion_records.extend([{'paper_id':pid,**item} for item in audit])
assert len(call_details)==24 and all(x['numeric_semantics_equal'] for x in conversion_records)
assert len(merged_out)==len(merged_norm)==43
assert all(merged_out[p]==original_out[p] and merged_norm[p]==original_norm[p] for p in original_out)
inputs=load(A2/'input_manifest.json');scope=load(A0/'evaluation_scope.json');gold=load(Path(scope['gold_path']))
assert set(merged_norm)==set(gold) and sum(len(gold[p]['TDMs']) for p in merged_norm)==295
for r in inputs:
 pid=r['paper_id'];docs=load(Path(r['cached_evidence_path']))
 assert merged_out[pid]['source_documents']==merged_norm[pid]['source_documents']==docs
 recovered=pid in requests['papers'];source=R if recovered else A2
 source_index.append({'paper_id':pid,'status':'RECOVERED_NUMERIC_RESULT_TYPE' if recovered else 'REUSED_UNCHANGED',
       'gold_count':len(gold[pid]['TDMs']),'record_count':len(merged_norm[pid]['normalized_output']),
       'output_path':str(source/'papers'/pid/'output.json'),'normalized_path':str(source/'papers'/pid/'normalization/normalized_output.json'),
       'raw_extraction_path':str(A2/'papers'/pid/'extraction/response_raw.txt'),'raw_extraction_sha256':digest(A2/'papers'/pid/'extraction/response_raw.txt'),
       'evidence_sha256':r['evidence_file_sha256'],'normalization_null_fields':sum(v is None for row in merged_norm[pid]['normalized_output'] for v in row.values())})
save(R/'merged/output.json',merged_out);save(R/'merged/normalized_output.json',merged_norm)
save(R/'output_index.json',source_index);save(R/'normalization_call_audit.json',call_details)
save(R/'conversion_verification.json',{'records':conversion_records,'count':13,'only_result_type_changed':True,'official_str_semantics':True,'no_rescaling':True,'record_order_and_duplicates_unchanged':True})

# Official evaluation uses exactly the frozen source, with no model invocation.
e=R/'evaluation';e.mkdir(exist_ok=True);sys.path.insert(0,str(SOURCE))
argv=[str(SOURCE/'tdm_eval.py'),'--gold_data_path',scope['gold_path'],'--normalized_tdm_output_path',str(R/'merged/normalized_output.json'),
      '--eval_results_path',str(e/'eval_results.json'),'--eval_values_path',str(e/'eval_values.json')]
buf=io.StringIO()
with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
 sys.argv=argv;runpy.run_path(str(SOURCE/'tdm_eval.py'),run_name='__main__')
(e/'official_eval.log').write_text(buf.getvalue(),encoding='utf-8')
save(e/'invocation.json',{'argv':argv,'official_source_sha256':digest(SOURCE/'tdm_eval.py'),'prediction_papers':43,'Gold':295,'failure_empty_placeholders':0})
ev=load(e/'eval_results.json');vals=load(e/'eval_values.json')
def prf(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0}
metrics={k:prf(v['Precision'],v['Recall']) for k,v in ev['Individual'].items()}
metrics['TDM']=prf(ev['Exact Match Precision wo Results'],ev['Exact Match Recall wo Results']);metrics['TDMR']=prf(ev['Exact Match Precision'],ev['Exact Match Recall'])
perpaper={}
for pid in merged_norm:
 perpaper[pid]={k:prf(v['Precision'][pid],v['Recall'][pid]) for k,v in vals['Individual'].items()}
 perpaper[pid]['TDM']=prf(vals['Exact Match Recall wo Precision'][pid],vals['Exact Match Recall wo Results'][pid]);perpaper[pid]['TDMR']=prf(vals['Exact Match Precision'][pid],vals['Exact Match Recall'][pid])
save(e/'metrics_with_f1.json',{'scope':'43 valid processed papers / 295 Gold; numeric Result compatibility recovery variant','metrics':metrics,'aggregation':'Official per-paper macro P/R; F1=2PR/(P+R) added separately'})
save(e/'per_paper_metrics.json',perpaper)
old=load(A2/'evaluation/fixed43/per_paper_metrics.json')
assert all(perpaper[p]==old[p]['metrics'] for p in original_norm)

lb=R/'leaderboard';lb.mkdir(exist_ok=True)
module=runpy.run_path(str(SOURCE/'leaderboard_eval.py'),run_name='official_offline_leaderboard')
args=SimpleNamespace(gold_leaderboards_file=scope['leaderboard_path'],masked_leaderboards_file='',normalized_output_file=str(R/'merged/normalized_output.json'),eval_results_file=str(lb/'eval_results.json'),eval_values_file=str(lb/'eval_values.json'))
module['main'](args)
boards=load(Path(scope['leaderboard_path']));constructed=module['construct_output_leaderboards'](boards,copy.deepcopy(merged_norm))
save(lb/'constructed_leaderboards.json',constructed);save(lb/'coverage_diagnostic.json',{'gold_leaderboards':27,'nonempty':sum(bool(v) for v in constructed.values()),'nonempty_rate':sum(bool(v) for v in constructed.values())/27})
save(lb/'invocation.json',{'source_sha256':digest(SOURCE/'leaderboard_eval.py'),'main_argument_adaptation':'Supply normalized_output_file expected by original main; CLI has inconsistent name. No source change.','Result_scaling':'Original leaderboard function scales values <1 by100 for listed metrics; not performed on original or normalized outputs'})

# Offline error analysis for recovered papers. No corrective mapping/scaling in predictions.
analysis=['# 两篇恢复后的逐条对照\n','恢复只解决Result类型，不代表数值、方向或Metric绑定正确。原始预测不修改。\n']
for pid in requests['papers']:
 analysis+=['\n## '+pid+'\n','|Gold Task / Dataset / Metric / Result|同TDM预测Result|说明|','|---|---|---|']
 for g in gold[pid]['TDMs']:
  same=[p['Result'] for p in merged_norm[pid]['normalized_output'] if all(p[k]==g[k] for k in ['Task','Dataset','Metric'])]
  note='无精确TDM对应'
  if same:
   exact=[x for x in same if Decimal(x)==Decimal(str(g['Result']))]
   note='严格数值相等' if exact else 'TDM相同，但原始数值不相等；未换算或修正'
  text=' / '.join(str(g[k]) for k in ['Task','Dataset','Metric','Result'])
  analysis.append(f'|{text}|{same}|{note}|')
(e/'recovered_paper_comparison.md').write_text('\n'.join(analysis),encoding='utf-8')

new_usage=load(R/'api_usage_summary.json');base_usage=load(A2/'api_usage_summary.json')
combined={k:base_usage[k]+new_usage[k] for k in ['prompt_tokens','completion_tokens','total_tokens']}
combined.update(extraction_requests=43,normalization_requests=base_usage['normalization_attempts']+24,total_requests=base_usage['request_attempts']+24,A1_trial_excluded=True,new_extraction_requests=0,new_normalization_requests=24)
save(R/'combined_A2_api_usage.json',combined)
before=load(A2/'evaluation/fixed43/metrics_with_f1.json')['metrics']
save(e/'comparison_with_original_A2.json',{'original_scope':'43 denominator; 2 failures assigned empty for evaluation only','recovered_scope':'43 processed, no failure placeholders',
      'original':before,'recovered':metrics,'F1_delta':{k:metrics[k]['F1']-before[k]['F1'] for k in metrics},'unchanged_41_paper_metrics_verified':True})
assert all(Path(p).exists() and digest(Path(p))==h for p,h in protected.items())
v={'status':'RECOVERY_COMPLETE_43_OF_43','papers':43,'gold':295,'records':sum(len(v['normalized_output']) for v in merged_norm.values()),
   'recovered_papers':list(requests['papers']),'reused_unchanged_papers':41,'numeric_result_conversions':13,'new_extraction_calls':0,'new_normalization_calls':24,
   'all_new_calls_http200':True,'all_new_calls_finish_stop':True,'all_new_response_models_match':True,'new_calls_no_retry':True,
   'official_normalization_replay_passed':True,'official_evaluation_completed':True,'unchanged_41_metrics_verified':True,
   'source_files_verified':len(protected),'source_files_changed':[],'raw_responses_unchanged':True,'approved_compatibility_variant':True,'no_unit_rescaling_in_predictions':True,
   'all_other_frozen_experiments_untouched':True,'tests_passed':6,'new_null_fields':sum(v is None for pid in requests['papers'] for row in merged_norm[pid]['normalized_output'] for v in row.values())}
save(R/'verification.json',v)
text='# GPT-5.6 Sol A2：两篇Result类型恢复\n\n状态：43/43篇完成，295/295 Gold覆盖，335条预测。原A2严格类型版保持原样，本目录为批准后的独立Result类型兼容恢复版。\n\n'
text+='1812.09471.pdf的6条与2002.03184.pdf的7条均只将数值Result按官方str(json.loads值)转成字符串；Task/Dataset/Metric、记录顺序、重复项、数值含义和原始响应不变。例如0.950转成"0.95"，原始数值字面量另存；0.918仍为"0.918"，不变为91.8。\n\n'
text+=f'6项离线测试通过；新增Extraction 0次，Normalization 24次（11+13），全部HTTP200/stop且返回gpt-5.6-sol，无重试。新增Tokens：输入{new_usage["prompt_tokens"]}、输出{new_usage["completion_tokens"]}、总计{new_usage["total_tokens"]}。A2加恢复累计{combined["total_requests"]}次、{combined["total_tokens"]} Tokens，不含A1试跑14次。\n\n'
text+='41篇结果原样复用且逐篇官方指标一致。两篇此前没有发起标准化，因此本轮24次均是新字段请求，不是重发失败请求。不按Gold选择输出。\n\n'
text+='## 官方指标\n\nP/R来自未经修改的tdm_eval.py，F1另按聚合P/R计算。43篇均有真实标准化输出，没有失败空预测占位。\n\n|指标|P|R|F1|原A2固定43分母F1|\n|---|---:|---:|---:|---:|\n'
for k,m in metrics.items():text+=f'|{k}|{m["Precision"]:.6f}|{m["Recall"]:.6f}|{m["F1"]:.6f}|{before[k]["F1"]:.6f}|\n'
text+='\n## 内容正确性限制\n\n类型恢复不修正预测的比例单位、数据集方向、指标或数值。逐条Gold对照见evaluation/recovered_paper_comparison.md。官方Leaderboard自身对部分小于1的结果乘100；这一原有评价行为不等于我们改写了Result，也可能使Leaderboard和TDMR表现不同。\n\n'
text+='## Leaderboard\n\n```json\n'+json.dumps(load(lb/'eval_results.json'),ensure_ascii=False,indent=2)+'\n```\n\n固定27个Gold榜；RBO为原版数值列表指标。官方脚本的命令行参数名不一致由独立Namespace适配，核心算法不变。\n\n'
text+=f'完整性：{len(protected)}个冻结来源文件哈希不变；原A2的请求、失败记录、输出和评价未覆盖。模型和Prompt、证据及标准化候选顺序均未变。本次修改仅为获准的Result类型兼容，原A2严格验收版与本恢复版分别保留。\n'
(R/'report.md').write_text(text,encoding='utf-8')
save(R/'result_manifest.json',{str(p.relative_to(R)):digest(p) for p in R.rglob('*') if p.is_file() and p.name!='result_manifest.json'})
print(json.dumps({'verification':v,'new_usage':new_usage,'combined':combined,'metrics':metrics,'leaderboard':load(lb/'eval_results.json')},ensure_ascii=False))
