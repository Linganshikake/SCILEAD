"""Build the stage1 evidence report and gate from actual saved measurements."""
from pathlib import Path
import csv, datetime, hashlib, json
P=Path(__file__).resolve().parent; FORMAL=P.parent; R=P/'remote_reports'; G=2**30
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,obj):
    assert not p.exists(), 'Do not overwrite a delivered report'
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=read(P/'remote_before.json'); after=read(P/'remote_after.json')
runtime=read(R/'runtime_result.json'); saved=read(R/'saved_artifact_verification.json')
samples=[json.loads(l) for l in (R/'resource_samples.jsonl').read_text().splitlines()]
manifest=read(FORMAL/'experiment_manifest.json'); local=read(P/'local_integrity_checks.json')
container=read(R/'container_after_stop.json'); health=read(R/'elasticsearch_health.json')
assert runtime['status']==saved['status']=='PASSED'
assert runtime['container_stopped'] and not runtime['remaining_running_containers']
assert all(p['exit_code']==0 for p in runtime['phases'])
assert saved['parsed_content_equal'] and saved['csv_pickle_json_equal'] and saved['scilead_wrapper_and_id_equal']
assert saved['model_generations']==saved['paid_api_calls']==runtime['model_generations']==runtime['paid_api_calls']==0
assert not container['State']['Running'] and not container['State']['OOMKilled'] and container['State']['ExitCode']==143
assert container['HostConfig']['Memory']==container['HostConfig']['MemorySwap']==3*G
assert container['HostConfig']['NanoCpus']==2*10**9
assert container['HostConfig']['PortBindings']['9200/tcp']==[{'HostIp':'127.0.0.1','HostPort':'9200'}]
assert container['Mounts'][0]['Source']=='/root/scilead/axcell/runs/20261022_formal/stage1/elasticsearch_data'
assert health['health']['status']=='green' and health['indices']==[]
for audit in (before,after):
    assert audit['original_assets_match'] and audit['single_paper_script_and_parsed_match'] and audit['single_paper_run_unchanged']
    assert not audit['package_diff_from_single_paper'] and audit['pip_check']['exit_code']==0
assert before['images']==after['images']
assert before['owned_containers']==after['owned_containers'], 'Original stopped container metadata changed'
assert not after['elasticsearch_port_open'] and not after['running_containers']['stdout'].strip()
assert 'axcell-formal-p1' not in after['task_tmux'].get('stdout','')
for e in read(P/'remote_transfer_manifest.json'):assert sha(R/e['path'])==e['sha256']
for e in read(FORMAL/'protected_inputs_before.json'):assert sha(Path(e['path']))==e['sha256']
for e in read(FORMAL/'stage0_delivery_manifest.json'):assert sha(FORMAL/e['path'])==e['sha256']
for e in read(FORMAL/'comparison_input_index.json'):assert sha(Path(e['path']))==e['sha256']
for name in ('runtime_probe.py','verify_saved_artifacts.py','authorization_and_limits.json'):assert sha(P/name)==sha(R/name)
vm_delta={k:samples[-1]['vmstat'][k]-samples[0]['vmstat'][k] for k in samples[0]['vmstat']}
assert all(v==0 for v in vm_delta.values())
assert all(s['swap_used_bytes']==0 for s in samples)
measurements={'runtime_seconds':runtime['elapsed_seconds'],
    'artifact_read_seconds':saved['elapsed_seconds'],'artifact_reader_max_rss_bytes':saved['child_max_rss_bytes'],
    'es_sampled_cgroup_peak_bytes':max(s['container'].get('memory.current',0) for s in samples),
    'es_sampled_process_tree_peak_rss_bytes':max(s['container'].get('process_tree_rss_bytes',0) for s in samples),
    'es_kernel_memory_peak_available':any('memory.peak' in s['container'] for s in samples),
    'host_min_available_bytes':min(s['mem_available_bytes'] for s in samples),
    'host_after_available_bytes':min(s['memory']['MemAvailable'] for s in after['memory_samples']),
    'disk_free_before_bytes':before['disk_free_bytes'],'disk_free_after_bytes':after['disk_free_bytes'],
    'isolated_es_data_apparent_bytes':runtime['es_data_du_bytes'],
    'system_wide_vmstat_deltas':vm_delta,'no_swap_configured_or_used':True,
    'phases':runtime['phases'],'sample_count':len(samples)}
