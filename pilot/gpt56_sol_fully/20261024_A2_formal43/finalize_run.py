"""Offline verification, official evaluation and report. Run only after batch exit."""
import os,sys,json,socket,runpy,io,contextlib,ast,hashlib
from pathlib import Path
from types import SimpleNamespace
from decimal import Decimal,InvalidOperation
from datetime import datetime
from collections import Counter
R=Path(__file__).resolve().parent;A0=R.parent/'20261024_A0_preparation';A1=R.parent/'20261024_A1_single_paper'
PROJECT=Path(r'D:\C++\SCILEAD');SOURCE=PROJECT/'emnlp2024-leaderboard-generation'
def deny(*a,**kw):raise RuntimeError('OFFLINE_NETWORK_FORBIDDEN')
socket.socket.connect=deny;socket.create_connection=deny
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false')
sys.dont_write_bytecode=True
sys.path.insert(0,str(A1))
from run_trial import load,save,digest,validate,MODEL
cp=load(R/'runtime_checkpoint.json');assert cp['state']!='RUNNING'
rows=load(R/'input_manifest.json');params=load(R/'generation_config.json')['extraction'];strings=load(A0/'candidate_sets.json');candidates={k:ast.literal_eval(v) for k,v in strings.items()}
prompts=load(A0/'frozen_prompts.json');extracted={};normalized={};details=[];usage_discrepancies=[]
for r in rows:
 pid=r['paper_id'];p=R/'papers'/pid;s=cp['papers'][pid]
 docs=load(Path(r['cached_evidence_path']))
 if (p/'output.json').exists():
  o=load(p/'output.json');resp=load(p/'extraction/response.json');pred=validate(resp,True)
  assert o[pid]['source_documents']==docs and o[pid]['output']==resp['choices'][0]['message']['content']
  assert load(p/'extraction/request.json')['messages']==load(Path(r['messages_path']))
  extracted.update(o)
 if s['normalization']=='COMPLETE':
  no=load(p/'normalization/normalized_output.json');nr=no[pid]['normalized_output'];assert no[pid]['source_documents']==docs and len(nr)==len(pred)
  j=0
  for i,record in enumerate(pred):
   for k,v in record.items():
    if k=='Result' or v in candidates[k]:expect=str(v)
    else:
     j+=1;f=p/'normalization/requests'/f'{j:03d}_record{i}_{k}'
     req=load(f/'request.json');answer=validate(load(f/'response.json'),False)
     assert req['messages']==[{'role':'system','content':prompts['normalization-system-prompt']},{'role':'user','content':'\n\nItem list: '+strings[k]+'\n\nInput: '+v+'\n\nAnswer: '}]
     expect=answer if answer in candidates[k] else None
    assert nr[i][k]==expect
  assert j==s['normalization_requests_planned']
  normalized.update(no)
for p in sorted((R/'papers').glob('*/**/state.json')):
 req=load(p.parent/'request.json');assert {k:v for k,v in req.items() if k!='messages'}==params
 state=load(p);resp=load(p.parent/'response.json') if (p.parent/'response.json').exists() else {}
 u=resp.get('usage') or {};top=(u.get('completion_tokens_details') or {}).get('reasoning_tokens');nested=((u.get('billing_usage') or {}).get('openai_usage') or {}).get('output_tokens_details') or {}
 if top!=nested.get('reasoning_tokens'):usage_discrepancies.append({'request':str(p.parent.relative_to(R)),'top_reasoning_tokens':top,'nested_reasoning_tokens':nested.get('reasoning_tokens')})
 details.append({'request':str(p.parent.relative_to(R)),'state':state['status'],'http_status':state.get('http_status'),'model':resp.get('model'),'finish_reason':(resp.get('choices') or [{}])[0].get('finish_reason'),'usage':u})
