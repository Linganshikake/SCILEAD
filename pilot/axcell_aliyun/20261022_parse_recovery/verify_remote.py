"""Fresh read-only integrity and output verification after the bounded attempt."""
import hashlib,json,subprocess,shutil,datetime
from pathlib import Path
ROOT=Path('/root/scilead/axcell')
F=ROOT/'runs/20261022_formal/stage2'
R=ROOT/'runs/20261022_parse_recovery'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 attempt=R/'attempt_2203_timeout600';assert (attempt/'attempt_finished.json').exists()
 manifest=json.loads((F/'parse_manifest.json').read_text());rows=manifest['papers'] if isinstance(manifest,dict) else manifest
 checked=[];paper_ids=[]
 for row in rows:
  if row['status']!='PARSE_COMPLETE':continue
  paper_ids.append(row['paper_id']);d=json.loads((F/'parse_logs'/row['paper_id']/'parser_result.json').read_text())
  for a in d['artifacts']:
   p=Path(a['path']);checked.append({'paper_id':row['paper_id'],'path':str(p),'bytes':p.stat().st_size if p.exists() else None,'sha256':sha(p) if p.exists() else None,'match':p.is_file() and p.stat().st_size==a['bytes'] and sha(p)==a['sha256']})
 assets=json.loads((F/'configuration.json').read_text())['expected_assets'];ac=[]
 for a in assets:
  p=ROOT/a['path'];ac.append({'path':str(p),'sha256':sha(p),'match':sha(p)==a['expected_sha256']})
 candidate={}
 for pid,version in [('1905.03197.pdf','1905.03197v3'),('2203.16804.pdf','2203.16804v1')]:
  p=attempt/'parsed/htmls'/version/'index.html';papers=attempt/'parsed/papers'/version
  candidate[pid]={'html_exists':p.is_file(),'html_bytes':p.stat().st_size if p.is_file() else 0,'html_sha256':sha(p) if p.is_file() else None,'parsed_directory_exists':papers.is_dir(),'content_validation':'PENDING_IF_PRESENT' if p.is_file() else 'NOT_POSSIBLE_NO_HTML','original_failed_html_exists':(F/'parsed/htmls'/version).exists()}
 output={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_success_papers':len(paper_ids),'paper_ids':paper_ids,'original_artifacts_checked':len(checked),'original_artifacts_all_unchanged':all(x['match'] for x in checked),'original_artifacts':checked,'protected_assets':ac,'protected_assets_all_match':all(x['match'] for x in ac),'recovery_candidates':candidate,'remaining_containers':subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines(),'disk_free_bytes':shutil.disk_usage(ROOT).free,'memory':Path('/proc/meminfo').read_text(),'recovery_files':{str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(R.rglob('*')) if p.is_file()},'image':subprocess.check_output(['docker','image','inspect','arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6','--format','{{.Id}}'],text=True).strip()}
 print(json.dumps(output))
if __name__=='__main__':main()
