"""Write phase-0 reports from measured metadata. Does not run any experiment stage."""
from pathlib import Path
import csv,datetime,hashlib,json
P=Path(__file__).resolve().parent;OLD=P.parent/'20261022_single_paper'
ROOT=Path(r'E:\SCILEAD\axcell');REPO=Path(r'D:\C++\SCILEAD\emnlp2024-leaderboard-generation')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def md(name,text):(P/name).write_text(text,encoding='utf-8')
def tab(rows):return '\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)
r=read(P/'remote_preflight.json');s=read(P/'input_audit_summary.json');limits=read(P/'remote_resource_limits.json');old=read(OLD/'final_config.json')
papers=list(csv.DictReader((P/'input_manifest.csv').open(encoding='utf-8-sig',newline='')))
ready=[x for x in papers if x['input_eligible']=='True'];assert len(ready)==39
assert not any(x['formal_evaluation_allowed']=='True' for x in papers)
available=min(x['memory']['MemAvailable'] for x in r['memory_samples'])/2**30
assert available>=6 and r['disk_free_bytes']>=20*2**30
assert r['original_assets_match'] and r['single_paper_run_unchanged'] and r['single_paper_script_and_parsed_match']
assert not r['package_diff_from_single_paper'] and r['pip_check']['exit_code']==0
assert not r['running_containers']['stdout'].strip() and not r['elasticsearch_port_open']
expected=[x['repo_digests'] for x in read(OLD/'remote_reports/verification.json')['images']]
assert [x['digests'] for x in r['images']]==expected
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
models=[x for x in r['original_assets'] if x['path'].startswith('models/')]
code=read(P/'scilead_code_checks.json')
policy={
 'stage':0,'state':'P0_AWAITING_USER_CONFIRMATION','allowed_current_actions':['read-only audits','new local stage-0 reports'],
 'phase1_authorized':False,'batch_parse_authorized':False,'batch_extraction_authorized':False,'paid_api_authorized':False,
 'next_stage_if_P0_confirmed':'stage 1: existing single-paper regression only; no new model generation',
 'gates':[{ 'id':'P'+str(i),'requires_explicit_user_confirmation':True,'authorizes_only_next_stage':True} for i in range(5)],
 'unknown_author36_scope_requires_user_decision':True}
save('stage_gate.json',policy)
reference_txt=Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021\references\scilead_emnlp_2024.txt')
reference_pdf=reference_txt.with_suffix('.pdf')
text=reference_txt.read_text(encoding='utf-8');lines=text.splitlines();matches=[{'line':i+1,'text':line} for i,line in enumerate(lines) if '36 TeX' in line]
save('paper_scope_evidence.json',{'source':'https://aclanthology.org/2024.emnlp-main.453/','local_pdf':str(reference_pdf),'pdf_sha256':sha(reference_pdf),'local_text':str(reference_txt),'text_sha256':sha(reference_txt),'section':'Appendix B','matched_lines':matches,'paraphrase':'Authors used 36 available TeX papers from the 43-paper dataset, evaluated against those papers Gold, and used GPT-4 Turbo fully predefined normalization. Exact IDs were not found in examined paper/local source/data files.','live_metadata_check':'See official_scope_fetch_status.json: all four live official metadata requests timed out; absence from unexamined live attachments is NOT established.'})
comparison_files={
 'gpt41_fully_normalized':Path(r'D:\C++\SCILEAD\pilot\full43_uncapped\merged\normalized_output.json'),
 'llama3_v2_fully_normalized':Path(r'D:\C++\SCILEAD\pilot\autodl_llama3\20261021_format_followup\format_v2\normalization\fully_llm\normalized_output.json'),
 'llama3_evaluation_gold':Path(r'D:\C++\SCILEAD\pilot\autodl_llama3\20261021_format_followup\format_v2\evaluation\gold_subset.json')}
comparison=[]
for name,path in comparison_files.items():
 d=read(path);comparison.append({'kind':name,'path':str(path),'sha256':sha(path),'paper_count':len(d),'current_input_overlap':len(set(d)&{x['paper_id'] for x in ready})})