assert extracted==load(R/'merged/output.json') and normalized==load(R/'merged/normalized_output.json')
protected=load(R/'protected_hashes.json');changed=[p for p,h in protected.items() if not Path(p).exists() or digest(Path(p))!=h];assert not changed
prep=load(R/'delivery_manifest.json');assert all(digest(R/p)==h for p,h in prep.items())
scope=load(A0/'evaluation_scope.json');gold=load(Path(scope['gold_path']));coverage=sum(len(gold[p]['TDMs']) for p in normalized)
assert digest(Path(scope['gold_path']))==scope['gold_sha256']
full=len(normalized)==43 and coverage==295
save(R/'usage_detail_audit.json',{'requests':details,'reasoning_field_discrepancies':usage_discrepancies,'policy':'Preserve provider totals; do not add nested reasoning again; not billing reconciliation'})
metrics={};leaderboard={};perpaper={};fixed_metrics={};fixed_scope_path=R/'merged/normalized_output.json'
terminal_queue=cp['state']=='QUEUE_FINISHED'
if terminal_queue and not full:
 fixed={r['paper_id']:normalized.get(r['paper_id'],{'normalized_output':[],'source_documents':load(Path(r['cached_evidence_path']))}) for r in rows}
 fixed_scope_path=R/'evaluation/fixed43/normalized_input_failure_empty.json'
 save(fixed_scope_path,fixed)
 save(R/'evaluation/fixed43/failure_placeholder_manifest.json',{'scope':'43 papers / 295 Gold fixed denominator','synthetic_empty_is_evaluation_only':True,
       'not_valid_empty_model_outputs':True,'original_predictions_not_modified':True,'failed_papers':[r['paper_id'] for r in rows if r['paper_id'] not in normalized],
       'policy':'Failed papers receive empty predictions only in this independent evaluation input; completed-only scores reported separately; this is not 43 valid successful generations'})
