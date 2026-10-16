from common import *
import argparse,collections,contextlib,types,subprocess
from concurrent.futures import ThreadPoolExecutor
from normalize import labels_and_plan

def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0'
    m=read(RUN/'input_manifest.json');raw=read(RUN/'input/output.json');norm=read(RUN/'normalization/normalized_output.json');coverage=read(RUN/'evaluation/coverage.json');usage=read(RUN/'api_usage_summary.json')
    assert sha(RUN/'input/output.json')==m['frozen_raw_sha256']
    assert raw==read(PREVIOUS/'fewshot_output.json')==read(RUN/'merged/output.json')
    import tdm_llm_normalization as official
    from prompting import TDMPrompt
    prompts=read(REPO/'prompts.json');et=TDMPrompt(prompts['few-shot-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    requests=[];replayed=[];tokens=collections.Counter();successes=0
    for row in m['papers']:
        p=row['id'];out=Path(row['normalization_dir']);docs=raw[p]['source_documents'];assert digest(docs)==row['source_documents_sha256']
        assert sha(row['extraction_file'])==row['extraction_sha256'] and sha(Path(row['extraction_dir'])/'api_calls/0001/request.json')==row['extraction_request_sha256']
        ep=read(Path(row['extraction_dir'])/'api_calls/0001/request.json')
        assert ep['messages']==wire(et.format_messages(question=prompts['query'],context='\n\n'.join(x['content'] for x in docs)))
        rows=json.loads(raw[p]['output']);labels,plan=labels_and_plan(p,rows);assert plan==read(out/'request_plan.json')
        states=[]
        for f in sorted(Path(row['calls_dir']).glob('*/attempt.json')):
            q=read(f.parent/'request.json');s=read(f.parent/'state.json');expected=plan[int(f.parent.name)-1]
            assert q['messages']==expected['messages'] and read(f.parent/'expected.json')==expected
            assert set(q)=={'messages','model','n','seed','stream','temperature'}
            assert q['model']==MODEL and q['temperature']==0 and q['seed']==0 and q['stream'] is False and q['n']==1
            assert s['prompt_sha256']==digest(expected['messages']) and s['candidate_sha256']==expected['candidate_sha256']
            assert s['position']=={k:expected[k] for k in ('paper','record','field')}
            if s['status']=='COMPLETE':
                body=read(f.parent/'response.json');assert digest(body)==s['response_sha256']
                assert s['http_status']==200 and s['returned_model']==MODEL and s['finish_reason']=='stop'
                assert s['raw_answer']==body['choices'][0]['message']['content']
                assert s['usage']==body['usage'];successes+=1
            for k in ('prompt_tokens','completion_tokens','total_tokens'):tokens[k]+=(s.get('usage') or {}).get(k,0) or 0
            requests.append({'paper':p,'record':expected['record'],'field':expected['field'],'status':s['status'],'path':str(f.parent),'finish_reason':s.get('finish_reason')});states.append(s)
        if p not in norm:continue
        assert len(states)==len(plan) and all(s['status']=='COMPLETE' for s in states)
        assert read(out.parent/'config.json')['is_few_shot'] is True
        assert norm[p]['source_documents']==docs and [x['Result'] for x in norm[p]['normalized_output']]==[x['Result'] for x in rows]
        replay=RUN/'verification_replay'/Path(p).stem;save(replay/'output.json',{p:raw[p]});save(replay/'config.json',{'is_few_shot':True,'model_type':'gpt4-turbo-128k'});cursor=[0]
        class Replay:
            def invoke(self,prompt):
                i=cursor[0];assert wire(prompt.to_messages())==plan[i]['messages'];cursor[0]+=1
                return types.SimpleNamespace(content=states[i]['raw_answer'])
        official.utils.llm_init_langchain=lambda config,max_new_tokens,seed:Replay()
        with (replay/'replay.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            official.main(argparse.Namespace(seed=0,max_new_tokens=None,gold_tdm_path=m['gold_path'],tdm_output_path=replay.as_posix()+'/',prompt_file=str(REPO/'prompts.json')))
        assert cursor[0]==len(plan) and read(replay/'normalization/normalized_output.json')=={p:norm[p]};replayed.append(p)
    assert len(requests)==usage['normalization_attempts'] and successes==usage['successful_responses'] and all(usage[k]==tokens[k] for k in tokens)
    assert len({x['path'] for x in requests})==len(requests)
    complete=len(norm)==43
    if complete:
        assert len(requests)==read(RUN/'precheck.json')['expected_requests']==453 and successes==453
        assert sum(len(v['normalized_output']) for v in norm.values())==293
        B=read(PREVIOUS/'evaluation/metrics_with_f1.json');C=read(RUN/'evaluation/metrics_with_f1.json')
        assert C['aggregate']['Result IIM']==B['aggregate']['Result IIM']
        assert C['strict_result_iim_auxiliary']==B['strict_result_iim_auxiliary']
        lb=RUN/'leaderboard_evaluation';assert read(lb/'official/execution_status.json')['status']=='COMPLETE'
        assert read(lb/'paper_metrics/leaderboard_metrics.json')['aggregate']['gold_leaderboards']==27
        for name in ('run_official_leaderboard_eval.py','evaluate_paper_metrics.py'):assert sha(lb/name)==sha(PREVIOUS/'leaderboard'/name)
    frozen=verify();nfiles=0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for root,expected in frozen['directories'].items():
            assert {str(p) for p in Path(root).rglob('*') if p.is_file()}==set(expected),root
            for (p,h),actual in zip(expected.items(),pool.map(sha,expected)):assert h==actual,p
            nfiles+=len(expected);print('UNCHANGED',Path(root).name,len(expected),flush=True)
    assert subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'status','--porcelain'],text=True)==frozen['git_status']
    assert subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'rev-parse','HEAD'],text=True).strip()==frozen['git_commit']
    verification={'coverage':coverage,'complete_author_fewshot_prompt_branch':complete,'new_extraction_requests':0,'normalization_attempts':len(requests),'successful_normalization_responses':successes,'all_successful_responses_http200_model_snapshot_stop':True,'all_actual_payloads_omit_output_limits':True,'normalization_prompt_key':NORMALIZATION_KEY,'is_few_shot':True,'static_examples_unchanged_and_rendered_once':True,'candidate_order_equal_B':True,'raw_extractions_identical_B':True,'source_documents_and_record_order_unchanged':True,'Result_strings_unchanged':True,'result_iim_and_strict_numerical_metrics_equal_B':complete,'offline_official_replay_papers':len(replayed),'frozen_files_unchanged':nfiles,'sources_prompt_gold_dependency_versions_unchanged':True,'official_git_status_unchanged':True,'automatic_retries':0,'new_pdf_embedding_retrieval_execution':False,'request_checks':requests,'evidence_hash_serialization':'SHA256 of json.dumps(ensure_ascii=False), preserving key order; file hashes separately recorded.'}
    save(RUN/'verification.json',verification)
    write_reports()
    plan=RUN/'execution_plan.md'
    if complete:plan.write_text(plan.read_text(encoding='utf-8').replace('- [ ]','- [x]'),encoding='utf-8')
    hashes={str(p.relative_to(RUN)):sha(p) for p in RUN.rglob('*') if p.is_file() and p!=RUN/'artifact_sha256.json'}
    save(RUN/'artifact_sha256.json',hashes);print('FINALIZED',len(hashes),flush=True)