save('comparison_input_index.json',comparison)
experiment={
 'experiment_name':'AxCell Extraction + GPT-4.1 Fully Normalization','run_id':'20261022_formal','created_utc':now,
 'current_stage':0,'status':policy['state'],'authorization':policy,
 'local_output_root':str(P),'planned_remote_output_root':'/root/scilead/axcell/runs/20261022_formal','remote_directory_created_by_P0':False,
 'ssh_alias':'scilead-aliyun','ssh_config_path':r'C:\Users\Administrator\.ssh\config','ssh_user':'root','ssh_port':22,
 'host_fingerprint':'SHA256:KGalzbokV4SulHzbq1wOCab/tALh6UzpY/curGepe4Q','authentication':'Prior designated credential loader; host identity checked before password authentication; no credentials stored in audit',
 'axcell_commit':old['axcell_revision'],'scilead_commit':'8bf74b0a830feb7035c6166dce3394dc344ae532',
 'axcell_source_root':'/root/scilead/axcell/source/axcell','scilead_source_root':str(REPO),'python_prefix':old['python_prefix'],
 'dependency_versions':r['packages'],'dependency_changes_this_stage':{},'docker_images':r['images'],'models':models,
 'environment_yml_sha256':sha(ROOT/'source/axcell/environment.yml'),'scilead_prompt_sha256':sha(REPO/'prompts.json'),'scilead_code_hashes_file':'scilead_code_checks.json',
 'input_manifest':{'path':'input_manifest.csv','sha256':sha(P/'input_manifest.csv'),'rows':43,'eligible_local_inputs':39,'eligible_gold_tdmrs':283,'all_source_tex_bytes':s['total_tex_bytes'],'ordered_proposed_paper_ids':[x['paper_id'] for x in ready],'order_policy':'Original Gold/inventory order, not prediction quality','author_36_membership':'UNVERIFIED','formal_evaluation_approved':False},
 'gold':{'tdm_path':str(ROOT/'data/gold/tdm_annotations.json'),'tdm_sha256':sha(ROOT/'data/gold/tdm_annotations.json'),'leaderboard_path':str(ROOT/'data/gold/leaderboards.json'),'leaderboard_sha256':sha(ROOT/'data/gold/leaderboards.json'),'papers':43,'tdmrs':295,'candidate_counts':s['candidate_counts']},
 'single_paper_reuse':{'paper_id':'1511.08308.pdf','source_version':'1511.08308v5','root':str(OLD),'remote_root':'/root/scilead/axcell/runs/20261022_single_paper','success_attempt':'console_progress_compat','result_file':str(OLD/'remote_reports/attempts/console_progress_compat/raw_outputs/records.json'),'result_sha256':sha(OLD/'remote_reports/attempts/console_progress_compat/raw_outputs/records.json'),'raw_predictions':2,'regeneration_allowed':False,'P1_regression_not_yet_executed':True},
 'method':{'entry_points':old['method_entry_points'],'filters':old['original_filters'],'runtime_adapters':old['runtime_adapters'],'weights_taxonomy_abbreviations_unchanged':True,'workers':1,'device':'cpu','OMP_NUM_THREADS':6,'MKL_NUM_THREADS':6,'use_crf':False},
 'resource_policy':{'start_min_mem_available_gib':6,'minimum_disk_reserve_gib':20,'stop_mem_available_gib':2,'stop_sustained_seconds':15,'container_limit_stop_ratio':0.95,'stop_on_oom':True,'sample_interval_seconds':3,'conversion_container_memory_gib':20,'conversion_cpus':6,'conversion_network_disabled':True,'es_memory_gib':3,'es_heap_gib':1,'es_cpus':2,'es_bind':'127.0.0.1:9200','no_system_memory_or_swap_changes':True,'disk_guard':'Recheck before each later stage/paper; pause on reserve violation; runtime disk monitor must be verified before batch approval'},
 'future_normalization':{'model':'gpt-4.1-2025-04-14','base_url':'https://9527.codes/v1','temperature':0,'seed':0,'stream':False,'max_retries':0,'omitted_parameters':['max_tokens','max_output_tokens','max_completion_tokens'],'model_fallback':None,'prompt_key':'normalization-system-prompt','candidate_scope':'All 43 Gold papers: 23 Tasks, 71 Datasets, 26 Metrics','candidate_order':'Actual order/template must be captured at P4; no request constructed in P0','result_policy':'Original result string unchanged','cache_policy':'Resume only identical already completed request identities; no deduplication of repeated fresh official per-field requests. Request identity includes paper/record/field, input, prompt, model, parameters and candidate serialization.','enabled':False,'requires_P4_approval':True,'requests_estimated':None,'cost_estimated':None},
 'evaluation':{'state':'NOT_EXECUTED','official_scripts_unchanged':True,'tdm_aggregation':'Official per-paper macro P/R; F1=2PR/(P+R), zero if P+R=0','author_36_comparison':'Blocked pending membership evidence or explicit acceptance of distinct available-TeX scope','gpt41_common_scope':'39 available-input papers, pending processing/gate approval','llama3_common_scope':s['comparison_scope'],'strict_one_to_one_diagnostic_separate':True,'leaderboard_scope_preview':s['leaderboard_scope_preview'],'source_warning':'Official Result substring matching, duplicate handling, numerical-list RBO and CLI arg mismatch retained; existing independent adapter to be reviewed at stage5, no source changes in P0'},
 'time':{'preflight_utc':r['utc_time'],'experiment_start_utc':None,'batch_runtime_seconds':0,'new_api_calls':0}}