if normalized:
 e=R/'evaluation';e.mkdir(exist_ok=True);sys.path.insert(0,str(SOURCE));log=io.StringIO()
 argv=[str(SOURCE/'tdm_eval.py'),'--gold_data_path',scope['gold_path'],'--normalized_tdm_output_path',str(R/'merged/normalized_output.json'),'--eval_results_path',str(e/'eval_results.json'),'--eval_values_path',str(e/'eval_values.json')]
 with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
  sys.argv=argv;runpy.run_path(str(SOURCE/'tdm_eval.py'),run_name='__main__')
 (e/'official_eval.log').write_text(log.getvalue(),encoding='utf-8')
 ev=load(e/'eval_results.json');values=load(e/'eval_values.json')
 def prf(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0}
 metrics={k:prf(v['Precision'],v['Recall']) for k,v in ev['Individual'].items()}
 metrics['TDM']=prf(ev['Exact Match Precision wo Results'],ev['Exact Match Recall wo Results']);metrics['TDMR']=prf(ev['Exact Match Precision'],ev['Exact Match Recall'])
 for pid in normalized:
  pp={k:prf(v['Precision'][pid],v['Recall'][pid]) for k,v in values['Individual'].items()}
  pp['TDM']=prf(values['Exact Match Recall wo Precision'][pid],values['Exact Match Recall wo Results'][pid]);pp['TDMR']=prf(values['Exact Match Precision'][pid],values['Exact Match Recall'][pid]);perpaper[pid]=pp
 save(e/'metrics_with_f1.json',{'scope':'FULL43' if full else 'COMPLETED_SUBSET_ONLY_NOT_FULL43','papers':len(normalized),'gold':coverage,'metrics':metrics,'aggregation':'Official per-paper macro P/R; F1=2PR/(P+R)'})
 save(e/'per_paper_metrics.json',perpaper)
 save(e/'evaluation_invocation.json',{'argv':argv,'official_source_sha256':digest(SOURCE/'tdm_eval.py'),'official_cli_unmodified':True,'scope_papers':list(normalized)})
 # Strict numeric + TDM, one-to-one diagnostic; official substring matching remains unchanged.
 comparison=['# Gold逐条诊断（独立辅助，不改官方指标）\n'];strict={}
 def number(v):
  try:
   x=Decimal(str(v));return x if x.is_finite() else None
  except InvalidOperation:return None
 for pid,no in normalized.items():
  pred=no['normalized_output'];used=set();matches=0;items=[]
  comparison+=['\n## '+pid+'\n','|Gold Task / Dataset / Metric / Result|预测位置（0起）|诊断|','|---|---|---|']
  for g in gold[pid]['TDMs']:
   exact=[i for i,p in enumerate(pred) if i not in used and all(p[k]==g[k] for k in ['Task','Dataset','Metric']) and number(p['Result']) is not None and number(p['Result'])==number(g['Result'])]
   same=[i for i,p in enumerate(pred) if number(p['Result']) is not None and number(p['Result'])==number(g['Result'])]
   if exact:idx=exact[0];used.add(idx);matches+=1;label='STRICT_TDMR_MATCH';chosen=[idx]
   elif same:label='RESULT_PRESENT_WITH_NULL' if any(any(pred[i][k] is None for k in ['Task','Dataset','Metric']) for i in same) else 'RESULT_PRESENT_TDM_MISMATCH';chosen=same
   else:label='RESULT_NOT_STRICTLY_FOUND';chosen=[]
   items.append({'gold':g,'prediction_indices':chosen,'diagnosis':label})
   gs=' / '.join(str(g[k]).replace('|','\\|') for k in ['Task','Dataset','Metric','Result'])
   comparison.append(f'|{gs}|{chosen}|{label}|')
  strict[pid]={'matches':matches,'gold':len(gold[pid]['TDMs']),'predictions':len(pred),'metrics':prf(matches/len(pred) if pred else 0,matches/len(gold[pid]['TDMs'])),'gold_diagnoses':items,'unmatched_prediction_indices':[i for i in range(len(pred)) if i not in used]}
 save(e/'strict_one_to_one.json',strict);(e/'tdmr_comparison.md').write_text('\n'.join(comparison),encoding='utf-8')
 if terminal_queue and not full:
  fixed_dir=R/'evaluation/fixed43'
  sys.argv=[str(SOURCE/'tdm_eval.py'),'--gold_data_path',scope['gold_path'],'--normalized_tdm_output_path',str(fixed_scope_path),'--eval_results_path',str(fixed_dir/'eval_results.json'),'--eval_values_path',str(fixed_dir/'eval_values.json')]
  runpy.run_path(str(SOURCE/'tdm_eval.py'),run_name='__main__')
  fe=load(fixed_dir/'eval_results.json');fv=load(fixed_dir/'eval_values.json')
  fixed_metrics={k:prf(v['Precision'],v['Recall']) for k,v in fe['Individual'].items()}
  fixed_metrics['TDM']=prf(fe['Exact Match Precision wo Results'],fe['Exact Match Recall wo Results']);fixed_metrics['TDMR']=prf(fe['Exact Match Precision'],fe['Exact Match Recall'])
  save(fixed_dir/'metrics_with_f1.json',{'scope':'43 papers / 295 Gold; failures assigned empty predictions ONLY for evaluation','successful_papers':len(normalized),'failed_papers':43-len(normalized),'metrics':fixed_metrics,'aggregation':'Unmodified official macro P/R, additional F1=2PR/(P+R)'})
  save(fixed_dir/'per_paper_metrics.json',{pid:{'status':cp['papers'][pid], 'metrics':{**{k:prf(v['Precision'][pid],v['Recall'][pid]) for k,v in fv['Individual'].items()},'TDM':prf(fv['Exact Match Recall wo Precision'][pid],fv['Exact Match Recall wo Results'][pid]),'TDMR':prf(fv['Exact Match Precision'][pid],fv['Exact Match Recall'][pid])}} for pid in fixed})
 if terminal_queue:
  # Original script CLI names are inconsistent: main reads normalized_output_file.
  # Supply that Namespace field; preserve and execute every original function unchanged.
  lb=R/'leaderboard';lb.mkdir(exist_ok=True)
  module=runpy.run_path(str(SOURCE/'leaderboard_eval.py'),run_name='offline_official_leaderboard')
  args=SimpleNamespace(gold_leaderboards_file=scope['leaderboard_path'],masked_leaderboards_file='',normalized_output_file=str(fixed_scope_path),eval_results_file=str(lb/'eval_results.json'),eval_values_file=str(lb/'eval_values.json'))
  module['main'](args);leaderboard=load(lb/'eval_results.json')
  boards=load(Path(scope['leaderboard_path']));output=module['construct_output_leaderboards'](boards,load(fixed_scope_path))
  save(lb/'constructed_leaderboards.json',output)
  save(lb/'invocation.json',{'entry':'Unmodified official main(SimpleNamespace)','normalized_output_file':str(fixed_scope_path),'reason':'CLI declares normalized_tdm_output_path but main reads normalized_output_file; independent invocation adapts argument name only','source_sha256':digest(SOURCE/'leaderboard_eval.py')})
  save(lb/'coverage_diagnostic.json',{'gold_leaderboards':len(boards),'constructed_keys':len(output),'nonempty_leaderboards':sum(bool(v) for v in output.values()),'nonempty_rate':sum(bool(v) for v in output.values())/len(boards),'status':'Auxiliary coverage; original numerical-list RBO preserved; not paper-ID ranking AO'})
