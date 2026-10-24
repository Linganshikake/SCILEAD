"""Build offline delivery reports from saved outputs; no model/API calls."""
from pathlib import Path
import collections,datetime,hashlib,json
P=Path(__file__).resolve().parent
R=P/'remote_reports'
A=R/'attempts/console_progress_compat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def gib(n):return n/2**30
def table(rows):return '\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

delivery=read(R/'delivery_hashes.json')
for e in delivery:
 p=R/e['path'];assert p.stat().st_size==e['bytes'] and digest(p)==e['sha256'],e['path']
remote=read(R/'verification.json');local=read(P/'local_asset_integrity.json')
assert remote['all_original_asset_hashes_match'] and local['all_match']
pins=read(R/'dependency_pin_verification.json');assert pins['all_explicit_original_pins_match_with_cpu_build_exception']
validated=read(R/'output_validation.json');assert validated['prediction_count']==2 and validated['pip_check']=='No broken requirements found.'
parsed=read(R/'parsed_artifacts.json');result=read(A/'extraction_result.json')
raw=read(A/'raw_outputs/records.json');prov=read(A/'raw_outputs/provenance.json')
events=read(A/'raw_outputs/pipeline_events.json')
types=next(e['tables'] for e in events if e['step']=='type_prediction::predicted')
type_counts=dict(collections.Counter(x['prediction'] for x in types))
stages={n:read(R/(n+'_linux_status.json')) for n in ['conversion','elasticsearch_start','extraction','elasticsearch_restart_console_fix','extraction_console_fix']}
for n in ['conversion','elasticsearch_start','elasticsearch_restart_console_fix','extraction_console_fix']:
 assert stages[n]['exit_code']==0 and stages[n]['stop_reason'] is None
samples=[readline for n in stages for readline in (json.loads(x) for x in (R/(n+'_linux_resources.jsonl')).read_text().splitlines())]
assert all(s['vmstat']['oom_kill']==0 and s['vmstat']['pswpin']==0 and s['vmstat']['pswpout']==0 for s in samples)
conv=stages['conversion'];ex=stages['extraction_console_fix'];es=stages['elasticsearch_restart_console_fix']
oldcfg=read(P/'config.json')
snapshot={**oldcfg,'status':'SINGLE_PAPER_EXTRACTION_COMPLETE_STOPPED','python_prefix':'/root/scilead/axcell/envs/axcell-original','actual_environment':read(R/'environment_validation.json'),'method_entry_points':['PaperExtractor(data_dir)(selected_source)','ResultsExtractor(models_dir)(paper, in_place=True)'],'original_filters':{'table_type_threshold':0.5,'confidence_first':0.8,'best_result_context':'paper','confidence_final':0.85},'runtime_adapters':['Docker SDK version=auto negotiation','Apply task container guards to stable container collection','Skip only zero-total console progress-bar rendering'],'new_paid_api_calls':0,'normalization':'NOT_EXECUTED','evaluation':'NOT_EXECUTED','successful_inference_passes':1,'model_initialization_attempts':2,'successful_result_attempt':'console_progress_compat','source_documents_note':'AxCell uses original table/cell provenance; this output does not claim PDF Retriever evidence','package_changes':pins['changes_to_preexisting_python_packages']}
write('final_config.json',snapshot)
write('resource_summary.json',{'stages':stages,'model_load_seconds':result['model_load_seconds'],'inference_seconds':result['inference_seconds'],'sampling_interval_seconds':3,'exact_container_peak_available':False,'oom_observed':False,'swap_in_out_pages':0,'final_memory':remote['memory'],'final_disk_free_bytes':remote['disk_free_bytes'],'memory_peak_stage':'model extraction','rss_note':'Sampled sum of task process group RSS may double-count shared memory; rusage is max child RSS, not simultaneous aggregate; neither includes ES cgroup usage.'})
tables={t['name']:t for t in parsed['tables']}
inspections=[]
for row,cell in zip(raw,prov):
 _,name,pos=cell['cell_ext_id'].split('/');i,j=map(int,pos.split('.'));t=tables[name]
 inspections.append({'prediction':row,'cell_ext_id':cell['cell_ext_id'],'row_index_zero_based':i,'column_index_zero_based':j,'caption':t['caption'],'source_raw_value':t['cells'][i][j]['raw_value'],'source_value':t['cells'][i][j]['value'],'source_row':[c['value'] for c in t['cells'][i]],'first_two_rows':[[c['value'] for c in rr] for rr in t['cells'][:2]]})
