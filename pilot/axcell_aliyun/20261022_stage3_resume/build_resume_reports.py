import csv,json,hashlib,datetime,collections
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'remote_results';G=2**30
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):(R/name).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
b=read(R/'remote_before.json');a=read(R/'final_audit.json');m=read(D/'extraction_manifest.json');q={x['paper_id']:x for x in read(R/'queue.json')}
batch=read(D/'batch_state.json');assert batch['status']!='RUNNING'
rows=m['rows'];ok=[x for x in rows if x['status'] in ['EXTRACTION_COMPLETE','VALID_EMPTY']];new=[x for x in rows if x.get('resource')];nonempty=[x for x in ok if x['record_count']>0]
counts={s:sum(x['status']==s for x in rows) for s in ['EXTRACTION_COMPLETE','VALID_EMPTY','FAILED','BLOCKED','PENDING','RUNNING']}
for x in rows:
 x.update(parsed_paper_path=q[x['paper_id']].get('parsed_paper_path'),html_path=q[x['paper_id']].get('html_path'),local_output_directory=str(D/'papers'/x['paper_id']))
 x['raw_output_path']=str(D/'papers'/x['paper_id']/'raw_outputs/records.json') if x in ok else None
 x['this_run_attempts']=int(x['paper_id'] in a['new_attempts'])
 x['prior_interrupted_attempts']=int(x['paper_id']=='1912.08777.pdf')
