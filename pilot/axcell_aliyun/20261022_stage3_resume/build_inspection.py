"""Offline source trace inspection, never edits predictions or evaluates against Gold."""
from pathlib import Path
import json,re,html,csv,collections
R=Path(__file__).resolve().parent;D=R/'remote_results/papers'
items=json.loads((R/'prediction_source_inspection.json').read_text(encoding='utf-8'))
def clean(s):return html.unescape(re.sub('<[^>]+>','',str(s)))
findings=[]
for paper in items:
 for item in paper['records']:
  p=item['prediction'];source=item['source'];row=item.get('raw_source_row') or [];headers=item.get('table_first_rows') or []
  text=' | '.join(map(clean,row));status=None;category=None
  if paper['paper_id']=='1511.08308.pdf' and source.endswith('table_06.csv/6.2'):
   category='METRIC_CELL_BINDING';status='已核实：列为Recall，原预测为F1'
  elif paper['paper_id']=='1511.08308.pdf' and source.endswith('table_11.csv/2.4'):
   category='COUNT_AS_SCORE';status='已核实：Test set size (# entities)，4,696为实体数'
  elif paper['paper_id']=='1603.01354.pdf' and source.endswith('table_06.csv/3.1'):
   category='DIMENSION_AS_SCORE';status='已核实：原表列为Dimension，Word2Vec的300是向量维度；同一行NER列为84.91。原预测F1=300.0完整保留'
  elif paper['paper_id']=='2020.findings-emnlp.378.pdf' and source.endswith('table_05.csv/14.6'):
   category='DATASET_COLUMN_BINDING_CANDIDATE';status='来源列头为RE，原预测数据集为ontontoes chinese v5；数值96.62与单元格一致，数据集绑定需结合正文复核，不作人工修正'
  elif re.search(r'(#\s*(params|parameters|tokens|entities)|number of|set size|million|seconds|speed|time \()',text,re.I):
   category='STATISTIC_OR_COST_ROW_CANDIDATE';status='待人工核实：来源行有数量/资源统计标记，不能仅依关键词断言错误'
  elif isinstance(p.get('score'),(int,float)) and p['score']>100 and re.search(r'F1|accuracy|ROUGE|BLEU',str(p.get('metric')),re.I):
   category='SCALE_OR_BINDING_CANDIDATE';status='待人工核实：指标名称与大于100数值组合，需结合量纲/表头确认'
  if category:findings.append({'paper_id':paper['paper_id'],'category':category,'status':status,**item})
(R/'source_findings.json').write_text(json.dumps(findings,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# 原始预测的来源检查','',
 '仅依据保留的原始表格/单元格、列头和行名记录现象，不计算Gold命中、IIM、ETM或Leaderboard指标，不修正任何预测。两条历史错误及新增维度误作分数均保留；明确标为“待核实”的项目不能等同于已确认错误。这里不是完整错误率评价。','',
 '| 论文 | 类别 | 原始模型/指标/分数 | 单元格来源 | 结论 |','|---|---|---|---|---|']
for x in findings:
 p=x['prediction'];lines.append('| '+ ' | '.join(str(v).replace('|','/') for v in [x['paper_id'],x['category'],str(p['model'])+' / '+str(p['metric'])+' / '+str(p['score']),x['source'],x['status']])+' |')
lines+=['','VALID_EMPTY表示官方流程成功结束且最终过滤后无记录。不能根据空输出重新生成，也不能用空预测冒充程序异常。FAILED/BLOCKED单列于extraction_status.csv。',
 '原始来源全部见prediction_source_inspection.json；中间候选和筛选原因见remote_results/papers/*/raw_outputs/events与pipeline_events.json。源CSV的坐标从0开始。模型列随原始记录保留，不依据其名称手工剔除Baseline。',
 '是否混入其他工作Baseline、是否存在Dev/Test或跨数据集绑定问题，需要进一步结合论文正文核查；本轮未用Gold筛选或指导输出。不能声称这里已全面确认每条预测的科学正确性。']
lines+=['','## 9篇有效空预测的原过滤轨迹','', '| 论文 | 最终阶段输入候选数 | 原日志汇总的剔除原因 |','|---|---:|---|']
for p in json.loads((R/'empty_inspection.json').read_text(encoding='utf-8')):
 last=p['filters'][-1] if p['filters'] else {}
 reasons='；'.join(k+': '+str(v) for k,v in last.get('removal_reason_counts',{}).items())
 lines.append('| '+p['paper_id']+' | '+str(last.get('proposals',0))+' | '+reasons+' |')
lines+=['','剔除原因直接来自原版pipeline_events，未改变0.8/0.85阈值或model-competing处理。长论文1912.08777.pdf已完成全部流程，空结果来自原筛选，而非再次被保护中断。']
(R/'error_inspection.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'papers_inspected':len(items),'raw_records':sum(p['record_count'] for p in items),'findings_by_category':dict(collections.Counter(x['category'] for x in findings))}))
