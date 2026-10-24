"""Offline P2 reporting from the original per-paper outputs and monitored states."""
from pathlib import Path
import csv, datetime, hashlib, json, statistics
P=Path(__file__).resolve().parent; F=P.parent; R=P/'remote_reports'; G=2**30
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
    assert not p.exists(),'Do not overwrite delivered reports'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=read(R/'parse_manifest.json');rows=manifest['papers'];batch=read(R/'batch_result.json')
queue=read(P/'queue.json');before=read(P/'remote_before.json');after=read(P/'remote_after.json')
remote_ver=read(R/'remote_output_verification.json');config=read(P/'configuration.json')
assert len(rows)==39 and [r['paper_id'] for r in rows]==[r['paper_id'] for r in queue]
assert not after['running_containers']['stdout'].strip() and not after['elasticsearch_port_open']
for d in [before,after]:
    assert d['original_assets_match'] and d['single_paper_run_unchanged'] and d['single_paper_script_and_parsed_match']
    assert not d['package_diff_from_single_paper'] and d['pip_check']['exit_code']==0
assert before['images']==after['images'] and before['owned_containers']==after['owned_containers']
assert remote_ver['status']=='PASSED' and not batch['remaining_task_containers']
for e in read(F/'protected_inputs_before.json'):assert sha(Path(e['path']))==e['sha256']
for e in read(F/'stage0_delivery_manifest.json'):assert sha(F/e['path'])==e['sha256']
for e in read(F/'stage1/stage1_delivery_manifest.json'):assert sha(F/e['path'])==e['sha256']
for e in read(P/'sync_manifest.json'):assert sha(Path(e['local']))==e['sha256']
revision2=read(P/'orchestration_revision2.json')
for name,h in revision2['scripts'].items():assert sha(P/name)==sha(R/name)==h
for name,h in config['scripts'].items():assert sha((P/'orchestration_v1'/name) if name!='parse_one.py' else P/name)==h
assert sha(P/'queue.json')==sha(R/'queue.json')==config['input_queue_sha256']
ok=[r for r in rows if r['status']=='PARSE_COMPLETE'];failed=[r for r in rows if r['status']=='FAILED']
resources=[];samples=[];errors=[];indexes=[];new_artifacts_checked=0
for row in rows:
    log=P/'parse_logs'/row['paper_id']; result=read(log/'parser_result.json') if (log/'parser_result.json').exists() else {}
    if row['status']=='PARSE_COMPLETE' and not row['reused']:
        for e in result['artifacts']:
            local=P/Path(e['path']).relative_to('/root/scilead/axcell/runs/20261022_formal/stage2')
            assert local.is_file() and local.stat().st_size==e['bytes'] and sha(local)==e['sha256'];new_artifacts_checked+=1
    if 'resource' in row:
        res=row['resource'];resources.append(res)
        for line in (log/'conversion_linux_resources.jsonl').read_text().splitlines():
            s=json.loads(line);s['paper_id']=row['paper_id'];samples.append(s)
    if row['status']=='FAILED':
        text='\n'.join(f.read_text(encoding='utf-8',errors='replace') for f in [log/'container_stderr.log',log/'process.log'] if f.exists())
        signals=[line.strip() for line in text.splitlines() if any(k in line for k in ['Fatal:','Conversion complete:','Unable to find any suitable','UnpackError','Timeout','timeout -s KILL','Error! Did not write','Traceback','Error:'])]
        category=('OFFICIAL_CONVERTER_300S_TIMEOUT' if 'timeout -s KILL 300 engrafo' in text and 'Killed' in text else
                  'LATEXML_TOO_MANY_ERRORS' if 'Fatal:too_many_errors' in text else
                  'NO_SUITABLE_TEX' if 'Unable to find any suitable tex file' in text else 'CONVERSION_OR_PARSE_ERROR')
        errors.append({'paper_id':row['paper_id'],'official_status':result.get('official_status'),'error':row.get('error'),
                       'container_exit':read(log/'container_exit.json') if (log/'container_exit.json').exists() else None,
                       'category':category,'diagnostic_log_lines':signals[-12:],'logs':str(log),'retries':0})
    local_paper=(F.parent/'20261022_single_paper/parsed_paper') if row['reused'] else P/'parsed/papers'/row['tex_version']
    indexes.append({'paper_id':row['paper_id'],'tex_version':row['tex_version'],'status':row['status'],'reused':row['reused'],
                    'remote_parsed_path':row.get('parsed_paper_path'),'remote_html_path':row.get('html_path'),
                    'local_parsed_path':str(local_paper) if row['status']=='PARSE_COMPLETE' else None,
                    'local_logs':str(log),'input_sha256':next(q['sha256'] for q in queue if q['paper_id']==row['paper_id'])})