fields=['paper_id','tex_version','parse_status','status','reused','record_count','seconds','exit_code','this_run_attempts','prior_interrupted_attempts','error','parsed_paper_path','raw_output_path','local_output_directory']
with (R/'extraction_status.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
local=[]
for path,h in read(R/'local_frozen_before.json').items():
 p=Path(path);local.append({'path':path,'match':p.is_file() and p.stat().st_size==h['bytes'] and sha(p)==h['sha256']})
save('local_frozen_after.json',local)
reused_checks=[]
for x in rows:
 if x.get('reused'):
  prior=R.parent/'20261022_stage3/remote_results/papers'/x['paper_id']
  for name,h in x['output_hashes'].items():reused_checks.append({'paper_id':x['paper_id'],'file':name,'match':sha(prior/name)==h==sha(D/'papers'/x['paper_id']/name)})
save('reused_output_verification.json',reused_checks)
resource=[]
for x in rows:
 r=x.get('resource',{})
 resource.append({'paper_id':x['paper_id'],'status':x['status'],'reused':x.get('reused',False),'seconds':x.get('seconds'),
 'worker_maxrss_gib':x.get('worker_maxrss_bytes',0)/G if 'worker_maxrss_bytes' in x else None,
 'sampled_worker_cgroup_gib':r.get('peak_worker_cgroup',0)/G if r else None,
 'sampled_worker_tree_rss_gib':r.get('peak_worker_tree_rss',0)/G if r else None,
 'sampled_es_gib':r.get('peak_es_cgroup',0)/G if r else None,'min_host_available_gib':r.get('min_host_available',0)/G if r else None,
 'peak_swap_gib':r.get('peak_swap',0)/G if r else None,'exit_code':x.get('exit_code')})
with (R/'resource_usage.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,list(resource[0]));w.writeheader();w.writerows(resource)
wall=(datetime.datetime.fromisoformat(batch['finished_utc'])-datetime.datetime.fromisoformat(batch['started_utc'])).total_seconds()
stats={'wall_seconds':wall,'new_attempts':len(a['new_attempts']),'reused_papers':3,'historical_stage3_attempts':3,'cumulative_stage3_new_attempts':len(a['new_attempts'])+3,
 'original_single_success_generation':1,'cumulative_including_original_single':len(a['new_attempts'])+4,
 'original_single_note':'Original successful single generation only; prior initialization failure before inference is not a generation.',
 'peak_worker_maxrss_gib':max([x.get('worker_maxrss_bytes',0) for x in new] or [0])/G,
 'peak_worker_cgroup_gib':max([x['resource']['peak_worker_cgroup'] for x in new] or [0])/G,
 'peak_es_cgroup_gib':max([x['resource']['peak_es_cgroup'] for x in new] or [0])/G,
 'min_available_gib':min([x['resource']['min_host_available'] for x in new] or [0])/G,
 'end_available_gib':a['memory_available_bytes']/G,'disk_before_gib':b['disk']['free']/G,'disk_after_gib':a['disk_free_bytes']/G,
 'oom_delta':a['vmstat']['oom_kill']-b['vmstat']['oom_kill'],'pswpin_delta':a['vmstat']['pswpin']-b['vmstat']['pswpin'],'pswpout_delta':a['vmstat']['pswpout']-b['vmstat']['pswpout']}
save('resource_summary.json',stats)
m.update(rows=rows,normalization_eligible_papers=[x['paper_id'] for x in nonempty],valid_empty_papers=[x['paper_id'] for x in ok if x['record_count']==0],parsed_gold_scope=248,author36_membership='UNVERIFIED',paid_api_calls=0,normalization='NOT_STARTED',evaluation='NOT_STARTED',configuration_path=str(R/'configuration.json'))
save('extraction_manifest.json',m)
v={'gate':'P3_AWAITING_ACCEPTANCE' if len(ok)==37 else 'P3_INCOMPLETE_CHECKPOINT','stage3_complete':len(ok)==37,'runnable_papers':37,'completed_papers':len(ok),'nonempty_papers':len(nonempty),'valid_empty_papers':counts['VALID_EMPTY'],'counts_including_2_parse_failures':counts,
 'raw_record_count':sum(x['record_count'] for x in ok),'new_attempts':len(a['new_attempts']),'previous_successes_reused_without_generation':all(x['match'] for x in reused_checks),
 'local_frozen_files':len(local),'local_frozen_unchanged':all(x['match'] for x in local),'remote_frozen_files':len(a['frozen_files']),'remote_frozen_unchanged':all(x['match'] for x in a['frozen_files']),
 'parsed_files':len(a['parsed']),'parsed_all_unchanged':all(x['match'] for x in a['parsed']),'source_model_files':len(a['assets']),'source_models_all_unchanged':all(x['match'] for x in a['assets']),
 'all_success_outputs_hash_and_structure_valid':all(x['all_output_hashes_match'] and x['provenance_aligned'] and x['result_strings'] for x in a['papers'] if x['status'] in ['EXTRACTION_COMPLETE','VALID_EMPTY']),
 'tdmr_field_type_anomalies':[{'paper_id':x['paper_id'],'anomalies':x['field_anomalies']} for x in a['papers'] if x.get('field_anomalies')],
 'dependencies_unchanged':a['dependency_freeze_unchanged'],'local_download_verified':read(R/'sync_verification.json'),'remaining_running_containers':a['running_containers'],
 'oom_delta':stats['oom_delta'],'paid_api_calls':0,'normalization':'NOT_STARTED','official_evaluation':'NOT_STARTED','author36_membership':'UNVERIFIED'}
save('stage3_verification.json',v)
lines=['# AxCell 阶段3：受控恢复与批量抽取（P3）','',
 f'本次在用户批准适当放宽保护后执行。37篇可运行输入已完成 **{len(ok)}/37**；非空预测{len(nonempty)}篇，VALID_EMPTY {counts["VALID_EMPTY"]}篇，原始记录合计 **{v["raw_record_count"]}条**。这里的完成仅指流程与结构校验，不表示预测正确。',
 f'本次新增{len(a["new_attempts"])}次模型抽取尝试：重试1912.08777.pdf一次，另处理33篇此前未启动论文。1911.10390.pdf、2001.04063.pdf、1511.08308.pdf原样复用。原阶段2失败的1905.03197.pdf、2203.16804.pdf保持FAILED，不解析、不抽取。',
 'GPT请求0，未标准化、未正式评价。停在P3等待验收。作者原论文36篇子集成员仍UNVERIFIED，本轮37篇不能称为作者36篇准确范围的复现。37篇解析范围对应248条Gold，仅是覆盖范围，不是命中数。','',
 '## 保护调整与方法保持','',
 '旧保护把“约90秒内内存增长2GiB且无新管线事件”当成失去进展，可能误判长结构识别阶段。此次移除该启发式停止，保留内存曲线，新增cgroup CPU计数，最长单篇从30分钟延长至60分钟。模型14GiB提前停止/18GiB硬限制、ES2.4/3GiB、主机4GiB可用、磁盘20GiB与新增OOM停止条件不变。清理阶段监控只读procfs/cgroup，避免Docker状态查询阻塞采样，并持久化清理期异常。',
 '9项保护/归属/异常清理测试、真实小型父子进程清理测试、原资源曲线重放通过。所有更改仅在独立编排层；旧目录、旧中止记录完整保留。',
 '直接复用原单篇适配脚本的extract_results与原版ResultsExtractor；固定原AxCell源码、模型、taxonomy、abbreviations、置信度0.8/0.85及候选筛选。仍为每篇空初始Elasticsearch索引，保持已验收单篇设置；不预索引其他论文，官方查询参数不变。作者实际索引语料未核实，作为复现限制保留。','',
 '## 逐篇状态','', '| 论文ID | 状态 | 原始记录数 | 文本/表格区域 | 本次秒数 | 退出码 | 说明 |','|---|---|---:|---|---:|---|---|']
for x in rows:
 note='复用，不重复生成' if x.get('reused') else x.get('error','') or ('本次授权重试一次' if x['paper_id']=='1912.08777.pdf' else '原版抽取')
 lines.append(f'| {x["paper_id"]} | {x["status"]} | {x.get("record_count") if x.get("record_count") is not None else "—"} | {q[x["paper_id"]].get("fragment_count","—")}/{q[x["paper_id"]].get("table_count","—")} | {x.get("seconds","—")} | {x.get("exit_code") if x.get("exit_code") is not None else "—"} | {note.replace("|","/")} |')
lines+=['','## 资源与完整性','',
 f'本次批次墙钟{wall/60:.2f}分钟（不含前置配置与最终同步）。本次新增尝试{stats["new_attempts"]}；累计阶段3尝试{stats["cumulative_stage3_new_attempts"]}（含上轮1次保护中止），另有原单篇成功生成1次。未自动重试失败或因低分重跑。',
 f'模型OS maxRSS最高{stats["peak_worker_maxrss_gib"]:.3f}GiB，模型cgroup采样峰值{stats["peak_worker_cgroup_gib"]:.3f}GiB，ES采样峰值{stats["peak_es_cgroup_gib"]:.3f}GiB。不同口径/时点不可相加作总峰值。最低MemAvailable {stats["min_available_gib"]:.3f}GiB，结束{stats["end_available_gib"]:.3f}GiB。',
 f'OOM增量{stats["oom_delta"]}，swap-in/out增量{stats["pswpin_delta"]}/{stats["pswpout_delta"]}。磁盘剩余{stats["disk_before_gib"]:.3f}→{stats["disk_after_gib"]:.3f}GiB（整盘变化含后台写入）。',
 f'哈希核验：本地冻结{len(local)}文件、远端冻结{len(a["frozen_files"])}文件，643个解析产物、91个源码/模型文件；详情见stage3_verification.json。3篇复用结果逐文件与旧输出一致。依赖版本无变化。',
 '旧中止不计入成功输出。VALID_EMPTY为流程成功的空预测，与程序FAILED和未运行BLOCKED分开。两篇解析失败保留，未静默排除。原预测及raw_outputs/events全部保留，未根据Gold筛选或修改。','',
 '## 输出与后续边界','',
 'extraction_status.csv、extraction_manifest.json、resource_usage.csv、resource_summary.json、stage3_verification.json；逐篇原始输出、provenance、中间候选、stdout/stderr、资源采样在remote_results/papers/<paper_id>/。预处理输入只复用，未重新解析。错误来源核查另见error_inspection.md。',
 f'有非空原始记录的{len(nonempty)}篇可在P3验收后进入标准化请求准备；VALID_EMPTY {counts["VALID_EMPTY"]}篇保留状态与分母，不虚构请求。标准化必须另经P4授权，固定gpt-4.1-2025-04-14。本轮到此停止。',
 '远端目录：/root/scilead/axcell/runs/20261022_stage3_resume/；报告镜像在reports/。保留ECS及Docker daemon，不自动关机或新增云资源。']
(R/'extraction_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(R/'resume.md').write_text('本次独立恢复已获得用户明确授权，允许1912.08777.pdf新增一次尝试及33篇初次尝试。旧3篇成功输出原样复用。后续只可校验检查点后跳过成功；FAILED/RUNNING/资源中止不得删除状态后自动再跑。保持旧20261022_stage3与原formal目录冻结。完成停P3；未经P4不得调用GPT。\n',encoding='utf-8')
print(json.dumps({'counts':counts,'records':v['raw_record_count'],'completed':len(ok),'stats':stats,'verification':v},ensure_ascii=True))
