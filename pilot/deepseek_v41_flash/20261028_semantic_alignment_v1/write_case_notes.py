"""Offline, source-backed case notes. Does not change predictions or requests."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261028'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

raw=read(ROOT/'variants/inputs/output.json')
examples=read(ROOT/'inspection/examples_before_after.json')
scope=read(ROOT/'inspection/gold_candidate_scope.json')
selected=[]
for e in examples:
 if (e['branch']=='cold_default' and e['stage']=='stage2') or (e['branch']=='cold_0' and e['paper']=='1811.09242.pdf') or (e['branch']=='cold_42' and e['paper']=='C18-1139.pdf'):
  selected.append({k:e[k] for k in ['branch','stage','paper','record','field','raw_extraction']} | {
   'before':e['baseline_event']['normalized'],'after':e['variant_event']['normalized'],
   'variant_call':e['variant_event'].get('call'),'response':{k:v for k,v in e.get('variant_response',{}).items() if k!='provider_reasoning_content'}})
docs=raw['1811.09242.pdf']['source_documents']
source=[{'index_zero_based':i,**d} for i,d in enumerate(docs) if 'Arnet' in d['content']]
assert len(source)==2 and 'SemEval 2013' in source[0]['content'] and '(a) Arnet Dataset' in source[1]['content']
arnet=next(e for e in selected if e['branch']=='cold_0')
assert arnet['before']=='Arnet' and arnet['after']=='SemEval 2013 Task 13'
german=next(e for e in selected if e['branch']=='cold_42')
assert german['raw_extraction']['Task']=='NER German' and german['after']=='CoNLL-2003 English'
old=read(BASE/'variants/partially/stage2/leaderboard_normalized_output.json')['1811.05021.pdf']['normalized_output'][1]
new=read(ROOT/'variants/partially/stage2/leaderboard_normalized_output.json')['1811.05021.pdf']['normalized_output'][1]
assert old['Task']=='Dialogue Act Classification' and new['Task']=='Dialog Act Classification'
assert all(old[k]==new[k] for k in ['Dataset','Metric','Result'])
evidence={'examples':selected,'arnet_source_documents':source,'partially_regression':{'paper':'1811.05021.pdf','record':2,'before':old,'after':new},
 'source_path':str(ROOT/'variants/inputs/output.json'),'source_sha256':sha(ROOT/'variants/inputs/output.json'),
 'gold_used_only_after_generation':True,'scope_summary':{k:v for k,v in scope.items() if k not in ['inside','outside']}}
(ROOT/'inspection/case_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
text='''# 语义对齐补充实验：可追溯案例与残余问题

本页只读取完成后的预测、处理事件、原始证据和Gold，用于离线分析。机器可读证据见 `case_evidence.json`；完整候选顺序与响应见 `examples_before_after.json`。

## 1. 缩写对齐恢复了原本正确的结果

Cold默认顺序，`2020.findings-emnlp.378.pdf` 第1—3条：

| Result（始终不变） | 原版第二阶段 Dataset | 补充要求后 Dataset | Task变化 |
| --- | --- | --- | --- |
| 90.32 | ON5E | Ontonotes v5 - English | Named Entity Recognition → Named Entity Recognition (NER) |
| 55.14 | WN16 | WNUT-16 - English | 同上 |
| 50.68 | WN17 | WNUT-17 - English | 同上 |

原版返回原tuple、按未匹配保留；新版逐字返回候选tuple。三个结果与该论文Gold对应。改善发生在既有正确数值的名称映射环节。

## 2. 语义匹配也出现了错误合并

Cold字符串种子0，`1811.09242.pdf` 第7条第一阶段Dataset请求10：`Arnet → SemEval 2013 Task 13`。原版保留`Arnet`。Result始终为`58.8`。

实际输入证据第7页的Table 4分别列出SemEval 2013、PubMed和Arnet；下一条表格证据标题为`(a) Arnet Dataset`，其中AutoSense的结果包含58.8。Arnet和SemEval 2013是不同数据集，不能合并。该错误在正式输出中原样保留。

## 3. 单字段输入仍会丢失跨字段的语言信息

Cold字符串种子42，`C18-1139.pdf` 第2条：原始Task为`NER German`，Dataset仅为`CoNLL-2003`，Result为`88.32±0.20`。第一阶段Dataset请求61将其映射为`CoNLL-2003 English`，第二阶段仍保留这一错误组合。

原版逐字段接口向这一请求提供Dataset名称和候选集合，没有提供相邻Task中的German限定。新增的语义要求没有改变这个输入结构；语言、版本等信息分散在不同字段时，仍会发生误绑定。

## 4. 指标下降也可能来自等义名称未落到Gold的精确写法

Partially的`1811.05021.pdf`由TDMR F1 1.00下降到0.50。第2条Task从`Dialogue Act Classification`变为`Dialog Act Classification`，Dataset `MapTask`、Metric `Accuracy`、Result `68.5`均未改变。两种Task拼写等义，但官方精确匹配采用前一种，且27个第二阶段候选榜中没有MapTask对应tuple，因此最终保留了该名称差异。

## 5. 第二阶段的覆盖范围

27个候选排行榜的TDM覆盖295条Gold中的140条；其余155条Gold的TDM没有对应候选榜。第二阶段只能用现有候选做映射，未匹配的tuple按原逻辑保留。这解释了部分第一阶段非标准名称在第二阶段继续存在。覆盖数不是最终F1上限：候选榜之外的记录也可能在第一阶段已正确标准化。

## 6. 本轮能说明什么

在固定Extraction的条件下，Partially最终TDMR F1从20.19%升到60.40%，Cold三顺序平均从10.74%升到51.18%。原先的名称对齐行为是明显的性能瓶颈，通用语义要求能恢复大量匹配。

Cold第一阶段TDMR F1三顺序均值反而从4.54%降到3.24%，最终改善集中体现在第二阶段候选tuple对齐。第一、二阶段的Prompt在本轮同时补充，第一阶段回答还会改变后续动态集合，因此单独某条新增要求的贡献需要另做消融才能量化。

全部Result、Extraction记录和RAG证据保持不变；Result IIM F1仍为81.26%。已有数值遗漏、列绑定错误不会由名称对齐自动纠正。错误合并、跨字段限定丢失、候选榜覆盖不足与精确名称差异仍可在上述记录中直接观察到。
'''
(ROOT/'inspection/case_notes.md').write_text(text,encoding='utf8')
print(json.dumps({'status':'PASS','selected_cases':len(selected),'source_documents':len(source)}))