def write_reports():
    comp=read(RUN/'evaluation/comparison_of_three_settings.json');u=read(RUN/'api_usage_summary.json');v=read(RUN/'verification.json');scope=comp['scope'];pre=read(RUN/'precheck.json')
    labels={'A':'Zero-shot Extraction + Zero-shot Normalization','B':'Few-shot Extraction + Zero-shot Normalization','C':'Few-shot Extraction + Few-shot Normalization'}
    lbs={'A':read(RUN.parent/'leaderboard_eval_full43_uncapped/paper_metrics/leaderboard_metrics.json')['aggregate'],'B':read(PREVIOUS/'leaderboard/paper_metrics/leaderboard_metrics.json')['aggregate']}
    if (RUN/'leaderboard_evaluation/paper_metrics/leaderboard_metrics.json').exists():lbs['C']=read(RUN/'leaderboard_evaluation/paper_metrics/leaderboard_metrics.json')['aggregate']
    save(RUN/'leaderboard_evaluation/comparison_of_three_settings.json',{'settings':labels,'aggregates':lbs,'gold_boards':27,'C_coverage':scope})
    lines=['# 作者完整 Few-shot Prompt 分支：标准化与评价','',f"完成 {scope['completed_papers']}/43 篇，{scope['records']}/293 条原始预测；Gold 覆盖 {scope['evaluated_gold']}/295。新增 Extraction 请求为 0。",'',
        '## Prompt 与方法','Extraction：few-shot-extraction-system-prompt，直接复用上一轮原始结果和 MATCHSUM 示例，未重新解析 PDF、生成嵌入或检索。Normalization：few-shot-normalization-system-prompt，is_few_shot=True，调用未经修改的官方 main 与 NormalizationPrompt。',
        '作者的 Pos tagging、PTB、F1 score 三个示例原样嵌在 System 消息中一次；双花括号按原版机制渲染。示例名称集合保持静态，Human 消息使用当前字段的实际候选集合与原始名称。没有追加论文上下文或 Gold 对应关系。',
        f"候选集合 23 Task / 71 Dataset / 26 Metric；PYTHONHASHSEED=0，序列化顺序与 B 完全相同。{pre['exact_fields_total']} 个字段精确命中直接保留，{pre['expected_requests']} 个字段需调用模型，未使用跨记录缓存。只有原始回答精确属于候选集合才保留，否则为 null；不去空格或引号，Result 不变。",'',
        '## API 与复现差异',f"gpt-4.1-2025-04-14，temperature=0、seed=0、stream=False；实际请求省略 max_tokens/max_completion_tokens/max_output_tokens，未添加 tools/response_format。尝试 {u['normalization_attempts']}，成功 {u['successful_responses']}，失败/不确定 {u['failed_or_uncertain']}，自动重试 0。",f"Prompt {u['prompt_tokens']:,}，Completion {u['completion_tokens']:,}，Total {u['total_tokens']:,} Tokens；未知用量请求 {u['unknown_usage_attempts']}。HTTP 耗时合计 {u['request_seconds']:.1f} 秒，执行墙钟 {u['wall_seconds']:.1f} 秒。旧 Extraction 请求和 B 的标准化请求均不计入本轮新增请求。第三方费用未按美元估算。",'保留 GPT-4.1 替代 GPT-4 Turbo、取消作者默认输出上限的差异。数据版本使用冻结本地 Gold（SHA256 见 input_manifest/freeze_before），不声称与原论文数字完全相同。seed 被接口接受不保证完全确定性。','',
        '## 官方元组评价','P/R 为原版 tdm_eval.py 的逐篇 Macro；F1=2PR/(P+R)，不是逐篇 F1 算术平均。','', '| 指标 | C Precision | C Recall | C F1 | A F1 | B F1 |','| --- | --- | --- | --- | --- | --- |']
    for key,c in comp['C']['aggregate'].items():lines.append(f"| {key} | {c['Precision']:.6f} | {c['Recall']:.6f} | {c['F1']:.6f} | {comp['A']['aggregate'][key]['F1']:.6f} | {comp['B']['aggregate'][key]['F1']:.6f} |")
    strict=comp['C']['strict_result'];lines+=['',f"Result 不变检查：官方 Result IIM F1={comp['C']['aggregate']['Result IIM']['F1']:.6f}，严格数值辅助 F1={strict['F1']:.6f}（P={strict['Precision']:.6f}，R={strict['Recall']:.6f}），均与 B 完全一致。严格指标使用同一有限 Decimal 相等方法，不清洗百分号或 ±，不替代官方字符串包含匹配。",'',
        '## 排行榜评价（配套补充）','固定同一份 27 个 Gold 榜。PC/RC/数值列表 RBO 使用原版函数；LR 是数值转换前的标准 TDM 命中，有效数值非空率另列；AO 使用论文 ID 排名。保持后写覆盖、排序方向、并列规则、空榜计零与 Macro 分母。RBO 不等于 AO。','', '| 指标 | A | B | C |','| --- | --- | --- | --- |']
    keys=('LR_exact_tdm_hit','LR_nonempty_finite_result','PC_official','RC_official','RBO_official_value_rankings','AO_paper_id_macro_all_gold_boards')
    if 'C' in lbs:
        for key in keys:lines.append('| '+key+' | '+' | '.join(f"{lbs[s][key]:.6f}" for s in 'ABC')+' |')
    else:lines.append('完整覆盖未完成，未生成全量 C 排行榜分数。')
    lines+=['','## 三组定义与映射变化']+[s+'. '+labels[s]+'；来源 '+comp[s]['source'] for s in 'ABC']
    lines+=['C 对齐作者官方完整 Few-shot Prompt 分支，Table 7 的 ETM/IIM 对照应使用 C。B 保留为只改变抽取 Prompt 的实验，不能替代 C；无论分数高低都不选择性覆盖。排行榜级评价是配套补充。','', '| 设置 | Task null | Dataset null | Metric null | 总 null |','| --- | --- | --- | --- | --- |']
    for s,counts in comp['null_fields'].items():lines.append('| '+s+' | '+' | '.join(str(counts.get(k,0)) for k in ('Task','Dataset','Metric'))+f" | {sum(counts.values())} |")
    lines+=['', 'B→C 映射变化：'+json.dumps(comp['mapping_change_counts'],ensure_ascii=False),'所有字段变化保存在 evaluation/comparison_of_three_settings.json，以 paper_id + 原始记录序号 + 字段关联。null→标签不自动等于语义正确，本文只记录变化，不进行科学因果归因。','', '| 论文 | 记录 | 字段 | 原始名称 | B | C |','| --- | --- | --- | --- | --- | --- |']
    distinct=set();examples=[]
    for x in comp['mapping_changes']:
        key=(x['field'],x['original_name'],x['B'],x['C'])
        if key not in distinct:distinct.add(key);examples.append(x)
    for x in examples[:15]:lines.append('| '+' | '.join(str(x[k]).replace('|','\\|') for k in ('paper','record','field','original_name','B','C'))+' |')
    lines+=['','## 每篇结果','','| 论文 | 条数 | B TDMR F1 | C Result F1 | C TDM F1 | C TDMR F1 |','| --- | --- | --- | --- | --- | --- |']
    for x in comp['per_paper']:lines.append(f"| {x['paper']} | {x['records']} | {x['B']['TDMR Exact Match']['F1']:.6f} | {x['C']['Result IIM']['F1']:.6f} | {x['C']['TDM Exact Match']['F1']:.6f} | {x['C']['TDMR Exact Match']['F1']:.6f} |")
    lines+=['','## 完整性与文件',f"{v['offline_official_replay_papers']} 篇通过原版标准化离线回放；{v['frozen_files_unchanged']} 个历史文件 SHA256 未改变，官方源码、Prompt、Gold、依赖版本和 Git 状态未改变。B 与 C 原始抽取、证据、293 条记录及 Result 顺序全部一致。",'核心产物：input_manifest.json、normalization/normalized_output.json、normalization/api_calls/、evaluation/、leaderboard_evaluation/、api_usage_summary.json、verification.json。历史实验文件未修改。','完成后停止，未启动 threshold=2 或其他实验。']
    if scope['completed_papers']<43:lines.insert(2,'部分完成；不能称为完整 43 篇实验。失败论文见 evaluation/coverage.json。')
    (RUN/'report.md').write_text('\n'.join(lines),encoding='utf-8')
    comparison=['# A / B / C 设置对照','']+[s+'. '+labels[s] for s in 'ABC']+['','B 与 C 的 43 篇原始抽取及 293 条 Result 字符串完全相同。C 使用作者完整 Few-shot 分支；不以得分高低选取结果。','', '| 指标 | A P/R/F1 | B P/R/F1 | C P/R/F1 |','| --- | --- | --- | --- |']
    for key in comp['C']['aggregate']:comparison.append('| '+key+' | '+' | '.join(' / '.join(f"{comp[s]['aggregate'][key][k]:.6f}" for k in ('Precision','Recall','F1')) for s in 'ABC')+' |')
    comparison+=['','完整排行榜、null 变化及逐篇结果见 report.md 和 evaluation/comparison_of_three_settings.json。对原论文 Table 7 优先使用 C；模型、生成上限与冻结数据版本差异仍然适用。']
    (RUN/'comparison_of_three_settings.md').write_text('\n'.join(comparison),encoding='utf-8')

if __name__=='__main__':main()
