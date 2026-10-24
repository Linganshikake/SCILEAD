"""Offline audit/report only; no inference, normalization or evaluation."""
import json,pathlib,hashlib,csv,datetime,collections,shutil
R=pathlib.Path(__file__).resolve().parent;D=R/'remote_results';G=2**30
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(name,d):(R/name).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=read(R/'remote_before.json');audit=read(R/'final_audit.json');manifest=read(D/'extraction_manifest.json');queue=read(R/'queue.json')
rows=manifest['rows'];qmap={x['paper_id']:x for x in queue};new=[x for x in rows if not x.get('reused') and qmap[x['paper_id']]['status']=='PARSE_COMPLETE']
success=[x for x in rows if x['status'] in ['EXTRACTION_COMPLETE','VALID_EMPTY']];nonempty=[x for x in success if x['record_count']>0]
counts=dict(collections.Counter(x['status'] for x in rows));records=sum(x['record_count'] for x in success)
localold=read(R/'local_frozen_before.json');localchecks=[]
for path,d in localold.items():
 p=pathlib.Path(path);localchecks.append({'path':path,'match':p.is_file() and p.stat().st_size==d['bytes'] and sha(p)==d['sha256']})
save('local_frozen_after.json',localchecks)
resource=[]
for x in rows:
 m=x.get('resource',{})
 resource.append({'paper_id':x['paper_id'],'status':x['status'],'reused':x.get('reused',False),'seconds':x.get('seconds'),
 'worker_maxrss_gib':x.get('worker_maxrss_bytes',0)/G if 'worker_maxrss_bytes' in x else None,
 'sampled_worker_cgroup_gib':m.get('peak_worker_cgroup',0)/G if m else None,'sampled_process_tree_rss_gib':m.get('peak_worker_tree_rss',0)/G if m else None,
 'sampled_es_cgroup_gib':m.get('peak_es_cgroup',0)/G if m else None,'min_host_available_gib':m.get('min_host_available',0)/G if m else None,
 'peak_swap_gib':m.get('peak_swap',0)/G if m else None,'exit_code':x.get('exit_code')})
