"""Copy only this new P4 report bundle; never overwrite an existing different file."""
from pathlib import Path
import hashlib,json,shutil
from datetime import datetime,timezone
SRC=Path(__file__).resolve().parent
BASE=Path(r'E:\SCILEAD\axcell\reports').resolve()
DST=(BASE/'20261022_stage4_preparation').resolve()
assert DST.parent==BASE and SRC.name==DST.name
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
previous=json.loads((DST/'sync_verification.json').read_text(encoding='utf-8')) if (DST/'sync_verification.json').exists() else None
previous_hashes={x['relative_path']:x['sha256'] for x in previous['files']} if previous else {}
files=[];updated_drafts=[]
for p in sorted(SRC.rglob('*')):
    if not p.is_file() or p.name=='sync_verification.json':continue
    assert p.suffix.lower() in ('.py','.md','.json','.csv','.zip') and not p.is_symlink()
    rel=p.relative_to(SRC);target=(DST/rel).resolve();assert target.is_relative_to(DST)
    if target.exists():
        if sha(target)!=sha(p):
            assert previous and previous['source']==str(SRC) and previous['destination']==str(DST)
            assert sha(target)==previous_hashes.get(rel.as_posix()),f'Untracked or externally changed file cannot be overwritten: {target}'
            assert json.loads((SRC/'verification.json').read_text(encoding='utf-8'))['status']=='P4_PREPARED_AWAITING_EXPLICIT_APPROVAL'
            shutil.copy2(p,target);updated_drafts.append(rel.as_posix())
    else:
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    a,b=sha(p),sha(target);assert a==b
    files.append({'relative_path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':a,'match':True})
record={'created_utc':datetime.now(timezone.utc).isoformat(),'source':str(SRC),'destination':str(DST),'file_count':len(files),'bytes':sum(x['bytes'] for x in files),'all_match':True,'files':files,'excluded_self':'sync_verification.json copied identically to both roots after checks','preexisting_experiment_files_overwritten':False,'models_or_credentials_copied':False,'updated_own_unapproved_preparation_drafts':updated_drafts}
text=json.dumps(record,ensure_ascii=False,indent=2)
(SRC/'sync_verification.json').write_text(text,encoding='utf-8');(DST/'sync_verification.json').write_text(text,encoding='utf-8')
assert sha(SRC/'sync_verification.json')==sha(DST/'sync_verification.json')
print(json.dumps({k:v for k,v in record.items() if k!='files'},ensure_ascii=True))
