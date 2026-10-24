"""Read-only source-container, Gold-metadata and frozen-asset audit for P0."""
from pathlib import Path,PurePosixPath
import csv,gzip,hashlib,json,subprocess,tarfile
P=Path(__file__).resolve().parent;ROOT=Path(r'E:\SCILEAD\axcell')
OLD=P.parent/'20261022_single_paper';HISTORY=Path(r'D:\C++\SCILEAD\pilot\axcell_local\20261021_235603')
REPO=Path(r'D:\C++\SCILEAD\emnlp2024-leaderboard-generation')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def git(*args):return subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),*args])

goldpath=ROOT/'data/gold/tdm_annotations.json';lbpath=ROOT/'data/gold/leaderboards.json'
gold=read(goldpath);lbs=read(lbpath)
assert len(gold)==43 and sum(len(x['TDMs']) for x in gold.values())==295
assert sha(goldpath)==read(Path(r'D:\C++\SCILEAD\pilot\full43_uncapped\manifest.json'))['gold_sha256']
inventory=list(csv.DictReader((HISTORY/'input_inventory.csv').open(encoding='utf-8-sig',newline='')))
assert len(inventory)==43 and {x['paper_id'] for x in inventory}==set(gold)
downloads=read(HISTORY/'tex_download_status.json')
sources={x['paper_id']:x for x in read(HISTORY/'additional_source_mapping.json')}
rows=[];archives=[];protected=[]
for original in inventory:
 paper=original['paper_id'];name=original['tex_path'];fp=Path(name) if name else None
 direct='arxiv.org/pdf/' in gold[paper]['PaperURL']
 mapping='GOLD_ARXIV_ID' if direct else ('BIBLIOGRAPHIC_TITLE_AUTHOR_MATCH' if original['arxiv_id'] and (sources.get(paper,{}).get('status')=='BIBLIOGRAPHIC_MATCH' or paper=='K19-1036.pdf') else 'UNVERIFIED')
 row={'paper_id':paper,'original_paper_identifier':Path(paper).stem,'paper_url':gold[paper]['PaperURL'],'gold_tdmr_count':len(gold[paper]['TDMs']),'arxiv_id':original['arxiv_id'],'tex_path':name,'tex_version':original['source_version'],'tex_url':original['tex_url'],'sha256':sha(fp) if fp and fp.is_file() else '', 'expected_sha256':original['tex_sha256'],'bytes':fp.stat().st_size if fp and fp.is_file() else 0,'in_scilead_43':True,'has_gold':True,'author_36_membership':'UNVERIFIED','source_mapping':mapping,'hash_match':False,'container_integrity':'MISSING','tex_member_count':0,'compile_completeness':'NOT_TESTED_P0','input_eligible':False,'formal_evaluation_allowed':False,'proposed_evaluation_scope':'NONE','remote_status':'PENDING_TRANSFER_AFTER_APPROVAL','notes':original['missing_reason']}
 if fp and fp.is_file():
  row['hash_match']=row['sha256']==row['expected_sha256'];d=downloads[original['arxiv_id']]
  assert row['hash_match'] and d['sha256']==row['sha256'] and fp.stat().st_size==d['bytes']
  protected.append({'path':str(fp),'sha256':row['sha256'],'bytes':fp.stat().st_size})
  check={'paper_id':paper,'kind':d['archive_kind'],'members':[],'invalid_paths':[],'bytes_read':0,'crc_checked':False}
  try:
   with fp.open('rb') as f:magic=f.read(2)
   if magic==b'\x1f\x8b':
    with gzip.open(fp,'rb') as f:
     while True:
      b=f.read(1024*1024)
      if not b:break
      check['bytes_read']+=len(b)
      if check['bytes_read']>512*1024*1024:raise RuntimeError('Archive expands beyond P0 read limit')
    check['crc_checked']=True
   if tarfile.is_tarfile(fp):
    with tarfile.open(fp,'r:*') as tf:
     for m in tf:
      path=PurePosixPath(m.name)
      if path.is_absolute() or '..' in path.parts or '\\' in m.name or ':' in m.name:check['invalid_paths'].append(m.name)
      if m.issym() or m.islnk() or not (m.isfile() or m.isdir()):check['invalid_paths'].append(m.name+':nonregular')
      if m.isfile():
       count=0
       with tf.extractfile(m) as f:
        for b in iter(lambda:f.read(1024*1024),b''):count+=len(b)
       assert count==m.size
       check['members'].append({'name':m.name,'bytes':m.size})
    tex=[x['name'] for x in check['members'] if x['name'].lower().endswith('.tex')]
   else:
    op=gzip.open if magic==b'\x1f\x8b' else open
    with op(fp,'rb') as f:content=f.read(16*1024*1024)
    assert b'\\document' in content or b'\\input' in content,'No recognizable TeX marker'
    tex=[fp.name]
   assert tex and not check['invalid_paths']
   if d['archive_kind']=='tar':assert set(tex)==set(d['tex_members'])
   row.update(container_integrity='READABLE_SIZE_HASH_AND_GZIP_CRC' if check['crc_checked'] else 'READABLE_SIZE_AND_HASH',tex_member_count=len(tex),input_eligible=mapping!='UNVERIFIED',proposed_evaluation_scope='LOCAL_AVAILABLE_TEX_PENDING_P0',notes='Author-used TeX version and author-36 membership unknown; readable archive does not prove successful compilation.')
   if paper=='1511.08308.pdf':row['remote_status']='EXISTING_VERIFIED_SINGLE_PAPER'
   check['passed']=True
  except Exception as e:check.update(passed=False,error_type=type(e).__name__,error=str(e));row.update(container_integrity='FAILED',notes='Source container failed integrity audit; do not process automatically.')
  archives.append(check)
 row['file_integrity_verified']=bool(row['hash_match'] and row['container_integrity'].startswith('READABLE'))
 row['author_used_tex_version']='UNVERIFIED'
 if not name:row['remote_status']='MISSING_SOURCE_NOT_QUEUED'
 rows.append(row)
