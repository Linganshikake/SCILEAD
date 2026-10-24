from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent;OLD=R.parent/'20261022_stage3'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(R/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
b=read(R/'remote_before.json')
assert not b['running_containers']['stdout'].strip() and b['loopback_9200_free']
assert b['parse_counts']=={'PARSE_COMPLETE':37,'FAILED':2}
assert all(x['match'] for x in b['assets']+b['parsed_artifacts']) and b['pip_check']['returncode']==0
c=read(OLD/'configuration.json');c.update(name='AxCell stage3 controlled resume; original extraction unchanged',new_extraction_count=34,
 reused_papers=['1911.10390.pdf','2001.04063.pdf','1511.08308.pdf'],authorized_retry='1912.08777.pdf',new_unstarted=33,
 prior_attempts_preserved=str(OLD),wall_time_limit_seconds=3600,no_progress_memory_growth='LOG_ONLY: sparse stage events and normal allocations do not stop work; absolute thresholds remain',
 cpu_accounting='cgroup cpu.stat usage_usec sampled',remote_before_sha256=sha(R/'remote_before.json'),
 scripts={p.name:sha(p) for p in [R/'controller.py',R/'worker.py',R/'policy.py',R/'test_policy.py']})
c.pop('reused_paper',None);save('configuration.json',c)
files={}
for folder in ['20261022_formal','20261022_parse_recovery','20261022_single_paper','20261022_stage3']:
 for p in (R.parent/folder).rglob('*'):
  if p.is_file():files[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)}
save('local_frozen_before.json',files)
samples=read(OLD/'remote_results/papers/1912.08777.pdf/all_resource_samples.json')
sys.path.insert(0,str(R));from policy import resource_stop
oldstop=[];newstop=[]
for i,s in enumerate(samples):
 if i>=45 and s['worker']-samples[i-45]['worker']>2*2**30 and s['elapsed']>115:oldstop.append(i)
 reason=resource_stop(s['available'],s['free'],s['worker'],s['es'],s['oom_kill'],1,s['elapsed'])
 if reason:newstop.append(reason)
assert oldstop and not newstop
save('trace_replay_test.json',{'old_policy_triggers':oldstop,'new_policy_triggers':newstop,'passed':True,'model_loads':0})
(R/'resume_protocol.md').write_text('''# Stage3受控恢复

用户已批准适当放宽保护并重试。只对上轮被误触发保护中止的1912.08777.pdf新增一次尝试，继续33篇未启动任务；3篇成功结果原样复用。原2篇解析失败不运行。旧stage3全部冻结，本轮独立目录20261022_stage3_resume。

根因假设：结构模型的内部执行阶段不频繁发管线事件，正常分配后的平台期被增长窗口误判。以历史采样重放验证：旧规则触发，新规则不触发；无模型成本。取消该启发式停批，新增CPU计数；保留14GiB模型提前停止/18GiB硬上限、ES2.4/3GiB、主机可用4GiB、磁盘20GiB与新增OOM停批。单篇墙钟由1800延长3600秒，仍有限。清理时只读取procfs/cgroup避免CLI阻塞监测，期间阈值异常写入持久停止标记。

原版ResultsExtractor、模型、taxonomy、abbreviations、阈值、单篇空初始ES与查询设置不变。不解析、不修改预测、不调用GPT、不标准化、不评价。即使结果为零或较差也不重跑。遇到真实资源停止条件保留结果后停批。完成后停P3。
''',encoding='utf-8')
print(json.dumps({'physical_available_gib':next(int(x.split()[1])*1024 for x in b['memory'].splitlines() if x.startswith('MemAvailable:'))/2**30,'disk_free_gib':b['disk']['free']/2**30,'reused':3,'new_attempts_authorized':34,'frozen_local_files':len(files),'trace_test':'passed'}))
