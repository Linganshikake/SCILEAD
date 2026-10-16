"""Summarize completed three independent runs, with unchanged audited metrics."""
import collections,statistics,shutil
from decimal import Decimal,InvalidOperation
from common import *

KEYS={'LR':'LR_exact_tdm_hit','有效非空榜率':'LR_nonempty_finite_result','PC':'PC_official','RC':'RC_official','RBO':'RBO_official_value_rankings','AO':'AO_paper_id_macro_all_gold_boards'}
RUNS=('order_default','order_0','order_42')
def mdtable(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x).replace('|','\\|').replace('\n',' ') for x in row)+' |' for row in rows])
def number(v):
    try:d=Decimal(str(v));return d if d.is_finite() else None
    except InvalidOperation:return None
def triple(r):return tuple(r[k] for k in ('Task','Dataset','Metric'))
def inspect_run(rid,raw,gold,boards):
    run=TOP/rid;s1=read(run/'stage1/normalized_output.json');s2=read(run/'stage2/leaderboard_normalized_output.json');e1=[read(p) for p in sorted((run/'stage1/events').glob('*.json'))];e2=[read(p) for p in sorted((run/'stage2/events').glob('*.json'))]
    bset={triple(b) for b in boards};allgold={triple(x) for g in gold.values() for x in g['TDMs']};echoes=[]
    for e in e2:
        if e['branch']!='unmatched_preserved':continue
        inp=e['original'];rawrow=json.loads(raw[e['paper']]['output'])[e['record']-1];item='('+', '.join(inp[k] for k in ('Task','Dataset','Metric'))+')'
        equal_result=[g for g in gold[e['paper']]['TDMs'] if number(g['Result']) is not None and number(g['Result'])==number(inp['Result'])]
        category='Exact Gold TDM exists outside the 27-board target' if triple(inp) in allgold-bset else 'UNREVIEWED: open-vocabulary aliases and extraction bindings cannot be decided from string nonmembership alone'
        reviewed=None
        # Offline case annotation only. This is not an alias dictionary used by either model stage.
        if e['paper']=='2020.findings-emnlp.378.pdf' and inp==rawrow and e['record']<=6:
            reference=ROOT/'pilot/outputs/gpt41_single_paper/extraction_analysis.md'
            reference_text=reference.read_text(encoding='utf-8');assert 'Table 5' in reference_text and 'ON5E' in reference_text
            target=gold[e['paper']]['TDMs'][e['record']-1];assert number(target['Result'])==number(inp['Result'])
            category='Reviewed existing target board but abbreviation/name not aligned' if triple(target) in bset else 'Reviewed legitimate dataset alias outside the 27-board target'
            reviewed={'basis':'Prior manual Table 5 OURS row and dataset definitions check; original six extraction rows unchanged','reference_path':str(reference),'reference_sha256':sha(reference),'gold_correspondence':target}
        echoes.append({'paper':e['paper'],'record':e['record'],'raw_extraction':rawrow,'stage1':inp,'stage2':e['normalized'],'raw_response':e['raw_answer'],'exact_echo':e['raw_answer']==item,'category':category,'reviewed_evidence':reviewed,'same_paper_equal_numeric_gold_candidates_OFFLINE_ONLY':equal_result,'raw_field_binding_requires_review':bool(equal_result) and all(triple(rawrow)!=triple(g) for g in equal_result),'caution':'Equal numeric value does not prove row correspondence or error cause. Gold not used in model input. The binding flag is diagnostic only; alias differences are not proof of extraction error.'})
    s1counts=collections.Counter(e['branch'] for e in e1);s2counts=collections.Counter(e['branch'] for e in e2)
    labels=read(run/'stage1/final_labels.json');counts={k:len(v['ordered_values']) for k,v in labels.items()}
    adds=collections.Counter(e['field'] for e in e1 if e['added_name'] is not None)
    nulls={k:sum(row[k] is None for x in s1.values() for row in x['normalized_output']) for k in ('Task','Dataset','Metric')}
    null_cases=[{**{k:e[k] for k in ('paper','record','field','original','raw_answer','call')},'candidate_order':e['labels_before'][e['field']]['ordered_values'],'reason':'Response is neither an exact current candidate nor exactly the original input. Original code stores null; successful transport is not a model-mapping success.'} for e in e1 if e['branch']=='null']
    categories=collections.Counter(e['category'] for e in echoes)
    result={'run_id':rid,'final_label_counts':counts,'new_names_by_field':dict(adds),'stage1_branches':dict(s1counts),'stage1_null_fields':nulls,'stage1_null_cases':null_cases,'stage2_branches':dict(s2counts),'stage2_exact_echoes':sum(e['exact_echo'] for e in echoes),'unmatched_categories':dict(categories),'echo_analysis':echoes,'classification_limits':'These are observed string-level facts, not exhaustive causal error labels. Noncanonical Cold Start names are not automatically semantically wrong.'}
    save(run/'inspection/observations.json',result)
    lines=['# 本轮观察（不修改预测）','',f'最终候选规模：{counts}；新增：{dict(adds)}。',f'阶段一分支：{dict(s1counts)}；null：{nulls}。',f'阶段二分支：{dict(s2counts)}；其中原样回答 {sum(e["exact_echo"] for e in echoes)} 次。','',
        '阶段一为开放名称空间，未与 Gold 精确相等不代表语义错误。阶段二集合外回答按原版保留；仅凭字符串和相同数值不能断定字段错绑。完整逐条候选对照保存在 observations.json，Gold 仅用于输出后的离线诊断。','',mdtable(['集合外回答的证据分类','数量'],categories.items()),'', '## 阶段一 null 原始回答',mdtable(['论文/记录','字段','输入原名','原始回答'],[[x['paper']+'/'+str(x['record']),x['field'],x['original'],repr(x['raw_answer'])] for x in null_cases]),'']
    for scope in ('all27','masked10'):
        b=read(run/'evaluation'/scope/'leaderboards/gold_vs_predicted.json');lines += [f'## {scope} 非空及缺失榜',mdtable(['Task','Dataset','Metric','有效预测论文数','Gold 论文数'],[[x['Task'],x['Dataset'],x['Metric'],len(x['predicted_official_numeric']),len(x['gold_official_numeric'])] for x in b]),'']
    (run/'inspection/findings.md').write_text('\n'.join(lines),encoding='utf-8')
    return result

