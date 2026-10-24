from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parents[1];OLD=R.parent/'20261021_formal42';S=R/'remote_snapshot'
STAGES=['fully_llm','fully_cs','partially_stage1','partially_stage2']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,lines):p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def trip(v):return ' / '.join(f'{100*v[k]:.2f}' for k in ['Precision','Recall','F1'])
def main():
    for p in (S/'token2048_diagnostic').rglob('*'):
        if p.is_file() and p.suffix in ['.json','.txt']:
            dest=R/p.relative_to(S);dest.parent.mkdir(parents=True,exist_ok=True);data=p.read_bytes()
            if dest.exists():assert dest.read_bytes()==data
            else:dest.write_bytes(data)
    recovered=read(R/'format_v2/recovery_manifest.json');usage={};allcalls=[]
    for p in S.rglob('complete.json'):
        if p.parent.parent.name not in ['new_calls','calls']:continue
        x=read(p)
        if 'actual_generation' not in x:continue
        stage=p.relative_to(S).parts;name='/'.join(stage[:-3]);q=read(p.with_name('request.json'));g=x['actual_generation'];row={'file':str(p.relative_to(R)),'stage':name,'request_sha256':sha(p.with_name('request.json')),'budget':q['max_new_tokens'],**g,'call_wall_seconds':x['seconds']};allcalls.append(row)
    for x in allcalls:
        u=usage.setdefault(x['stage'],{'calls':0,'input_tokens':0,'output_tokens':0,'generation_seconds':0,'finish_reasons':collections.Counter()});u['calls']+=1
        for k in ['input_tokens','output_tokens','generation_seconds']:u[k]+=x[k]
        u['finish_reasons'][x['finish_reason']]+=1
    reuse={stage:read(S/'format_v2/normalization'/stage/'done.json') for stage in STAGES if stage!='fully_cs'}
    u={'new_local_generations':len(allcalls),'new_extraction_calls':sum('token2048_diagnostic/extraction'==x['stage'] for x in allcalls),'new_normalization_calls':sum(x['stage']!='token2048_diagnostic/extraction' for x in allcalls),'paid_api_calls':0,'new_input_tokens':sum(x['input_tokens'] for x in allcalls),'new_output_tokens':sum(x['output_tokens'] for x in allcalls),'new_generation_seconds':sum(x['generation_seconds'] for x in allcalls),'stages':usage,'main_v2_reuse':reuse,'historical_audit_offline_replay_calls':sum(read(p)['offline_replay_requests'] for p in (S/'audit/official_replay').glob('*/done.json')),'actual_calls':allcalls};save(R/'reports/usage_summary.json',u)
    before_raw=read(OLD/'remote_snapshot/extraction/prepared_output.json');raw=read(R/'format_v2/extraction/prepared_output.json');comparison={};changes={};actions=[]
    for stage in STAGES:
        d=R/'format_v2/evaluation'/stage;v2=read(d/'metrics_with_f1.json')['aggregate'];v1=read(OLD/'evaluation'/('llama3_'+stage)/'metrics_with_f1.json')['aggregate'];comparison[stage]={k:{'v1':v1[k],'v2':v2[k],'delta':{x:v2[k][x]-v1[k][x] for x in v2[k]}} for k in v2}
        new=read(S/'format_v2/normalization'/stage/'normalized_output.json');old=read(OLD/'evaluation'/('llama3_'+stage)/'evaluation_input_fixed42.json')
        changed=[p for p in before_raw if new[p]!=old[p]];changes[stage]={'unchanged_old_papers':40-len(changed),'changed_old_papers':changed,'new_papers':[p for p in new if p not in before_raw]}
        dest=R/'format_v2/normalization'/stage/'normalized_output.json';data=(S/'format_v2/normalization'/stage/'normalized_output.json').read_bytes();dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==data
        else:dest.write_bytes(data)
        a1=read(OLD/'evaluation'/('llama3_'+stage)/'per_paper_metrics.json');a2=read(d/'per_paper_metrics.json');save(d/'per_paper_v1_v2.json',{p:{'v1':a1[p],'v2':a2[p],'delta':{k:{x:a2[p][k][x]-a1[p][k][x] for x in a2[p][k]} for k in a2[p]}} for p in a2})
    for p in sorted((S/'format_v2/normalization/partially_stage1/events').glob('*.json')):
        ev=read(p);c=ev['context'];ans=ev['official_answer_after_slice'];field=c['field'];candidate=c['candidate_state'][field]['order'];action='existing_candidate' if ans in candidate else ('new_label' if field in ['Task','Dataset'] and ans==c['source_row'][field] else 'null')
        actions.append({'paper_id':c['paper_id'],'record_index':c['record_index'],'field':field,'origin':ev['origin'],'action':action,'accepted_name':ans if action!='null' else None})
    save(R/'format_v2/normalization/partially_stage1/update_events.json',actions);save(R/'format_v2/comparison_values.json',comparison);save(R/'format_v2/downstream_change_audit.json',changes)
    lines=['# V1 / V2 固定42篇配对比较','','范围均为42篇、259 Gold、27榜、131榜内Gold条目。差值使用未舍入值计算；百分制。F1由官方Macro P/R计算，不是逐篇F1平均。','','|设置|指标|V1 P/R/F1|V2 P/R/F1|F1差（百分点）|','|---|---|---|---|---:|']
    for stage,v in comparison.items():
        for metric,x in v.items():lines.append(f'|{stage}|{metric}|{trip(x["v1"])}|{trip(x["v2"])}|{100*x["delta"]["F1"]:+.6f}|')
    lines+=['','## 排行榜指标','','官方RBO比较数值列表；AO比较论文ID。两者不合并。','','|设置|版本|LR|非空榜率|PC|RC|RBO|AO|','|---|---|---:|---:|---:|---:|---:|---:|'];boards={}
    for stage in STAGES:
        boards[stage]={}
        for ver,d in [('V1',OLD/'evaluation'/('llama3_'+stage)),('V2',R/'format_v2/evaluation'/stage)]:
            x=read(d/'leaderboard_official.json')['gold_results'];y=read(d/'leaderboard_supplementary.json');vals={'LR':y['LR_exact_tdm_hit'],'nonempty':y['LR_nonempty_finite_result'],'PC':x['Paper Coverage'],'RC':x['Result Coverage'],'RBO':x['RBO'],'AO':y['AO_paper_id_macro_all_gold_boards']};boards[stage][ver]=vals;lines.append('|'+stage+'|'+ver+'|'+'|'.join(f'{100*v:.4f}' for v in vals.values())+'|')
        boards[stage]['delta']={k:boards[stage]['V2'][k]-boards[stage]['V1'][k] for k in boards[stage]['V2']}
    save(R/'format_v2/leaderboard_comparison_values.json',boards)
    lines+=['','## 变化来源','','新增10条记录只来自1901.10430.pdf的原有完整响应，没有新增Extraction。Partially在原固定队列第26位（零基25）重新核对动态状态，未将恢复论文追加到末尾。','各阶段原40篇是否改变见downstream_change_audit.json；每次复用核对paper/record/field、原始行、完整候选状态及其序列化、当前部分结果、真实Prompt和生成参数。不同位置的同名字段不共享缓存。']
    for stage,x in changes.items():lines.append(f'- {stage}：原40篇中{x["unchanged_old_papers"]}篇不变；变化论文={x["changed_old_papers"]}。')
    lines+=['','因此只有在上述变化清单为空时，分数差才可归于新增论文的可评预测；不预设动态状态一定改变后续结果。严格数值辅助指标及逐篇差值分别在各evaluation子目录，官方重复计数与Recall>1未剪裁。']
    write(R/'format_v2/comparison_v1_v2.md',lines)
    diag=read(S/'token2048_diagnostic/done.json');tc=read(S/'token2048_diagnostic/token_comparison.json');gen=diag['actual_generation'];p=read(S/'token2048_diagnostic/parse.json')
    diaglines=['# 单篇2048输出预算诊断','','这是独立预算诊断，不是V2原1024预算的格式修复。仅执行一次Extraction，未混入V2主结果。',f'输入{gen["input_tokens"]}，输出{gen["output_tokens"]} Tokens；停止原因{gen["finish_reason"]}；V2结构有效={p["ok"]}；记录数={p.get("records")}。',f'生成耗时{gen["generation_seconds"]:.3f}秒，GPU allocated峰值{gen["peak_allocated_bytes"]/1024**3:.3f}GiB。','唯一允许的生成参数变化为max_new_tokens 1024→2048；真实请求JSON与旧请求逐字段核对。',f'旧文本由固定tokenizer重建：长度匹配={tc["old_length_matches_logged"]}；末ID匹配={tc["old_last_id_matches_logged"]}；decode round-trip={tc["old_decode_roundtrip"]}。',f'新实际Token IDs与旧重建IDs的最长共同前缀={tc["longest_common_reconstructed_token_prefix"]}；前1024一致={tc["first1024_equal_to_reconstructed_old"]}；新文本含完整旧文本前缀={tc["new_text_starts_with_exact_old_text"]}。','历史没有保存完整生成IDs，因此此ID比较不能称为“两个实际历史张量完全一致”。新IDs为直接捕获，文本前缀另有独立核验。']
    if p['ok'] and gen['finish_reason']=='eos':
        diaglines+=['','|单篇设置|指标|P/R/F1（%）|','|---|---|---|']
        for stage in ['fully_llm','fully_cs']:
            for k,x in read(R/'token2048_diagnostic/evaluation'/stage/'metrics_with_f1.json').items():diaglines.append(f'|{stage}|{k}|{trip(x)}|')
    else:diaglines+=['','新输出仍不符合冻结V2规则，停止该分支；未继续4096、未重试、未运行该篇下游。']
    write(R/'token2048_diagnostic/diagnostic_report.md',diaglines)
    report=['# SCILEAD Llama-3 格式恢复与预算诊断报告','','|论文|原失败原因|是否恢复|规则|新Extraction|有效记录数|归属|','|---|---|---|---|---:|---:|---|','|1901.10430.pdf|正常EOS但三个独立数组|是|V2完整多数组按序合并|0|10|V2主结果|','|2105.03654.pdf|1024上限，截断在第32条Metric键内|V2不恢复|不补写、不截尾|0|0|V2仍计空预测|',f'|2105.03654.pdf|独立2048预算诊断|{p["ok"]}|新响应接受冻结V2检查|1|{p.get("records",0)}|仅token2048_diagnostic|','','V2为41/42篇格式有效，281条TDMR；原40篇输出文本和记录逐字不变。有效论文Gold覆盖252/259；评价固定42篇259 Gold。1912.08777.pdf保持BLOCKED，未处理。','','## 实验流程与结果','','19项解析边界测试通过；先冻结规则/代码哈希，再执行下游和评分。完整原始记录片段、字符偏移、类型及每篇规则命中见audit/papers。','Fully/CS仅处理恢复输入，原40篇不变；Partially按原序从头离线重建，按严格状态匹配复用。完整元组P/R/F1和排行榜对照见[comparison_v1_v2.md](../format_v2/comparison_v1_v2.md)。','','|设置|V1 TDMR F1|V2 TDMR F1|差（百分点）|','|---|---:|---:|---:|']
    for stage in STAGES:
        x=comparison[stage]['TDMR'];report.append(f'|{stage}|{100*x["v1"]["F1"]:.6f}|{100*x["v2"]["F1"]:.6f}|{100*x["delta"]["F1"]:+.6f}|')
    report+=['','## 复用、调用与资源','','|阶段|严格匹配复用请求|新增生成|','|---|---:|---:|']
    for stage,x in reuse.items():report.append(f'|{stage}|{x["reused_requests"]}|{x["new_generations"]}|')
    report += [f'另有{u["historical_audit_offline_replay_calls"]}次历史响应离线重放用于重建位置和状态索引，不属于模型调用。全轮新增本地模型生成{u["new_local_generations"]}次，其中Extraction {u["new_extraction_calls"]}次、Normalization {u["new_normalization_calls"]}次；付费API为0。输入{u["new_input_tokens"]:,}、输出{u["new_output_tokens"]:,} Tokens。',f'实际新增纯生成时间{u["new_generation_seconds"]:.3f}秒；各阶段墙钟及历史CS缓存失败保留在remote_snapshot/workflow_complete.json与cs_repair_complete.json。','','## 工程问题与边界','','CS首次运行因隔离缓存目录未暴露固定revision自定义代码而失败，发生在新增映射前。修复仅复制两份已校验代码到本轮离线缓存并显式设置缓存路径，模型权重、版本、CPU FP32及Top-1逻辑不变。原日志保留；没有重复已成功的CS论文。','Partially新增行未改变后续响应时，以完整请求/候选状态核验为依据，不能仅凭名称相同复用。该事实及全部原40篇对照见downstream_change_audit.json。','2048诊断的停止状态、完整性和Token前缀证据见[diagnostic_report.md](../token2048_diagnostic/diagnostic_report.md)。不把其输出纳入主结果，不启动Partially预算重跑。','官方字符串包含匹配、重复计数及排行榜后写覆盖全部保留；严格数值一对一指标只是辅助诊断，不裁剪原版Recall。','','## 完整性与交付','','最终完整性、脱敏、环境、调用计数和传输核验见verification.json；原formal42、官方源码、Prompt、Gold与冻结证据保持受保护。','本地：D:/C++/SCILEAD/pilot/autodl_llama3/20261021_format_followup。','远程：/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup；执行原始文件在根目录，最终报告在delivery/。','未启动其他模型或新实验；任务模型由子进程结束释放，服务器未关机。']
    write(R/'reports/run_report.md',report)
    print(json.dumps({'v2_valid':41,'main_new_calls':sum(x['new_generations'] for x in reuse.values()),'new_calls_total':u['new_local_generations'],'diagnostic':diag,'tdmr_f1':{k:v['TDMR']['v2']['F1'] for k,v in comparison.items()}}))
if __name__=='__main__':main()
