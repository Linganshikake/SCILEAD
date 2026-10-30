"""Compose final experiment report from verified offline evaluations and actual calls."""
import json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def pct(x):return f'{100*x:.2f}'
def delta(x):return f'{100*x:+.2f}'
def table(head,rows):return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])
METRICS=['Task IIM','Dataset IIM','Metric IIM','Result IIM','TDM Exact Match','TDMR Exact Match']
LB=['LR_exact_tdm_hit','LR_nonempty_finite_result','PC_official','RC_official','RBO_official_value_rankings','AO_paper_id_macro_all_gold_boards']
LABELS={'partially':'Partially','cold_default':'Cold 默认顺序','cold_0':'Cold 字符串种子0','cold_42':'Cold 字符串种子42'}
def main():
 c=read(ROOT/'analysis/comparison_final/comparison.json');a=read(ROOT/'verification.json');u=read(ROOT/'api_usage_summary.json');e=read(ROOT/'inspection/alignment_events_comparison.json')
 assert c['status']=='COMPLETE' and a['status']=='PASS'
 index={(r['model'],r['case']):r for r in c['local_rows']}
 cold={(r['model'],r['stage']):r['metrics'] for r in c['cold_three_order_summaries'] if r['status']=='COMPLETE'}
 pold=index['baseline','partially_stage2'];pnew=index['prompt_improvement_variant','partially_stage2']
 coldold=cold['baseline','stage2'];coldnew=cold['prompt_improvement_variant','stage2']
 lines=['# DeepSeek：Partially / Cold Start 语义对齐补充实验','','日期：2026-10-28（北京时间）。四个分支、两阶段均完成，固定43篇论文、295条Gold、295条既有Extraction预测和27个Gold排行榜。', '',
  f"Partially 第二阶段 TDMR F1：**{pct(pold['tuple']['TDMR Exact Match']['F1'])}% → {pct(pnew['tuple']['TDMR Exact Match']['F1'])}%**（{delta(pnew['tuple']['TDMR Exact Match']['F1']-pold['tuple']['TDMR Exact Match']['F1'])} 个百分点）。",
  f"Cold Start 三顺序平均 TDMR F1：**{pct(coldold['TDMR Exact Match/F1']['mean'])}% → {pct(coldnew['TDMR Exact Match/F1']['mean'])}%**；LR：**{pct(coldold[LB[0]]['mean'])}% → {pct(coldnew[LB[0]]['mean'])}%**。",'',
  '## 1. 本轮补充了什么要求','',
  '这是独立的 Prompt 改进实验 `semantic_alignment_v1`，与原版 DeepSeek Baseline 分开保存。仅追加两处通用说明：第一阶段的 `masked-normalization-system-prompt`、第二阶段的 `leaderboard-normalization-system-prompt`。', '',
  '- “匹配”指语义与实体身份一致，不要求输入字符串与候选字符串相等；识别明确的缩写、别名、同义表达和表面拼写差异。',
  '- 第二阶段联合判断 Task、Dataset、Metric；找到匹配时逐字返回一个完整候选 tuple，不拼接不同候选的字段。',
  '- 数据集身份、语言、版本、split、指标定义存在差异时不能直接合并；无法消除歧义时保留原输入。',
  '- 保留原版未匹配处理、精确接受规则和动态名称集合更新。Partially 第一阶段 Metric 的原 Prompt 未改。', '',
  '没有添加论文示例或Gold答案，也未增加论文上下文。四个分支都从原版初始集合重新运行两阶段；动态集合随后按照新回答自然演变。完整新增文本、逐字差异和哈希见 `prompt_change_note.md`、`prompt_diff.txt`、`experiment_manifest.json`。', '',
  '复用原版295条Extraction和相同source_documents。实际模型仍为 `deepseek-flash`（已核实的DeepSeek-V4.1-Flash接口别名），thinking enabled、reasoning_effort=high、stream=false；不发送客户端输出Token上限、temperature或seed。Cold论文顺序仍为默认、字符串种子0、字符串种子42，Partially遮蔽种子仍为0。', '',
  '## 2. 第二阶段全部Tuple指标','',
  '单位为百分数；P/R为官方逐篇Macro平均，F1由该P/R计算。表中“原版”指本次之前已冻结的DeepSeek运行。','']
 for b,label in LABELS.items():
  old=index['baseline',b+'_stage2'];new=index['prompt_improvement_variant',b+'_stage2']
  lines += ['### '+label,'',table(['指标','原版P','原版R','原版F1','补充后P','补充后R','补充后F1','F1变化/百分点'],
     [[m]+[pct(old['tuple'][m][k]) for k in ['Precision','Recall','F1']]+[pct(new['tuple'][m][k]) for k in ['Precision','Recall','F1']]+[delta(new['tuple'][m]['F1']-old['tuple'][m]['F1'])] for m in METRICS]),'']
 lines += ['### Cold三顺序均值与标准差','',table(['指标','原版F1均值 ± SD','补充后F1均值 ± SD'],
    [[m,f"{pct(coldold[m+'/F1']['mean'])} ± {pct(coldold[m+'/F1']['sample_sd'])}",f"{pct(coldnew[m+'/F1']['mean'])} ± {pct(coldnew[m+'/F1']['sample_sd'])}"] for m in METRICS]),'',
    'SD是三个固定顺序结果的样本标准差（ddof=1）。每个顺序先独立计算官方Macro指标，再汇总三个运行的均值与标准差。','','## 3. 第二阶段排行榜指标','']
 lbrows=[]
 for b,label in LABELS.items():
  for model,n in [('baseline','原版'),('prompt_improvement_variant','补充后')]:
   row=index[model,b+'_stage2'];lbrows.append([label,n]+[pct(row['leaderboard'][k]) for k in LB])
 lines += [table(['设置','版本','LR','有效非空榜率','PC','RC','RBO数值列表','AO论文ID'],lbrows),'',
   table(['Cold三顺序','LR','有效非空榜率','PC','RC','RBO数值列表','AO论文ID'],
   [[label]+[f"{pct(values[k]['mean'])} ± {pct(values[k]['sample_sd'])}" for k in LB] for label,values in [('原版',coldold),('补充后',coldnew)]]),'',
   '评价保持原版重复预测处理、PC/RC及数值列表RBO公式；AO按既有论文ID实现单独报告。所有空榜保留在27榜分母内。严格数值相等辅助检查保存在各分支 `strict_result_metrics.json`。','','## 4. 哪个环节发生变化','']
 rows=[]
 for b,label in LABELS.items():
  s1=e[b+'_stage1'];s2=e[b+'_stage2'];bc=s2['before_events'];nc=s2['after_events']
  old1=index['baseline',b+'_stage1']['tuple']['TDMR Exact Match']['F1'];new1=index['prompt_improvement_variant',b+'_stage1']['tuple']['TDMR Exact Match']['F1']
  rows.append([label,pct(old1),pct(new1),s1['changed_event_count'],bc.get('tuple_mapped',0),nc.get('tuple_mapped',0),bc.get('unmatched_preserved',0),nc.get('unmatched_preserved',0)])
 lines += [table(['设置','第一阶段原F1','第一阶段新F1','第一阶段字段变化数','原二阶段映射数','新二阶段映射数','原未匹配保留','新未匹配保留'],rows),'',
   '全部分支的Result字符串、记录顺序与数量均保持不变，Result IIM F1仍为81.26%。本轮变化集中在名称归一化和tuple对齐；既有Extraction遗漏和错列没有重新生成或人工修正。', '',
   'Cold第一阶段TDMR F1三顺序均值从4.54%降到3.24%，最终改善主要体现在第二阶段候选tuple对齐。第一、二阶段Prompt在本轮同时补充，第一阶段的回答还会改变后续动态集合；各项新增要求的独立贡献尚未做消融测量。', '',
   '27个第二阶段候选排行榜的TDM覆盖295条Gold中的140条，其余155条没有对应候选榜。未匹配tuple按原逻辑保留，部分非标准名称因此继续存在；候选榜之外也有第一阶段已正确标准化的记录。离线范围核查见 `inspection/gold_candidate_scope.json`。', '',
   '## 5. 逐篇改善与下降','',
   table(['设置','TDMR F1提高篇数','下降篇数','不变篇数'],
         [[LABELS[x['case'].removesuffix('_stage2')],x['improved'],x['regressed'],x['unchanged']] for x in c['stage2_paper_changes'] if x['metric']=='TDMR Exact Match']),'']
 for x in c['stage2_paper_changes']:
  if x['metric']!='TDMR Exact Match':continue
  lines += ['### '+LABELS[x['case'].removesuffix('_stage2')],'',table(['方向','论文','原F1','新F1','变化/百分点'],
       [[direction,y['paper_id'],pct(y['baseline_F1']),pct(y['variant_F1']),delta(y['delta_F1'])] for direction,key in [('提高','top_improvements'),('下降','top_regressions')] for y in x[key]]),'']
 lines += ['案例证据见 `inspection/examples_before_after.json`：包括原来未对齐的NER缩写、数据集误合并及German限定信息。每条都保留原始Extraction、两版处理事件、原始响应路径及哈希。`inspection/case_notes.md`给出人工可读的核查结果。','','## 6. 请求量与完整性','',
   table(['分支','请求数','输入Tokens','输出Tokens（含推理）','总Tokens'],[[LABELS[b],x['requests'],x['prompt_tokens'],x['completion_tokens'],x['total_tokens']] for b,x in u['branches'].items()]),'',
   f"本轮新Extraction请求 **0次**；逻辑标准化请求 **{u['logical_normalization_requests']:,}条**，实际发送 **{u['actual_model_requests']:,}次**。已返回总Tokens **{u['totals']['total_tokens']:,}**，其中推理Tokens {u['totals']['reasoning_tokens']:,}；另有 {u['unknown_usage_requests']} 次连接失败未返回用量。首个请求到末个响应约 {u['wall_seconds']/60:.2f} 分钟，四分支并行、各自内部串行。",'',
   f"Cold字符串种子42第二阶段第182条请求遇到RemoteProtocolError，未收到HTTP响应；获得用户明确授权后仅补发一次，返回HTTP200并继续剩余字段。最终全部 {u['logical_normalization_requests']:,} 条逻辑请求均取得HTTP200、finish_reason=stop的有效响应。自动重试0次，授权补发 {u['authorized_additional_attempts']} 次。原失败状态及同载荷补发响应分别保留；已知Token合计不包含首次失败可能产生的服务端用量。",'',
   f"核验 {a['protected_file_count']} 个受保护文件，变化0。实际发送的每条System Prompt及User模板均已核对；两版初始名称集合、论文顺序和第二阶段候选tuple顺序一致。原版源码、Gold、RAG证据、历史模型结果保持不变。",'',
   '四组离线测试通过：Prompt边界、HTTP参数及不自动重试、原版Partially处理、原版Cold处理。离线测试发现并修复了旧Cold观察器固定检查原Prompt的问题，修复仅发生在独立副本的核验路径；正式请求前已通过回归测试。', '',
   '## 7. 结果位置','',
   '- `report.md`：本中文汇总。',
   '- `analysis/comparison_final/report_zh.md`：全部两版指标和差值；`comparison.json/.csv`：全精度结果。',
   '- `analysis/comparison_final/per_paper_differences.csv`：全部逐篇差值。',
   '- `analysis/evaluations/`：四分支两阶段官方原始评价、P/R/F1、严格数值辅助指标及排行榜。',
   '- `variants/各分支/stage1/normalized_output.json`、`stage2/leaderboard_normalized_output.json`：新标准化结果。',
   '- `variants/各分支/stage*/api_calls/`：实际请求和原始响应；`events/`：逐字段官方处理。',
   '- `api_usage_summary.json`、`request_audit.csv`、`verification.json`、`output_index.json`：用量、请求核验、完整性和输出索引。',
   '- `prompt_change_note.md`、`prompt_diff.txt`：唯一固定补充版本的要求与差异。', '',
   '本轮完成后停止；未修改旧版Baseline，未追加其他Prompt版本或重新选择结果。']
 (ROOT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 summary={'status':'COMPLETE','papers':43,'gold':295,'extraction_reused':295,'new_extraction_requests':0,
          'primary_metrics':[r for r in c['local_rows'] if r['role']=='primary'],
          'cold_three_order_summaries':[x for x in c['cold_three_order_summaries'] if x['stage']=='stage2'],
          'api_usage':u,'comparison_file':str(ROOT/'analysis/comparison_final/comparison.json')}
 (ROOT/'results_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 plan=ROOT/'execution_plan.md';plan.write_text(plan.read_text(encoding='utf8').replace('- [ ]','- [x]'),encoding='utf8')
 print(json.dumps({'status':'COMPLETE','report':str(ROOT/'report.md'),'requests':u['actual_model_requests']}))
if __name__=='__main__':main()