assert len({r['paper_id'] for r in rows})==43
available=[r for r in rows if r['input_eligible']]
assert len(available)==39
assert len({r['tex_path'] for r in available})==39
with (P/'input_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('source_container_audit.json',archives)

sm=read(ROOT/'manifests/axcell_source_manifest.json');models=read(HISTORY/'model_manifest.json')
checks=[]
for e in sm['files']:
 fp=ROOT/'source/axcell'/e['path'];h=sha(fp);checks.append({'kind':'axcell_source','path':str(fp),'sha256':h,'match':h==e['sha256']});protected.append({'path':str(fp),'sha256':h,'bytes':fp.stat().st_size})
for e in models['files']:
 fp=Path(e['path']);h=sha(fp);checks.append({'kind':'model','path':str(fp),'sha256':h,'match':h==e['sha256']});protected.append({'path':str(fp),'sha256':h,'bytes':fp.stat().st_size})
for fp in [ROOT/'models/taxonomy.json',ROOT/'models/metrics.json',ROOT/'models/abbreviations.json']:read(fp)
assert all(x['match'] for x in checks)
assert git('rev-parse','HEAD').decode().strip()=='8bf74b0a830feb7035c6166dce3394dc344ae532'
code_checks=[]
for line in git('ls-tree','-r','HEAD').decode().splitlines():
 meta,path=line.split('\t');fp=REPO/path;blob=git('show','HEAD:'+path)
 actual=fp.read_bytes();matches=actual==blob or actual.replace(b'\r\n',b'\n')==blob
 code_checks.append({'path':path,'working_sha256':sha(fp),'git_blob':meta.split()[2],'matches_git_allowing_checkout_crlf':matches})
 protected.append({'path':str(fp),'sha256':sha(fp),'bytes':fp.stat().st_size})
assert all(x['matches_git_allowing_checkout_crlf'] for x in code_checks)
original_gold=Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data')
goldchecks=[]
for name in ['tdm_annotations.json','leaderboards.json','README.md']:
 a=ROOT/'data/gold'/name;b=original_gold/name
 goldchecks.append({'name':name,'working_sha256':sha(a),'original_sha256':sha(b),'match':sha(a)==sha(b)})
 for fp in [a,b]:protected.append({'path':str(fp),'sha256':sha(fp),'bytes':fp.stat().st_size})
assert all(x['match'] for x in goldchecks)
single_checks=[]
for e in read(OLD/'remote_reports/delivery_hashes.json'):
 fp=OLD/'remote_reports'/e['path'];h=sha(fp);single_checks.append({'path':str(fp),'sha256':h,'match':h==e['sha256']});protected.append({'path':str(fp),'sha256':h,'bytes':fp.stat().st_size})
assert all(x['match'] for x in single_checks)
for name in ['single_paper_resource_report.md','manifest.json','final_config.json','output_inspection.json','resource_summary.json','verification.json']:
 fp=OLD/name;protected.append({'path':str(fp),'sha256':sha(fp),'bytes':fp.stat().st_size})
inspection=read(OLD/'output_inspection.json');assert not inspection['uses_gold_answers']
save('single_paper_error_baseline.json',inspection)
ids={r['paper_id'] for r in available}
llama_gold=read(Path(r'D:\C++\SCILEAD\pilot\autodl_llama3\20261021_format_followup\format_v2\evaluation\gold_subset.json'))
assert len(llama_gold)==42 and set(gold)-set(llama_gold)=={'1912.08777.pdf'}
common=ids.intersection(llama_gold)
comparison={'local_available_ids':sorted(ids),'llama3_42_common_ids':sorted(common),'llama3_common_gold_count':sum(len(gold[x]['TDMs']) for x in common),'author_36_confirmed_members':[],'author_36_unresolved_ids':list(gold),'author_used_tex_version_verified':False}
summary={'gold_papers':len(gold),'gold_tdmrs':sum(len(x['TDMs']) for x in gold.values()),'gold_leaderboards':len(lbs),'candidate_counts':{k:len({t[k] for v in gold.values() for t in v['TDMs']}) for k in ['Task','Dataset','Metric']},'input_ready_count':len(available),'input_ready_gold_tdmrs':sum(r['gold_tdmr_count'] for r in available),'missing':[r for r in rows if not r['input_eligible']],'total_tex_bytes':sum(r['bytes'] for r in available),'remote_transfer_pending_count':sum(r['remote_status']=='PENDING_TRANSFER_AFTER_APPROVAL' for r in available),'source_mapping_counts':dict(__import__('collections').Counter(r['source_mapping'] for r in available)),'source_container_passes':sum(x['passed'] for x in archives),'source_count':len(sm['files']),'models_verified':len(models['files']),'single_run_files_verified':len(single_checks),'local_gold_hashes':goldchecks,'leaderboard_scope_preview':{'original_gold_leaderboards':len(lbs),'with_any_available_paper':sum(bool(set(lb['Leaderboard'])&ids) for lb in lbs),'entries_with_available_papers':sum(len(set(lb['Leaderboard'])&ids) for lb in lbs),'note':'Preview only; final denominator and nonempty/scope rules require staged approval. No evaluation run.'},'comparison_scope':comparison}
save('input_audit_summary.json',summary);save('local_asset_checks.json',checks);save('scilead_code_checks.json',code_checks);save('protected_inputs_before.json',protected)
print(json.dumps({k:v for k,v in summary.items() if k not in ['missing','local_gold_hashes','comparison_scope']},ensure_ascii=True))
print('MISSING',json.dumps([x['paper_id'] for x in summary['missing']]))