failures=[]
for pid,s in cp['papers'].items():
 if s['extraction']=='FORMAT_FAILED':
  response=load(R/'papers'/pid/'extraction/response.json');text=response['choices'][0]['message']['content']
  try:raw=json.loads(text)
  except ValueError:raw=None
  failures.append({'paper_id':pid,'reason':s['error'],'json_parseable':raw is not None,'record_count':len(raw) if isinstance(raw,list) else None,
      'non_string_fields':[{'record':i,'field':k,'type':type(v).__name__,'raw_value':v} for i,x in enumerate(raw or []) for k,v in x.items() if not isinstance(v,str)],
      'normalization_attempts':0,'no_conversion_or_regeneration':True})
save(R/'inspection/format_failures.json',failures)
diagnoses=Counter(x['diagnosis'] for p in (strict.values() if normalized else []) for x in p['gold_diagnoses'])
save(R/'inspection/error_summary.json',{'gold_diagnosis_counts_completed_subset':dict(diagnoses),'normalization_null_fields':sum(v is None for no in normalized.values() for p in no['normalized_output'] for v in p.values()),
     'format_failure_papers':failures,'warning':'Result mismatch categories are auxiliary: not proof of baseline contamination without original table inspection; no prediction correction'})
v={'status':'COMPLETE43' if full else 'QUEUE_FINISHED_WITH_FORMAT_FAILURES' if terminal_queue else cp['state'],'completed_papers':len(normalized),'gold_covered':coverage,'target_papers':43,'target_gold':295,'extracted_papers':len(extracted),'records':sum(len(json.loads(o['output'])) for o in extracted.values()),'all_request_parameters_match':True,'normalization_official_replay_passed':True,'protected_files_checked':len(protected),'protected_files_changed':changed,'preparation_files_unchanged':True,'A1_not_reused':True,'stop_reason':cp.get('stop_reason'),'official_evaluation_completed_subset':len(normalized),'all43_valid_outputs':full,'fixed43_evaluation_completed':terminal_queue,'fixed43_failure_empty_placeholders':43-len(normalized) if terminal_queue else None,'usage_discrepancy_requests':len(usage_discrepancies),'no_model_calls_in_finalization':True,
   'all_response_http_200':all(d['http_status']==200 for d in details),'all_finish_reason_stop':all(d['finish_reason']=='stop' for d in details),'all_response_model_ids_match':all(d['model']==MODEL for d in details),
   'run_elapsed_seconds':(datetime.fromisoformat(cp['updated_utc'])-datetime.fromisoformat(cp['started_utc'])).total_seconds()}
save(R/'final_verification.json',v)
u=load(R/'api_usage_summary.json');lines=['# GPT-5.6 Sol Fully LLM A2正式实验报告\n',f'状态：{v["status"]}。完成 {len(normalized)}/43篇，Gold覆盖 {coverage}/295；Extraction有效 {len(extracted)} 篇，共 {v["records"]} 条预测。',f'请求 {u["request_attempts"]} 次（Extraction {u["extraction_attempts"]}，Normalization {u["normalization_attempts"]}），HTTP200 {u["http_200"]}；已报告输入 {u["prompt_tokens"]}、输出 {u["completion_tokens"]}、总Tokens {u["total_tokens"]}；缺失用量 {u["unknown_usage_requests"]} 次。A1的14次请求不计入。',f'停止原因：{json.dumps(cp.get("stop_reason"),ensure_ascii=False)}。无自动重发、无模型切换、无Prompt修改。',f'参数：gpt-5.6-sol、medium、max_completion_tokens=32768、stream=false；不传temperature/seed/tools/response_format。原始证据与候选顺序保持不变。',f'本轮传输来自直连TLS校验连接。中转站底层身份、推理参数执行和全局隐藏限制不能仅凭响应标签证明。{len(usage_discrepancies)}次用量出现推理Token口径差异，原样保留，不重复叠加，不核算费用。', '\n## 官方评价\n', '仅完成子集的指标不能称为43篇全量。' if not full else '全43篇/295 Gold完成。官方逐篇Macro聚合P/R，F1额外取2PR/(P+R)。', '|指标|P|R|F1|','|---|---:|---:|---:|']
for k,m in metrics.items():lines.append(f'|{k}|{m["Precision"]:.6f}|{m["Recall"]:.6f}|{m["F1"]:.6f}|')
lines+=['\n## 逐篇状态\n','|论文|Gold|抽取状态|记录数|标准化状态|标准化请求完成/计划|null字段|','|---|---:|---|---:|---|---|---:|']
for r in rows:
 s=cp['papers'][r['paper_id']];lines.append(f'|{r["paper_id"]}|{r["gold_count_audit_only"]}|{s["extraction"]}|{s["records"]}|{s["normalization"]}|{s["normalization_requests_complete"]}/{s["normalization_requests_planned"]}|{s["null_fields"]}|')
