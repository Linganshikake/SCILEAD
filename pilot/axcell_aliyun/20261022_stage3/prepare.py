import json,pathlib,hashlib,datetime,sys
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,d):(R/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
before=json.loads((R/'remote_before.json').read_text(encoding='utf-8'))
assert len(before['parsed_artifacts'])==643 and all(x['match'] for x in before['parsed_artifacts'])
assert len(before['assets'])==91 and all(x['match'] for x in before['assets'])
manifest=json.loads((R.parent/'20261022_formal/parse_manifest.json').read_text(encoding='utf-8'))
queue=manifest['rows'];assert len(queue)==39 and sum(x['status']=='PARSE_COMPLETE' for x in queue)==37
assert {x['paper_id'] for x in queue if x['status']=='FAILED'}=={'1905.03197.pdf','2203.16804.pdf'}
save('queue.json',queue)
if not (R/'local_frozen_before.json').exists():
 paths={}
 for folder in ['20261022_formal','20261022_parse_recovery','20261022_single_paper']:
  for p in (R.parent/folder).rglob('*'):
   if p.is_file():paths[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)}
 save('local_frozen_before.json',paths)
config={'name':'AxCell Extraction (stage3 only; GPT-4.1 Fully Normalization pending P3/P4)',
 'axcell_commit':'f4648d8fee1aa8482d007a38828da9dc06630f0e','scilead_commit':'8bf74b0a830feb7035c6166dce3394dc344ae532',
 'official_entrypoint':'ResultsExtractor(models)(paper,in_place=True)',
 'single_adapter_sha256':'074537f9041a8acff837c2a320c5f097c4b41e782a9d63bd3dd8ff36815ae27b',
 'thresholds':[0.8,0.85],'use_crf':False,'cpu':True,'serial':True,
 'es_policy':'Independent empty initial ES index per paper, same as verified single-paper setup; original paper_limit=30,corpus_limit=10 unchanged. Author corpus not established.',
 'es_image':'docker.elastic.co/elasticsearch/elasticsearch-oss@sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b',
 'worker_memory_hard_gib':18,'worker_memory_early_stop_gib':14,'es_memory_hard_gib':3,'es_memory_early_stop_gib':2.4,
 'start_mem_available_min_gib':6,'run_mem_available_stop_gib':4,'disk_reserve_gib':20,'sampling_seconds':2,'stop_grace_seconds':2,
 'wall_time_limit_seconds':1800,'no_progress_memory_growth':'growth >2GiB / approx90s AND no pipeline event >90s -> stop batch',
 'new_oom_stops_batch':True,'preexisting_kernel_oom_count':before['vmstat']['oom_kill'],
 'max_attempts_per_new_paper':1,'reused_paper':'1511.08308.pdf','new_extraction_count':36,'runnable_count':37,
 'excluded_parse_failed':['1905.03197.pdf','2203.16804.pdf'],'author36_membership':'UNVERIFIED',
 'api_calls_authorized':0,'normalization_authorized':False,'evaluation_authorized':False,
 'queue_sha256':sha(R/'queue.json'),'remote_before_sha256':sha(R/'remote_before.json'),
 'scripts':{p.name:sha(p) for p in [R/'controller.py',R/'worker.py',R/'policy.py',R/'test_policy.py']}}
save('configuration.json',config)
(R/'pip_freeze.txt').write_text(before['pip_freeze']['stdout'],encoding='utf-8')
print(json.dumps({'queue':len(queue),'runnable':37,'new':36,'local_protected_files':len(json.loads((R/'local_frozen_before.json').read_text(encoding='utf-8')))}))
