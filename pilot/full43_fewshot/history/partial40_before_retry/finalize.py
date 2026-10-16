from common import *
import argparse, collections, subprocess, types, contextlib
from concurrent.futures import ThreadPoolExecutor
def main():
    setup();m=read(RUN/'manifest.json');raw=read(RUN/'fewshot_output.json');norm=read(RUN/'fewshot_normalized_output.json');base=read(BASE/'merged/output.json');metrics=read(RUN/'evaluation/metrics_with_f1.json');coverage=metrics['scope'];requests=[];replay=[];token_totals={k:0 for k in ('prompt_tokens','completion_tokens','total_tokens')}
    import tdm_llm_normalization as official
    from prompting import TDMPrompt
    prompts=read(REPO/'prompts.json');template=TDMPrompt(prompts['few-shot-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    for r in m['papers']:
        p=r['id'];assert digest(read(r['evidence_path'])['source_documents'])==r['source_documents_sha256']==digest(base[p]['source_documents'])
        expected_messages=wire(template.format_messages(question=prompts['query'],context='\n\n'.join(d['content'] for d in base[p]['source_documents'])))
        assert read(Path(r['extraction_dir'])/'request_plan.json')[0]['messages']==expected_messages
        for stage,out in [('extract',Path(r['extraction_dir'])),('normalize',Path(r['normalization_dir']))]:
            for f in sorted((out/'api_calls').glob('*/attempt.json')):
                q=read(f.parent/'request.json');s=read(f.parent/'state.json');assert q['model']==MODEL and q['temperature']==0 and q['seed']==0 and q['stream'] is False
                assert not set(q)&{'max_tokens','max_output_tokens','max_completion_tokens','tools','functions','response_format','stop'}
                # HTTP SDK reverses JSON object-key order (content/role), which
                # does not change message roles, text, or message sequence.
                e=read(f.parent/'expected.json');assert q['messages']==e['messages'];assert s['prompt_sha256']==digest(e['messages'])
                if s['status']=='COMPLETE':
                    b=read(f.parent/'response.json');assert s['response_sha256']==digest(b);assert s['http_status']==200 and s['returned_model']==MODEL and s['finish_reason']=='stop'
                    assert s['raw_answer']==b['choices'][0]['message']['content']
                    if stage=='extract':assert raw[p]['output']==s['raw_answer']
                if (f.parent/'response.json').exists():
                    body=read(f.parent/'response.json')
                    for k in token_totals:token_totals[k]+=(body.get('usage') or {}).get(k,0) or 0
                requests.append({'paper':p,'stage':stage,'path':str(f.parent),'status':s['status'],'finish_reason':s.get('finish_reason'),'request_id':s.get('request_id'),'response_model':s.get('returned_model')})
        if p in raw:assert validate(raw[p]['output'])['schema_valid']
        if p not in norm:continue
        assert validate(raw[p]['output'])['schema_valid'];assert norm[p]['source_documents']==raw[p]['source_documents']==base[p]['source_documents']
        plan=read(Path(r['normalization_dir'])/'request_plan.json');states=[read(x) for x in sorted((Path(r['normalization_dir'])/'api_calls').glob('*/state.json'))];assert len(states)==len(plan)
        # Re-execute original normalization main offline with recorded answers.
        folder=RUN/'verification_replay'/Path(p).stem;save(folder/'output.json',{p:raw[p]});save(folder/'config.json',{'is_few_shot':False,'model_type':'gpt4-turbo-128k'});cursor=[0]
        class Replay:
            def invoke(self,prompt):
                i=cursor[0];assert wire(prompt.to_messages())==plan[i]['messages'];cursor[0]+=1;return types.SimpleNamespace(content=states[i]['raw_answer'])
        official.utils.llm_init_langchain=lambda config,max_new_tokens,seed:Replay()
        with (folder/'replay.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            official.main(argparse.Namespace(seed=0,max_new_tokens=None,gold_tdm_path=m['gold_path'],tdm_output_path=folder.as_posix()+'/',prompt_file=str(REPO/'prompts.json')))
        assert cursor[0]==len(plan);assert read(folder/'normalization/normalized_output.json')=={p:norm[p]};replay.append(p)
    # Recompute frozen baseline offline into this run only.
    accounting=read(RUN/'api_usage_summary.json')['total'];assert accounting['requests']==len(requests)
    assert all(accounting[k]==v for k,v in token_totals.items())
    if len(norm)==43:
        assert len([x for x in requests if x['stage']=='extract'])==43
        assert len([x for x in requests if x['stage']=='normalize'])==read(RUN/'normalization_precheck.json')['expected_requests']
    import tdm_eval
    out=RUN/'evaluation/zero_shot_recheck';out.mkdir(exist_ok=True)
    tdm_eval.main(argparse.Namespace(gold_data_path=m['gold_path'],normalized_tdm_output_path=str(BASE/'merged/normalized_output.json'),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json')))
    assert read(out/'eval_results.json')==read(BASE/'evaluation/eval_results.json');assert read(out/'eval_values.json')==read(BASE/'evaluation/eval_values.json')
    f=verify();nfiles=0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for root,files in f['directories'].items():
            assert {str(p) for p in Path(root).rglob('*') if p.is_file()}==set(files)
            for (p,h),actual in zip(files.items(),pool.map(sha,files)):assert actual==h,p
            nfiles+=len(files);print('PRESERVED',root,len(files),flush=True)
    status=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'status','--porcelain'],text=True);assert status==f['git_status']
    assert subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'rev-parse','HEAD'],text=True).strip()==f['git_commit']
    verification={'coverage':coverage,'request_count':len(requests),'request_checks':requests,'all_requests_omit_output_limits':True,'all_successful_responses_http200_snapshot_stop':all(x['status']=='COMPLETE' and x['finish_reason']=='stop' and x['response_model']==MODEL for x in requests),'all_completed_extractions_schema_valid':True,'evidence_equal_to_zero_shot_papers':len(m['papers']),'official_normalization_replay_papers':len(replay),'frozen_baseline_eval_recomputed_identically':True,'frozen_files_unchanged':nfiles,'official_sources_gold_dependencies_unchanged':True,'git_status_unchanged':True,'mock_network_requests':0,'no_pdf_embedding_retrieval_execution':True,'no_automatic_retries':True}
    verification['dependency_check_scope']='Installed distribution names and versions match frozen snapshot; no package installation or upgrade performed.'
    verification['all_attempts_successful_and_stop']=verification['all_successful_responses_http200_snapshot_stop']
    verification['all_successful_responses_http200_snapshot_stop']=all(x['finish_reason']=='stop' and x['response_model']==MODEL for x in requests if x['status']=='COMPLETE')
    verification['prompt_hash_verification']='Expected role/content serialization hash plus exact message-list/dict equality; SDK object-key ordering is immaterial. See hash_serialization_audit.json.'
    save(RUN/'verification.json',verification)
    write_report()
    if coverage['completed_papers']==43:
        plan=RUN/'execution_plan.md';plan.write_text(plan.read_text(encoding='utf-8').replace('- [ ]','- [x]'),encoding='utf-8')
    artifact={str(p.relative_to(RUN)):sha(p) for p in RUN.rglob('*') if p.is_file() and p.name!='artifact_sha256.json'};save(RUN/'artifact_sha256.json',artifact);print('FINALIZED',len(artifact),'files')
def write_report():
    me=read(RUN/'evaluation/metrics_with_f1.json');old=read(BASE/'evaluation/metrics_with_f1.json');comp=read(RUN/'evaluation/comparison.json');usage=read(RUN/'api_usage_summary.json');verify=read(RUN/'verification.json');coverage=me['scope'];summaries=read(RUN/'stage_summary.json');diag=read(RUN/'evaluation/error_analysis.json');newcount=comp['record_count_few'];errors=collections.Counter()
    old=dict(old,aggregate=comp['aggregate_zero'])
    for a in diag.values():errors.update(a['category_counts'])
    lbpath=RUN/'leaderboard/paper_metrics/leaderboard_metrics.json';lb=read(lbpath)['aggregate'] if lbpath.exists() else {};oldlb=read(RUN.parent/'leaderboard_eval_full43_uncapped/paper_metrics/leaderboard_metrics.json')['aggregate']
    lines=['# SCILEAD GPT-4.1 Few-shot 实验报告','',f"完成 {coverage['completed_papers']}/43 篇，覆盖 {coverage['evaluated_gold']}/295 条 Gold。新抽取 {newcount} 条；Zero-shot 为 284 条。所有原始响应、异常和 null 均按真实结果保留。",'',
    '## Prompt 与复现边界','作者 prompts.json 的 few-shot-extraction-system-prompt 原样复用。MATCHSUM 示例包含论文摘要、方法/数据集文字、Table 3–5 和 18 条示例输出；Section 6.3 明确示例论文不属于 SciLead。Appendix G 给出基础抽取/标准化模板，完整 Few-shot 示例以仓库文件为准。',
    '示例嵌在 System 中，仅出现一次；Human 消息继续使用官方 TDMPrompt 的 Query + Retrieved document contents 格式。43 篇 source_documents 与冻结 Baseline 全等，包括顺序、元数据和文本；284 是历史预测条数，不是论文输入数。',
    '作者示例的 ROGUE 拼写及末尾三个输出把 Multi-News 数值标为 WikiHow 的不一致均保留，未纠正。示例输入/输出、原始模板及格式化消息哈希已保存。',
    '本轮只改变 Extraction Prompt。上游 is_few_shot 同时切换标准化 Prompt，因此独立 normalization_input/config.json 选择 is_few_shot=False，调用原始标准化 main，候选 23 Task / 71 Dataset / 26 Metric 的内容、顺序和 Prompt 与 Fully Zero-shot 相同。未使用上游 few-shot-normalization-system-prompt，也未添加缓存。',
    '这符合本轮控制变量设定，并复用作者示例；不能声称等同于上游 is_few_shot 全开运行。原论文使用 GPT-4 Turbo，本轮使用 GPT-4.1 固定快照，且无客户端输出上限，故也不是原论文数值结果的严格重复。','',
    '## API 与完整性',f"模型 {MODEL}；temperature=0、seed=0、stream=False。{usage['total']['requests']} 次实际请求：Extraction {usage['stages']['extract']['requests']}，Normalization {usage['stages']['normalize']['requests']}。成功响应 {usage['total']['successful_responses']}，失败/不确定 {usage['total']['failed_or_uncertain']}；自动重试 0。",f"Prompt Tokens {usage['total']['prompt_tokens']:,}，Completion Tokens {usage['total']['completion_tokens']:,}，Total Tokens {usage['total']['total_tokens']:,}。未知用量请求 {usage['total']['unknown_usage_attempts']}；调用耗时合计 {usage['total']['request_seconds']:.1f} 秒，流水线墙钟 {usage['wall_seconds_since_api_start']:.1f} 秒。金额未核对平台账单。",'实际请求 JSON 已核验没有 max_tokens、max_completion_tokens、max_output_tokens、tools 或 response_format；完整输入未截断。seed 被接口接受不代表完全确定性。',f"完成输出均通过 JSON/字段检查；全部请求 HTTP200 + 指定模型 + finish_reason=stop：{verify['all_successful_responses_http200_snapshot_stop']}。官方源码、Gold、依赖和 {verify['frozen_files_unchanged']} 个既有文件未改变。",'',
    '## 官方 IIM / ETM','P/R 来自原版 tdm_eval.py 的逐篇 Macro 聚合；F1=2PR/(P+R) 为额外计算，不是逐篇 F1 平均。保留官方 Result 字符串包含匹配及其计数行为。','',
    '| 指标 | Few P | Few R | Few F1 | Zero F1 | ΔF1 |','| --- | --- | --- | --- | --- | --- |']
    for k,v in me['aggregate'].items():lines.append(f"| {k} | {v['Precision']:.6f} | {v['Recall']:.6f} | {v['F1']:.6f} | {old['aggregate'][k]['F1']:.6f} | {v['F1']-old['aggregate'][k]['F1']:+.6f} |")
    strict=me['strict_result_iim_auxiliary'];lines+=['',f"辅助严格数值 IIM：P={strict['Precision']:.6f}，R={strict['Recall']:.6f}，F1={strict['F1']:.6f}。使用有限 Decimal 数值相等，不包含百分比缩放；不替代官方指标。",'', '## Leaderboard（固定 27 榜）','PC/RC/RBO 使用原版代码；LR 和 AO 沿用之前审计的补充实现。LR 为数值转换前的精确 TDM 榜命中率，有效非空榜率另列；AO 按论文 ID 排名，空榜计零，27 榜 Macro。RBO 按官方结果值排序，保留默认 p=1。RC 可因官方非一对一数值匹配超过 1，不截断。','','| 指标 | Few-shot | Zero-shot | Δ |','| --- | --- | --- | --- |']
    for k in ('LR_exact_tdm_hit','LR_nonempty_finite_result','PC_official','RC_official','RBO_official_value_rankings','AO_paper_id_macro_all_gold_boards'):
        if k in lb:lines.append(f'| {k} | {lb[k]:.6f} | {oldlb[k]:.6f} | {lb[k]-oldlb[k]:+.6f} |')
    lines+=['','## 错误记录与范围',json.dumps(dict(errors),ensure_ascii=False),'逐条 Gold 对照、原始与标准化预测及严格数值候选保存在 evaluation/tdmr_comparison.md 和 error_analysis.json。数值匹配但 TDM 不同仅标为绑定或标签不匹配，不能自动证明 Baseline 混入；非 Gold 数值也可能是变体、Dev/Test 或不同粒度，需回查原始证据。',f"官方包含匹配与严格数值匹配不一致的预测/Gold 对数：{sum(len(x['substring_vs_strict_discrepancies']) for x in diag.values())}。",'提升/下降不作为重试依据。Prompt 变化与重新调用模型的波动共同存在，不能把差异全部归因于示例。','', '## 每篇结果','','| 论文 | Gold | 证据 | 抽取条数 | 标准化请求 | null字段 | Result F1 | TDM F1 | TDMR F1 |','| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for s in summaries:
        p=s['paper'];pm=me['per_paper'].get(p);tail=' | '.join(f"{pm[k]['F1']:.6f}" for k in ('Result IIM','TDM Exact Match','TDMR Exact Match')) if pm else '未完成 | 未完成 | 未完成'
        lines.append(f"| {p} | {s['gold']} | {s['evidence_count']} | {s['extraction'].get('records')} | {s['normalization'].get('requests')} | {s['normalization'].get('null_fields')} | {tail} |")
    nstat=read(RUN/'normalization_statistics.json')
    lines+=['','## 标准化语义结果',f"候选集合精确命中直接保留 {nstat['exact_fields_skipped']} 个字段；LLM 回答位于候选集合 {nstat['llm_answers_in_candidate_set']} 次；最终 null 字段 {nstat['null_fields']} 个。null 为官方映射结果，不等于 HTTP 失败。全部 Result 字符串保持原样。",'','## 人工核查案例','见 inspection/reviewed_cases.md：1912.08777 的新 36 条数值对应第 9 页 Table 4 的 mixed/stochastic 配置，Gold 则主要对应第 7 页 Table 1；更多条目不意味着命中 Gold，也不能据此称为 Baseline 混入。其他典型变化与逐条证据见 comparison_with_zero_shot.md、inspection/findings.md。','','## 保存与恢复','所有新文件在 full43_fewshot。按 run.py --stage extract / normalize 恢复时已记录结果自动跳过，未完成且已有 attempt 的位置禁止自动重发。原始响应先保存再更新检查点。offline_tests 和 verification_replay 不计收费请求。','本轮结束，不执行 threshold=2、开源模型或其他改进实验。']
    if coverage['completed_papers']<43:
        lines[2]=f"**部分完成，不能称为完整 43 篇 Few-shot Baseline。** Extraction 已完成 43/43 篇、{newcount} 条预测；Normalization / Evaluation 完成 {coverage['completed_papers']}/43 篇，对应 {coverage['evaluated_gold']}/295 条 Gold。"
        i=lines.index('## 官方 IIM / ETM');lines.insert(i+1,f"本表仅比较相同的 {coverage['completed_papers']} 篇 Few-shot 与 Zero-shot；不是全量 43 篇分数。")
        i=lines.index('## Leaderboard（固定 27 榜）');j=lines.index('## 错误记录与范围')
        lines[i:j]=['## Leaderboard（固定 27 榜）','因三篇标准化失败，完整 43 篇预测的 LR / PC / RC / RBO / AO 尚未生成。状态见 leaderboard/status.json；不以部分预测冒充全量结果。','']
        lines+=['','## 未完成论文及比较范围','标准化因服务商 HTTP 502 停止：'+', '.join(x['paper'] for x in coverage['failed'])+'。失败请求没有自动重试，返回 Token Usage 缺失，实际计费未知。',f"IIM/ETM 对照仅比较相同 {coverage['completed_papers']} 篇。完整 43 篇 Zero-shot 分数单独保存在 comparison.json，不能与部分 Few-shot 直接作完整实验比较。",'43 篇抽取全部成功，但完整 Leaderboard 对照尚未生成；本报告没有将部分预测称为完整 43 篇排行榜结果。']
    lines+=['','## 典型提升与下降','C18-1139 的官方 TDMR F1 从 0.5 到 1.0：原始 Dataset 增加 English/German 区分，后续名称映射成功；Result 未改动。D18-1105 从 1.0 到 0.5：原始抽取完全相同，SwDA 的两次标准化实际请求 payload 也相同，但旧回答为标准名称，本次为 None。该实例直接表明不能把全部分数变化归因于 Few-shot Extraction Prompt。证据见 inspection/normalization_repeat_variation.json 和 reviewed_cases.md。']
    (RUN/'report.md').write_text('\n'.join(lines).replace('Gold、依赖和','Gold、依赖版本和').replace('全部请求 HTTP200','成功响应 HTTP200'),encoding='utf-8')
    ranked=sorted(comp['papers'],key=lambda x:x['tdmr_f1_delta'],reverse=True);c=['# Few-shot 与 Zero-shot 对照','',f'抽取条数：284 → {newcount}。所有论文使用相同冻结证据；唯一预设变化为 Extraction Prompt。','模型重新请求可能带来变化，不能仅由此对 Prompt 效果作因果判断。','', '| 指标 | Zero P/R/F1 | Few P/R/F1 |','| --- | --- | --- |']
    c.insert(4,f"以下 IIM/ETM 仅比较共同完成的 {coverage['completed_papers']} 篇；43 篇抽取条数与标准化完成覆盖范围分开报告。")
    for k,v in me['aggregate'].items():c.append('| '+k+' | '+' / '.join(f"{old['aggregate'][k][n]:.6f}" for n in ('Precision','Recall','F1'))+' | '+' / '.join(f'{v[n]:.6f}' for n in ('Precision','Recall','F1'))+' |')
    c+=['','## 逐篇变化（按 TDMR F1 差排序）','','| 论文 | 原条数→新条数 | 原null→新null | Result F1旧→新 | TDM F1旧→新 | TDMR F1旧→新 | ΔTDMR |','| --- | --- | --- | --- | --- | --- | --- |']
    for p in ranked:
        vs=['{:.6f} → {:.6f}'.format(p['zero_shot'][k]['F1'],p['few_shot'][k]['F1']) for k in ('Result IIM','TDM Exact Match','TDMR Exact Match')];c.append(f"| {p['paper']} | {p['old_records']}→{p['new_records']} | {p['old_null_fields']}→{p['new_null_fields']} | "+' | '.join(vs)+f" | {p['tdmr_f1_delta']:+.6f} |")
    c+=['','## 最大变化案例','以下仅列真实新增/消失的模型记录，详细归因需与冻结 source_documents 对照。']
    for p in ranked[:3]+ranked[-3:]:c+=['','### '+p['paper'],f"ΔTDMR F1={p['tdmr_f1_delta']:+.6f}",'```json',json.dumps({'added_raw_records':p['added_raw_records'],'removed_raw_records':p['removed_raw_records']},ensure_ascii=False,indent=2),'```']
    c+=['','## 与原论文观察对照','原论文 Section 6.3 报告 ETM 略降、Task/Metric IIM 提升。本轮方向按上表实际值记录；使用 GPT-4.1、固定证据与本轮只切换抽取 Prompt 的设定，不预设相同趋势。','标准化仍可能将不在集合内的回答变为 null；这类错误与抽取数值遗漏分别记录，未手工纠正。']
    (RUN/'comparison_with_zero_shot.md').write_text('\n'.join(c),encoding='utf-8')
if __name__=='__main__':main()