lines+=['\n## 完整性与恢复\n',f'{len(protected)}个受保护文件及A2准备文件全部保持原哈希。逐请求attempt.lock/状态/原始响应防止重复发送；失败或UNKNOWN不能自动重发。输入重建、PDF解析和检索均未执行。', '原始与标准化结果位于papers/及merged/；官方评价和逐条独立数值诊断位于evaluation/。未匹配预测不能仅据Gold缺席断言Baseline混入，需原文进一步确认。',
 f'批次墙钟耗时{v["run_elapsed_seconds"]:.2f}秒，进程峰值RSS {u["process_peak_rss_bytes"]/2**20:.2f}MiB。',
 '全部请求结束后的秘密扫描尝试读取本进程锁文件，Windows返回PermissionError；已复现根因并修复独立编排层（不扫描固定单字节锁）。4项回归测试通过，仅离线补齐汇总，新增请求0。实际执行脚本快照及哈希保留，官方源码未改。',
 '两篇格式失败分别为1812.09471.pdf（6条）和2002.03184.pdf（7条）；均为完整JSON数组且stop，仅Result为浮点数。本轮严格字符串协议未允许转换，保持原始响应，未进行Llama实验的兼容转换或自动恢复。']
if leaderboard:lines+=['\n## 官方Leaderboard指标\n','```json',json.dumps(leaderboard,ensure_ascii=False,indent=2),'```','完整27榜。通过独立Namespace适配官方CLI参数命名不一致，评价函数未改动。RBO基于官方数值列表，非论文ID排名。']
if fixed_metrics:
 lines+=['\n## 固定43篇分母评价（失败为空预测，仅评价副本）\n',f'实际成功{len(normalized)}/43篇。失败论文原响应不变，只在独立fixed43评价输入中置空；不将其标为模型有效空输出或完整成功。','|指标|P|R|F1|','|---|---:|---:|---:|']
 for k,m in fixed_metrics.items():lines.append(f'|{k}|{m["Precision"]:.6f}|{m["Recall"]:.6f}|{m["F1"]:.6f}|')
if terminal_queue:
 old_path=PROJECT/'pilot/full43_uncapped/evaluation/metrics_with_f1.json';old=load(old_path)
 assert old['scope']['completed_papers']==43 and old['scope']['evaluated_gold_tdmrs']==295
 comparison={'scope':'43 papers / 295 Gold; end-to-end Fully LLM, different model and generation configurations','failures_assigned_empty_only_for_evaluation':not full,'successful_new_papers':len(normalized),'reference_path':str(old_path),'reference_sha256':digest(old_path),'metrics':{}}
 lines+=['\n## 与冻结GPT-4.1 Fully基线的描述性对照\n','|指标|GPT-4.1 F1|GPT-5.6 Sol F1|差值|','|---|---:|---:|---:|']
 for k,new in (fixed_metrics or metrics).items():
  old_key=k+' IIM' if k in ['Task','Dataset','Metric','Result'] else k+' Exact Match'
  previous=old['aggregate'][old_key];delta=new['F1']-previous['F1']
  comparison['metrics'][k]={'GPT-4.1':previous,'GPT-5.6 Sol':new,'F1_delta':delta}
  lines.append(f'|{k}|{previous["F1"]:.6f}|{new["F1"]:.6f}|{delta:+.6f}|')
 lines+=['两阶段均更换基座，并使用medium reasoning及32768输出预算，不能把差异单独归因于Extraction或模型强弱；未进行Prompt优化或按得分选择重跑。']
 save(R/'evaluation/comparison_with_gpt41.json',comparison)
(R/'report.md').write_text(''.join(line+('\n' if line.startswith('|') else '\n\n') for line in lines),encoding='utf-8')
save(R/'result_manifest.json',{str(p.relative_to(R)):digest(p) for p in R.rglob('*') if p.is_file() and p.name!='result_manifest.json'})
print(json.dumps({'verification':v,'metrics':metrics,'api_usage':u},ensure_ascii=False))