def main():
    setup();assert RUN==TOP and read(TOP/'execution_status.json')['status']=='ALL_RUNS_COMPLETE';frozen=verify();manifest=read(TOP/'experiment_manifest.json');raw=read(manifest['raw_input_path']);conf=read(TOP/'order_default/config.json');gold=read(conf['gold_path']);boards=read(conf['leaderboards_path'])
    assert sha(TOP/'references/masked10.json')==manifest['masked10_sha256']==sha(manifest['masked10_source'])
    gold_groups=collections.defaultdict(set)
    for paper,item in gold.items():
        for row in item['TDMs']:gold_groups[triple(row)].add(paper)
    data_counts={'papers':len(gold),'gold_tdmrs':sum(len(x['TDMs']) for x in gold.values()),'unique_gold_tdm':len(gold_groups),'groups_at_least_three_papers':sum(len(v)>=3 for v in gold_groups.values()),'supplied_gold_boards':len(boards),'supplied_board_entries':sum(len(x['Leaderboard']) for x in boards),'paper_historical_unique_tdm_and_boards':[138,27],'historical_data_identity_not_proven':True}
    save(TOP/'summary/data_counts.json',data_counts)
    summaries={};observations={};usage={};allnorm={};indices={}
    for rid in RUNS:
        root=TOP/rid;v=read(root/'verification.json');assert v['status']=='PASS';order=read(root/'paper_order.json');assert len(order['papers'])==43 and set(order['papers'])==set(raw) and sha(root/'paper_order.json')==manifest['orders'][rid]['paper_order_sha256']
        initial=read(root/'stage1/initial_labels.json');assert all(not x['ordered_values'] and x['serialized']=='set()' for x in initial.values())
        summaries[rid]={scope:read(root/'evaluation'/scope/'paper_metrics/leaderboard_metrics.json')['aggregate'] for scope in ('all27','masked10')}
        usage[rid]=read(root/'api_usage_summary.json');observations[rid]=inspect_run(rid,raw,gold,boards)
        allnorm[rid]={stage:read(root/stage/filename) for stage,filename in [('stage1','normalized_output.json'),('stage2','leaderboard_normalized_output.json')]}
        for stage,data in allnorm[rid].items():
            assert list(data)==order['papers'] and sum(len(x['normalized_output']) for x in data.values())==284
            for p in raw:
                assert data[p]['source_documents']==raw[p]['source_documents']
                assert [x['Result'] for x in data[p]['normalized_output']]==[x['Result'] for x in json.loads(raw[p]['output'])]
        indices[rid]={'config':str(root/'config.json'),'paper_order':str(root/'paper_order.json'),'stage1':str(root/'stage1/normalized_output.json'),'stage2':str(root/'stage2/leaderboard_normalized_output.json'),'verification':str(root/'verification.json'),'api_call_directories':[str(root/s/'api_calls') for s in ('stage1','stage2')]}
        save(root/'api_calls/index.json',{'run_id':rid,'stage1_path':str(root/'stage1/api_calls'),'stage2_path':str(root/'stage2/api_calls'),'purpose':'Index only, no duplicate accounting'})
    agg={}
    for scope in ('all27','masked10'):
        agg[scope]={name:{'values':{rid:summaries[rid][scope][key] for rid in RUNS},'mean':statistics.mean(summaries[rid][scope][key] for rid in RUNS),'sample_std_ddof1':statistics.stdev(summaries[rid][scope][key] for rid in RUNS),'population_std_ddof0':statistics.pstdev(summaries[rid][scope][key] for rid in RUNS)} for name,key in KEYS.items()}
        save(TOP/'summary'/f'{scope}_mean_std.json',{'status':'THREE_COMPLETE_RUNS','aggregation':'Each run macro over all target boards, then arithmetic mean and SD across three run-level aggregates; predictions never pooled.','main_ddof':1,'author_ddof':'unconfirmed','metrics':agg[scope]})
    # Compare the same paper/record/field, without assuming repeated surface names mean the same entity.
    differences=[]
    for p,x in raw.items():
        for i,row in enumerate(json.loads(x['output'])):
            for k in ('Task','Dataset','Metric'):
                stages={stage:{rid:allnorm[rid][stage][p]['normalized_output'][i][k] for rid in RUNS} for stage in ('stage1','stage2')}
                if any(len(set(v.values()))>1 for v in stages.values()):differences.append({'paper':p,'record':i+1,'field':k,'raw_name':row[k],**stages})
    save(TOP/'summary/order_name_variation.json',{'same_position_differences':differences,'count':len(differences),'interpretation':'Order-dependent candidate histories and stochastic service responses can both contribute; no isolated causal attribution.'})
    variation_lines=['# 同一记录位置在三个顺序下的名称变化','', '按相同 paper_id + record_index + field 比较，输入抽取不变；不把所有名称差异判为语义错误。模型服务也可能有随机性，不能只归因于排序。','',mdtable(['论文/记录','字段','原始名称','阶段','default','种子字符串 0','种子字符串 42'],[[str(d['paper'])+'/'+str(d['record']),d['field'],d['raw_name'],stage,*[d[stage][rid] for rid in RUNS]] for d in differences for stage in ('stage1','stage2') if len(set(d[stage].values()))>1])]
    (TOP/'summary/order_name_variation.md').write_text('\n'.join(variation_lines)+'\n',encoding='utf-8')
    baseline_sources={'Fully + LLM':LB/'paper_metrics/leaderboard_metrics.json','Fully + CS':CS/'leaderboard_evaluation/paper_metrics/leaderboard_metrics.json','Partially all27':PARTIAL/'leaderboard_evaluation/all27/paper_metrics/leaderboard_metrics.json','Partially masked10':PARTIAL/'leaderboard_evaluation/masked_subset/paper_metrics/leaderboard_metrics.json'}
    baselines={k:read(p)['aggregate'] for k,p in baseline_sources.items()};save(TOP/'summary/baseline_comparison.json',{'source_paths_and_sha256':{k:{'path':str(p),'sha256':sha(p)} for k,p in baseline_sources.items()},'baseline_metrics':baselines,'cold_runs':summaries,'cold_aggregates':agg})
    total={k:sum(usage[rid]['total'][k] for rid in RUNS) for k in usage[RUNS[0]]['total']}
    api={'runs':usage,'total':total,'wall_seconds_since_preparation':time.time()-manifest['started_epoch'],'cost':'Actual intermediary invoice unknown; no LangChain dollar estimate used','tests_and_replay_excluded':True,'new_extraction_requests':0}
    save(TOP/'api_usage_summary.json',api)
    report=['# SCILEAD GPT-4.1 Cold Start 三种顺序实验','',
        '三轮均已完成：每轮 43 篇论文、284 条原始预测；完整 Gold 295 条。只重新执行两阶段标准化，没有重新解析、检索、抽取、CS 兜底或修改官方方法。',
        '', '## 审计与配置',
        'Partially 的 204 次阶段二请求全部核验；189 次原样返回来自真实模型响应，15 次精确候选映射，68 条 null 跳过，12 条完整 TDM 精确匹配跳过。未发现模板或适配错误，旧结果保持原样。',
        '默认运行保持原始 JSON 键顺序；另外两轮使用官方字符串排序种子 "0"、"42"，通过 random.seed + random.sample 生成；模型 seed 是整数 0，PYTHONHASHSEED=0。每轮 Task/Dataset/Metric 从三个空集合开始。',
        '实际模型 gpt-4.1-2025-04-14，temperature=0、seed=0、stream=False；不发送 max_tokens 等上限参数，无自动重试、语义缓存或人工修正。此输出参数与作者阶段一默认 15、阶段二默认 100 不同。全部候选序列化、消息、响应及事件已保存。',
        '', '## 主要排行榜结果',
        'LR 指精确 TDM 命中；有效非空榜率另外列出。PC/RC/RBO 由原版代码计算，AO 为已审计的论文 ID 排名补充实现。各轮先对全部目标榜 Macro 汇总，再对三个运行汇总；主标准差 ddof=1，另存 ddof=0。论文正文及 Appendix F 未明确 ddof，因此不声称该统计细节与作者完全一致。',
        'Masked 10 直接复用 Partially 文件并校验哈希，未使用 Cold Start 自动生成的 27 榜文件代替。',
        f'本地提供的 27 榜含 {data_counts["supplied_board_entries"]} 条榜内论文记录；完整 Gold 实际有 {data_counts["unique_gold_tdm"]} 个唯一 TDM、{data_counts["groups_at_least_three_papers"]} 个至少三篇的分组，与论文历史统计 138/27 存在差异。沿用冻结的 27 榜，不自行扩大或重建，亦不声称已证明历史数据版本完全相同。']
    for scope in ('all27','masked10'):
        report += ['',f'### {scope}',mdtable(['运行',*KEYS],[[rid,*[f'{summaries[rid][scope][key]:.6f}' for key in KEYS.values()]] for rid in RUNS]+[['均值 ± 样本标准差',*[f"{agg[scope][name]['mean']:.6f} ± {agg[scope][name]['sample_std_ddof1']:.6f}" for name in KEYS]]]),'']
    report += ['## 动态名称与阶段二行为',mdtable(['运行','Task/Dataset/Metric 最终规模','新增名称','映射已有名称','null Task/Dataset/Metric','阶段二请求','精确映射','原样返回'],[[rid,'/'.join(str(observations[rid]['final_label_counts'][k]) for k in ('Task','Dataset','Metric')),observations[rid]['stage1_branches'].get('original_name_added',0),observations[rid]['stage1_branches'].get('existing_candidate',0),'/'.join(str(observations[rid]['stage1_null_fields'][k]) for k in ('Task','Dataset','Metric')),usage[rid]['stage2']['attempts'],observations[rid]['stage2_branches'].get('tuple_mapped',0),observations[rid]['stage2_exact_echoes']] for rid in RUNS]),'',
        mdtable(['运行','论文/记录','null 字段','原始输入','原始回答'],[[rid,x['paper']+'/'+str(x['record']),x['field'],x['original'],repr(x['raw_answer'])] for rid in RUNS for x in observations[rid]['stage1_null_cases']]),
        '上述 null 来自成功请求后未满足原版字符串成员/原名判断的回答；没有去引号、修正拼写或改写返回值，不能把它们计为接口失败。',
        f'同一 paper_id + record_index + field 在三轮任一阶段存在不同标准名称的字段位置共 {len(differences)} 个；完整对照见 summary/order_name_variation.json。候选历史随顺序变化，模型服务也不保证确定性，不能将全部差异单独归因于论文顺序。',
        '开放名称与 Gold 不同不等同于语义错误。集合外回答区分：已核验的目标榜名称未对齐、已核验的合法榜外 TDM/别名、尚待人工核验。首篇的人工案例依据历史 Table 5 OURS 行及数据集定义检查；只有当前行与该原始抽取保持一致时才采用这项已核验对应关系。另保存同论文同数值 Gold 候选及原抽取字段差异，供排查已有字段错绑；无法确认的错误不计入确定根因统计。没有把相同数值自动认定为对应行。',
        '', '## 不变性与辅助诊断',
        '每轮每条 Result 字符串、记录顺序及 source_documents 保持原样。官方 Result IIM F1 均为 0.703840880674；严格 Decimal 数值相等诊断 F1 均为 0.586781786324。其余 ETM/IIM 仅保存为诊断，不能冒充论文报告的 Cold Start 主结果。不同论文迭代顺序可能产生约 1e-16 浮点求和差异，验收采用 1e-14 容差，未修改官方指标。',
        '', '## API 用量',mdtable(['运行','阶段一请求','阶段二请求','成功','失败/状态不明','Prompt Tokens','Completion Tokens','总 Tokens','请求秒数'],[[rid,usage[rid]['stage1']['attempts'],usage[rid]['stage2']['attempts'],usage[rid]['total']['successful_responses'],usage[rid]['total']['failed_or_uncertain'],usage[rid]['total']['prompt_tokens'],usage[rid]['total']['completion_tokens'],usage[rid]['total']['total_tokens'],round(usage[rid]['total']['request_seconds'],2)] for rid in RUNS]),'',
        f'合计 {total["attempts"]} 次真实请求，成功 {total["successful_responses"]} 次；失败或状态不明 {total["failed_or_uncertain"]} 次；未知用量 {total["unknown_usage_attempts"]} 次。总 Tokens {total["total_tokens"]}，HTTP 请求累计 {total["request_seconds"]:.2f} 秒，准备至验收墙钟 {api["wall_seconds_since_preparation"]:.2f} 秒。平台账单金额未知，未用 LangChain 成本估计冒充结算。',
        '', '## 冻结与交付',
        f'四个历史目录共 {sum(map(len,frozen["directories"].values()))} 个文件的文件列表与 SHA-256 未变；官方源码、Prompt、Gold、依赖未变。逐轮实际响应经原版 main 离线重放，候选顺序、事件、输出一致，重放新增 API 为 0。',
        '各轮包含完整顺序/config、stage1 和 stage2 输出、逐请求真实 wire payload/raw response、候选更新事件、checkpoint、all27/masked10 评测及 verification。根目录 summary 保留每轮原始数值、均值与两种标准差；comparison_with_partially.md 为历史基线对比，README.md 说明断点恢复。',
        '本轮结束，不启动其他实验。']
    (TOP/'report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    comp=['# 与已冻结 Baseline 的描述性对比','', '全部数据从原始评测 JSON 读取；路径和哈希见 summary/baseline_comparison.json。不同实验的名称候选协议不同，以下仅作描述性对比，不是单因素因果实验。','', '## 全部 27 榜',mdtable(['Baseline',*KEYS],[[name,*[f'{baselines[name][key]:.6f}' for key in KEYS.values()]] for name in ('Fully + LLM','Fully + CS','Partially all27')]+[['Cold Start 三轮均值',*[f"{agg['all27'][name]['mean']:.6f}" for name in KEYS]]]),'','## 同一 Masked 10 榜',mdtable(['Baseline',*KEYS],[['Partially',*[f"{baselines['Partially masked10'][key]:.6f}" for key in KEYS.values()]],['Cold Start 三轮均值',*[f"{agg['masked10'][name]['mean']:.6f}" for name in KEYS]]]),'','未根据任何分数修改候选、Prompt、返回值或选择运行结果。']
    partial_nulls=read(PARTIAL/'stage1/summary.json')['null_fields'];partial_labels=read(PARTIAL/'stage1/final_labels.json')
    comp += ['', '## 开放名称与 null 观察',f'Partially 阶段一最终候选规模：{ {k:len(v["ordered_values"]) for k,v in partial_labels.items()} }；null 字段：{partial_nulls}。',mdtable(['Cold Start 运行','最终候选规模','null 字段'],[[rid,observations[rid]['final_label_counts'],observations[rid]['stage1_null_fields']] for rid in RUNS]),'','Partially 的 Metric 使用固定名称集合，Cold Start 则允许 Metric 原名新增，两者按作者各自协议执行。较少 null 不代表更高的语义正确率；候选别名分散和最终榜单对齐需要分别观察。']
    (TOP/'comparison_with_partially.md').write_text('\n'.join(comp)+'\n',encoding='utf-8')
    save(TOP/'output_index.json',indices)
    verify();manifest['status']='THREE_RUNS_COMPLETE_VERIFIED';save(TOP/'experiment_manifest.json',manifest)
    save(TOP/'verification.json',{'status':'PASS','complete_runs':3,'papers_per_run':43,'predictions_per_run':284,'gold_records':295,'initial_sets_empty_all_runs':True,'paper_orders_cli_string_types_verified':True,'all27_and_same_masked10_evaluated':True,'all_successful_requests_uncapped':True,'all_http200_model_snapshot_finish_stop':True,'actual_prompts_and_candidate_order_verified':True,'original_main_replay_matches_all_runs':True,'results_record_order_sources_unchanged':True,'result_iim_f1':0.7038408806738071,'strict_result_f1':0.5867817863240564,'frozen_directories':{p:len(v) for p,v in frozen['directories'].items()},'source_gold_prompt_dependencies_unchanged':True,'new_parsing_retrieval_extraction':0,'paid_requests':total['attempts'],'failed_or_uncertain':total['failed_or_uncertain'],'unknown_usage':total['unknown_usage_attempts'],'aggregation':{'n':3,'main_ddof':1,'additional_ddof':0,'no_prediction_pooling':True},'author_ddof_unconfirmed':True})
    save(TOP/'artifact_sha256.json',{str(p.relative_to(TOP)):sha(p) for p in TOP.rglob('*') if p.is_file() and p.name!='artifact_sha256.json' and 'runtime' not in p.parts})
    print(json.dumps({'status':'COMPLETE','total_usage':total,'all27':agg['all27'],'masked10':agg['masked10']},ensure_ascii=False))
if __name__=='__main__':main()