metric={'successful_papers':len(ok),'failed_papers':len(failed),'successful_gold_count':sum(r['gold_tdmr_count'] for r in ok),
        'stage2_scope_papers':39,'stage2_scope_gold':283,'new_attempts':len(resources),'reused_papers':sum(r['reused'] for r in rows),
        'fragments':sum(r.get('fragment_count',0) for r in ok),'table_regions':sum(r.get('table_count',0) for r in ok),
        'container_sample_peak_bytes':max((c['peak_sampled_memory_bytes'] for r in resources for c in r['containers'].values()),default=0),
        'parser_max_rss_bytes':max((r['rusage_maxrss_bytes'] for r in resources),default=0),
        'host_min_available_bytes':min((s['memory']['MemAvailable'] for s in samples),default=0),
        'host_after_available_bytes':min(x['memory']['MemAvailable'] for x in after['memory_samples']),
        'mean_attempt_seconds':statistics.mean(r['seconds'] for r in resources) if resources else 0,
        'sum_attempt_seconds':sum(r['seconds'] for r in resources),'batch_seconds':batch['seconds_this_invocation']+read(P/'orchestration_v1/batch_result.json')['seconds_this_invocation'],
        'wall_elapsed_seconds':(datetime.datetime.fromisoformat(batch['utc'])-datetime.datetime.fromisoformat(read(R/'orchestration_v1/batch_owner.json')['utc'])).total_seconds(),
        'disk_free_before_bytes':before['disk_free_bytes'],'disk_free_after_bytes':after['disk_free_bytes'],
        'whole_disk_growth_bytes':before['disk_free_bytes']-after['disk_free_bytes'],
        'swap_growth_max_bytes':max((r['swap_growth_bytes'] or 0 for r in resources),default=0),
        'resource_stops':[{'paper_id':r['paper_id'],'reason':r['resource']['stop_reason']} for r in rows if r.get('resource',{}).get('stop_reason')],
        'new_artifacts_checked_locally':new_artifacts_checked,
        'task_storage':remote_ver['task_storage'],
        'oom_counter_increases':sum(max(0,b['vmstat']['oom_kill']-a['vmstat']['oom_kill']) for a,b in zip(samples,samples[1:])),
        'swapin_counter_increases':sum(max(0,b['vmstat']['pswpin']-a['vmstat']['pswpin']) for a,b in zip(samples,samples[1:])),
        'swapout_counter_increases':sum(max(0,b['vmstat']['pswpout']-a['vmstat']['pswpout']) for a,b in zip(samples,samples[1:]))}
save(P/'resource_summary.json',metric);save(P/'failure_analysis.json',errors);save(P/'parsed_output_index.json',indexes)
fields=['paper_id','status','reused','fragment_count','table_count','seconds','error','parsed_paper_path','html_path']
for name,records,keys in [('parse_status.csv',rows,fields),('parse_resource_usage.csv',[
 {'paper_id':s['paper_id'],'elapsed_seconds':s['elapsed_seconds'],'mem_available_gib':s['memory']['MemAvailable']/G,
  'disk_free_gib':s['disk_free_bytes']/G,'process_group_rss_gib':s['owned_rss_sum']/G,
  'container_usage_gib':max((c.get('memory.current',0) for c in s['containers']),default=0)/G,
  'swap_used_gib':(s['memory']['SwapTotal']-s['memory']['SwapFree'])/G,**s['vmstat']} for s in samples],
 ['paper_id','elapsed_seconds','mem_available_gib','disk_free_gib','process_group_rss_gib','container_usage_gib','swap_used_gib','oom_kill','pswpin','pswpout'])]:
    target=F/name;assert not target.exists()
    with target.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(records)
save(F/'parse_manifest.json',{'stage':2,'configuration_sha256':config['configuration_sha256'],'rows':rows,'local_indexes':indexes,'source_manifest_sha256':config['original_input_manifest_sha256'],'author36_membership':'UNVERIFIED'})
verification={'status':'P2_AWAITING_USER_CONFIRMATION','all_39_recorded':True,'counts':batch['counts'],
              'remote_verification':remote_ver,'all_checked_new_and_old_artifact_hashes_match':True,
              'historical_P0_P1_reports_unchanged':True,'dependency_changes':{},'docker_images_unchanged':True,
              'single_paper_reused_without_regeneration':True,'new_model_loads':0,'new_extractions':0,'GPT_calls':0,
              'remaining_running_containers':[],'stage3_authorized':False,'author36_membership':'UNVERIFIED'}
