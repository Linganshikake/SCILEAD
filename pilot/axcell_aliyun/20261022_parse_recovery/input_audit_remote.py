import hashlib,importlib.util,json,tarfile,re
from pathlib import Path
ROOT=Path('/root/scilead/axcell')
F=ROOT/'runs/20261022_formal/stage2'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
spec=importlib.util.spec_from_file_location('original_guess',ROOT/'source/axcell/axcell/scripts/guess_main.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
queue=json.loads((F/'queue.json').read_text());result={}
for pid in ['1905.03197.pdf','2203.16804.pdf']:
 row=next(r for r in queue if r['paper_id']==pid)
 path=Path(row['remote_source']);unpacked=F/'parsed/unpacked_sources'/row['tex_version'];members=[]
 with tarfile.open(path) as t:
  for member in t.getmembers():
   if not member.isfile():continue
   h=hashlib.sha256();f=t.extractfile(member)
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
   p=unpacked/member.name
   members.append({'path':member.name,'archive_sha256':h.hexdigest(),'unpacked_sha256':sha(p) if p.is_file() else None,'bytes':member.size,'match':p.is_file() and sha(p)==h.hexdigest()})
  if pid=='2203.16804.pdf':
   text=t.extractfile('anthology.bib').read().decode('utf-8',errors='replace');bib_count=len(re.findall(r'^\s*@\w+\s*\{',text,re.M))
  else:bib_count=None
 result[pid]={'archive':str(path),'sha256':sha(path),'expected_sha256':row['sha256'],'all_members_preserved':all(x['match'] for x in members),'members':members,'main':str(m.guess_main(unpacked)),'main_priorities':{p.name:m.calc_priority(p) for p in unpacked.glob('*.tex')},'anthology_bib_entry_markers':bib_count}
assets=json.loads((F/'configuration.json').read_text())['expected_assets']
result['protected_assets']=[{'path':x['path'],'match':sha(ROOT/x['path'])==x['expected_sha256'],'sha256':sha(ROOT/x['path'])} for x in assets]
print(json.dumps(result))