with (R/'resource_usage.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(resource[0]));w.writeheader();w.writerows(resource)
for x in rows:
 q=qmap[x['paper_id']];x['parsed_paper_path']=q.get('parsed_paper_path');x['html_path']=q.get('html_path')
 x['local_output_directory']=str(D/'papers'/x['paper_id'])
 x['raw_output_path']=str(D/'papers'/x['paper_id']/'raw_outputs/records.json') if x['status'] in ['EXTRACTION_COMPLETE','VALID_EMPTY'] else None
 if x.get('resource_stop'):x['exit_status_note']='Controller requested systemctl stop; raw worker exit code unavailable after transient unit removal. Not an observed zero exit.'
with (R/'extraction_status.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['paper_id','tex_version','parse_status','status','reused','record_count','seconds','exit_code','error','parsed_paper_path','raw_output_path','local_output_directory']
 w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
manifest['local_paper_output_root']=str(D/'papers');manifest['normalization_eligible_papers']=[x['paper_id'] for x in success]
manifest['nonempty_pending_normalization']=[x['paper_id'] for x in nonempty];manifest['extraction_scientific_correctness']='NOT guaranteed by structural validation; raw errors retained'
save('extraction_manifest.json',manifest)
batch=read(D/'batch_state.json');elapsed=(datetime.datetime.fromisoformat(batch['finished_utc'])-datetime.datetime.fromisoformat(batch['started_utc'])).total_seconds()
stats={'wall_seconds':elapsed,'new_attempt_count':len(audit['new_attempts']),'new_record_count':sum(x.get('record_count') or 0 for x in new),
 'peak_worker_maxrss_gib':max([x.get('worker_maxrss_bytes',0) for x in new] or [0])/G,
 'sampled_worker_cgroup_peak_gib':max([x.get('resource',{}).get('peak_worker_cgroup',0) for x in new] or [0])/G,
 'sampled_es_cgroup_peak_gib':max([x.get('resource',{}).get('peak_es_cgroup',0) for x in new] or [0])/G,
 'minimum_available_gib':min([x['resource']['min_host_available'] for x in new if x.get('resource')] or [0])/G,
 'end_available_gib':audit['memory_available_bytes']/G,'disk_before_gib':before['disk']['free']/G,'disk_after_gib':audit['disk_free_bytes']/G,
 'oom_delta':audit['vmstat']['oom_kill']-before['vmstat']['oom_kill'],
 'swapin_delta':audit['vmstat']['pswpin']-before['vmstat']['pswpin'],'swapout_delta':audit['vmstat']['pswpout']-before['vmstat']['pswpout']}
save('resource_summary.json',stats)
verification={'gate':'P3_CHECKPOINT_INCOMPLETE_AWAITING_USER_REVIEW' if len(success)<37 else 'P3_AWAITING_USER_ACCEPTANCE','stage3_complete':len(success)==37,'counts_39':counts,'runnable_count':37,'successful_pipeline_count':len(success),'nonempty_count':len(nonempty),'total_raw_records':records,
 'new_attempts':len(audit['new_attempts']),'reused':['1511.08308.pdf'],'excluded_parse_failures':['1905.03197.pdf','2203.16804.pdf'],
 'all_remote_frozen_files_unchanged':all(x['match'] for x in audit['frozen_files']),'remote_frozen_files_checked':len(audit['frozen_files']),
 'all_local_frozen_files_unchanged':all(x['match'] for x in localchecks),'local_frozen_files_checked':len(localchecks),
 'all_643_parse_artifacts_unchanged':len(audit['parsed'])==643 and all(x['match'] for x in audit['parsed']),
 'all_91_source_and_model_files_unchanged':len(audit['assets'])==91 and all(x['match'] for x in audit['assets']),
 'all_successful_outputs_verified':all(x['all_output_hashes_match'] and x['provenance_aligned'] and x['result_strings'] for x in audit['papers'] if x['status'] in ['EXTRACTION_COMPLETE','VALID_EMPTY']),
 'dependencies_unchanged':audit['dependency_freeze_unchanged'],'local_download_hashes':read(R/'sync_verification.json'),
 'remaining_running_containers':audit['running_containers'],'oom_delta':stats['oom_delta'],'paid_api_calls':0,'normalization':'NOT_STARTED','official_evaluation':'NOT_STARTED','author36_membership':'UNVERIFIED'}
save('stage3_verification.json',verification)
lines=['# AxCell 阶段3：批量 Extraction（P3阶段性检查点）','',
 '**本轮未完成37篇批量任务。** 1912.08777.pdf触发编排保护后，按用户要求停止整批，33篇未启动。原因详见 resource_stop_analysis.md；不能将该保护中止称为已证实的内存耗尽或AxCell算法错误。','',
 f'37 篇可运行输入中，流程完成 {len(success)} 篇；非空预测 {len(nonempty)} 篇，VALID_EMPTY {counts.get("VALID_EMPTY",0)} 篇。原始记录共 **{records} 条**，其中新增 {stats["new_record_count"]} 条、复用单篇 2 条。这里的“完成/记录有效”仅表示程序及结构检查通过，不表示预测正确。','',
 f'新增模型抽取尝试 {len(audit["new_attempts"])} 次，串行运行；1511.08308.pdf 完整复用，未再次生成。1905.03197.pdf、2203.16804.pdf 保持阶段2 FAILED，未重试解析或抽取。GPT 请求 **0**，未标准化、未正式评价。','',
 '**作者原论文36篇子集成员仍未完全核实（UNVERIFIED）**。本轮不能称为作者36篇范围复现。37篇解析范围覆盖248条Gold，仅表示范围，不是抽取命中。另两篇解析失败与4篇无TeX仍是全量覆盖限制。','',
 '## 逐篇状态','', '| 论文ID | 状态 | 原始记录 | 文本/表格区域 | 本轮耗时秒 | 最大RSS GiB | 说明 |','|---|---|---:|---|---:|---:|---|']
for x in rows:
 q=qmap[x['paper_id']];note='复用历史成功结果，零新增生成' if x.get('reused') else x.get('error','') or '原版抽取'
 rss=f'{x["worker_maxrss_bytes"]/G:.3f}' if 'worker_maxrss_bytes' in x else '—'
 lines.append(f'| {x["paper_id"]} | {x["status"]} | {x.get("record_count") if x.get("record_count") is not None else "—"} | {q.get("fragment_count","—")}/{q.get("table_count","—")} | {x.get("seconds","—")} | {rss} | {note.replace(chr(10)," ").replace("|","/")} |')
lines+=['','## 方法与资源','',
 '固定 AxCell commit f4648d8fee1aa8482d007a38828da9dc06630f0e。直接导入已验收单篇 run_single.py 并校验SHA256，调用相同 ResultsExtractor；仅绑定论文ID、冻结解析产物副本和独立输出目录。继续使用相同模型、taxonomy、abbreviations、结构/置信度/最佳结果过滤器（0.8、0.85），只保留已验证的空进度条显示兼容层。没有重新解析、训练、修正或根据Gold筛选。','',
 '每篇使用独立空初始 Elasticsearch 6.7.1 索引，与单篇验证相同；原 paper_limit=30、corpus_limit=10 查询参数不变，索引只由该论文的官方流程写入。作者完整ES索引语料尚未核实，不能声称这一语料条件已完全复现。ES和模型串行启动/停止，不并发预加载。','',
 f'本轮墙钟 {elapsed/60:.2f} 分钟；已正常退出的新抽取进程OS最大RSS {stats["peak_worker_maxrss_gib"]:.3f} GiB（被保护中止的进程没有最终rusage记录，另见采样值）；进程组cgroup采样峰值 {stats["sampled_worker_cgroup_peak_gib"]:.3f} GiB；ES cgroup采样峰值 {stats["sampled_es_cgroup_peak_gib"]:.3f} GiB。口径不同且不一定同时出现，不相加当作精确总峰值。最低主机可用RAM {stats["minimum_available_gib"]:.3f} GiB，结束 {stats["end_available_gib"]:.3f} GiB。',
 f'内核OOM增量 {stats["oom_delta"]}（运行前历史计数为1），swap-in/out增量 {stats["swapin_delta"]}/{stats["swapout_delta"]}。磁盘可用 {stats["disk_before_gib"]:.3f} → {stats["disk_after_gib"]:.3f} GiB（全盘变化含后台写入）。','',
 '启动保护≥6GiB可用RAM、≥20GiB磁盘；运行低于4GiB可用RAM即停；模型cgroup达到14GiB、ES达到2.4GiB提前停止（硬限制18/3GiB）；持续增长且无进展、OOM和1800秒墙钟保护均停批。独立任务服务2秒退出宽限，监控清理过程。没有修改系统全局内存/swap或安装依赖。','',
 '## 错误保留与后续边界','',
 '1511.08308.pdf 的两条原始错误完整保留：Table 6 的Recall 91.85被绑定为F1；Table 11测试集实体数量4696被当成F1分数。原值、来源cell_ext_id和中间候选保存在raw_outputs，未用于人工修正规则。其他结果须结合来源表格审查，不把高数值或零预测直接等同程序错误。','',
 '原模型序列化对象加载时出现的SourceChangeWarning与空生成器警告原样保留，未因此替换依赖或修补模型。具体异常以逐篇worker.stderr.log、controller_error.log及state.json为准。','',
 '成功非空论文可在P3验收后进入标准化请求准备；VALID_EMPTY属于成功空预测，应保留分母和状态，不需要为其虚构标准化请求。失败/阻塞论文不能冒充已完成结果。标准化须遵循后续P4付费授权；模型将固定gpt-4.1-2025-04-14。','',
 '## 完整性与产物','',f'本地历史文件检查 {len(localchecks)} 个，远端冻结文件检查 {len(audit["frozen_files"])} 个；详见stage3_verification.json。所有解析产物、源码、模型和依赖均单独核验。原正式阶段2报告未更新、两篇失败记录未改写。',
 '本目录包含extraction_status.csv、extraction_manifest.json、resource_usage.csv、resource_summary.json、stage3_verification.json。remote_results/papers/<paper_id>/保存输入副本、原始记录/表格来源/全部候选与筛选轨迹、运行日志和资源检查点。服务索引数据仅保留远端，不复制模型。',
 '远端：/root/scilead/axcell/runs/20261022_stage3/。所有本任务容器已停止（以verification实际清单为准），Docker daemon与ECS保留。没有自动关机或新增云资源。','',
 '**本轮在P3阶段性检查点停止，待用户复核保护规则与后续恢复范围；尚未达到37篇全部完成的P3验收条件，不启动GPT标准化或正式评价。**']
(R/'extraction_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(R/'resume.md').write_text('成功检查点必须核验output_hashes后跳过。FAILED/VALID_EMPTY不得为改善质量重跑；RUNNING或资源停止检查点需人工核查。控制器持有fcntl锁；随机任务ID和归属标记保护停止范围。当前阶段结束，未经新的明确授权不要重启批次。阶段2和单篇历史结果只读。\n',encoding='utf-8')
print(json.dumps({'counts':counts,'completed':len(success),'nonempty':len(nonempty),'records':records,'stats':stats,'integrity':verification},ensure_ascii=True))