verification['orchestration_revision2']={'tests':'7 policy cases plus 2 Linux RED->GREEN regressions','scientific_method_unchanged':True,'failed_papers_not_retried':True,'prior_run_preserved':'stage2/orchestration_v1'}
save(F/'stage2_verification.json',verification)
save(F/'stage2_gate.json',{'stage':2,'state':'P2_AWAITING_USER_CONFIRMATION','stage3_extraction_authorized':False,'paid_api_authorized':False,'counts':batch['counts'],'author36_membership':'UNVERIFIED'})
table='\n'.join('| '+ ' | '.join([r['paper_id'],str(r['gold_tdmr_count']),r['status']+('（复用）' if r['reused'] else ''),str(r.get('fragment_count','—')),str(r.get('table_count','—')),f"{r.get('seconds',0) or 0:.1f}",r.get('error','') or '—'])+' |' for r in rows)
error_text='\n'.join(f"- **{e['paper_id']}**：`{e['error']}` / `{e['category']}`，容器退出信息 `{e['container_exit']}`。原始日志：`stage2/parse_logs/{e['paper_id']}/`。末尾诊断："+' / '.join(e['diagnostic_log_lines'][-3:]) for e in errors) or '无失败。'
report=f'''# P2：AxCell 批量 TeX 转换与解析

已按冻结的 39 篇可用输入清单执行阶段 2，当前停在 **P2，未授权阶段 3**。成功 {len(ok)}/39，失败 {len(failed)}/39；其余状态见表。成功产物覆盖 {metric['successful_gold_count']}/283 条本范围 Gold，仅表示论文覆盖，不是抽取命中。原数据集另有 4 篇无 TeX（12 Gold），未新增输入或混入队列。

相对于完整 SciLead，当前解析成功覆盖 {len(ok)}/43 篇、{metric['successful_gold_count']}/295 条 Gold。两篇失败合计 35 条 Gold，不能在后续比较中忽略其覆盖差异。

实际新增转换尝试 {len(resources)} 次，已有单篇 `1511.08308.pdf` / TeX v5 原样复用，不重新转换或抽取。没有自动重试、没有 Elasticsearch、没有模型加载或 ResultsExtractor、GPT 请求 0。没有因输出质量筛选论文。

## 固定配置与范围

AxCell commit `f4648d8fee1aa8482d007a38828da9dc06630f0e`；原版 `PaperExtractor(data_root)(source)` → `PaperText.from_html` → 原版表格提取与保存。Engrafo 镜像 `arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6`，digest `sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e`。沿用已验证 Docker SDK `version=auto` 适配和稳定 containers 集合上的运行保护；源码/TeX/模型不改。

串行，一次一篇；转换容器 20 GiB、6 CPU、网络关闭、官方 remove=True。启动门槛可用 RAM ≥6 GiB、磁盘余量 ≥20 GiB；持续低内存/容器接近上限/OOM 保护沿用 P0/P1；每篇最长 600 秒，失败保留状态。4 项本地及远端保护/断点测试通过；实际超时清理测试仅运行无模型测试进程，其所属子进程全部退出。

**作者 36 篇子集的确切成员仍 UNVERIFIED，确认属于作者范围的数量仍无法给出；39 篇不能称为作者 36 篇复现。** 输入及 Gold 数量仅用于范围记录，不参与解析。

## 逐篇结果

| 论文 ID | Gold 数 | 状态 | 文本片段 | table/tabular 区域 | 耗时秒（见口径） | 错误 |
|---|---:|---|---:|---:|---:|---|
{table}

区域数是原解析器的 table/tabular 产物数量，不等于结果表数量或正确表格数；包含图形/统计表等时保持原样，未人工删改。合计 {metric['fragments']} 个片段、{metric['table_regions']} 个区域。这里没有给出抽取记录数或准确率，因为尚未运行阶段 3。

## 失败诊断与保留策略

{error_text}

完整日志优先于以上摘要。仅归类原失败，不升级镜像、不补装 TeX 样式、不改宏、不更换输入版本，不为了通过而重跑。失败论文不会默默剔除；正式后续评价范围需在后续验收中说明。

独立审查发现调度保护边界问题后，曾暂停控制器，让当前转换自然结束并保存检查点。只修复 owner 写失败时的 finally 清理、先停止生产进程后清理容器、清理失败优先停止后续队列、恢复未尝试的 BLOCKED 与已完成子进程对应的 RUNNING 状态。7 项策略测试及两项 Linux 实际进程清理 RED→GREEN 回归通过。v1 脚本/检查点保留，revision2 单独记录；原 `parse_one.py`、TeX、镜像、解析方法均未改变。恢复时跳过所有已成功或已失败的论文，没有重新生成挑选结果。

## 资源与完整性

- 从首次批次启动到最终结束的墙钟时间 {metric['wall_elapsed_seconds']:.1f} 秒（含检查点暂停/工程处理）；两次控制器调用计时合计 {metric['batch_seconds']:.1f} 秒；{len(resources)} 次新增尝试的监控包络总计 {metric['sum_attempt_seconds']:.1f} 秒，平均 {metric['mean_attempt_seconds']:.1f} 秒（含失败）。逐篇表中成功项使用原入口内部秒数，失败项使用监控包络秒数；复用项为 0，表示本轮未再次转换。
- 转换容器 cgroup 采样峰值 {metric['container_sample_peak_bytes']/G:.3f} GiB；Python/监控子进程 OS maxRSS 最大 {metric['parser_max_rss_bytes']/G:.3f} GiB；不把二者相加当作同步精确总峰值。
- 最低 MemAvailable {metric['host_min_available_bytes']/G:.3f} GiB；结束复测 {metric['host_after_available_bytes']/G:.3f} GiB。
- OOM 计数增长 {metric['oom_counter_increases']}，swap-in/out 增长 {metric['swapin_counter_increases']}/{metric['swapout_counter_increases']}；最大采样 swap 增长 {metric['swap_growth_max_bytes']/G:.3f} GiB。
- 磁盘剩余由 {before['disk_free_bytes']/G:.3f} GiB 到 {after['disk_free_bytes']/G:.3f} GiB；全盘净占用增加 {metric['whole_disk_growth_bytes']/G:.3f} GiB（含后台写入，非精确独占任务占用）。
- 分项实际分配磁盘：TeX归档 {remote_ver['task_storage']['parsed/sources']['allocated_bytes']/2**20:.2f} MiB，解包输入 {remote_ver['task_storage']['parsed/unpacked_sources']['allocated_bytes']/2**20:.2f} MiB，HTML {remote_ver['task_storage']['parsed/htmls']['allocated_bytes']/2**20:.2f} MiB，文本/表格 {remote_ver['task_storage']['parsed/papers']['allocated_bytes']/2**20:.2f} MiB，逐篇日志 {remote_ver['task_storage']['parse_logs']['allocated_bytes']/2**20:.2f} MiB。字节明细见 `stage2/resource_summary.json`，没有删除失败产物腾空间。
- 远端独立核验 {remote_ver['parsed_artifact_files_checked']} 个解析产物哈希；本地新同步产物 {new_artifacts_checked} 个匹配。39 篇输入、原源码/模型/单篇产物、P0/P1 报告及保护文件均经核验未改；依赖无变化，pip check 通过。
- 任务容器全部退出；不关闭既有 Docker daemon/服务器，不新增云实例/存储，不产生 GPT 费用。ECS 自身正常计费不因本报告而停止。

## 产物与断点

`parse_manifest.json`、`parse_status.csv`、`parse_resource_usage.csv`、`stage2_verification.json`、`stage2_gate.json`；详细索引 `stage2/parsed_output_index.json`，新解析产物 `stage2/parsed/papers/`、`stage2/parsed/htmls/`，逐篇日志 `stage2/parse_logs/`。复用单篇索引指向原只读产物，不伪造新运行。

远端 `/root/scilead/axcell/runs/20261022_formal/stage2/` 保留解包输入、中间产物、日志和状态。成功阶段只有输入/配置/全部产物哈希一致才可跳过；FAILED、RUNNING 或已有 attempt 不自动再次生成。进程独占锁避免双启动。不要直接删除 attempt 或状态以强行重跑。

本轮到此停止。下一步仅在 P2 明确确认后，基于验收通过的解析产物进入原版 AxCell 抽取，并停在 P3；不能自动调用 GPT。失败项的处理边界需要保留在批准范围中。
'''
target=F/'parse_summary.md';assert not target.exists();target.write_text(report,encoding='utf-8')
print(json.dumps(metric,ensure_ascii=False))