assert inspections[0]['source_value']=='91.85' and inspections[0]['first_two_rows'][1][2]=='Recall'
assert inspections[1]['source_row'][0]=='Test set size (# entities)' and inspections[1]['source_value']=='4,696'
write('output_inspection.json',{'uses_gold_answers':False,'source':'Saved original parsed tables and returned original predictions','records':inspections,'table_type_predictions':types,'filter_counts':[{'sequence':e['sequence'],'step':e['step'],'input_count':e['proposal_count'],'kept_count':len(e['kept_ids'])} for e in events if e['step'].startswith('filtering::')]})
base='remote_reports/attempts/console_progress_compat/'
manifest={'experiment':oldcfg['experiment'],'scope':'one paper on Aliyun ECS','status':'SINGLE_PAPER_EXTRACTION_COMPLETE_STOPPED','paper_id':oldcfg['paper_id'],'source_version':oldcfg['tex_version'],'input_selection':'Previously frozen input-ready selection by availability; no score-based selection','tex_sha256':read(P/'transfer_manifest.json')['selected_paper']['tex_sha256'],'parsed_fragments':parsed['fragment_count'],'parsed_table_regions':parsed['table_count'],'predictions':len(raw),'raw_records':base+'raw_outputs/records.json','raw_pickle':base+'raw_outputs/records.pkl','provenance':base+'raw_outputs/provenance.json','pipeline_events':base+'raw_outputs/pipeline_events.json','scilead_field_adapter':base+'scilead_compatible_outputs/output.json','first_attempt_failure':'remote_reports/extract_error.json','resource_summary':'resource_summary.json','report':'single_paper_resource_report.md','paid_api_calls':0,'batch_executed':False,'author_36_membership':'UNVERIFIED','remote_root':oldcfg['remote_root'],'remote_run':'/root/scilead/axcell/runs/20261022_single_paper'}
write('manifest.json',manifest)
write('verification.json',{'status':'VERIFIED_SINGLE_PAPER_EXECUTION_NOT_ACCURACY','remote_original_assets_checked':len(remote['checks']),'remote_hashes_match':True,'local_original_assets_checked':len(local['files']),'local_hashes_match':True,'downloaded_report_files_hash_checked':len(delivery),'downloaded_report_hashes_match':True,'explicit_original_version_pins_match_with_cpu_build_exception':True,'output_validation':validated,'source_models_thresholds_unchanged':True,'historical_scilead_experiments_written':False,'historical_scilead_hash_reaudit_performed':False,'normalization_or_evaluation_pass_claimed':False})
stage_rows=[['阶段','完成情况','进程内存 / 容器采样峰值（GiB）','耗时','产物或错误'],['---','---','---','---','---']]
for name,label in [('conversion','TeX 转换及解析'),('elasticsearch_start','ES 首次启动'),('extraction','首次模型初始化'),('elasticsearch_restart_console_fix','ES 受控恢复'),('extraction_console_fix','模型抽取与退出清理')]:
 d=stages[name];cp='；'.join(k+': '+format(gib(v['peak_sampled_memory_bytes']),'.3f') for k,v in d['containers'].items()) or '无'
 stage_rows.append([label,'完成，exit=0' if d['exit_code']==0 else '失败，exit=1',f"进程组采样 {gib(d['peak_sampled_owned_process_group_rss_bytes']):.3f}；子进程 maxRSS {gib(d['rusage_maxrss_bytes']):.3f}；容器 {cp}",f"{d['seconds']:.2f} 秒",'空进度条除零；未生成预测' if name=='extraction' else {'conversion':'154 文本片段、11 区域','elasticsearch_start':'6.7.1，127.0.0.1:9200','elasticsearch_restart_console_fix':'原服务恢复，确认索引为空','extraction_console_fix':'2 条原始预测，服务正常停止'}[name]])
