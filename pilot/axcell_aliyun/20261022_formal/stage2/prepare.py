"""Freeze authorized inputs and copy the validated monitor into the new stage."""
from pathlib import Path
import csv, json
from policy import sha
P=Path(__file__).resolve().parent;F=P.parent
OLD=F.parent/'20261022_single_paper'
assert not (P/'queue.json').exists()
rows=list(csv.DictReader((F/'input_manifest.csv').open(encoding='utf-8-sig')))
expected=json.loads((F/'experiment_manifest.json').read_text(encoding='utf-8'))
assert sha(F/'input_manifest.csv')==expected['input_manifest']['sha256']
queue=[]
for row in rows:
    if row['input_eligible']!='True':continue
    p=Path(row['tex_path']);assert sha(p)==row['sha256'] and p.stat().st_size==int(row['bytes'])
    reused=row['paper_id']=='1511.08308.pdf'
    queue.append({'paper_id':row['paper_id'],'tex_version':row['tex_version'],'sha256':row['sha256'],
      'bytes':int(row['bytes']),'local_source':str(p),'remote_source':('/root/scilead/axcell/data/sources/' if reused else '/root/scilead/axcell/runs/20261022_formal/stage2/parsed/sources/')+row['tex_version'],
      'reuse_original_single':reused,'gold_tdmr_count':int(row['gold_tdmr_count']),'author36_membership':'UNVERIFIED'})
assert len(queue)==39 and sum(r['gold_tdmr_count'] for r in queue)==283
(P/'queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8')
text=(OLD/'monitor.py').read_text(encoding='utf-8-sig')
text=text.replace('import argparse,datetime,json,os,resource,signal,subprocess,time','import argparse,datetime,json,os,resource,signal,subprocess,time,shutil\nfrom policy import disk_guard')
text=text.replace('axcell-single-20261022','axcell-formal-parse-20261022')
text=text.replace("ap.add_argument('--stage',required=True);","ap.add_argument('--run',required=True);ap.add_argument('--stage',required=True);")
text=text.replace("run=Path('/root/scilead/axcell/runs/20261022_single_paper');run.mkdir(exist_ok=True)","run=Path(a.run).resolve();assert run.is_relative_to(Path('/root/scilead/axcell/runs/20261022_formal/stage2'));run.mkdir(parents=True,exist_ok=True)")
text=text.replace("s={'elapsed_seconds':tick-start,", "s={'disk_free_bytes':shutil.disk_usage(run).free,'elapsed_seconds':tick-start,")
text=text.replace("if stop.exists():reason='TASK_STOP_REQUEST'", "if disk_guard(s['disk_free_bytes']):reason='DISK_RESERVE'\n        if stop.exists():reason='TASK_STOP_REQUEST'")
(P/'monitor.py').write_text(text,encoding='utf-8')
config={'stage':2,'user_authorization':'可进入阶段2','workers':1,'original_input_manifest_sha256':sha(F/'input_manifest.csv'),
 'input_queue_sha256':sha(P/'queue.json'),'axcell_commit':expected['axcell_commit'],
 'image':expected['docker_images'][0],'models_not_loaded':True,'ES_not_started':True,'no_API':True,
 'start_min_ram_gib':6,'disk_reserve_gib':20,'stop_low_ram_gib':2,'sustained_seconds':15,
 'container_memory_gib':20,'container_cpus':6,'network_disabled':True,'threads':6,
 'per_paper_timeout_seconds':600,'no_automatic_retry':True,'expected_assets':json.loads((P/'remote_before.json').read_text())['original_assets'],
 'scripts':{n:sha(P/n) for n in ['parse_one.py','policy.py','monitor.py','batch_parse.py']}}
config['configuration_sha256']=__import__('hashlib').sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
(P/'configuration.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'papers':39,'new_inputs_to_transfer':38,'new_tex_bytes':sum(r['bytes'] for r in queue if not r['reuse_original_single']),'gold':283,'no_batch_launched_yet':True}))