csvpath=FORMAL/'single_paper_resource_usage.csv';assert not csvpath.exists()
fields=['utc','elapsed_seconds','phase','host_mem_available_gib','host_committed_as_gib','host_swap_used_gib','disk_free_gib',
        'controller_tree_rss_gib','child_tree_rss_gib','es_tree_rss_gib','es_cgroup_current_gib','es_cgroup_limit_gib',
        'es_kernel_peak_gib','es_swap_gib','pswpin','pswpout','oom_kill','pgmajfault']
with csvpath.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for s in samples:
        c=s['container'];row={k:s[k] for k in ['utc','elapsed_seconds','phase']}
        for dest,src in [('host_mem_available_gib','mem_available_bytes'),('host_committed_as_gib','committed_as_bytes'),
                         ('host_swap_used_gib','swap_used_bytes'),('disk_free_gib','disk_free_bytes'),
                         ('controller_tree_rss_gib','controller_tree_rss_bytes'),('child_tree_rss_gib','child_tree_rss_bytes')]:row[dest]=s[src]/G
        for dest,src in [('es_tree_rss_gib','process_tree_rss_bytes'),('es_cgroup_current_gib','memory.current'),
                         ('es_cgroup_limit_gib','limit_bytes'),('es_kernel_peak_gib','memory.peak'),('es_swap_gib','memory.swap.current')]:row[dest]=c[src]/G if src in c else ''
        row.update(s['vmstat']);w.writerow(row)
verification={'status':'P1_REGRESSION_PASSED_AWAITING_CONFIRMATION','stage':1,'utc_completed':runtime['utc_completed'],
    'paper_id':'1511.08308.pdf','source_version':'1511.08308v5','source_selection':'Reuse previously selected availability-based single paper; no new selection',
    'original_result_sha256':manifest['single_paper_reuse']['result_sha256'],
    'saved_artifact_validation':saved,'measurements':measurements,
    'protection':{'remote_source_input_model_assets_checked':len(after['original_assets']),
                  'remote_script_and_parsed_artifacts_checked':len(after['single_paper_script_and_parsed_checks']),
                  'remote_prior_run_reports_checked':len(after['single_paper_run_checks']),
                  'local_protected_files_checked':local['protected_file_count'],'p0_delivery_files_checked':local['p0_delivery_count'],
                  'all_checked_files_unchanged':True,'original_es_container_state_unchanged':True,
                  'original_es_index_not_mounted_or_started':True,'full_historical_weight_rehash_claimed':False},
    'configuration':{'axcell_commit':manifest['axcell_commit'],'scilead_commit':manifest['scilead_commit'],
                     'docker_images_unchanged':True,'dependency_diff':{},'pip_check':'No broken requirements found.',
                     'filters':manifest['method']['filters'],'model_taxonomy_abbreviation_hashes_match':True,
                     'source_and_input_files_unchanged':True,'original_progress_display_adapter_unchanged':True},
    'service':{'version':'6.7.1','health':'green','started_new_isolated_container':True,'container_name':container['Name'],
               'normal_stop':True,'docker_stop_exit_code':0,'container_exit_code':143,'oom':False,
               'old_data_reused':False,'old_data_not_touched_by_probe':True,'no_running_containers_after':True},
    'new_conversions':0,'new_extractions':0,'new_model_weight_loads':0,'paid_api_calls':0,
    'new_cloud_resources':0,'system_configuration_changes':False,
    'author_36_membership':'UNVERIFIED','batch_parse_started':False,'batch_extraction_started':False,
    'next_gate':'P1: user confirmation required before stage2'}
write(FORMAL/'single_paper_verification.json',verification)
gate={'state':'P1_AWAITING_USER_CONFIRMATION','stage1_status':'COMPLETE','stage1_authorization':'可以进入下一阶段',
      'previous_gate':'P0','stage2_batch_parse_authorized':False,'stage3_extraction_authorized':False,
      'paid_api_authorized':False,'author36_membership':'UNVERIFIED',
      'scope_for_next_stage':'39 available-input papers/283 Gold proposed; 1511.08308.pdf parsed artifacts reused, other38 pending; not verified author36',
      'P0_records':'Immutable stage0 snapshots; this stage1_gate.json is the current gate state'}
