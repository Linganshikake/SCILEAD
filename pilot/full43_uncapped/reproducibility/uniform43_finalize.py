"""Offline phase-9 audit and old/new comparison; never edits model outputs."""
import ast, collections, hashlib, importlib.metadata, json, os, shutil, subprocess, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]; PILOT=ROOT/'pilot'; RUN=PILOT/'full43_uncapped'; OLD=PILOT/'full43'; REPO=ROOT/'emnlp2024-leaderboard-generation'; SCRIPTS=Path(__file__).parent
CAPS={'max_tokens','max_completion_tokens','max_output_tokens'};MODEL='gpt-4.1-2025-04-14'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metric(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0.0}
def historical_extract(d):
    fs=list(d.glob('api_calls/*/request.json'));return read(fs[0] if fs else d/'request_payload.json')
def main():
    m=read(RUN/'manifest.json');env=read(RUN/'environment.json');goldpath=Path(m['gold_path']);assert sha(goldpath)==m['gold_sha256'];gold=read(goldpath)
    assert len(m['papers'])==43 and len({r['id'] for r in m['papers']})==43 and sum(r['gold_count'] for r in m['papers'])==295
    assert set(gold)=={r['id'] for r in m['papers']}
    preserved=read(RUN/'preserved_existing_sha256.json')
    for p,h in preserved.items():assert sha(Path(p))==h,p
    for p,h in env['source_sha256'].items():assert sha(Path(p))==h,p
    assert env['dependencies']=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    git=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'status','--porcelain'],cwd=REPO,text=True,capture_output=True,check=True);assert not git.stdout.strip()
    commit=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'rev-parse','HEAD'],cwd=REPO,text=True).strip();assert commit==env['git_commit']
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HOME=str(ROOT/'assets/huggingface'));sys.path.insert(0,str(REPO))
    from prompting import NormalizationPrompt
    template=NormalizationPrompt(read(REPO/'prompts.json')['normalization-system-prompt'],'gpt4-turbo-128k').prompt_template
    labels={k:{r[k] for p in gold.values() for r in p['TDMs']} for k in ('Task','Dataset','Metric')};assert {k:len(v) for k,v in labels.items()}=={'Task':23,'Dataset':71,'Metric':26}
    selected=collections.Counter();new=collections.Counter();reused=collections.Counter();response_ids=set();audit=[];comparison=[];failures=[]
    oldmetrics=read(OLD/'evaluation/metrics_with_f1.json');metrics=read(RUN/'evaluation/metrics_with_f1.json');merged=read(RUN/'merged/output.json');mergednorm=read(RUN/'merged/normalized_output.json')
    summaries={s['paper']:s for s in read(RUN/'stage_summary.json')};oldsummaries={s['paper']:s for s in read(OLD/'stage_summary.json')}
    for row in m['papers']:
        ident=row['id'];ex=Path(row['extraction_dir']);no=Path(row['normalization_dir']);src=Path(row['source_extraction_dir'])
        assert sha(Path(row['preprocess_dir'])/'processed_docs.pkl')==row['evidence_sha256']==sha(Path(row['source_preprocess_dir'])/'processed_docs.pkl')
        if row['extraction_reused']:assert sha(ex/'output.json')==sha(src/'output.json')
        if row['normalization_reused']:assert sha(no/'normalized_output.json')==sha(Path(row['source_normalization_dir'])/'normalized_output.json')
        if not (ex/'summary.json').exists() or read(ex/'summary.json')['status']!='COMPLETE' or not (no/'summary.json').exists() or read(no/'summary.json')['status']!='COMPLETE':
            failures.append({'paper':ident,'status':row['status']});continue
        rawdoc=read(ex/'output.json')[ident];raw=json.loads(rawdoc['output']);normdoc=read(no/'normalized_output.json')[ident];nr=normdoc['normalized_output']
        assert rawdoc==merged[ident] and normdoc==mergednorm[ident]
        assert rawdoc['source_documents']==read(src/'output.json')[ident]['source_documents']==normdoc['source_documents']
        assert len(raw)==len(nr) and all(isinstance(r,dict) and set(r)=={'Task','Dataset','Metric','Result'} and all(isinstance(v,str) for v in r.values()) for r in raw)
        assert [r['Result'] for r in raw]==[r['Result'] for r in nr]
        if not row['normalization_reused']:assert read(no/'config.json')['input_sha256']==sha(ex/'output.json')
        actual=read(ex/'api_calls/0001/request.json');old=historical_extract(src)
        assert {k:v for k,v in actual.items() if k not in CAPS}=={k:v for k,v in old.items() if k not in CAPS}
        sets=read(no/'candidate_sets.json');assert {k:ast.literal_eval(v) for k,v in sets.items()}==labels
        plan=read(no/'request_plan.json');expected_indices=[(i+1,k,v) for i,r in enumerate(raw) for k,v in r.items() if k!='Result' and v not in labels[k]]
        assert len(plan)==len(expected_indices);normalized_replay=[dict(r) for r in raw]
        for index,(entry,(record,field,value)) in enumerate(zip(plan,expected_indices),1):
            assert (entry['record'],entry['field'],entry['original_value'])==(record,field,value)
            messages=[{'role':{'system':'system','human':'user'}[mm.type],'content':mm.content} for mm in template.invoke({'items':sets[field],'input':value}).to_messages()]
            assert entry['messages']==messages
            state=read(no/f'api_calls/{index:04d}/state.json');answer=state['raw_answer'];normalized_replay[record-1][field]=answer if answer in labels[field] else None
        assert normalized_replay==nr,'Official field mapping differs: '+ident
        stage_counts={}
        for stage,folder,is_reused in [('extract',ex,row['extraction_reused']),('normalize',no,row['normalization_reused'])]:
            calls=sorted(folder.glob('api_calls/*/attempt.json'));assert len(calls)==(1 if stage=='extract' else len(plan))
            count=len(calls);stage_counts[stage]=count;dest=reused if is_reused else new
            for attempt in calls:
                d=attempt.parent;q=read(d/'request.json');state=read(d/'state.json');response=read(d/'response.json')
                assert not (CAPS & q.keys()),str(d)
                assert q['model']==MODEL and q['temperature']==0 and q['seed']==0 and not q.get('stream',False) and q.get('n',1)==1
                assert state['status']=='COMPLETE' and state['attempts']==1 and read(attempt)['attempt']==1
                assert state['http_status']==200 and state['returned_model']==MODEL and state['finish_reason']=='stop'
                assert response['model']==MODEL and response['choices'][0]['finish_reason']=='stop' and response['choices'][0]['message']['content']==state['raw_answer']
                assert response['id'] not in response_ids;response_ids.add(response['id'])
                assert q['messages']==state['expected']['messages'];assert state['usage']==response['usage']
                if stage=='extract':assert state['raw_answer']==rawdoc['output']
                for target in (selected,dest):
                    target['requests']+=1;target[stage+'_requests']+=1
                    for k in ('prompt_tokens','completion_tokens','total_tokens'):target[k]+=state['usage'][k]
            if stage=='extract' and not is_reused:assert count==1
        audit.append({'paper':ident,'extraction_reused':row['extraction_reused'],'normalization_reused':row['normalization_reused'],'evidence_and_messages_identical':True,'schema_valid':True,'normalization_official_logic_replay_matches':True,'all_requests_uncapped_stop_http200':True,'requests':stage_counts,'normalization_null_fields':sum(v is None for r in nr for v in r.values()),'extracted_records':len(raw)})
        om=oldmetrics['per_paper'][ident];nm=metrics['per_paper'][ident]
        if row['normalization_reused']:assert om==nm
        comparison.append({'paper':ident,'gold_count':row['gold_count'],'extraction_reused':row['extraction_reused'],'normalization_reused':row['normalization_reused'],'old_extracted_records':oldsummaries[ident]['extracted_records'],'new_extracted_records':len(raw),'old_null_fields':oldsummaries[ident]['normalized_null_fields'],'new_null_fields':summaries[ident]['normalized_null_fields'],'old_metrics':om,'new_metrics':nm})
    assert len(audit)+len(failures)==43
    successful_new=dict(new);failed_attempts=0
    for archive_entry in m.get('failed_attempt_archives',[]):
        archive=Path(archive_entry['path']);authorization=read(RUN/'recovery_authorization.json')
        assert str(archive)==authorization['failure_archive']
        for relative,h in authorization['failure_files_sha256'].items():assert sha(archive/relative)==h
        for attempt in archive.glob('api_calls/*/attempt.json'):
            state=read(attempt.parent/'state.json');q=read(attempt.parent/'request.json')
            assert state['status']=='FAILED' and not state.get('http_status') and not (CAPS & q.keys())
            assert state['error_type']=='APIConnectionError';failed_attempts+=1;new['requests']+=1;new['normalize_requests']+=1
        assert read(archive/'api_calls/0001/request.json')==read(Path(next(r for r in m['papers'] if r['id']==archive_entry['paper'])['normalization_dir'])/'api_calls/0001/request.json')
    assert failed_attempts<=1
    accounting=read(RUN/'api_usage_summary.json');prior=read(OLD/'api_usage_summary.json')['cumulative_selected']
    for k in ('requests','prompt_tokens','completion_tokens','total_tokens'):
        assert accounting['new_experiment'][k]==new[k] and accounting['selected_reused_stages'][k]==reused[k]
        assert accounting['cumulative_selected'][k]==prior[k]+new[k]
    accounting.update(current_baseline_selected_requests=dict(selected),new_experiment_by_stage=dict(new),new_successful_requests_by_stage=successful_new,new_failed_attempts=failed_attempts,selected_reused_requests_by_stage=dict(reused),accounting_note='Cumulative execution = full43 historical cumulative + newly executed requests including archived connection failure; current selected baseline excludes superseded capped successes and failures. Copied long-paper extraction counted once as reused. Tokens are known usage, not an upper bound on possible billed usage.')
    accounting['execution_wall_seconds']=round(max(read(RUN/'execution_finished.json')['epoch'],read(RUN/'recovery_finished.json')['epoch'] if (RUN/'recovery_finished.json').exists() else 0)-read(RUN/'execution_started.json')['epoch'],3)
    save(RUN/'api_usage_summary.json',accounting)
    for name,ag in metrics['aggregate'].items():
        pm=[p[name] for p in metrics['per_paper'].values()];calculated=metric(sum(v['Precision'] for v in pm)/len(pm),sum(v['Recall'] for v in pm)/len(pm))
        assert all(abs(ag[k]-calculated[k])<1e-12 for k in ag)
    diagnostics=read(RUN/'evaluation/error_analysis.json');aux=[v['strict_result_iim'] for v in diagnostics.values()];strict=metric(sum(v['Precision'] for v in aux)/len(aux),sum(v['Recall'] for v in aux)/len(aux))
    save(RUN/'evaluation/strict_result_metrics.json',{'aggregate':strict,'definition':'Auxiliary Decimal finite numeric equality. Distinct nonnumeric strings retained in denominator. Does not replace official substring-based Result IIM.','substring_vs_strict_pair_count':sum(len(v['substring_vs_strict_discrepancies']) for v in diagnostics.values())})
    save(RUN/'evaluation/comparison_with_full43.json',{'old_aggregate':oldmetrics['aggregate'],'new_aggregate':metrics['aggregate'],'per_paper':comparison,'old_usage':read(OLD/'api_usage_summary.json'),'new_usage':accounting,'causal_claim':False})
    v=read(RUN/'verification.json');v.update(preserved_files_checked=len(preserved),dependencies_unchanged=True,gold_unchanged=True,git_commit=commit,candidate_counts={k:len(vv) for k,vv in labels.items()},extractions_rerun=sum(not r['extraction_reused'] for r in m['papers']),normalizations_rerun=sum(not r['normalization_reused'] for r in m['papers']),pdf_parsing_embedding_retrieval_reruns=0,all_selected_requests_omit_output_limits=not failures,all_selected_requests_http200_stop_snapshot=not failures,all_extraction_schemas_valid=not failures,all_official_normalization_replays_match=not failures,new_requests=dict(new),selected_requests=dict(selected),reused_28_metrics_identical=True,request_ids_unique=True,aggregate_recalculation_verified=True,failures=failures,per_paper=audit)
    v.update(new_successful_requests=successful_new,new_failed_attempts=failed_attempts,unknown_usage_attempts=failed_attempts,explicitly_authorized_bounded_reissue=bool(failed_attempts),automatic_retries=0)
    save(RUN/'verification.json',v)
    lines=['# 新旧 Baseline 配置与结果对照','','旧版包含 14 篇 Extraction 的 max_tokens=1024、历史 15 篇 Normalization 的 max_tokens=15。新版所选成功请求全部省略客户端输出上限；此前长论文 Extraction 与后续 28 篇两个阶段直接复用。实际 wire JSON 逐条核验，配置中的 null 仅是记录，未作为上限发送。','','14 篇新 Extraction 的完整请求在移除输出上限字段后与历史请求完全一致；43 篇证据缓存字节哈希一致，没有重新解析 PDF、Embedding 或检索。标准化仍使用完整 Gold 名称集合、原始 Prompt 和逐字段处理，无缓存，Result 保持原字符串。','','新旧结果差异不能直接归因于移除输出上限：模型重新调用也可能产生随机变化，seed 参数被接受不等于确定性已获保证。','','| 指标 | 旧 P | 旧 R | 旧 F1 | 新 P | 新 R | 新 F1 | F1 差值 |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for name,n in metrics['aggregate'].items():
        o=oldmetrics['aggregate'][name];lines.append(f'| {name} | {o["Precision"]:.6f} | {o["Recall"]:.6f} | {o["F1"]:.6f} | {n["Precision"]:.6f} | {n["Recall"]:.6f} | {n["F1"]:.6f} | {n["F1"]-o["F1"]:+.6f} |')
    lines+=['','以下为旧 → 新；F1 均按各篇自己的 P/R 计算。','','| 论文 | 抽取条数 | null 字段 | Result F1 | TDM F1 | TDMR F1 |','|---|---:|---:|---:|---:|---:|']
    for c in comparison:
        cells=[f'{c["old_metrics"][k]["F1"]:.6f} → {c["new_metrics"][k]["F1"]:.6f}' for k in ('Result IIM','TDM Exact Match','TDMR Exact Match')]
        lines.append(f'| {c["paper"]} | {c["old_extracted_records"]} → {c["new_extracted_records"]} | {c["old_null_fields"]} → {c["new_null_fields"]} | '+ ' | '.join(cells)+' |')
    lines+=['','## 请求量口径','',f'本轮新增 {new["requests"]} 次（Extraction {new["extract_requests"]}、Normalization {new["normalize_requests"]}），{new["prompt_tokens"]:,} 输入 + {new["completion_tokens"]:,} 输出 = {new["total_tokens"]:,} Tokens。',f'旧版历史累计 {prior["requests"]} 次 / {prior["total_tokens"]:,} Tokens；本轮后累计 {accounting["cumulative_selected"]["requests"]} 次 / {accounting["cumulative_selected"]["total_tokens"]:,} Tokens。',f'当前新版结果实际选中的请求共 {selected["requests"]} 次 / {selected["total_tokens"]:,} Tokens，其中复用 {reused["requests"]} 次。该口径不含已被替换的旧成功请求与旧截断请求，不能当作全部历史费用。','未取得服务商账单；不推算美元费用。']
    if failed_attempts:lines+=['',f'其中 {failed_attempts} 次连接失败没有 HTTP 响应，Token Usage 与是否计费未知；经用户明确授权仅补发一次相同请求，原失败日志完整保留。上述 Token 合计只统计有记录的用量，不能排除该失败尝试的额外费用。']
    (RUN/'configuration_comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    report=(RUN/'report.md').read_text(encoding='utf-8')
    intro=['# SCILEAD 43 篇统一无客户端输出上限 Baseline','',f'完成 {len(audit)}/43 篇、{metrics["scope"]["evaluated_gold_tdmrs"]}/295 条 Gold 覆盖。重新 Extraction 14 篇、重新 Normalization 15 篇；长论文 Extraction 直接复用，后续 28 篇完整复用。', '',f'本轮新增 {new["requests"]} 次 API 请求：14 次 Extraction、{new["normalize_requests"]} 次逐字段 Normalization；输入 {new["prompt_tokens"]:,}、输出 {new["completion_tokens"]:,}、合计 {new["total_tokens"]:,} Tokens。API 流水线墙钟 {accounting["execution_wall_seconds"]:.1f} 秒。', '',f'所选成功请求共 {selected["requests"]} 次，全部 HTTP 200、返回 {MODEL}、finish_reason=stop，实际 wire JSON 全部省略 max_tokens / max_completion_tokens / max_output_tokens。43 份抽取均通过 JSON 与字段类型检查；标准化按原始逐字段逻辑离线重放一致，null 原样保留。', '',f'TDMR F1：旧版 {oldmetrics["aggregate"]["TDMR Exact Match"]["F1"]:.6f} → 新版 {metrics["aggregate"]["TDMR Exact Match"]["F1"]:.6f}。不能将差异直接归因于输出上限，重新调用模型本身可能引入变化。', '',f'{len(preserved):,} 个历史文件、官方源码与 Prompt、Gold、{len(env["dependencies"])} 个依赖版本均保持不变。43 篇输入证据与历史请求一致，本轮 PDF 解析、Embedding、Chroma 检索执行次数均为 0。','',f'辅助严格数值 Result IIM：P={strict["Precision"]:.6f}、R={strict["Recall"]:.6f}、F1={strict["F1"]:.6f}。这是额外诊断，不替代官方字符串包含匹配指标。','','完整新旧逐篇比较见 [configuration_comparison.md](configuration_comparison.md)；逐条 Gold / 原始预测 / 标准化输出见 [tdmr_comparison.md](evaluation/tdmr_comparison.md)；分类见 [findings.md](inspection/findings.md)。','']
    if failed_attempts:intro+=['一次标准化连接失败未收到 HTTP 响应；经用户明确授权，仅补发一次相同请求并成功完成。原失败日志与授权记录保留，未自动重试。新增请求数包含这次失败尝试；其 Token 与费用未知，已知 Token 合计不包含未知用量。所选结果全部 finish_reason=stop，并不表示每次尝试均收到 stop。','']
    (RUN/'report.md').write_text('\n'.join(intro)+'\n'+report[report.index('## 完成覆盖率'):],encoding='utf-8')
    (RUN/'README.md').write_text('''# 统一配置 Baseline 与断点续跑

本目录是独立实验版本；旧 full43、subset5、subset15、subset15_uncapped_retry 均只读保留。manifest 的 source_* 路径索引历史数据，*_reused 指示每个阶段是否复用。长论文抽取文件复制到新目录，仅为官方标准化脚本的相对输出路径服务；复制不会产生 API 请求，哈希一致并按历史用量计一次。

执行入口（scilead Python）：`pilot/scripts/uniform43_run.py --run`。只执行明确选定的 API 阶段；绝不调用 PDF 预处理或向量检索。完整阶段跳过，已完成的单次请求仅可在同序号、同消息下重放本地响应；重复名称仍独立调用。未完成/失败 attempt 拒绝自动重试，非法或截断输出停止该篇后续阶段。不可再次使用 --prepare 覆盖实验。

离线评测：`uniform43_evaluate.py`；逐条检查：`inspect_full43.py --run-root D:\\C++\\SCILEAD\\pilot\\full43_uncapped`；核验与对照：`uniform43_finalize.py`。重新生成汇总时先执行评测，再检查、核验。最终 file_integrity_sha256.json 是汇总写入结束后的文件清单，重新汇总后应再生成。

源码、依赖、Gold、历史文件哈希与新旧输入比较均在 verification.json / preserved_existing_sha256.json / environment.json / input_preflight.json 中。实际脱敏请求和响应在每个阶段 api_calls；候选名称及顺序在 normalization/candidate_sets.json，逐条计划在 request_plan.json。

API Key 仅由已验证适配器在运行时从指定安全配置读取，不进入本目录记录。服务商账单不可用，Token Usage 不等同于实际货币账单。
''',encoding='utf-8')
    reproducibility=RUN/'reproducibility';reproducibility.mkdir(exist_ok=True)
    for name in ('uniform43_run.py','uniform43_evaluate.py','uniform43_finalize.py','uniform43_recover_once.py','scilead_api.py','inspect_full43.py'):shutil.copy2(SCRIPTS/name,reproducibility/name)
    save(reproducibility/'adapter_sha256.json',{f.name:sha(f) for f in reproducibility.glob('*.py')})
    print(json.dumps({'complete':len(audit),'new_requests':dict(new),'selected_requests':dict(selected),'aggregate':metrics['aggregate'],'preserved_files':len(preserved)},ensure_ascii=False))
if __name__=='__main__':main()
