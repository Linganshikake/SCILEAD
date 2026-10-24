"""Pull only task reports and selected parsed artifacts; never download environments/models."""
from pathlib import Path
import json,stat,hashlib
LOCAL=Path(__file__).resolve().parent
import remote,paramiko
ROOT='/root/scilead/axcell'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def main():
 t=remote.connect();s=paramiko.SFTPClient.from_transport(t);rows=[]
 try:
  for source,target in [(ROOT+'/runs/20261022_single_paper',LOCAL/'remote_reports'),(ROOT+'/data/papers/1511.08308v5',LOCAL/'parsed_paper'),(ROOT+'/data/htmls/1511.08308v5',LOCAL/'parsed_html')]:
   try:s.stat(source)
   except FileNotFoundError:continue
   queue=[(source,target)]
   while queue:
    folder,out=queue.pop()
    for entry in s.listdir_attr(folder):
     name=entry.filename
     if name in ['.','..'] or '/' in name or '\\' in name:raise RuntimeError('Invalid remote filename')
     src=folder+'/'+name;dst=out/name
     if stat.S_ISDIR(entry.st_mode):queue.append((src,dst));continue
     if not stat.S_ISREG(entry.st_mode) or entry.st_size>50*1024*1024:raise RuntimeError('Unexpected report artifact type or size')
     if name.endswith('.env'):raise RuntimeError('Credential file must never be synced')
     dst.parent.mkdir(parents=True,exist_ok=True)
     tmp=dst.with_name(dst.name+'.transfer');s.get(src,str(tmp));tmp.replace(dst)
     rows.append({'remote':src,'local_relative':str(dst.relative_to(LOCAL)),'bytes':dst.stat().st_size,'sha256':digest(dst)})
  (LOCAL/'report_sync_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
  print(json.dumps({'files_synced':len(rows),'bytes':sum(x['bytes'] for x in rows)}))
 finally:s.close();t.close()
if __name__=='__main__':main()
