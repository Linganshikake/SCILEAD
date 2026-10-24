"""Offline diagnostic categories, explicitly separated from causal/semantic claims."""
from pathlib import Path
import json,decimal,collections,hashlib
R=Path(__file__).resolve().parents[1];S=R/'remote_snapshot'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def number(x):
    try:
        d=decimal.Decimal(str(x).strip());return d if d.is_finite() else None
    except decimal.InvalidOperation:return None
def main():
    raw=read(S/'extraction/prepared_output.json');gold=read(R/'evaluation/gold_subset.json');batch=read(S/'batch_status.json');summary={};details={}
    for stage in ['fully_llm','fully_cs','partially_stage1','partially_stage2']:
        e=R/'evaluation'/('llama3_'+stage);norm=read(e/'evaluation_input_fixed42.json');counts=collections.Counter();cases=[];overwrites=[];extra=[];duplicates=[]
        for pid in gold:
            pred=norm[pid]['normalized_output'];original=json.loads(raw[pid]['output']) if pid in raw else []
            for gi,g in enumerate(gold[pid]['TDMs']):
                if pid not in raw:kind='EXTRACTION_FORMAT_FAILED';indices=[]
                else:
                    indices=[j for j,x in enumerate(pred) if number(x['Result']) is not None and number(x['Result'])==number(g['Result'])]
                    exact=[j for j in indices if all(pred[j][k]==g[k] for k in ['Task','Dataset','Metric'])]
                    if exact:kind='STRICT_TDMR_MATCH'
                    elif not indices:kind='RESULT_NOT_PRESENT_AS_STRICT_NUMBER'
                    elif any(any(pred[j][k] is None for k in ['Task','Dataset','Metric']) for j in indices):kind='VALUE_PRESENT_WITH_NORMALIZATION_NULL'
                    else:kind='VALUE_PRESENT_NAMES_OR_BINDING_UNRESOLVED'
                counts[kind]+=1
                cases.append({'paper_id':pid,'gold_index':gi,'gold':g,'category':kind,'predictions':[{'index':j,'extracted':original[j],'normalized':pred[j]} for j in indices]})
            seen={}
            for j,x in enumerate(pred):
                key=(x['Task'],x['Dataset'],x['Metric'])
                if key in seen:overwrites.append({'paper_id':pid,'tdm':list(key),'earlier_index':seen[key],'later_index':j,'earlier_result':pred[seen[key]]['Result'],'later_result':x['Result'],'official_rule':'Later value overwrites if it converts to float and maps to target leaderboard; no max selection'})
                seen[key]=j
            goldnums={number(g['Result']) for g in gold[pid]['TDMs']};goldnums.discard(None)
            for j,x in enumerate(original):
                v=number(x['Result'])
                if v is not None and v not in goldnums:extra.append({'paper_id':pid,'prediction_index':j,'extraction':x,'classification':'NON_GOLD_NUMERIC_VALUE_CANDIDATE_NOT_PROVEN_BASELINE'})
            c=collections.Counter(json.dumps(x,sort_keys=True) for x in original)
            duplicates.extend({'paper_id':pid,'record':json.loads(k),'count':n} for k,n in c.items() if n>1)
        vals=read(e/'per_paper_metrics.json');overone=[{'paper_id':p,'metric':k,'component':a,'value':b} for p,v in vals.items() for k,x in v.items() for a,b in x.items() if b>1]
        summary[stage]={'gold_row_categories':dict(counts),'prediction_numeric_values_absent_from_gold':len(extra),'duplicate_extracted_record_groups':len(duplicates),'repeated_normalized_tdm_candidates':len(overwrites),'official_scores_over_one':overone}
        details[stage]={'gold_rows':cases,'extra_numeric_candidates':extra,'duplicate_records_retained':duplicates,'repeated_tdm_order':overwrites}
    calls={}
    for stage,folder in [('fully_llm','fully_llm'),('partially_stage1','partially/stage1'),('partially_stage2','partially/stage2')]:
        logs=S/'normalization'/folder/'calls';items=[read(p) for p in sorted(logs.glob('*/field_context.json'))];count=collections.Counter();groups=collections.defaultdict(list)
        for x in items:
            answer=x.get('raw_answer','');processed=x.get('official_answer_after_slice','');count['calls']+=1;count['non_newline_prefix_author_sliced_anyway']+=not answer.startswith('\n\n');count['candidate_match_after_official_slice']+=x.get('in_candidates',False);count['literal_None_after_slice']+=processed=='None'
            count['would_only_match_after_extra_strip_not_applied']+=not x.get('in_candidates',False) and processed.strip() in x['candidate_order'];groups[x['prompt_sha256']].append(x)
        repeated=[{'prompt_sha256':k,'count':len(v),'response_variants':len({x.get('raw_answer') for x in v})} for k,v in groups.items() if len(v)>1]
        calls[stage]={'counts':dict(count),'repeated_prompts_called_independently':repeated}
    save(R/'inspection/diagnostic_summary.json',summary);save(R/'inspection/diagnostic_details.json',details);save(R/'inspection/normalization_response_patterns.json',calls)
    lines=['# 实际错误与边界（离线诊断）','','以下分类不修改预测。数值相同不证明语义对应；非Gold数值不自动等于Baseline混入。未据Gold重写名称、补全结果或选择更高分输出。','','|配置|严格TDMR命中Gold行|格式失败Gold行|严格数值未出现|数值存在但含null|数值存在但名称/绑定不匹配|','|---|---:|---:|---:|---:|---:|']
    categories=['STRICT_TDMR_MATCH','EXTRACTION_FORMAT_FAILED','RESULT_NOT_PRESENT_AS_STRICT_NUMBER','VALUE_PRESENT_WITH_NORMALIZATION_NULL','VALUE_PRESENT_NAMES_OR_BINDING_UNRESOLVED']
    for k,v in summary.items():lines.append('|'+k+'|'+'|'.join(str(v['gold_row_categories'].get(c,0)) for c in categories)+'|')
    lines+=['','这些是以259条Gold逐行统计的辅助计数，不是官方Precision或Recall；同一预测值可能对应多个Gold值，不能当作一对一匹配总数。严格一对一辅助TDMR指标另存于evaluation。','','## 可直接验证的现象','']
    for pid,v in batch['papers'].items():
        if v.get('parse_status')=='FAILED':lines.append(f'- {pid}：{v.get("reason")}；原始响应保留，不进入标准化，固定42篇评价记空。')
    for stage,v in calls.items():lines.append(f'- {stage}：{v["counts"]}；重复Prompt仍逐次真实调用，共{len(v["repeated_prompts_called_independently"])}组；没有加入缓存。')
    lines+=['','## 代表性名称问题（按固定论文/Gold顺序取例，不筛选高分）','']
    for kind in categories[2:]:
        examples=[x for x in details['fully_llm']['gold_rows'] if x['category']==kind][:3]
        for x in examples:lines.append('- '+json.dumps(x,ensure_ascii=False))
    lines+=['','## 解读限制','','Baseline混入、Dev/Test混淆、表格读取错误需要回查论文证据。当前自动诊断只将它们列为待人工核对候选，不将所有额外数值强行归因于Baseline。','官方Result采用双向字符串包含关系，可能出现不同数值的匹配；严格整串Decimal检查单独报告。百分号、区间、±值不在严格辅助指标里被自动修正。','官方元组评价保留重复项的影响；同论文同TDM的排行榜构建使用后写覆盖。报告保留大于1的原版分数（若有），不裁剪、不去重改分。']
    (R/'inspection/findings.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps({'inspection_complete':True,'settings':len(summary)}))
if __name__=='__main__':main()