save('experiment_manifest.json',experiment)
save('dependency_snapshot.json',r['packages'])
versions={x:r['packages']['packages'].get(x) for x in ['torch','torchvision','numpy','pandas','fastai','fastprogress','spacy','scispacy','docker','docker-compose','elasticsearch','elasticsearch-dsl']}
versionrows=[['依赖','当前版本'],['---','---'],['Python','3.7.1']]+[[k,v] for k,v in versions.items()]
imagerows=[['镜像','实际 digest'],['---','---']]+[[x['reference'],x['digests'][0].split('@')[1]] for x in r['images']]
md('environment_preflight.md',f'''# 阶段 0：环境预检查

状态：**已有环境可复用；P0 等待确认**。当前只进行元数据、文件哈希、依赖和资源只读检查，没有运行 P1 服务回归、批量解析、模型抽取或 API。

已显式读取 Administrator 的 SSH 配置：`scilead-aliyun → root@123.56.138.148:22`，StrictHostKeyChecking=true。实际认证复用此前指定的凭据加载器，先核对已确认的 Ed25519 主机指纹，再认证；未读取或展示私钥，未在新文件保存密码/Token。隔离终端默认账户不同，已使用显式用户配置处理；没有修改 SSH config 或全局 Git 配置。

AxCell 固定提交 `{old['axcell_revision']}`，本地 82 个源文件和远端对应文件全部哈希匹配。SCILEAD Git HEAD 为 `8bf74b0a830feb7035c6166dce3394dc344ae532`，21 个跟踪文件与 Git blob 一致（核对 Windows checkout CRLF）；官方源码/Prompt/Gold 均未修改。

{tab(versionrows)}

环境位于 `{old['python_prefix']}`，包版本清单与成功单篇结束时完全一致；`pip check` 返回 0：`No broken requirements found.`。无重新安装或升级；此前 7 个未固定传递依赖兼容版本继续保留，CPU wheel 例外不变。P0 不导入模型权重。

{tab(imagerows)}

Docker Engine 29.9.2 正常运行，两个固定镜像已存在。任务容器均停止。Elasticsearch 6.7.1 镜像、停止容器、3 GiB 限额及 127.0.0.1:9200 绑定保留；9200 当前未监听，与上轮正常停止状态一致。**本轮没有启动它，因此不能声称已重新验证服务就绪**；必要服务回归属于获批后的 P1。

模型、taxonomy、metrics、abbreviations 和 SentencePiece 词表共 7 个文件，本地与远端 SHA256 匹配既有清单；总文件字节数 {sum(x['actual_bytes'] for x in models):,}。这表示与已下载冻结文件相同，不把本地计算的 SHA256 冒充作者发布的校验值。官方 taxonomy 未替换为 SciLead Gold。

单篇成功输出和日志的 192 个冻结文件保持一致；此前脚本与解析产物的 46 个远端哈希也一致。`single_paper_error_baseline.json` 固定了两处原始错误：91.85 为 Recall 列却预测为 F1；4696 为实体数量却预测为分数。没有重新推理或人工修正。本阶段的只读复核不等于已经完成 P1。

未来沿用原版 `PaperExtractor`、`ResultsExtractor`，type threshold=0.5，结构过滤→confidence 0.8→paper BestResult→confidence 0.85，use_crf=False；只复用已验证的 Docker API 协商、资源封装和空进度条显示适配。

本阶段未发现需要修改系统配置、重新下载模型或增购云资源的依据。云实例原有运行费用继续存在；本阶段新增 GPT/API 费用为 0。详细证据：`remote_preflight.json`、`local_asset_checks.json`、`scilead_code_checks.json`、`dependency_snapshot.json`。
''')
mem=r['memory_samples'][0]['memory'];cgrows=[['cgroup','memory.max','memory.high','cpu.max'],['---']*4]+[[x['path'],x['memory.max'],x['memory.high'],x['cpu.max']] for x in limits['cgroup_ancestry']]
md('resource_preflight.md',f'''# 阶段 0：资源预检查

测量时间 UTC：{r['utc_time']}；上海时间：{datetime.datetime.fromisoformat(r['utc_time']).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}。

| 项目 | 当前实测 |
|---|---|
| 主机 | Ubuntu 22.04.5 LTS，8 vCPU，nproc=8 |
| 物理内存 | {mem['MemTotal']/2**30:.3f} GiB |
| 三次采样最低 MemAvailable | {available:.3f} GiB |
| Swap | 0；本阶段未启用或调整 |
| Committed_AS / CommitLimit | {mem['Committed_AS']/2**30:.3f} / {mem['CommitLimit']/2**30:.3f} GiB，Linux 指标，不套用 Windows 提交限额语义 |
| 数据路径挂载 | `/root/scilead/axcell` 和 `/var/lib/docker` 均在 `/dev/nvme0n1p3`，ext4，挂载 `/` |
| df 可见文件系统容量 / 余量 | 78.373 / {r['disk_free_bytes']/2**30:.3f} GiB；云盘标称 80 GiB，无独立数据盘 |
| inode | 总 5,224,464；余 4,774,718（本次 df -i） |
| Docker / 任务容器 | Engine active；运行容器 0 |
| Elasticsearch | 停止；没有因 P0 检查启动 |

{tab(cgrows)}

`max` 表示相应 cgroup 没有该硬限额；根级文件不存在不代表主机内存无限。有效主机 RAM 仍为约 30.69 GiB。停止的 ES 容器限制为 3 GiB、CPU 2、无额外容器 swap；转换容器计划限制保持 20 GiB/6 CPU。当前零模型负载，**没有新的运行峰值测量**。

此前单篇模型子进程 maxRSS 约 4.813 GiB，ES 采样峰值约 1.304 GiB，CPU 推理约 65.3 秒；仅作为已有基线，不当作本轮批量实测。P0 证明当前满足 ≥6 GiB 可用内存及 ≥20 GiB 磁盘余量的启动门槛，不能保证所有长论文/复杂表格的峰值。

39 个本地 TeX 合计 {s['total_tex_bytes']:,} bytes（{s['total_tex_bytes']/2**20:.2f} MiB）；远端目前只存一篇既有输入，其余 38 篇尚未传送，待后续授权。现有 56 GiB 余量足以容纳这些输入；批量转换临时文件和日志峰值未知，后续仍逐篇测量并保持 20 GiB 工作余量。

冻结保护条件：串行一次一篇、单份模型；阶段/每篇开始前重测资源；RAM 连续 15 秒低于 2 GiB、容器连续 15 秒达到 95% 限额、OOM 或磁盘工作余量不足时保存日志并停止任务所属进程/容器。转换容器退出后才进入模型服务阶段，不同时预加载多个模型。未来批量磁盘监测需在 P2 前验证；本轮未创建或启动批量程序。

无需修改 WSL、swap、分页文件、Docker 全局设置或云实例规格。原有云实例正常计费，不新增云资源或付费 GPT 调用。服务器未关机，Docker daemon 保持原状态。
''')
missingrows=[['缺少已核实 TeX 的论文','Gold TDMR','原因'],['---','---','---']]+[[x['paper_id'],x['gold_tdmr_count'],'未获得可核实的 TeX/arXiv 来源映射；不采用猜测替代'] for x in s['missing']]
idrows=[['论文 ID','Gold TDMR','TeX 版本','输入可用性','作者 36 篇成员'],['---']*5]+[[x['paper_id'],x['gold_tdmr_count'],x['tex_version'] or '—','可用；待 P0 确认' if x['input_eligible']=='True' else '缺少来源','未核实'] for x in papers]
common=s['comparison_scope'];assert len(common['llama3_42_common_ids'])==38 and common['llama3_common_gold_count']==247
md('scope_and_gold_audit.md',f'''# 阶段 0：论文范围与 Gold 审计

## 结论与暂停

本地 39 份既有 TeX 通过 SHA256、大小、tar 成员可读性及 gzip CRC 检查，对应 SciLead 的 **39 篇 / 283 条 Gold TDMR**。完整 Gold 仍为 **43 篇 / 295 条**；剩余 4 篇共 12 条缺少已核实 TeX。

**作者原论文 36 篇的确切成员及所用 TeX 版本仍未核实。** 当前不能把这 39 篇命名为“原论文 36 篇范围复现”，也不能宣称其中某 36 篇就是作者集合。本轮冻结的是输入证据和范围提案，`formal_evaluation_allowed=False` 明确表示尚未获得 P0/P后续阶段批准；不是说这些有 Gold 的论文无法评价。

## 作者依据与查找边界

已读原论文 [Appendix B](https://aclanthology.org/2024.emnlp-main.453/)，其说明从 43 篇中取得 36 篇 TeX，AxCell 的 tuple/leaderboard 评价使用这些论文的 Gold，标准化采用 GPT-4 Turbo Fully Pre-defined。正文及当前本地固定版官方代码、数据 README、TSV/JSON 结构均未发现可识别作者 36 篇成员的标记。

已检查官方 Git commit 的 21 个跟踪文件、原始数据包目录（README、tdm_annotations.json/tsv、leaderboards.json）、历史 AxCell manifest/来源映射。公开 GitHub 固定树/Release、ACL 论文页和 TUdata 入口的本轮网络访问均 ReadTimeout；见 `official_scope_fetch_status.json`。因此只能报告**已检查材料未找到名单**，不能断言作者从未公开名单。无未经批准的作者联系或第三方替代数据。

39 篇中 31 篇直接使用 Gold 的 arXiv ID，8 篇依据既有官方书目标题及作者匹配记录映射到 arXiv。固定当前明确 vN 和 SHA256，作者所用版本未知；同题同作者不是字节一致证明。压缩包完整性通过只说明当前取得的容器可完整读取，不代表所有 TeX 引用、编译依赖或输出表格已验证；编译完整性统一 `NOT_TESTED_P0`，需要 P2 实测。

{tab(missingrows)}

## 拟用范围与公平比较

- 本地可用输入范围：39 篇 / 283 Gold，仅按来源与完整性确定，没有利用 AxCell 得分筛选。完整 43 行 `input_manifest.csv` 保留缺失项，避免静默删失。
- 作者范围：43 个 paper ID 对“是否属于作者 36 篇”均为 UNVERIFIED。需要作者明细或其他可靠成员证据，不能从 39 中任取 36。
- 如你接受独立的“当前可用 TeX 39 篇”复现口径，后续需在同一 39 篇上离线重算已有 GPT-4.1 冻结结果；不能与 GPT-4.1 全 43 篇分数直接作受控比较。
- Llama-3 V2 的实际 Gold 清单为 42 篇（不含 `1912.08777.pdf`），与这 39 篇交集为 **38 篇 / 247 Gold**。后续三模型公平比较应另报此共同范围，并保留各自完整范围的描述性结果；本阶段没有运行评价。
- 39 篇与完整 27 个 Gold Leaderboards 都有交集，保留 131 条榜内论文记录。这是按论文集合重新计算的范围统计，不代表已构建 27 个有效预测榜，也不能套用历史 Llama 子集指标。

完整 Fully 候选集合仍从 43 篇 Gold 构建：23 Task、71 Dataset、26 Metric；不因评价子集缩减候选集。Gold 字节哈希与历史冻结 GPT-4.1 实验一致。阶段 0 只统计/审计元数据，未把 Gold 对应答案送入任何模型。

后续官方评价保持原逻辑：逐篇 Macro P/R、聚合 P/R 算 F1；Result 字符串包含关系、重复记录处理、数值列表 RBO 均保持。严格一对一数值诊断单列。官方 leaderboard CLI 参数名存在已知不一致，后续只复用现有独立入口适配，不能修改算法。LR/有效非空榜率/论文 ID AO 不冒充官方脚本直接输出。

## 全部输入索引

{tab(idrows)}

当前停在 **P0**。确认只能授权紧接着的 P1 单篇产物回归；P1 不重新生成预测，完成后还需停在 P1。不会自动开始批量或 GPT 调用。
''')
md('P0_report.md',f'''# P0：环境与范围确认

阶段 0 已执行；**等待用户确认，未进入阶段 1**。

| 项目 | 结果 |
|---|---|
| 当前资源 | 8 vCPU；可用 RAM 最低 {available:.2f} GiB；磁盘余量 {r['disk_free_bytes']/2**30:.2f} GiB |
| 环境 | 依赖无变更，pip check 通过，固定镜像和 7 个模型/词表文件完整 |
| 服务 | Docker active；运行容器 0；ES 保持停止，本阶段未启动 |
| 输入 | 39 篇 TeX 完整性通过，对应 283 Gold；31 篇直接 arXiv、8 篇书目映射 |
| 缺失 | 128538.pdf、D19-1367.pdf、C18-1139.pdf、D18-1105.pdf，共 12 Gold |
| 作者 36 篇 | 具体成员及 TeX 版本仍 UNVERIFIED；实时官方元数据访问超时 |
| 服务器已存 TeX | 单篇验证的一篇；其余 38 篇待后续授权再传送 |
| 单篇结果 | 原 2 条预测/证据保留；Recall/F1 绑定与实体数量误抽错误未修正 |
| 系统/费用 | 不需当前配置修改或新增云资源；本阶段模型生成和付费 API 均 0 |

建议待确认口径：保留作者范围未核实标记，使用“当前可用 TeX 39 篇”作为独立复现范围提案；与 GPT-4.1 按 39 篇、与 Llama-3/GPT-4.1 按共同 38 篇另行比较。尚未批准正式评价，所有 input_manifest 行的 `formal_evaluation_allowed` 仍为 False。

文件：`input_manifest.csv`、`experiment_manifest.json`、`environment_preflight.md`、`resource_preflight.md`、`scope_and_gold_audit.md`。后续阶段状态见 `stage_gate.json`。

请确认 P0 的范围与环境记录；确认后只进入 P1 单篇回归，不会自动进入 P2 批量解析。若必须严格取得作者 36 篇名单才继续，则保持范围阻塞并等待可靠名单。
''')
print(json.dumps({'stage':0,'state':policy['state'],'input_rows':len(papers),'eligible':len(ready),'author36_verified':False,'generated_required_outputs':True}))
