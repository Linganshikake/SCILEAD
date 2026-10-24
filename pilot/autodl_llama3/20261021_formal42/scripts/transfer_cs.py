"""Copy already verified official CS weights, never fetch a new model or credentials."""
from pathlib import Path
import sys,json,hashlib,time,posixpath
R=Path(__file__).resolve().parents[1];P=Path(r'D:\C++\SCILEAD\pilot');sys.path.insert(0,str(P/'autodl_setup/20261021/scripts'))
from remote_client import connect,execute
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')
m=read(P/'full43_cs/model_manifest.json');cache=P.parent/'assets/hf_cache';rr='/root/autodl-tmp/scilead/runs/llama3/20261021_formal42';weightroot='/root/autodl-tmp/scilead/models/bilingual-embedding-large'
files=[]
for rel,digest in m['model_files_sha256'].items():files.append((Path(m['local_snapshot'])/rel,weightroot+'/'+rel.replace('\\','/'),digest))
code=cache/'models--dangvantuan--bilingual_impl/snapshots'/m['code_revision']
for rel,digest in m['code_files_sha256'].items():files.append((code/rel,rr+'/cache/hub/models--dangvantuan--bilingual_impl/snapshots/'+m['code_revision']+'/'+rel,digest))
probes={}
for line in (P/'full43_cs/normalization/mapping_audit.jsonl').read_text(encoding='utf-8').splitlines():
    x=json.loads(line)
    if not x['exact_match'] and x['field'] not in probes:probes[x['field']]=x
    if len(probes)==3:break
reference={'model':m,'candidate_labels':read(P/'full43_cs/candidate_labels.json')['labels'],'probes':list(probes.values()),'score_tolerance':1e-5}
save(R/'config/cs_reference.json',reference)
c=connect();sf=c.open_sftp();started=time.monotonic();records=[]
def mkdir(path):
    if path=='/root/autodl-tmp/scilead':return
    mkdir(posixpath.dirname(path))
    try:sf.stat(path)
    except FileNotFoundError:sf.mkdir(path)
try:
    for local,remote,digest in files:
        mkdir(posixpath.dirname(remote))
        with local.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest
        try:exists=sf.stat(remote).st_size==local.stat().st_size
        except FileNotFoundError:exists=False
        if not exists:
            tmp=remote+'.uploading';last=[0]
            def progress(done,total):
                if time.monotonic()-last[0]>30:
                    save(R/'cs_transfer_progress.json',{'file':local.name,'bytes':done,'total':total,'elapsed':time.monotonic()-started});print(json.dumps({'file':local.name,'percent':round(done/total*100,1)}),flush=True);last[0]=time.monotonic()
            sf.put(str(local),tmp,callback=progress,confirm=True);sf.rename(tmp,remote)
        records.append({'path':remote,'bytes':local.stat().st_size,'sha256':digest})
    for name,data in [('cs_reference.json',reference),('cs_model_transfer.json',records)]:
        target=rr+'/config/'+name
        with sf.open(target,'wb') as f:f.write(json.dumps(data,indent=2).encode())
    code='from pathlib import Path\nimport json,hashlib\nfiles='+repr(records)+'\nfor x in files:\n with Path(x["path"]).open("rb") as f:assert hashlib.file_digest(f,"sha256").hexdigest()==x["sha256"]\nprint(json.dumps({"status":"ALL_SHA256_MATCH","files":len(files)}))'
    # Server Python3.10 lacks hashlib.file_digest; chunked hash is equivalent.
    code=code.replace('hashlib.file_digest(f,"sha256").hexdigest()','(lambda h: ([h.update(b) for b in iter(lambda: f.read(1048576),b"")],h.hexdigest())[1])(hashlib.sha256())')
    v=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',code,timeout=180);assert v['exit_code']==0
    save(R/'cs_transfer_verified.json',{'files':records,'verification':json.loads(v['stdout']),'seconds':time.monotonic()-started,'source':'existing local pinned snapshot; no network model download'})
    print(json.dumps({'status':'TRANSFERRED_SHA256_VERIFIED','files':len(files),'seconds':time.monotonic()-started}))
finally:sf.close();c.close()
