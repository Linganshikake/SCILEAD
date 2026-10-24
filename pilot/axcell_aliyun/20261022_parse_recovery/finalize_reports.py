"""Uniform fail-closed validation and Chinese recovery report generation."""
import csv,datetime,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
F=R.parent/'20261022_formal'
A=R/'remote_snapshot/attempt_2203_timeout600'
L=A/'parse_logs/2203.16804.pdf'
REMOTE='/root/scilead/axcell/runs/20261022_parse_recovery'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(name,d):(R/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 before=read(R/'frozen_local_before.json')
 current={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(F.rglob('*')) if p.is_file()}
 assert current==before,'Frozen local files changed'
 rb=read(R/'remote_before.json');ra=read(R/'remote_after.json');rv=read(R/'remote_verification.json')
 assert rb['frozen_formal']==ra['frozen_formal'],'Frozen remote files changed'
 assert rv['original_success_papers']==37 and rv['original_artifacts_all_unchanged'] and rv['protected_assets_all_match']
 protected=read(R/'protected_source_before.json')
 assert all(Path(p).stat().st_size==d['bytes'] and sha(Path(p))==d['sha256'] for p,d in protected.items())
 synced=read(R/'sync_manifest.json')
 assert all((R/'remote_snapshot'/x['relative_path']).stat().st_size==x['bytes'] and sha(R/'remote_snapshot'/x['relative_path'])==x['sha256']==rv['recovery_files'][x['relative_path']]['sha256'] for x in synced)
 original_failure_logs=[]
 for pid in ['1905.03197.pdf','2203.16804.pdf']:
  for p in (R/'diagnosis'/pid/'original_failure_logs').iterdir():
   original=F/'stage2/parse_logs'/pid/p.name
   assert sha(p)==sha(original)
   original_failure_logs.append({'paper_id':pid,'path':str(original),'copy':str(p),'sha256':sha(p)})
 status=read(L/'conversion_linux_status.json');finished=read(A/'attempt_finished.json');conf=read(A/'configuration.json')
 samples=[json.loads(l) for l in (L/'conversion_linux_resources.jsonl').read_text().splitlines()]
 containers=[c for s in samples for c in s['containers']]
 assert status['stop_reason']=='TASK_CONTAINER_NEAR_MEMORY_LIMIT'
 assert not rv['remaining_containers'] and not status['cleanup']['containers']['remaining_running_task_containers']
 assert not status['cleanup']['process_group']['remaining_live_members']
 assert all(not c['partial_outputs'] for c in containers)
 assert all(not d['html_exists'] and not d['parsed_directory_exists'] for d in rv['recovery_candidates'].values())
 assert not any(c['oom_killed'] or c.get('events',{}).get('oom_kill',0) for c in containers)
 oom=read(R/'oom_audit.json')
 assert ra['vmstat']['oom_kill']-rb['vmstat']['oom_kill']==1
 assert any('CONSTRAINT_MEMCG' in line and '75933' in line for line in oom['kernel_journal']['matching_context'])
 peak=max(c['memory.current'] for c in containers);perl=max(p['rss_bytes'] for c in containers for p in c['processes'] if p['name']=='perl')
 cpu=max(c['cpu_stat']['usage_usec'] for c in containers)/1e6
 resources={'samples':len(samples),'sample_interval_seconds':3,'elapsed_seconds_including_cleanup':finished['seconds'],'last_sample_seconds':samples[-1]['elapsed_seconds'],'peak_sampled_container_bytes':peak,'kernel_confirmed_container_memory_bytes':20*2**30,'peak_sampled_perl_rss_bytes':perl,'kernel_perl_rss_bytes':(20891308+11116)*1024,'peak_sampled_wrapper_tree_rss_bytes':status['peak_sampled_owned_process_group_rss_bytes'],'container_cpu_seconds_last_sample':cpu,'min_sampled_host_available_bytes':status['min_ecs_available_bytes'],'oom_count_delta':ra['vmstat']['oom_kill']-rb['vmstat']['oom_kill'],'oom_scope':'CONSTRAINT_MEMCG task container c31b0592c630, perl PID75933, during cleanup at 17:33:38 +0800','swap_growth_bytes':status['swap_growth_bytes'],'monitor_stop_reason':status['stop_reason'],'final_failure':'RESOURCE_LIMIT_OOM_DURING_CLEANUP','outer_exit_code':finished['exit_code'],'child_exit_code':status['exit_code'],'wrapper_forced_kill':status['cleanup']['process_group']['forced_kill'],'kernel_killed_perl':True,'disk_free_bytes_after':rv['disk_free_bytes'],'memory_peak_precision':'Periodic samples missed cleanup-window peak; kernel log proves 20 GiB cgroup usage and OOM. Raw monitor record preserved.'}
 save('recovery_resource_summary.json',resources)
 rows=[{'paper_id':'1905.03197.pdf','label':'RECOVERY','status':'BLOCKED_COMPATIBILITY','root_cause_confirmed':'FIRST_FATAL_DEPENDENCY_CHAIN_CONFIRMED','recovery_attempt_count':0,'attempt_method':'READ_ONLY_DIAGNOSIS_ONLY','configuration_difference':'NONE_APPLIED','success':False,'fragment_count':None,'table_count':None,'seconds':None,'peak_container_bytes':None,'output_path':'diagnosis/1905.03197.pdf','reason':'tikzmark requires expl3 primitives unsupported by fixed LaTeXML; no safe entrypoint/file-layout fix'},
 {'paper_id':'2203.16804.pdf','label':'RECOVERY_TIMEOUT_600','status':'FAILED_RESOURCE_LIMIT_OOM','root_cause_confirmed':'POSTPROCESS_CPU_MEMORY_GROWTH_CONFIRMED_SPECIFIC_TRIGGER_UNRESOLVED','recovery_attempt_count':1,'attempt_method':'ONE_TIMEOUT_ONLY_DIAGNOSTIC','configuration_difference':'latex2html.sh timeout 300 -> 600 only; read-only monitoring added','success':False,'fragment_count':None,'table_count':None,'seconds':finished['seconds'],'peak_container_bytes':20*2**30,'output_path':'remote_snapshot/attempt_2203_timeout600','reason':'TASK_CONTAINER_NEAR_MEMORY_LIMIT followed by MEMCG_OOM during cleanup'}]
 with (R/'recovery_attempts.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 verification={'status':'INTEGRITY_PASSED_RECOVERY_UNSUCCESSFUL','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'local_formal_files_checked':len(before),'local_formal_unchanged':True,'remote_formal_files_checked':len(rb['frozen_formal']),'remote_formal_unchanged':True,'formal_success_papers':37,'formal_failure_papers':2,'formal_success_artifacts_checked':rv['original_artifacts_checked'],'formal_success_artifacts_unchanged':True,'protected_remote_assets_checked':len(rv['protected_assets']),'protected_assets_unchanged':True,'fixed_image_unchanged':rv['image']==conf['image']['id'],'recovery_artifact_sync_files_checked':len(synced),'recovery_artifact_sync_hashes_match':True,'original_failure_log_files_retained':len(original_failure_logs),'input_archives_and_members_match':True,'candidate_validation':rv['recovery_candidates'],'html_content_check':'NOT_POSSIBLE_NO_HTML','AxCell_loader_check':'NOT_RUN_NO_PARSE_ARTIFACTS','key_table_preservation':'UNVERIFIABLE_NO_OUTPUT; source originals unchanged','recovered_papers':0,'new_model_extractions':0,'GPT_calls':0,'running_task_containers':[],'kernel_confirmed_task_OOM':True,'OOM_events':1,'stage3_authorized':False,'P2_status':'AWAITING_USER_FINAL_ACCEPTANCE'}
 save('recovery_verification.json',verification)
 manifest={'label':'RECOVERY','date':'2026-10-22','local_directory':str(R),'remote_directory':REMOTE,'remote_directory_reason':'/data absent; reuse verified persistent ext4 root disk','formal_directory':str(F),'axcell_commit':conf['axcell_commit'],'image':conf['image'],'model_loads':0,'API_calls':0,'normalization':False,'rows':rows,'inputs':read(R/'selected_inputs.json'),'read_only_input_audit':'input_audit_remote.json','first_failure_records':original_failure_logs,'attempt_configuration':conf,'scripts':read(A/'prelaunch.json')['scripts'],'resources':resources,'source_structure_counts':{pid:{k:read(R/'diagnosis'/pid/'source_structure.json')[k] for k in ['main','table_float_count','tabular_begin_count']} for pid in ['1905.03197.pdf','2203.16804.pdf']},'source_count_note':'Static TeX markers, not successful parsed output counts.','compatibility_proposal_executed':False,'formal_manifest_updated':False,'stage3_started':False,'author36_membership':'UNVERIFIED; no scope change'}
 save('recovery_manifest.json',manifest)
 diagnosis=f'''# 两篇失败的诊断与受控恢复记录

本轮完成只读诊断与一次受控恢复尝试，**未恢复任一论文**。所有结果为 RECOVERY，不改正式阶段 2。

## 1905.03197.pdf

主文件 `unified.tex` 正确，官方优先级 15；其他两份 TeX 优先级 0。原包 7 个文件与正式解压逐文件匹配，包括 `neurips_2019.sty`、`settings.tex`、`math_commands.tex`。没有解压或文件组织修复的依据。

原 `container_stderr.log:167` 首个 Error 为 `Package expl3 Error: Required primitives not found`，位置 `expl3-code.tex:288`。调用链：`unified.tex:22` → `settings.tex:14–15` → TikZ/tikzmark → 镜像中的 `expl3, l3keys2e, xparse`。随后才出现 `\\ExplSyntaxOn`、`\\cs` 等连锁错误，最终 101 errors/1 fatal。固定 LaTeXML 为 0.8.4，镜像没有独立 expl3/tikzmark binding。

`capt-of.sty`、`scalerel.sty`、`adjustbox.sty` 在镜像内实际存在；缺少 binding 的警告不能等同源文件下载缺失。首个错误已定位，但不保证修复它后不存在其他兼容问题。

没有执行重复转换或宏补丁。具体独立兼容诊断提案见 `1905_compatibility_proposal.md`；不删除宏、表格或正文，不使用猜测定义。静态 TeX 计数为 10 个 table/table* 块、14 个 tabular 起始标记；没有可验证的解析产物。

## 2203.16804.pdf

主文件 `acl.tex` 正确；原包 10 个文件与正式解压一致，`acl.sty` 和 `acl_natbib.bst` 都在。原日志另有 pgfplots `compat=1.17` 不被镜像所含最多 1.16 支持、`\\DeclareUnicodeCharacter`、`\\aboverulesep`、`\\belowrulesep` 未定义；这些错误未在正文消化阶段直接终止转换，不能断言与后处理异常无关。本轮没有修改它们。

原 300 秒运行在约 26 秒完成正文消化、构建、数学处理并进入 Scan。最后可见步骤为 `Scan index.html ... DBStatus: 517/0 objects`。历史容器峰值约 10.70 GiB，无 OOM 或 swap；没有保存 CPU 历史，失败容器/临时目录已经清理，没有残留 HTML，不能补造历史 CPU 数据。

固定 Engrafo 使用 readline 逐行转发 LaTeXML 日志，而部分 NoteBegin/进度没有换行，故日志沉默不能直接证明死锁。源码含 37,517,244 字节 `anthology.bib`，静态标记计数 70,470，是潜在后处理负担。**尚未证实本次持续增长发生在参考文献转换，不能将该假说当作根因。**

在原任务无 OOM/换页且资源余量充分的条件下，仅执行一次获准诊断。恢复版 `latex2html.sh` 相对原文件逐字节唯一差异是 `timeout -s KILL 300 engrafo` 改为 600。原镜像、输入 SHA256、官方补丁、主文件选择、原版 PaperExtractor、6 CPU/20 GiB/禁网配置保持一致。监控器新增只读 CPU/文件位置/中间文件观察，外层 660 秒看门狗只供解析清理，不增加 Engrafo 的 600 秒上限。

实际运行 {finished['seconds']:.2f} 秒（含清理），最后采样在 {samples[-1]['elapsed_seconds']:.2f} 秒。Perl 持续 CPU 计算，容器累计 CPU 约 {cpu:.2f} 秒；没有观察到网络等待或外部工具阻塞。采样峰值容器 {peak/2**30:.3f} GiB、Perl RSS {perl/2**30:.3f} GiB。最后采样时仍没有 HTML/XML/log 中间文件。触发 95% 容器上限持续 15 秒的保护，原因 `{status['stop_reason']}`；SIGTERM 停止包装进程，随后 `docker stop` 返回 0。但是保护未及时阻止容器继续分配内存：内核日志确认 17:33:38（北京时间）清理窗口内达到 **20 GiB**，对同一容器 PID75933 的 Perl 触发 **1 次 CONSTRAINT_MEMCG OOM kill**。它不是全宿主物理内存耗尽。无交换增长。外层退出码 125，包装子进程 -15；这**不是运行足 600 秒后再次超时**。

原始监控最后一条记录的 OOM 标志仍为 false，原因是它随后进入清理且不再采样；结束后的全局 oom_kill 增量与内核日志补足了这个盲区。保留原始记录，不修改成事后数据。本轮早先基于采样作出的“无 OOM”进度判断已经更正。保护阈值的 15 秒持续条件及容器停止延迟对这一快速增长场景不足；后续资源保护需要提前触发并覆盖清理窗口，不能把本次资源使用称为稳定或通过。

可确认：延长超时未在保护范围内恢复；LaTeXML 后处理持续计算并增长内存。未确认：具体函数/循环、是否正在构建大型参考文献、剩余完成时间。没有再次延长、改内存上限、缩减 bibliography 或替换 PDF 文本。原 13 个 table/table* 和 13 个 tabular 源结构完整保留，但没有 HTML 可供表头、行名、数值验收。

## 原版补丁行为与工程记录

实时 Docker stdout 显示 1171.patch 中仓库 `MANIFEST` 文件在安装目录不存在，清单 hunk 被跳过；NeurIPS、Post.pm、MakeBibliography.pm，以及后续 URL/ICML 代码补丁执行。没有新增补丁，也没有修复这个原版安装目录差异。原 1905 日志已成功加载 NeurIPS binding，不是遗漏 NeurIPS 补丁。

只读审计曾产生一份 `guess_main.cpython-310.pyc`；按创建时间/路径核实后保留诊断副本并精确移除，后续禁写字节码，源码文本未改变。初次独立核验误用本地汇总字段 rows，而远端实际字段为 papers，已仅修复审计脚本并重做只读检查；该工程修正没有重跑转换。初次大段 SSH 输出读取不完整，改用 SFTP 读取已保存的同一审计文件并校验，没有重复镜像转换。

## 完整性

本地冻结目录 {len(before)} 文件、远端冻结目录 {len(rb['frozen_formal'])} 文件的前后内容及大小相同。37 篇成功论文的 {rv['original_artifacts_checked']} 个产物按原 manifest 全部匹配；{len(rv['protected_assets'])} 个源码、模型等既有资产匹配。两篇原失败日志均保留，所有输入归档和解压文件匹配。没有模型抽取、GPT/API 调用或阶段 3 运行。
'''
 (R/'failure_diagnosis.md').write_text(diagnosis,encoding='utf-8')
 summary=f'''# AxCell 阶段 2 定点恢复总结

**结论：诊断和受控恢复尝试已完成，两篇均未恢复。正式解析结果仍为 37 成功 / 2 失败，恢复成功 0 篇。**

| 论文 ID | 原始失败原因 | 根因是否确定 | 本轮恢复尝试 | 是否恢复 | 处理差异 | 输出路径 |
|---|---|---|---:|---|---|---|
| 1905.03197.pdf | LaTeXML 101 errors / fatal | 首个致命依赖链已确定：tikzmark → expl3 原语不兼容 | 0 | 否，兼容方案未实施 | 无修改，仅诊断 | `diagnosis/1905.03197.pdf/` |
| 2203.16804.pdf | 原版 300 秒超时 | 已定位后处理 CPU/内存增长，具体触发点未确定 | 1 | 否，保护停止期间容器 OOM | 仅转换超时 300→600；新增只读观测 | `remote_snapshot/attempt_2203_timeout600/` |

没有把 HTML 存在当作成功：两篇目前连可验证的 HTML 都没有，因此解析文本/表格数量均为 **N/A**，不能声称表格完整，也不能用源码表格计数冒充解析数量。原始 TeX 未修改。1905 的源码静态标记为 10 个 table/table*、14 个 tabular；2203 为 13、13，仅用于将来内容核验。

| 2203 诊断指标 | 实测 |
|---|---:|
| 总耗时（含清理） | {finished['seconds']:.2f} 秒 |
| 最后采样时间 | {samples[-1]['elapsed_seconds']:.2f} 秒 |
| 容器采样峰值（含缓存） | {peak/2**30:.3f} GiB |
| 内核确认的容器内存占用 | 20.000 GiB，达到限制 |
| Perl 进程采样 RSS 峰值 | {perl/2**30:.3f} GiB |
| 包装进程树采样 RSS 峰值（不含容器） | {status['peak_sampled_owned_process_group_rss_bytes']/2**30:.3f} GiB |
| 宿主可用内存最低值 | {status['min_ecs_available_bytes']/2**30:.3f} GiB |
| 容器 OOM / swap 增长 | 1 次 / 0 |
| 原因 | 先触发 TASK_CONTAINER_NEAR_MEMORY_LIMIT，清理期间仍发生 MEMCG OOM |
| 外层退出码 / 包装子进程退出码 | 125 / -15 |

达到 95% 的 20 GiB 容器上限持续 15 秒后开始清理，但停止延迟期间内存继续增长，内核在 17:33:38 杀死容器内 Perl。未等待满 600 秒，更未提高到 900 秒。容器与本任务进程现已全部退出。此前“无 OOM”的阶段性判断只覆盖最后采样前，已由 `oom_audit.json` 的内核证据更正。此资源保护未完全避免容器 OOM，不能宣称资源运行稳定。恢复后磁盘剩余约 {rv['disk_free_bytes']/2**30:.2f} GiB。

`1905_compatibility_proposal.md` 是未实施的诊断提案；600 秒运行属于补充诊断，不属于原 300 秒配置。没有新的原版解析成功结果。

完整性核验通过：本地正式目录 {len(before)} 文件、远端 {len(rb['frozen_formal'])} 文件前后不变；37 篇 / {rv['original_artifacts_checked']} 个解析产物与原 manifest 相符；{len(rv['protected_assets'])} 个原有源码和模型等资产相符；两篇失败记录未覆盖。复用结果仍不是已确认的作者原 36 篇范围。

输出保存在本目录。远端使用 `{REMOTE}/`；原因是 `/data` 不存在，实际持久挂载为 ext4 系统盘 `/dev/nvme0n1p3`。核心交付：`failure_diagnosis.md`、`recovery_attempts.csv`、`recovery_manifest.json`、`recovery_verification.json`、本总结。资源与日志见 `recovery_resource_summary.json`、`remote_snapshot/`。

**阶段 3：尚未启动。** 既有 37 篇经原阶段 2 解析并再次通过完整性核验，可作为待验收的输入；两篇失败不能纳入成功解析清单。等待用户对“37 篇成功、2 篇保留失败”的阶段 2 最终范围确认，或另行批准具体兼容诊断后再推进。没有模型抽取和付费 API 调用。
'''
 (R/'recovery_summary.md').write_text(summary,encoding='utf-8')
 save('artifact_manifest.json',{str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(R.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json'})
 print(json.dumps({'status':verification['status'],'formal_success':37,'recovered':0,'attempts':1,'container_peak_GiB':peak/2**30,'local_formal_unchanged':True,'remote_formal_unchanged':True,'original_artifacts':rv['original_artifacts_checked'],'reports':5}))
if __name__=='__main__':main()
