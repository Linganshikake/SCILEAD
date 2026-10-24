"""Transfer only frozen AxCell source, verified models, one TeX and isolated bootstrap."""
import hashlib,json,tarfile,time
from pathlib import Path,PurePosixPath
from remote import connect
import paramiko
OUT=Path(__file__).resolve().parent
LOCAL=Path(r'E:\SCILEAD\axcell')
REMOTE='/root/scilead/axcell'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 source=json.loads((LOCAL/'manifests/axcell_source_manifest.json').read_text())
 models=json.loads((LOCAL/'runs/20261021_235603/model_manifest.json').read_text())
 policy=json.loads((LOCAL/'active_execution_policy.json').read_text())
 selected=policy['selected_paper'];assert selected['paper_id']=='1511.08308.pdf'
 entries=[]
 for e in source['files']:
  src=LOCAL/'source/axcell'/e['path'];assert sha(src)==e['sha256']
  entries.append((src,'source/axcell/'+e['path'],e['sha256']))
 tex=Path(selected['tex_path']);assert sha(tex)==selected['tex_sha256']
 entries.append((tex,'data/sources/1511.08308v5',selected['tex_sha256']))
 bootstrap=LOCAL/'envs/bootstrap/micromamba';digest=sha(bootstrap)
 assert digest=='366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3'
 entries.append((bootstrap,'envs/bootstrap/micromamba',digest))
 archive=Path(models['path']);assert archive.stat().st_size==models['bytes'] and sha(archive)==models['sha256']
 for e in models['files']:assert sha(Path(e['path']))==e['sha256']
 manifest={'axcell_revision':source['revision'],'selected_paper':selected,'model_archive':{'relative':'cache/models.tar.xz','bytes':archive.stat().st_size,'sha256':models['sha256']},'model_files':[{'relative':'models/'+Path(e['path']).name,'bytes':e['bytes'],'sha256':e['sha256']} for e in models['files']],'files':[{'relative':rel,'bytes':src.stat().st_size,'sha256':h} for src,rel,h in entries],'no_credentials_in_transfer':True,'max_papers':1,'paid_api_authorized':False,'author_36_subset_membership':'UNVERIFIED'}
 mf=OUT/'transfer_manifest.json';mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 bundle=OUT/'source_bootstrap_one_paper.tar.gz'
 with tarfile.open(bundle,'w:gz') as tf:
  for src,rel,h in entries:tf.add(src,arcname=rel,recursive=False)
  tf.add(mf,arcname='manifests/transfer_manifest.json',recursive=False)
 t=connect();sftp=paramiko.SFTPClient.from_transport(t)
 try:
  for p in ['/root/scilead',REMOTE,REMOTE+'/cache',REMOTE+'/runs',REMOTE+'/runs/20261022_single_paper',REMOTE+'/scripts']:
   try:sftp.stat(p)
   except FileNotFoundError:sftp.mkdir(p)
  uploads=[(bundle,REMOTE+'/cache/source_bootstrap_one_paper.tar.gz'),(archive,REMOTE+'/cache/models.tar.xz')]
  for src,dest in uploads:
   try:sftp.stat(dest);raise RuntimeError('Destination exists; verify before reuse')
   except FileNotFoundError:pass
   tick=[time.monotonic()]
   def progress(sent,total):
    if time.monotonic()-tick[0]>=20 or sent==total:
     print(json.dumps({'file':src.name,'bytes_sent':sent,'bytes_total':total}),flush=True);tick[0]=time.monotonic()
   sftp.put(str(src),dest+'.part',callback=progress);sftp.rename(dest+'.part',dest)
  print(json.dumps({'status':'TRANSFERRED_PENDING_REMOTE_HASH','files':len(entries),'model_files':len(models['files']),'bundle_sha256':sha(bundle),'bundle_bytes':bundle.stat().st_size}),flush=True)
 finally:sftp.close();t.close()
if __name__=='__main__':main()