write(FORMAL/'stage1_gate.json',gate)
phase={p['phase']:p for p in runtime['phases']}
report=f'''# P1：AxCell 单篇回归验收

阶段 1 已通过，停在 **P1，等待确认后才进入阶段 2**。执行主机为阿里云 ECS；本轮只复用 `1511.08308.pdf` / `1511.08308v5`，没有新转换、模型权重加载、预测生成或 GPT 调用。

## 回归结果

从未经修改的既有 `scripts/run_single.py` 导入 `collection()`，实际调用原版 `PaperCollection.from_files(jobs=1)` 读取文件。读回的标题、154 个文本片段、11 个 table/tabular 区域及全部表格单元格，与原 `parsed_artifacts.json` 一致。此处没有重新解析 HTML/TeX。11 个区域仍包含原解析器输出的 Figure 4，不人工删除。

JSON、CSV、PKL 的两条记录一致；SCILEAD 包装中的论文 ID、字段映射和 Result 字符串一致，`source_documents=[]` 保持原样，AxCell 的来源另存 provenance。374 条既有 pipeline 事件可读，最终过滤的两个单元格 ID 与返回记录对应。读取检查进程临时禁止网络连接与 `torch.load`，只读产物不依赖模型加载或外部调用。

| 记录 | 原始 Task / Dataset / Metric / Result | 原始来源 | 离线核查结论 |
|---|---|---|---|
| 1 | Named Entity Recognition / CoNLL 2003 (English) / F1 / 91.85 | `table_06.csv/6.2` | 对应表头是 Recall；指标绑定错误仍保留 |
| 2 | Named Entity Recognition / Ontonotes v5 (English) / F1 / 4696.0 | `table_11.csv/2.4` | 原文为 Test set size (# entities)，属于 NW 列实体数；统计量误抽仍保留 |

这些核查只读取原表及既有输出，不用 Gold 修正或重新生成结果。流程与文件一致性通过不代表两条预测正确。

## 固定配置与完整性

- AxCell commit：`{manifest['axcell_commit']}`；SCILEAD commit：`{manifest['scilead_commit']}`。
- TeX v5 SHA256：`e0483008622131070662aafc040258a8fe97f50d7039cea85c6f690473625aea`。
- 原始 records.json SHA256：`{manifest['single_paper_reuse']['result_sha256']}`。
- Engrafo、Elasticsearch 的固定镜像 ID/digest 不变；7 个模型、taxonomy、abbreviations、tokenizer 文件 SHA256 不变。
- 依赖无差异，`pip check` 通过。Python 3.7.1、PyTorch 1.3.1+cpu、fastai 1.0.55 保持不变。
- 原阈值保留：表类型 0.5；结构筛选 → 置信度 0.8 → paper 范围 BestResult → 置信度 0.85；CPU、`use_crf=False`、OMP/MKL 6 线程。原显示兼容适配不变。
- 前后复核远端 91 个源码/输入/模型/启动资产、46 个脚本/解析文件、192 个历史报告文件；本地 353 个保护文件及 28 个 P0 交付文件，全部匹配。既有 GPT/Llama 比较输入索引哈希亦匹配。没有宣称重新哈希全部历史实验资源。

## 本轮资源测量

启动保护为可用 RAM ≥6 GiB、磁盘保留 ≥20 GiB；连续 15 秒可用 RAM <2 GiB 或容器使用率 ≥95%、OOM、超时均停止本任务。使用 tmux、独占锁和单次 attempt 标记；失败不会自动重跑。

| 检查阶段 | 结果 | 内存 | 耗时 | 产物/状态 |
|---|---|---|---|---|
| 既有产物读回与结构回归 | 通过，exit=0 | 子进程 OS maxRSS {saved['child_max_rss_bytes']/G:.3f} GiB | 子进程 {saved['elapsed_seconds']:.3f} 秒；监控包络 {phase['saved_artifact_read']['seconds']:.3f} 秒 | 154 片段、11 区域、2 条原始记录一致 |
| ES 6.7.1 服务启动 | 通过，exit=0 | 生命周期 cgroup 采样峰值 {measurements['es_sampled_cgroup_peak_bytes']/G:.3f} GiB / 3 GiB 限额 | {phase['service_startup']['seconds']:.3f} 秒 | 仅监听 127.0.0.1:9200 |
| ES 健康与空闲观察 | green，空索引 | JVM heap 1 GiB；2 CPU | {phase['service_ready']['seconds']:.3f} 秒 | 独立 P1 数据目录，没有索引论文 |
| 正常停止 | Docker stop exit=0 | 容器已停止 | {phase['service_shutdown']['seconds']:.3f} 秒 | 容器 exit=143（SIGTERM），OOMKilled=false |

ES 容器进程树 RSS 采样峰值为 {measurements['es_sampled_process_tree_peak_rss_bytes']/G:.3f} GiB，与 cgroup 使用量口径不同，不相加。内核未暴露 `memory.peak`，报告的是采样峰值；读取子进程不足一秒，使用其 OS maxRSS，不能拿较低的周期采样值代替。

运行总计 {runtime['elapsed_seconds']:.3f} 秒，15 个资源采样点；主机最低 MemAvailable {measurements['host_min_available_bytes']/G:.3f} GiB。阶段结束再次复测可用 RAM {measurements['host_after_available_bytes']/G:.3f} GiB，磁盘剩余 {after['disk_free_bytes']/G:.3f} GiB。OOM、swap-in/out、major page fault 计数增长均为 0；服务器无 swap。

本轮独立 ES 数据目录表观大小 {runtime['es_data_du_bytes']:,} 字节；前后全盘可用空间变化 {(before['disk_free_bytes']-after['disk_free_bytes'])/2**20:.3f} MiB，这个系统级差值包含日志等背景写入，不作为精确任务占用。没有安装依赖、下载镜像、扩容或修改系统配置；使用的是既有付费 ECS，本轮新增 GPT 请求为 0。

为保护历史索引，新建 `axcell-formal-p1-es`，只挂载 `.../20261022_formal/stage1/elasticsearch_data`；原 `elasticsearch-single` 未挂载、原容器未启动且元数据不变。新容器、日志和隔离数据保留供复核；所有容器已停止，9200 端口关闭，任务 tmux 已结束，Docker daemon 保持此前状态。

## 证据边界与下一阶段

本轮证明已有产物可复用、固定环境可读取结果以及服务可正常启动停止，**没有重新测量模型推理峰值或批量稳定性**。历史唯一成功推理耗时 65.271 秒、模型子进程 maxRSS 4.813 GiB 是上一轮记录；本轮没有把它计为新运行。此前初始化的 fastprogress 空进度条错误日志仍保留，显示兼容方案未变。

原作者 36 篇的确切成员与 TeX 版本仍未核实。39 篇可用 TeX 对应 283 条 Gold，不能称为作者 36 篇范围。前次确认只授权本阶段，正式评价口径仍须明确；不根据当前两个错误选择或排除论文。

若确认进入阶段 2，将沿用冻结清单，复用本篇转换产物、串行处理其余 38 篇的 TeX 转换与解析，保留失败状态，并停在 P2。阶段 2 不运行 AxCell 模型抽取、不调用 GPT。本报告不授权越过 P1，也不自动启动批量。

## 文件

- `single_paper_verification.json`：结构、配置、哈希与停止状态。
- `single_paper_resource_usage.csv`：逐采样资源明细。
- `stage1_gate.json`：当前 P1 待确认状态；P0 manifest/gate 保持历史快照。
- `stage1/remote_reports/`：实际运行脚本、原始日志、容器 inspect、资源 JSONL、读回检查。
- `stage1/remote_before.json`、`remote_after.json`：前后只读核验。
- 远端：`/root/scilead/axcell/runs/20261022_formal/stage1/`。
'''
dest=FORMAL/'single_paper_regression.md';assert not dest.exists();dest.write_text(report,encoding='utf-8')
delivery=[]
for p in sorted(P.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.name!='stage1_delivery_manifest.json':delivery.append({'path':str(p.relative_to(FORMAL)),'bytes':p.stat().st_size,'sha256':sha(p)})
for name in ['single_paper_regression.md','single_paper_verification.json','single_paper_resource_usage.csv','stage1_gate.json']:
    p=FORMAL/name;delivery.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p)})
write(P/'stage1_delivery_manifest.json',delivery)
print(json.dumps({'status':verification['status'],'files':len(delivery),'es_peak_gib':measurements['es_sampled_cgroup_peak_bytes']/G,'min_host_ram_gib':measurements['host_min_available_bytes']/G,'new_extractions':0,'api_calls':0},ensure_ascii=False))
