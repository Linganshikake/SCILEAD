"""Synchronize the completed new stage only; existing different files are protected."""
from pathlib import Path
import hashlib,json,shutil
from datetime import datetime,timezone
SRC=Path(__file__).resolve().parent;BASE=Path(r'E:\SCILEAD\axcell\reports').resolve();DST=(BASE/SRC.name).resolve()
assert SRC.name=='20261022_stage5' and DST.parent==BASE
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
assert json.loads((SRC/'verification.json').read_text(encoding='utf-8'))['status']=='P5_COMPLETE'
assert not (SRC/'execution.lock').exists()
files=[]
for p in sorted(SRC.rglob('*')):
    if not p.is_file() or p.name=='sync_verification.json':continue
    assert not p.is_symlink() and p.suffix in ('.json','.md','.csv','.py','.txt','.log')
    rel=p.relative_to(SRC);dest=(DST/rel).resolve();assert dest.is_relative_to(DST)
    if dest.exists():assert sha(dest)==sha(p),f'Existing different file will not be overwritten: {dest}'
    else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    h=sha(p);assert sha(dest)==h;files.append({'relative_path':rel.as_posix(),'sha256':h,'bytes':p.stat().st_size,'match':True})
verification={'utc':datetime.now(timezone.utc).isoformat(),'source':str(SRC),'destination':str(DST),'files':files,'file_count':len(files),'all_match':True,'total_bytes':sum(f['bytes'] for f in files),'old_experiments_overwritten':False,'credentials_copied':False}
data=json.dumps(verification,ensure_ascii=False,indent=2)
(SRC/'sync_verification.json').write_text(data,encoding='utf-8');(DST/'sync_verification.json').write_text(data,encoding='utf-8');assert sha(SRC/'sync_verification.json')==sha(DST/'sync_verification.json')
print(json.dumps({k:v for k,v in verification.items() if k!='files'},ensure_ascii=True))