pred_rows=[['Task','Dataset','Metric','Result','原版 model 字段','来源'],['---']*6]
for x,p in zip(raw,prov):pred_rows.append([x['task'],x['dataset'],x['metric'],str(x['score']),x['model'],p['cell_ext_id']])
package_rows=[['未固定的传递依赖','初次求解','最终兼容版本'],['---']*3]+[[k,v['before'],v['after']] for k,v in pins['changes_to_preexisting_python_packages'].items()]
one=read(R/'conversion_result.json')['seconds']+result['model_load_seconds']+result['inference_seconds']+es['seconds']
doc=f'''# AxCell ECS 单篇分阶段资源验证

实验名称：**AxCell Extraction + GPT-4.1 Fully Normalization**。本轮只执行前半段的单篇 CPU 验证，已完成并停止；GPT Normalization、SCILEAD Evaluation、39 篇批量均未执行，付费 API 调用为 0。

## 实际完成范围

在阿里云 ECS `/root/scilead/axcell` 使用冻结源码 `f4648d8fee1aa8482d007a38828da9dc06630f0e`、原版 7 个模型文件与固定 Engrafo/Elasticsearch 镜像，完成 `PaperExtractor → ResultsExtractor`。论文固定为 `1511.08308.pdf`（TeX `1511.08308v5`，Named Entity Recognition with Bidirectional LSTM-CNNs），延用先前按输入可用性选定的清单，没有按得分挑选。

只传输了这一篇既有 TeX，没有重新下载 39 篇 TeX 或 AxCell 模型。39 是本地取得的输入数，**原论文 36 篇 AxCell 子集的成员关系仍未核实**。

## 环境与保护条件

ECS 实测 Ubuntu 22.04.5、8 vCPU、{gib(remote['memory']['MemTotal']):.3f} GiB RAM；无 swap。使用已有 Docker Engine 29.9.2，未改全局 Docker 配置。80 GiB 系统盘挂载 `/`、ext4；无独立数据盘。结束时可用 RAM {gib(remote['memory']['MemAvailable']):.3f} GiB、磁盘余量 {gib(remote['disk_free_bytes']):.3f} GiB。

执行环境为 `/root/scilead/axcell/envs/axcell-original`：Python 3.7.1、PyTorch 1.3.1+cpu、torchvision 0.4.2+cpu、NumPy 1.18.1、fastai 1.0.55、spaCy 2.2.3、fastprogress 0.1.21。官方所有显式版本约束通过核对；torch/torchvision 使用相同版本的官方 CPU 构建。最终 `pip check`：`No broken requirements found.`

启动门槛为实际执行主机可用 RAM ≥6 GiB、磁盘工作余量 ≥20 GiB。运行保护：可用 RAM 连续 15 秒低于 2 GiB、任务容器连续 15 秒达到限额 95%、OOM、手动停止标记或阶段超时，保存日志后只停止任务所属进程/容器。转换容器上限 20 GiB/6 CPU、网络关闭；ES 上限 3 GiB/2 CPU、JVM heap 1 GiB、只绑定 127.0.0.1。转换容器退出后才启用 ES。模型计算为 CPU，OMP/MKL 线程为 6。

本轮实际运行在 ECS，未启动 Windows WSL/Docker，未修改本机 WSL、swap 或分页配置；不能把 ECS 的内存测量当成 Windows 本机测量。

## 分阶段实测

{table(stage_rows)}

成功抽取内部计时：模型加载 {result['model_load_seconds']:.3f} 秒，实际推理 {result['inference_seconds']:.3f} 秒。内存峰值在模型抽取阶段：OS 记录的子进程最大 RSS 为 {gib(ex['rusage_maxrss_bytes']):.3f} GiB；3 秒采样的任务进程组 RSS 最大为 {gib(ex['peak_sampled_owned_process_group_rss_bytes']):.3f} GiB。两者口径不同，不可互相替代。ES 在该阶段采样峰值为 {gib(ex['containers']['/axcell-single-es']['peak_sampled_memory_bytes']):.3f} GiB；与模型数值不构成精确的同步总峰值。

容器内核没有提供 `memory.peak`，因此表中容器数据是采样峰值，不是精确峰值。进程组 RSS 相加可能重复计算共享页。整个模型阶段最低主机 MemAvailable 为 {gib(ex['min_ecs_available_bytes']):.3f} GiB；所有实验阶段 OOM 计数和 swap-in/out 增长均为 0。ES 退出码 143 来自正常 SIGTERM 停止，Docker stop 返回 0，非 OOM。

## 解析及原始预测

解析产物为 {parsed['fragment_count']} 个文本片段、{parsed['table_count']} 个 table/tabular 区域，其中包含原解析器输出的 Figure 4 区域，未人工删改。表格分类为 {type_counts}。原版过滤流程从 179 个候选，经结构过滤 128、第一层置信度过滤 121、BestResult 2、最终置信度过滤保留 2 条。

{table(pred_rows)}

以上是未经人工修改的模型返回结果。JSON/CSV/PKL、原始单元格、过滤事件及 provenance 均保留；SCILEAD 兼容文件只映射字段名并把 Result 转为字符串。`source_documents=[]` 明确表示这里使用 AxCell 表格单元格来源，并未引入 PDF Retriever。

输出后的原表复核发现：

- `table_06.csv/6.2` 的 91.85 对应 CoNLL-2003 的 **Recall** 列，原模型却绑定到 F1；该行 F1 实际列为 `91.62 (+- 0.33)`。这是指标/数值绑定错误，保留预测 91.85。
- `table_11.csv/2.4` 的 4,696 是 NW 类别的 **Test set size (# entities)**，被保留为 Ontonotes F1=4696.0。数据集统计行被当成实验结果，同时丢失细分列语义。原记录不删不改。

上述核对只用已解析表格，不读取该论文 Gold 答案，不计算准确率。两条预测不等于两条正确结果。模型完成后没有为改善质量再次推理。

## 工程问题及处理

1. 旧版依赖与跨境下载：固定镜像及官方软件包传输慢、部分超时，保留各次退出状态和缓存，有限续传。GitHub/PyTorch/PyPI 官方文件通过本地 HTTPS 与 SSH 转送；PyPI 下载产物逐项与官方 SHA256 校验，临时转发已关闭。没有替换模型或浮动镜像。
2. 官方显式依赖版本保留，初次求解出的 7 个未固定传递依赖不兼容旧 Docker SDK/IPython/Compose 或 awscli；只在独立环境中作如下调整，没有使用 `--no-deps`，最终依赖检查通过。

{table(package_rows)}

3. Docker SDK 4.1.0 与 Engine 29.9.2 的协议协商，通过独立适配层设置 `version=auto`；源码不变。转换调用同样只附加任务标识、CPU/内存/网络保护。
4. 首次模型初始化因 `fastprogress 0.1.21` 对空序列绘制进度条除零而失败，尚未进入论文推理。保留首次日志，在独立适配层仅跳过 total=0 的控制台绘制；空/非空迭代等价性已验证。第二次初始化使用新目录 `attempts/console_progress_compat`，只进行一次成功推理。没有更换框架、权重、阈值或输入。
5. 原版权重加载出现 PyTorch `SourceChangeWarning`，警告完整保留；未改权重或生成补丁。当前验证不宣称与原作者运行环境逐位一致。

## 完整性与停止状态

远端 {len(remote['checks'])} 个源码/输入/模型/启动文件与传输清单 SHA256 全部一致；本地 {len(local['files'])} 个原源码、模型、模型压缩包及选定 TeX 与已有清单一致；同步的 {len(delivery)} 个远端报告文件逐一校验大小和 SHA256。官方环境文件未改。D 盘历史 SCILEAD 冻结结果、Gold、Prompt 和 E 盘原始实验资源未写入；本轮未重新计算全部历史实验文件哈希，不作超出审计范围的声明。

任务容器已全部停止，转换容器由原调用自动移除；没有运行中的任务 tmux/进程，临时 PyPI 转发监听已关闭。保留已有 Docker daemon、镜像、模型、环境和 ES 数据；未关机或更改云实例。后续批量和付费调用均仍需确认。

## 资源判断和下一步边界

**ECS 已满足这篇论文的完整 CPU 流程，适合把串行处理作为后续验证方向；一篇不足以证明全部输入的峰值和稳定性。** 当前内存余量充足，未发现需要扩容或 swap 的依据。若后续获得批量授权，应继续逐篇隔离、相同资源保护、成功产物跳过，先核对 39 个来源版本及与作者 36 篇子集的关系。

本机 16 GiB Windows 未在本轮重新验证。已观测模型子进程峰值约 4.81 GiB，另有 ES 约 1.30 GiB 及 WSL/Docker/系统开销，原先 6 GiB 仅是启动保护，不能据此承诺本机串行稳定；本轮不建议仅调高 WSL 限额来认定物理内存问题已解决。

在依赖和镜像已准备好、同等复杂度的假设下，本篇转换+模型加载+推理+一次 ES 启动约 {one:.1f} 秒。纯线性外推 39 篇约 {39*one/60:.1f} 分钟，仅作粗略参照，未包含下载、失败排查、复杂表格差异、Normalization 和评价，不能作为可靠批量工期。后续 GPT Fully Normalization 固定 `gpt-4.1-2025-04-14`，必须先提交实际待映射字段请求量与费用估算，再等待授权。

## 文件入口

- 本地报告目录：`{P}`。
- 远端运行目录：`/root/scilead/axcell/runs/20261022_single_paper`。
- `manifest.json`：论文与输出索引；`final_config.json`：实际配置和兼容性差异。
- `{base}raw_outputs/records.json`、`records.csv`、`records.pkl`：原始预测；同目录 `provenance.json`、`pipeline_events.json`：来源及过滤记录。
- `{base}scilead_compatible_outputs/output.json`：只作字段格式映射，未标准化。
- `parsed_paper/`、`parsed_html/`：原解析产物；`output_inspection.json`：离线错误定位。
- `resource_summary.json`、`verification.json`、`local_asset_integrity.json`、`report_sync_manifest.json`：资源与完整性证据。
- `remote_reports/dependency_freeze.txt`、`conda-explicit.txt`、`dependency_pin_verification.json`、`pip_check_final.txt`：环境记录。

单篇阶段完成后停止；没有自动启动批量、GPT 标准化或其他模型实验。
'''
(P/'single_paper_resource_report.md').write_text(doc,encoding='utf-8')
(P/'run_report.md').write_text(doc,encoding='utf-8')
with (P/'progress.md').open('a',encoding='utf-8') as f:
 f.write('\nFinal status: single-paper official CPU extraction complete. pip check passes; all original explicit pins match with CPU wheel build exception; seven transitive compatibility constraints recorded. First model initialization failed before inference on fastprogress console zero-total division; original failure preserved. A display-only wrapper passed empty/nonempty equivalence checks; second initialization and single inference pass succeeded, 2 raw predictions, 4.643 s model loading / 65.271 s inference. Offline source-table inspection found Recall/F1 misbinding and dataset-size row extraction; no predictions corrected or regenerated. Owned services and temporary PyPI relay stopped. All allowlisted original local/remote assets and synchronized report hashes match. No paid API, normalization, evaluation or batch executed. See final reports and manifest.\n')
print(json.dumps({'reports_created':True,'original_records':len(raw),'delivery_files_verified':len(delivery),'process_rusage_peak_gib':round(gib(ex['rusage_maxrss_bytes']),3),'es_sampled_peak_gib':round(gib(ex['containers']['/axcell-single-es']['peak_sampled_memory_bytes']),3),'type_counts':type_counts},ensure_ascii=True))
