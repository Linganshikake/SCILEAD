"""Summarize actual completed artifacts; never infer success from a running process."""
from pathlib import Path
import json,hashlib,collections,datetime,sys,shutil
R=Path(__file__).resolve().parents[1];S=R/'remote_snapshot';D=R.parent/'20261021_diagnostic';P=R.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,lines):p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def pct(v):return f'{100*v:.2f}'
STAGES={'Fully LLM':'fully_llm','Fully CS':'fully_cs','Partially Stage1':'partially_stage1','Partially Stage2':'partially_stage2'}
def main():
    assert read(S/'formal_remote_complete.json')['status']=='COMPLETE'
    scope=read(R/'config/scope42.json');ids=scope['eligible_ids'];gold=read(R/'evaluation/gold_subset.json');batch=read(S/'batch_status.json');raw=read(S/'extraction/raw_output.json');prepared=read(S/'extraction/prepared_output.json')
    evals={k:read(R/'evaluation'/('llama3_'+v)/'metrics_with_f1.json')['aggregate'] for k,v in STAGES.items()}
    gptevals={k:read(R/'evaluation'/('gpt41_'+v)/'metrics_with_f1.json')['aggregate'] for k,v in STAGES.items()}
    norms={k:read(R/'evaluation'/('llama3_'+v)/'evaluation_input_fixed42.json') for k,v in STAGES.items()}
    events={};usage={};all_calls=[]
    def summarize(name,paths,reused=False):
        items=[]
        for p in paths:
            x=read(p);q=read(p.with_name('request.json'));actual=x['actual_generation'];assert q['do_sample'] is False and q['seed']==0
            row={'complete_file':str(p.relative_to(R)),'request_sha256':sha(p.with_name('request.json')),'budget':q['max_new_tokens'],'reused_generation':reused,**actual,'call_wall_seconds':x['seconds'],'process_peak_rss_bytes':x['process_peak_rss_bytes']};items.append(row);all_calls.append(dict(row,stage=name))
        return {'calls':len(items),'input_tokens':sum(x['input_tokens'] for x in items),'output_tokens':sum(x['output_tokens'] for x in items),'generation_seconds':sum(x['generation_seconds'] for x in items),'call_wall_seconds':sum(x['call_wall_seconds'] for x in items),'finish_reasons':dict(collections.Counter(x['finish_reason'] for x in items)),'peak_gpu_allocated_bytes':max((x['peak_allocated_bytes'] for x in items),default=0),'calls_detail':items}
    reuse=read(R/'config/reuse.json')
    usage['new_extraction']=summarize('new_extraction',[S/'extraction'/p.removesuffix('.pdf')/'extraction/calls/000000/complete.json' for p in ids if p not in reuse and (S/'extraction'/p.removesuffix('.pdf')/'extraction/calls/000000/complete.json').exists()])
    usage['reused_extraction']=summarize('reused_extraction',[S/'extraction'/p.removesuffix('.pdf')/'raw/calls/000000/complete.json' for p in reuse],True)
    paths={'fully_llm':S/'normalization/fully_llm','partially_stage1':S/'normalization/partially/stage1','partially_stage2':S/'normalization/partially/stage2'}
    for name,path in paths.items():
        usage[name]=summarize(name,sorted((path/'calls').glob('*/complete.json')));events[name]=[read(p) for p in sorted((path/'calls').glob('*/field_context.json'))]
    summary={'paid_api_calls':0,'generation_calls_new':sum(v['calls'] for k,v in usage.items() if k!='reused_extraction'),'generation_calls_reused':4,'input_tokens_new':sum(v['input_tokens'] for k,v in usage.items() if k!='reused_extraction'),'output_tokens_new':sum(v['output_tokens'] for k,v in usage.items() if k!='reused_extraction'),'stages':usage,'extraction_wall_seconds':batch['extraction_wall_seconds'],'cs_seconds':read(S/'normalization/fully_cs/complete.json')['seconds'],'remote_partial_seconds':read(S/'partial_status.json')['seconds'],'note':'Local Hugging Face generations, not API requests. Reused four paper responses are not charged again. Token sum spans different normalization stages; CS embedding calls are separate.'};save(R/'generation_usage.json',summary)
    summary['fully_llm_wall_seconds']=read(S/'normalization/fully_llm/timing.json')['seconds']
    summary['formal_remote_wall_seconds_including_offline_replay']=(S/'formal_remote_complete.json').stat().st_mtime-(S/'launch.json').stat().st_mtime
    summary['new_pure_generation_seconds']=sum(v['generation_seconds'] for k,v in usage.items() if k!='reused_extraction')
    save(R/'generation_usage.json',summary)
    states=[];formatted=[]
    for pid in ids:
        v=batch['papers'][pid];aud=v.get('format_audit',{});row={'paper_id':pid,'gold_tdmrs':len(gold[pid]['TDMs']),'generation_status':v['generation_status'],'parse_status':v.get('parse_status','BLOCKED'),'normalization_status':'COMPLETE' if pid in prepared else 'BLOCKED','evaluation_status':'COMPLETE_FIXED42','reused_generation':pid in reuse,'extraction_records':v.get('records'),'format_applied':v.get('format_applied',False),'failure_reason':v.get('reason'),'raw_output_path':str((S/'extraction'/pid.removesuffix('.pdf')/('raw' if pid in reuse else 'extraction')/'output.json').relative_to(R)),'source_documents':len(raw[pid]['source_documents']) if pid in raw else None,'normalization':{}}
        if pid in prepared:
            parsed=json.loads(prepared[pid]['output']);assert len(parsed)==row['extraction_records'];assert prepared[pid]['source_documents']==raw[pid]['source_documents']
            rawtext=raw[pid]['output'];candidate=prepared[pid]['output'];assert candidate==rawtext or candidate==rawtext[aud['span'][0]:aud['span'][1]]
            formatted.append({'paper_id':pid,'approved_rule_v1_applied':row['format_applied'],'original_text_sha256':hashlib.sha256(rawtext.encode()).hexdigest(),'normalization_input_text_sha256':hashlib.sha256(candidate.encode()).hexdigest(),'verbatim_array_preserved':True,'rows':len(parsed),'result_types':aud['result_types'],'duplicate_records':len(parsed)-len({json.dumps(x,sort_keys=True) for x in parsed})})
        for label,name in STAGES.items():
            n=norms[label][pid]['normalized_output'];counts={k:sum(x[k] is None for x in n) for k in ['Task','Dataset','Metric']};calls=[x for x in events.get(name,[]) if x['paper_id']==pid]
            row['normalization'][name]={'records':len(n),'null_fields':counts,'model_calls':len(calls)}
        states.append(row)
    states.append({'paper_id':'1912.08777.pdf','gold_tdmrs':36,'generation_status':'BLOCKED','reason':'55324 input tokens; native8192; no source truncation, Rope change or model switch'})
    save(R/'experiment_manifest.json',{'scope':scope,'source_commit':'8bf74b0a830feb7035c6166dce3394dc344ae532','papers':states,'completed_generation_papers':sum(x['generation_status']=='COMPLETE' for x in states),'valid_extraction_papers':len(prepared),'valid_extraction_gold_tdmrs':sum(len(gold[p]['TDMs']) for p in prepared),'evaluation_scope_papers':42,'evaluation_scope_gold_tdmrs':259})
    save(R/'format_application_audit.json',formatted)
    save(R/'normalization/field_call_index.json',events)
    canonical={
        'extraction/output.json':'extraction/raw_output.json',
        'extraction/prepared_output.json':'extraction/prepared_output.json',
        'normalization/fully_llm/normalized_output.json':'normalization/fully_llm/normalization/normalized_output.json',
        'normalization/fully_cs/normalized_output.json':'normalization/fully_cs/normalized_output.json',
        'normalization/partially/stage1/normalized_output.json':'normalization/partially/stage1/partially_masked_normalization/partially_masked_normalized_output.json',
        'normalization/partially/stage2/normalized_output.json':'normalization/partially/stage2/leaderboard_normalized_output.json'}
    for target,source in canonical.items():
        dest=R/target;data=(S/source).read_bytes();dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==data
        else:dest.write_bytes(data)
    save(R/'canonical_output_index.json',{k:{'source':'remote_snapshot/'+v,'sha256':sha(R/k),'byte_identical_copy':True} for k,v in canonical.items()})
    for name in STAGES.values():
        source=R/'evaluation'/('llama3_'+name);target=R/'normalization'/name;target.mkdir(parents=True,exist_ok=True)
        save(target/'output_index.json',{'evaluation_input':str((source/'evaluation_input_fixed42.json').relative_to(R)),'evaluation_input_includes_failed_empty_predictions':True,'raw_actual_normalized_output':'See remote_snapshot/normalization; failures never inserted into raw outputs'})
    save(R/'extraction/output_index.json',{'raw_output':'remote_snapshot/extraction/raw_output.json','approved_normalization_input':'remote_snapshot/extraction/prepared_output.json','valid_papers':list(prepared),'failed_papers':[p for p in ids if p not in prepared]})
    report=['# SCILEAD Llama-3 70B：42篇正式子集实验','','本轮执行 A/B/C/D/E；没有运行 Cold Start、threshold=2、Llama-2 或付费API。',f'成功生成 {sum(x["generation_status"]=="COMPLETE" for x in states)}/42 篇；格式有效 {len(prepared)}/42 篇，实际有效输入 Gold 覆盖 {sum(len(gold[p]["TDMs"]) for p in prepared)}/259。固定分母评价42篇/259条Gold。超长论文另列 BLOCKED，不能称为完整43篇复现。','','## 设置与流程','','冻结证据 → 官方 Llama-3 Zero-shot / RetrievalQA stuff → 经批准的格式规则v1 → Fully LLM / CS / Partially两阶段 → 未修改官方评价。', '模型 revision：50fd307e57011801c7833c87efa1984ddf2db42f；A80080GB；作者4-bit FP4，模型bfloat16，量化计算float32；greedy、seed0。Extraction预算1024；标准化15；Partially Stage2 100。保持原始EOS与模板，不套用GPT无上限配置。','标准化候选由完整43篇Gold构造23/71/26名称；Partially掩码仍用完整27榜、seed0。Gold对应答案不进入抽取输入。','生成失败或格式失败保持原样；只在独立evaluation_input_fixed42.json中记空预测以固定分母。','','## 官方元组指标（百分制，P / R / F1）','','F1=2PR/(P+R)，P/R为官方逐篇Macro均值；不是逐篇F1平均。','','|指标|'+'|'.join(STAGES)+'|','|---|'+'---|'*len(STAGES)]
    for k in next(iter(evals.values())):report.append('|'+k+'|'+'|'.join(' / '.join(pct(evals[label][k][x]) for x in ['Precision','Recall','F1']) for label in STAGES)+'|')
    report+=['','## 排行榜（27榜、131条范围内Gold条目）','','|设置|LR|有效非空榜率|PC|RC|官方RBO|独立论文ID AO|','|---|---:|---:|---:|---:|---:|---:|']
    for label,name in STAGES.items():
        e=R/'evaluation'/('llama3_'+name);b=read(e/'leaderboard_official.json')['gold_results'];a=read(e/'leaderboard_supplementary.json');report.append('|'+label+'|'+'|'.join(pct(x) for x in [a['LR_exact_tdm_hit'],a['LR_nonempty_finite_result'],b['Paper Coverage'],b['Result Coverage'],b['RBO'],a['AO_paper_id_macro_all_gold_boards']])+'|')
    report+=['','官方RBO比较去重后的结果数值排名；独立AO比较论文ID。两者不能混为一个指标。','','## 覆盖与失败','','|论文|Gold数|证据数|抽取条数|格式|Fully LLM null字段|Result/TDM/TDMR F1|','|---|---:|---:|---:|---|---:|---|']
    pm=read(R/'evaluation/llama3_fully_llm/per_paper_metrics.json')
    for x in states[:-1]:report.append('|'+ '|'.join([x['paper_id'],str(x['gold_tdmrs']),str(x['source_documents']),str(x['extraction_records']),x['parse_status']+(('：'+str(x['failure_reason'])) if x['failure_reason'] else ''),str(sum(x['normalization']['fully_llm']['null_fields'].values())),' / '.join(pct(pm[x['paper_id']][k]['F1']) for k in ['Result IIM','TDM','TDMR'])])+'|')
    report+=['','## 运行记录',f'新增本地模型生成 {summary["generation_calls_new"]} 次；复用4次已有抽取；付费API为0次。新增输入 {summary["input_tokens_new"]:,} Tokens，输出 {summary["output_tokens_new"]:,} Tokens。',f'本轮Extraction墙钟 {summary["extraction_wall_seconds"]/60:.1f} 分钟；CS {summary["cs_seconds"]:.1f} 秒；CS+Partially两阶段共 {summary["remote_partial_seconds"]/60:.1f} 分钟。模型加载时间包含在各阶段墙钟中；详细纯生成时间和峰值显存见 generation_usage.json。','短标准化响应仍按官方 `[2:]` 处理；未在候选集合中的答案保留null。达到15 Tokens的响应没有擅自扩限或重试，EOS统计见调用记录。','','## 可比性与边界','','同42篇GPT参考见 comparison_with_gpt41.md。GPT为固定快照但不设客户端输出上限，Llama保持作者预算；提示模板也按各自官方模型分支。不是控制所有生成参数的纯模型因果比较。','GPT Partially是历史43篇动态流程输出的42篇筛选；本轮只在可解析的42篇子集输入上动态更新，更新历史不完全相同。','原论文为43篇295Gold与27榜140条，不能将本轮分数直接相减称为全量复现差距。原文与本地硬件、冻结PDF证据、依赖兼容版本和格式协议等差异均需披露，未经对照实验不作单因素归因。','','## 文件与复核','','原始生成、逐字段请求/候选顺序/响应、标准化真实输出均在 remote_snapshot；evaluation 中保存官方分数、逐篇指标、严格数值辅助指标及259条Gold逐行对照。','完整性、Prompt/证据不变及官方流程离线重放验证见 verification.json。继续运行说明见 README.md。']
    report[3]=f'取得42/42篇原始生成响应（41篇EOS结束、1篇达到长度预算）；格式有效 {len(prepared)}/42 篇，实际有效输入 Gold 覆盖 {sum(len(gold[p]["TDMs"]) for p in prepared)}/259。固定分母评价42篇/259条Gold。超长论文另列 BLOCKED，不能称为完整43篇复现。'
    report=[x.replace('短标准化响应仍按官方 `[2:]` 处理；未在候选集合中的答案保留null。达到15 Tokens的响应没有擅自扩限或重试，EOS统计见调用记录。','短标准化响应仍按官方 `[2:]` 处理。Fully LLM拒绝不在候选集合中的答案并保留null；Partially按原版条件接受已有名称、动态新增名称或拒绝。Fully有1次、Partially Stage1有4次响应达到15 Tokens预算，真实响应保留，没有扩限或重试。') for x in report]
    at=report.index('## 可比性与边界')
    peak=max(x['peak_gpu_allocated_bytes'] for x in usage.values())/1024**3
    extra=[
        f'远程正式启动至完成离线重放共 {summary["formal_remote_wall_seconds_including_offline_replay"]/60:.2f} 分钟；其中Fully LLM墙钟 {summary["fully_llm_wall_seconds"]/60:.2f} 分钟，新增纯生成累计 {summary["new_pure_generation_seconds"]/60:.2f} 分钟。记录的最大GPU allocated峰值约 {peak:.2f} GiB（含复用诊断生成）；它不等于驱动层整卡占用。结束检查GPU已释放至0 MiB，服务器未关机；AutoDL租用费用未核算。',
        '', '## 格式定位与协议', '',
        '42篇底层pipeline原始返回均核对为“请求Prompt + 作者包装后的响应”，没有重复拼接Prompt或错误套用chat template。说明性前缀来自模型自身生成。官方README允许在标准化前纠正格式，但未定义具体算法；本轮规则v1经过用户明确批准，属于需要披露的格式协议。官方标准化本身将Result转为字符串，适配层不提前改写数值。',
        f'40篇有效输出中，{sum(x["approved_rule_v1_applied"] for x in formatted)}篇移除了批准的外层包装；数组内部逐字符不变。`2105.03654.pdf` 的1024 Tokens响应截断；`1901.10430.pdf` 虽正常EOS却返回三个独立数组，均未补全、拼接或重新生成。',
        '', '## 结果解读与辅助诊断', '',
        'Fully LLM与CS复用同一份271条Extraction，是本轮可直接配对的标准化对照：TDMR F1分别27.25%与24.64%。同范围冻结GPT Fully LLM为43.16%；其Result IIM F1为72.06%，本轮为42.34%。但本轮TDM F1为65.86%，高于GPT的61.83%，说明名称三元组匹配与正确数值及其绑定需要分开评估；不能将整体差距归结为名称标准化。',
        'Partially Stage1的470次名称调用接受已有候选412次，新增10个Task和13个Dataset，其余35次为null。Stage2共175次模型调用，其中86条TDM发生改变，全部Result保持原值；TDMR F1由10.12%到22.04%。这是原版流程两个阶段的观察，不用于选择性报告较高分。',
        '额外严格数值检查：Result IIM F1为25.99%；Fully LLM、CS、Partially Stage1、Stage2的严格一对一TDMR F1分别14.45%、11.77%、4.64%、11.28%。该辅助检查要求整个字符串可解析为Decimal，不接受百分号或“均值±波动”等表达，故不能把全部差额视为错误中心值。',
        '`1511.08308.pdf` 保留重复预测后，官方脚本对部分设置给出TDMR Recall=1.5；未剪裁或改写该官方结果。额外一对一严格评价用于揭示重复计数影响，不能替代官方分数。',
        '具体证据核对：`2020.findings-emnlp.378.pdf` 的正确最佳值已在Table 5，但抽取混入Table 2变体并发生跨列绑定；`D18-1279.pdf` 选择了比较基线值，并将Spanish列数值绑定到CoNLL-2003。这些错误在Extraction发生，标准化名称无法修复；扁平表格可能增加难度，但没有额外解析对照，不能认定其为唯一原因。完整页码和数值见 [人工案例核对](inspection/manual_cases.md)。',
        ''
    ]
    report[at:at]=extra
    write(R/'run_report.md',report)
    comp=['# 与GPT-4.1的同42篇范围比较','','以下为同范围描述性比较，分数均为百分制。历史GPT输出没有重新请求。Partially动态候选更新历史与输出预算存在差异，不是单一模型因素实验。','','|设置|指标|Llama-3 P/R/F1|GPT-4.1 P/R/F1|F1差（百分点）|','|---|---|---|---|---:|']
    for label in STAGES:
        for k,v in evals[label].items():
            g=gptevals[label][k];comp.append('|'+label+'|'+k+'|'+' / '.join(pct(v[x]) for x in ['Precision','Recall','F1'])+'|'+' / '.join(pct(g[x]) for x in ['Precision','Recall','F1'])+f'|{100*(v["F1"]-g["F1"]):+.2f}|')
    write(R/'comparison_with_gpt41.md',comp)
    paper=read(D/'references/paper_metrics.json');lines=['# 原论文参考与本轮结果','','[官方论文](https://aclanthology.org/2024.emnlp-main.453.pdf)。原文43篇；本轮42篇；仅并列参考，不计算正式差值。百分制P/R/F1。','','|设置|指标|原论文Llama-3（43篇）|本轮Llama-3（42篇）|','|---|---|---|---|']
    for name,m in paper['metrics'].items():
        for key,vals in m.items():
            k=key.replace(' Exact Match','');labels=['Partially Stage1','Partially Stage2'] if name=='Partially' else [name]
            local_values='；'.join(label+': '+' / '.join(pct(evals[label][k][x]) for x in ['Precision','Recall','F1']) for label in labels)
            lines.append('|'+name+'|'+key+'|'+' / '.join(f'{x:.2f}' for x in vals)+'|'+local_values+'|')
    lines+=['','原文未将Partially元组表明确绑定到具体阶段输出JSON，本报告并列保留Stage1和Stage2，不挑较高值作为原论文对应结果。','原论文表5的AO名称沿用原文；本报告分别列出官方数值RBO与独立论文ID AO，不能未经定义核验直接互换。','Llama-3 Cold Start 是原文另有实验，按本轮限制只列待确认，未执行。'];write(R/'comparison_with_paper.md',lines)
    write(R/'context_scope.md',['# 固定范围','',f'42篇、259 Gold；27榜、131榜内条目。排除1912.08777.pdf（55324输入Tokens，36 Gold）。','原生8192上下文；抽取预留1024。不截断证据、不过滤表格、不改RoPE。候选名称/掩码仍来自完整43篇Gold。','失败为空仅用于独立评价输入，报告有效覆盖，不把失败悄悄剔除。'])
    write(R/'format_audit.md',['# 格式规则v1实际应用','','已获用户明确批准。只保留唯一完整数组；移除精确中性前缀或完整代码围栏。数组内部逐字符不变。Result数值及重复记录保留，随后由官方标准化str()转换。','未知前后缀、多数组、重复键、非法字段、非有限数、截断均失败；不自动重试。',f'本次格式有效{len(prepared)}篇；实际移除外层包装{sum(x["approved_rule_v1_applied"] for x in formatted)}篇。逐篇原文/整理文本SHA和重复数见format_application_audit.json。','底层诊断函数保留原来的候选状态字段；是否正式应用以本目录approval.json及format_application_audit.json为准。'])
    print(json.dumps({'reports_written':True,'valid_extraction_papers':len(prepared),'new_generations':summary['generation_calls_new']}))
if __name__=='__main__':main()
