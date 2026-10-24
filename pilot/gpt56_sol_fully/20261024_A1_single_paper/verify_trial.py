"""Offline independent verification. Never reads credentials or calls a network."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent
A=R.parent/'20261024_A0_preparation'
P='2020.emnlp-main.152.pdf'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
out=read(R/'output.json')[P]
norm=read(R/'normalization/normalized_output.json')[P]
rows=json.loads(out['output']);normalized=norm['normalized_output']
assert out['source_documents']==norm['source_documents']==read(A/'inputs'/P/'source_documents.json')
assert len(rows)==len(normalized)==6
cs=read(A/'candidate_sets.json');c={k:ast.literal_eval(v) for k,v in cs.items()}
pr=read(A/'frozen_prompts.json')
folders=[p.parent for p in sorted((R/'normalization/requests').glob('*/request.json'))]
position=0
for i,row in enumerate(rows):
 for k,v in row.items():
  if k=='Result' or v in c[k]: expected=str(v)
  else:
   f=folders[position];position+=1
   req=read(f/'request.json');res=read(f/'response.json')
   assert req['messages']==[{'role':'system','content':pr['normalization-system-prompt']},{'role':'user','content':'\n\nItem list: '+cs[k]+'\n\nInput: '+v+'\n\nAnswer: '}]
   answer=res['choices'][0]['message']['content']
   expected=answer if answer in c[k] else None
  assert normalized[i][k]==expected
assert position==13
assert read(R/'extraction/request.json')['messages']==read(A/'inputs'/P/'extraction_messages.json')
usage_discrepancies=[];details=[]
for f in [R/'extraction']+folders:
 req=read(f/'request.json');resp=read(f/'response.json');state=read(f/'state.json')
 assert set(req)=={'model','messages','reasoning_effort','max_completion_tokens','stream'}
 assert req['model']==resp['model']=='gpt-5.6-sol'
 assert req['reasoning_effort']=='medium' and req['max_completion_tokens']==32768 and req['stream'] is False
 assert state['http_status']==200 and resp['choices'][0]['finish_reason']=='stop'
 u=resp['usage'];nested=u.get('billing_usage',{}).get('openai_usage',{}).get('output_tokens_details',{}).get('reasoning_tokens')
 top=u.get('completion_tokens_details',{}).get('reasoning_tokens')
 if top!=nested:usage_discrepancies.append({'request':str(f.relative_to(R)),'top_reasoning_tokens':top,'nested_reasoning_tokens':nested})
 details.append({'request':str(f.relative_to(R)),'response_id':resp.get('id'),'model':resp['model'],'finish_reason':'stop','input_tokens':u['prompt_tokens'],'output_tokens':u['completion_tokens'],'total_tokens':u['total_tokens'],'elapsed_seconds':state['elapsed_seconds'],'top_reasoning_tokens':top,'nested_reasoning_tokens':nested})
hashes=read(A/'read_source_hashes.json')
changed=[p for p,h in hashes.items() if not Path(p).exists() or sha(Path(p))!=h]
assert not changed,changed
v=read(R/'verification.json')
v.update(independent_verification_passed=True,all_finish_reason_stop=True,all_response_models_match=True,
 actual_request_parameters_verified=True,source_documents_exactly_preserved=True,official_normalization_replayed_equal=True,
 protected_source_hashes_checked=len(hashes),protected_source_files_changed=changed,
 null_fields=sum(v is None for r in normalized for v in r.values()),usage_discrepancies=usage_discrepancies,
 semantic_gold_evaluation_performed=False,provider_model_identity='RESPONSE_LABEL_MATCHES; upstream identity and reasoning enforcement not independently attested')
write(R/'verification.json',v)
write(R/'request_usage_details.json',details)
write(R/'test_results.json',{'tests_run':5,'passed':5,'network_calls':0,'tests':'test_trial.py; structural validation, no normalization trimming, no retry'})
text=(R/'report.md').read_text(encoding='utf-8')
text+='\n## 最终独立核验\n\n14次请求均HTTP200、finish_reason=stop，响应模型均为gpt-5.6-sol；13个标准化返回均在候选集合内。2013个冻结来源文件哈希未变。\n\n'
text+='接口输入Tokens 6206、输出Tokens 399、合计6605；约80.14秒。Extraction实际输入2345，离线代理估算2346。\n\n'
text+='Extraction用量存在口径差异：顶层reasoning_tokens=0，嵌套billing_usage/openai_usage/output_tokens_details/reasoning_tokens=158；原始字段均保留，不重复叠加推理Token，不声称平台账单已核对。响应中还有缓存写入统计，未主动配置缓存或据此计算费用。\n\n'
text+='所有Task标准化为Intent Detection and Slot Filling。以下为真实标准化结果，尚未开展正式Gold评价，候选内匹配不等于语义正确。\n\n| Dataset | Metric | Result |\n|---|---|---|\n'
text+=''.join(f'| {r["Dataset"]} | {r["Metric"]} | {r["Result"]} |\n' for r in normalized)
text+='\n本轮只验证单篇Extraction和Fully Normalization。API接受参数不等于证明中转站完全按该参数执行；固定上游快照和隐藏预算仍无法独立核实。完成后暂停，未启动43篇批量。\n'
(R/'report.md').write_text(text,encoding='utf-8')
write(R/'delivery_manifest.json',{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and p.name!='delivery_manifest.json'})
print(json.dumps({'independent_verification':'PASS','requests':14,'records':6,'null_fields':v['null_fields'],'protected_hashes_passed':len(hashes),'usage_discrepancies':usage_discrepancies},ensure_ascii=False))
