"""Publish independent recovery reports, with round-trip file hashes."""
import hashlib,json,stat,sys
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R));import client
REMOTE='/root/scilead/axcell/runs/20261022_parse_recovery'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 files=[p for p in R.iterdir() if p.is_file() and p.suffix in ['.md','.json','.csv','.py','.log'] and p.name not in ['artifact_manifest.json','report_sync_verification.json']]
 files += [p for p in (R/'diagnosis').rglob('*') if p.is_file() and 'original_input' not in p.parts]
 t=client.remote.connect();records=[]
 try:
  s=client.paramiko.SFTPClient.from_transport(t)
  def mkdir(path):
   try:s.stat(path);return
   except FileNotFoundError:pass
   mkdir(path.rsplit('/',1)[0]);s.mkdir(path)
  for p in files:
   rel=p.relative_to(R).as_posix();dest=REMOTE+'/'+rel;mkdir(dest.rsplit('/',1)[0]);b=p.read_bytes()
   try:
    with s.open(dest,'rb') as f:existing=f.read()
    if sha(existing)!=sha(b):
     # Preserve raw remote formatting/content; deliver the local report copy separately.
     dest=REMOTE+'/delivery/'+rel;mkdir(dest.rsplit('/',1)[0])
     try:
      with s.open(dest,'rb') as f:assert sha(f.read())==sha(b),'Differing delivered report already exists'
     except FileNotFoundError:s.put(str(p),dest)
   except FileNotFoundError:s.put(str(p),dest)
   with s.open(dest,'rb') as f:actual=sha(f.read())
   assert actual==sha(b)
   records.append({'relative_path':rel,'remote_path':dest,'bytes':len(b),'sha256':actual,'roundtrip_match':True})
  # Original archives remain on the server. Copy only these two, into the independent diagnosis tree.
  code=r'''
import hashlib,json,shutil
from pathlib import Path
R=Path('/root/scilead/axcell/runs/20261022_parse_recovery')
rows=json.loads((R/'selected_inputs.json').read_text());out=[]
for row in rows:
 p=Path(row['remote_source']);dest=R/'diagnosis'/row['paper_id']/'original_input'/row['tex_version'];dest.parent.mkdir(exist_ok=True)
 assert p.resolve().is_relative_to(Path('/root/scilead/axcell/runs/20261022_formal/stage2/parsed/sources'))
 if not dest.exists():shutil.copy2(p,dest)
 h=hashlib.sha256(dest.read_bytes()).hexdigest();assert h==row['sha256'];out.append({'paper_id':row['paper_id'],'path':str(dest),'sha256':h})
print(json.dumps(out))
'''
  exit_code,out,err=client.execute(t,'PYTHONDONTWRITEBYTECODE=1 python3 -',code.encode(),timeout=30)
  assert exit_code==0,err.decode()
  result={'remote_directory':REMOTE,'files':records,'input_archives':json.loads(out),'all_roundtrip_hashes_match':True}
  p=R/'report_sync_verification.json';p.write_text(json.dumps(result,indent=2),encoding='utf-8');s.put(str(p),REMOTE+'/report_sync_verification.json')
  print(json.dumps({'uploaded_or_identical':len(records),'hashes_match':True,'remote_directory':REMOTE}))
 finally:t.close()
if __name__=='__main__':main()
