"""Offline diagnostics only; never rewrites predictions or official evaluation."""
from pathlib import Path
from decimal import Decimal,InvalidOperation
from collections import Counter
import re,json,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pattern=re.compile(r'^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(?:%|±\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)\s*%?)?\s*$')
def central(text):
 m=pattern.fullmatch(str(text));return Decimal(m.group(1)) if m else None
def simple(text):
 try:return Decimal(str(text))
 except InvalidOperation:return None
scope=read(R.parent/'20261024_A0_preparation/evaluation_scope.json');gold=read(Path(scope['gold_path']));pred=read(R/'merged/normalized_output.json')
protected=[R/'merged/normalized_output.json',R/'evaluation/fixed43/eval_results.json',R/'evaluation/eval_results.json']
before={str(p):sha(p) for p in protected}
counts=Counter();examples=[];perpaper={}
for pid,no in pred.items():
 rows=no['normalized_output'];used=set();checks=[]
 for g in gold[pid]['TDMs']:
  value=Decimal(str(g['Result']))
  exact=[i for i,p in enumerate(rows) if i not in used and all(p[k]==g[k] for k in ['Task','Dataset','Metric']) and central(p['Result'])==value]
  if exact:
   i=exact[0];used.add(i)
   label='SIMPLE_NUMERIC_TDM_MATCH' if simple(rows[i]['Result'])==value else 'DECORATED_RESULT_SAME_CENTRAL_VALUE_AND_TDM'
   indices=[i]
  else:
   same=[i for i,p in enumerate(rows) if central(p['Result'])==value]
   if same:
    label='CENTRAL_VALUE_PRESENT_WITH_NULL_OR_TDM_MISMATCH';indices=same
   else:
    indices=[i for i,p in enumerate(rows) if all(p[k]==g[k] for k in ['Task','Dataset','Metric'])]
    label='SAME_TDM_DIFFERENT_OR_UNINTERPRETABLE_VALUE' if indices else 'NO_MATCHING_TDM_OR_CENTRAL_VALUE'
  counts[label]+=1
  item={'gold':g,'prediction_indices':indices,'prediction_results':[rows[i]['Result'] for i in indices],'diagnosis':label}
  checks.append(item)
  if label!='SIMPLE_NUMERIC_TDM_MATCH' and len(examples)<18:examples.append({'paper_id':pid,**item})
 perpaper[pid]=checks
assert all(sha(Path(p))==h for p,h in before.items())
write(R/'inspection/result_representation_audit.json',{'scope':'41 completed papers / 282 Gold; diagnostic only','counts':dict(counts),'per_paper':perpaper,'examples':examples,
      'rule':'Recognize a single leading numeric value with optional % or ± uncertainty suffix, no unit rescaling; preserve raw prediction. This is NOT strict whole-string numeric equality and does not replace official metrics.',
      'original_predictions_and_official_scores_unchanged':True})
summary=read(R/'inspection/error_summary.json');summary['strict_parser_warning']='RESULT_NOT_STRICTLY_FOUND includes percent and uncertainty representations; do not label every case as omission or incorrect extraction.';summary['representation_audit_counts']=dict(counts);write(R/'inspection/error_summary.json',summary)
text='\n\n## Result表示差异的补充诊断\n\n严格Decimal诊断有155条TDMR匹配，但其余条目不都代表数值错误：带%或±标准差的原始Result不能直接解析成单个Decimal。独立诊断识别主数值及后缀，不进行单位换算、不改原预测、不替换官方评价。\n\n'
text+='|诊断|Gold条数|\n|---|---:|\n'+''.join(f'|{k}|{v}|\n' for k,v in counts.items())
text+='\n例如2020.emnlp-main.152.pdf的6个结果含百分号，主数值与Gold一致；D18-1279.pdf的结果保留±标准差。1709.04109.pdf的97.53±0.03与Gold97.59仍不相等，不能因格式解释而认定数值正确。详细逐条记录见inspection/result_representation_audit.json。\n'
p=R/'report.md';p.write_text(p.read_text(encoding='utf-8')+text,encoding='utf-8')
write(R/'result_manifest.json',{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and p.name!='result_manifest.json'})
print(json.dumps(dict(counts),ensure_ascii=False))
