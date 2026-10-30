"""Final independent audit and Chinese delivery; never requests a model."""
import concurrent.futures,statistics
from datetime import datetime
from variant_runtime import *
from evaluate_variants import aggregate_results

BRANCHES=('partially','cold_default','cold_0','cold_42')
NAMES={'fully_llm':'Fully + LLM（既有）','fully_cs':'Fully + CS','partially':'Partially','cold_default':'Cold Start 默认','cold_0':'Cold Start "0"','cold_42':'Cold Start "42"'}
METRICS=('Task IIM','Dataset IIM','Metric IIM','Result IIM','TDM Exact Match','TDMR Exact Match')
def main():
    setup();start=time.monotonic();calls=[];issues=[];cases=[];unresolved=[]
    protected=read(TOP/'protected_hashes.json')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        checked=list(pool.map(lambda item:(item[0],Path(item[0]).is_file() and sha(item[0])==item[1]),protected.items()))
    changed=[p for p,ok in checked if not ok];assert not changed,'FROZEN_FILES_CHANGED'
    source=read(BASE/'merged/output.json');raw=read(TOP/'inputs/output.json')
    assert set(raw)==set(source) and all(raw[p]==source[p] for p in raw)
    frozen_methods={k:sha(REPO/k) for k in ('tdm_embedding_normalization.py','tdm_llm_masked_normalization.py','leaderboard_llm_normalization.py','tdm_eval.py','leaderboard_eval.py','prompts.json')}
    for branch in BRANCHES:
        cfg=read(TOP/branch/'config.json')
        for stage in ('stage1','stage2'):
            root=TOP/branch/stage
            summary=read(root/'summary.json') if (root/'summary.json').exists() else {}
            if summary.get('status')!='COMPLETE':issues.append({'branch':branch,'stage':stage,'status':summary.get('status','PENDING'),'reason':summary.get('error')})
            if summary.get('status')=='COMPLETE':assert sha(summary['output_path'])==summary['output_sha256']
            for logical in sorted((root/'api_calls').glob('*/attempt.lock')):
                if not (logical.parent/'accepted.json').exists():unresolved.append(str(logical.parent))
            for p in sorted((root/'api_calls').rglob('state.json')):
                folder=p.parent;logical=folder.parent if folder.name=='retry_1' else folder
                s=read(p);e=read(logical/'expected.json');q=read(folder/'request.json')
                if folder.name=='retry_1':
                    authorization=read(logical/'retry_authorization.json')
                    assert authorization['scope'].removesuffix(' only')==f'{branch}/{stage}/{logical.name}','RETRY_SCOPE_MISMATCH'
                    assert authorization['max_additional_attempts']==1 and authorization['original_request_sha256']==sha(logical/'request.json')
                    assert q==read(logical/'request.json'),'RETRY_PAYLOAD_CHANGED'
                assert q==frozen.payload(e['messages']) and q['model']==MODEL
                assert not set(q)&{'temperature','seed','max_tokens','tools','response_format','max_output_tokens'}
                accepted=s.get('http_status')==200 and (folder/'accepted.json').is_file();body=read(folder/'response.json') if (folder/'response.json').exists() else {}
                finish=(body.get('choices') or [{}])[0].get('finish_reason')
                if accepted:
                    a=read(folder/'accepted.json');assert s['http_status']==200 and sha(folder/'response.json')==a['response_sha256']
                    assert frozen.validate(body,False)==a['raw_answer'] and body['model']==MODEL and finish=='stop'
                usage=s.get('usage') or {}
                calls.append({'branch':branch,'stage':stage,'call':str(folder.relative_to(root/'api_calls')),'authorized_retry':folder.name=='retry_1','paper':e['paper'],'record':e['record'],'field':e['field'],'request_model':q['model'],'response_model':body.get('model'),'http_status':s.get('http_status'),'finish_reason':finish,'accepted':accepted,'prompt_tokens':usage.get('prompt_tokens'),'completion_tokens':usage.get('completion_tokens'),'total_tokens':usage.get('total_tokens'),'elapsed_seconds':s.get('elapsed_seconds'),'started_utc':s.get('started_utc'),'response_id':s.get('response_id'),'raw_response_path':str(folder/'response_raw.txt'),'request_sha256':sha(folder/'request.json'),'candidate_sha256':e['candidate_sha256'],'prompt_sha256':e['prompt_sha256']})
            # Categorize actual official decisions; no inferred semantic repairs.
            events=[read(p) for p in sorted((root/'events').glob('*.json'))]
            if stage=='stage1':
                categories={name:sum(e.get('branch')==name for e in events) for name in ('exact_or_result','existing_candidate','original_name_added','null')}
                selected=[{'paper':e['paper'],'record':e['record'],'field':e['field'],'original':e['original'],'raw_answer':e.get('raw_answer'),'normalized':e['normalized'],'branch':e['branch']} for e in events if e.get('branch')=='null']
            else:
                categories={name:sum(e.get('branch')==name for e in events) for name in ('null_skipped','exact_tuple','tuple_mapped','unmatched_preserved')}
                selected=[{'paper':e['paper'],'record':e['record'],'original':e['original'],'raw_answer':e.get('raw_answer'),'normalized':e['normalized'],'branch':e['branch']} for e in events if e.get('branch') in ('tuple_mapped','unmatched_preserved')][:20]
            cases.append({'branch':branch,'stage':stage,'categories':categories,'examples':selected,'interpretation':'Branches and string acceptance only; unmatched/added names are not automatically semantic errors.'})
    with (TOP/'request_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
        if calls:w=csv.DictWriter(f,fieldnames=list(calls[0]));w.writeheader();w.writerows(calls)
    usage={k:sum(c[k] or 0 for c in calls) for k in ('prompt_tokens','completion_tokens','total_tokens','elapsed_seconds')}
    usage.update(actual_requests=len(calls),successful_requests=sum(c['accepted'] for c in calls),failed_or_unknown=sum(not c['accepted'] for c in calls),unknown_usage_requests=sum(c['total_tokens'] is None for c in calls),authorized_additional_attempts=sum(c['authorized_retry'] for c in calls),unresolved_logical_requests=unresolved,new_extraction_requests=0,fully_cs_model_api_requests=0,automatic_retries=0,historical_fully_requests_excluded=720)
    if calls:
        starts=[datetime.fromisoformat(c['started_utc']).timestamp() for c in calls]
        usage['api_wall_seconds']=max(t+(c['elapsed_seconds'] or 0) for t,c in zip(starts,calls))-min(starts)
        usage['elapsed_seconds_definition']='Sum of individual request latencies; branches overlap. api_wall_seconds spans first send through last response, including pauses.'
    usage['failures_by_http_status']={str(code):sum(c['http_status']==code and not c['accepted'] for c in calls) for code in sorted({c['http_status'] for c in calls if c['http_status'] is not None and not c['accepted']})}
    save(TOP/'api_usage_summary.json',usage);save(TOP/'inspection/normalization_decisions.json',cases)
    cs=read(TOP/'fully_cs/verification.json');assert cs['status']=='PASS' and cs['predicted_tdmrs']==335
    baseline=aggregate_results(read(BASE/'evaluation/eval_results.json'))
    metrics={'fully_llm':baseline,'fully_cs':read(TOP/'fully_cs/evaluation/metrics_with_f1.json')['aggregate']}
    stage1_metrics={}
    boards={'fully_llm':read(TOP/'evaluation_references/gpt56_fully/all27/paper_metrics/leaderboard_metrics.json')['aggregate'],'fully_cs':read(TOP/'fully_cs/leaderboard_evaluation/paper_metrics/leaderboard_metrics.json')['aggregate']}
    for branch in BRANCHES:
        path=TOP/branch/'evaluation/stage2/metrics_with_f1.json';lb=TOP/branch/'evaluation/all27/paper_metrics/leaderboard_metrics.json'
        if path.exists():metrics[branch]=read(path)['aggregate']
        if lb.exists():boards[branch]=read(lb)['aggregate']
        s1=TOP/branch/'evaluation/stage1/metrics_with_f1.json'
        if s1.exists():stage1_metrics[branch]=read(s1)['aggregate']
    report_status=read(TOP/'summary/report_status.json') if (TOP/'summary/report_status.json').exists() else {}
    complete=not issues and not unresolved and report_status.get('status')=='COMPLETE'
    # All historical protected directories retain both contents and file membership.
    directories=(BASE,PILOT/'gpt56_sol_fully/20261024_A2_formal43',PILOT/'full43_uncapped',PILOT/'full43_cs',PILOT/'full43_partially',PILOT/'full43_cold_start')
    membership={}
    for d in directories:
        before={p for p in protected if Path(p).is_relative_to(d)};after={str(p) for p in d.rglob('*') if p.is_file()}
        membership[str(d)]={'unchanged':before==after,'added':sorted(after-before),'removed':sorted(before-after)}
    assert all(x['unchanged'] for x in membership.values())
    verification={'status':'PASS_COMPLETE' if complete else 'INCOMPLETE','papers':43,'gold_records':295,'predictions_per_run':335,'fully_cs':cs['status'],'branch_issues':issues,'all_recorded_requests_accepted':usage['failed_or_unknown']==0,'all_logical_requests_resolved':not unresolved,'authorized_additional_attempts':usage['authorized_additional_attempts'],'generation_parameters':read(TOP/'generation_config.json'),'actual_request_parameters_audited':len(calls),'source_hashes_checked':len(checked),'changed_frozen_files':changed,'frozen_file_membership':membership,'official_source_hashes':frozen_methods,'per_paper_extraction_content_unchanged':True,'new_extraction_calls':0,'no_new_retrieval':True,'no_automatic_retries':True,'provider_backing_model_identity_independently_verified':False,'verification_seconds':time.monotonic()-start}
    save(TOP/'verification.json',verification);save(TOP/'metrics_summary.json',{'tuple_metrics_stage1':stage1_metrics,'tuple_metrics_stage2':metrics,'leaderboards_all27':boards,'cold_statistics':read(TOP/'summary/cold_statistics.json') if (TOP/'summary/cold_statistics.json').exists() else None})
    manifest=read(TOP/'experiment_manifest.json')
    if not (TOP/'engineering/experiment_manifest_prepared.json').exists():save(TOP/'engineering/experiment_manifest_prepared.json',manifest)
    manifest.update(status='COMPLETE' if complete else 'INCOMPLETE',finalized_epoch=time.time(),actual_normalization_requests=len(calls),successful_responses=usage['successful_requests'],verification_path=str(TOP/'verification.json'),metrics_summary_path=str(TOP/'metrics_summary.json'))
    save(TOP/'experiment_manifest.json',manifest)
    lines=['# GPT-5.6 Sol：Fully + CS、Partially与Cold Start实验汇总','',f'状态：{"全部完成" if complete else "部分完成，见阻塞记录"}。43篇论文、295条Gold，复用335条冻结抽取记录；没有重新解析、检索或Extraction。','',
      '本轮独立目录：`D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024`。Mixtral未启动。','',
      '## 配置与流程','',
      '- Fully + CS：原版bilingual-embedding-large、CPU FP32、cosine top-1，无额外相似度阈值；23/71/26候选及顺序不变。',
      '- Partially：原版seed=0遮蔽规则（固定10个被遮蔽榜），先动态名称标准化，再进行官方27榜TDM匹配。',
      '- Cold Start：Task/Dataset/Metric从空集合开始，分别执行默认顺序、字符串种子"0"及"42"两种顺序；每轮包含相同的两个官方阶段。',
      '- GPT请求沿用已验证Fully参数：gpt-5.6-sol、reasoning_effort=medium、max_completion_tokens=32768、stream=false；不发送temperature、seed、tools或response_format。方法内部随机种子仍为0。',
      '- 原版脚本gpt4-turbo-128k只用于选择消息角色和处理分支；真实请求与响应标识均单独核查。没有语义缓存、人工改写、去重或按Gold选择答案。',
      '- 为保持历史顺序比较，仅调整新输入副本的论文键顺序；每篇记录、字段、Result、证据内容和顺序不变。原始GPT56恢复结果及其他冻结结果均未覆盖。','',
      '## 元组指标','',
      '下表全部为F1（百分比）。P/R由官方逐篇Macro给出，F1=2PR/(P+R)，并非逐篇F1算术均值。完整P/R/F1、阶段一和阶段二结果分别保存。Cold Start的元组指标作为诊断，主要比较仍为排行榜指标。','',
      '|设置|Task IIM|Dataset IIM|Metric IIM|Result IIM|TDM|TDMR|','|---|---:|---:|---:|---:|---:|---:|']
    for name,m in metrics.items():lines.append('|'+NAMES[name]+'|'+'|'.join(f'{m[k]["F1"]*100:.2f}' for k in METRICS)+'|')
    lines+=['','上表Partially/Cold Start为第二阶段排行榜TDM匹配后的元组诊断；Fully仅有名称标准化。由于第二阶段接受范围为27个排行榜TDM，不能把其与Fully名称标准化视为完全同一评价条件。第一阶段名称标准化结果如下，更适合观察动态名称集合的影响。','',
        '|第一阶段名称标准化|Task IIM|Dataset IIM|Metric IIM|Result IIM|TDM|TDMR|','|---|---:|---:|---:|---:|---:|---:|']
    for name,m in stage1_metrics.items():lines.append('|'+NAMES[name]+'|'+'|'.join(f'{m[k]["F1"]*100:.2f}' for k in METRICS)+'|')
    lines+=['','动态候选名称数量（起始→最终）：','','|设置|Task|Dataset|Metric|','|---|---:|---:|---:|']
    for name in BRANCHES:
        first=TOP/name/'stage1/initial_labels.json';last=TOP/name/'stage1/final_labels.json'
        if first.exists() and last.exists():
            a,z=read(first),read(last)
            lines.append('|'+NAMES[name]+'|'+'|'.join(f'{len(a[k]["ordered_values"])}→{len(z[k]["ordered_values"])}' for k in ('Task','Dataset','Metric'))+'|')
    lines+=['','名称被原版逻辑接受不等于与Gold名称完全一致。默认顺序Cold Start在2020.findings-emnlp.378.pdf中保留了ON5E、F1 score等名称，第二阶段才将其中部分映射到27榜候选；六个Result均未改变。具体对照见`inspection/candidate_scope_example.md`。此为输出完成后的离线分析，未反馈模型或修改预测。']
    lines+=['','## 排行榜指标：固定27个Gold榜','','|设置|LR|有效非空榜率|PC|RC|数值列表RBO|论文ID AO|','|---|---:|---:|---:|---:|---:|---:|']
    keys=('LR_exact_tdm_hit','LR_nonempty_finite_result','PC_official','RC_official','RBO_official_value_rankings','AO_paper_id_macro_all_gold_boards')
    for name,m in boards.items():lines.append('|'+NAMES[name]+'|'+'|'.join(f'{m[k]*100:.2f}' for k in keys)+'|')
    cold=read(TOP/'summary/cold_statistics.json') if (TOP/'summary/cold_statistics.json').exists() else {}
    if cold.get('status')=='COMPLETE':
        stats=cold['leaderboards']['all27'];labels=('LR','Finite nonempty','PC','RC','RBO (values)','AO (paper IDs)')
        lines+=['|Cold Start均值±样本标准差|'+'|'.join(f'{stats[k]["mean"]*100:.2f} ± {stats[k]["sample_std_ddof1"]*100:.2f}' for k in labels)+'|']
    lines+=['','PC/RC/RBO使用未经修改的官方评价。LR和论文ID AO为已有审计定义的补充指标；官方RBO不是论文ID AO。保留重复记录、官方数值转换及最后有效记录覆盖规则。另有masked10子集指标、严格Decimal数值辅助诊断，不替代原版分数。','',
      '## 调用与完整性','',f'本轮实际标准化请求{len(calls)}次，成功{usage["successful_requests"]}次，失败/未知{usage["failed_or_unknown"]}次。输入Tokens {usage["prompt_tokens"]}，输出Tokens {usage["completion_tokens"]}，总Tokens {usage["total_tokens"]}。不包含历史Fully的720次请求。',
      f'核对{len(checked)}个冻结文件内容及历史目录文件清单，均未改变。官方源码、Prompt、Gold及每篇原始抽取不变。全部运行记录见request_audit.csv、api_usage_summary.json、verification.json。','',
      '## 比较解释与报告索引','',
      'Fully + LLM与Fully + CS使用同一批335条抽取，可比较两种标准化方法的影响；Partially与Cold Start还改变了候选信息条件及动态名称更新过程。GPT-4.1历史实验为284条抽取、不同生成参数，跨模型分数差异不能只归因于标准化模型。',
      'Cold Start三轮先各自计算Macro指标，再统计均值与标准差（主报ddof=1，另存ddof=0）；不合并三轮预测。原论文未明确标准差ddof，保留该限制。',
      '- `report.md`：两阶段全部P/R/F1、masked10/all27、与GPT-4.1的详细对比。',
      '- `fully_cs/report.md`：CS方法、每项指标、资源和完整性。',
      '- `summary/variant_comparison.json`、`summary/cold_statistics.json`：机器可读对照与三轮统计。',
      '- `inspection/normalization_decisions.json`：动态名称新增、null及榜级匹配分支；仅描述真实处理结果，不自动把未匹配名称认定为语义错误。',
      '- 各分支`stage1/`、`stage2/`：标准化原始响应、实际请求参数、候选集合顺序、事件、检查点及最终输出。','']
    position=lines.index('## 调用与完整性')+3
    lines[position:position]=['',f'原始失败按HTTP状态统计为{usage["failures_by_http_status"]}；经用户分别批准，额外尝试{usage["authorized_additional_attempts"]}次。当前未解决请求位置{len(unresolved)}个。失败未返回用量，Token总数仅为已知用量。API墙钟耗时约{usage.get("api_wall_seconds",0)/60:.1f}分钟，含暂停与恢复。成功响应不重发；本地文件占用仅重试相同内容的写入。','']
    if issues:lines+=['## 未完成项','',json.dumps(issues,ensure_ascii=False,indent=2)]
    (TOP/'实验结果汇总.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'status':verification['status'],'requests':len(calls),'tokens':usage['total_tokens'],'protected_files':len(checked),'report':str(TOP/'实验结果汇总.md')},ensure_ascii=False))
    return 0 if complete else 2
if __name__=='__main__':sys.exit(main())
