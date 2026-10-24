"""Retrieve completed isolated recovery artifacts; preserve frozen paths."""
import hashlib,json,stat,sys
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R));import client
REMOTE='/root/scilead/axcell/runs/20261022_parse_recovery'
def main():
 t=client.remote.connect()
 try:
  s=client.paramiko.SFTPClient.from_transport(t)
  s.stat(REMOTE+'/attempt_2203_timeout600/attempt_finished.json')
  out=R/'remote_snapshot';out.mkdir(exist_ok=True);records=[]
  def walk(path,rel=''):
   for a in sorted(s.listdir_attr(path),key=lambda x:x.filename):
    nextrel=(rel+'/'+a.filename).lstrip('/');dest=out/nextrel
    if stat.S_ISDIR(a.st_mode):dest.mkdir(exist_ok=True);walk(path+'/'+a.filename,nextrel)
    elif stat.S_ISREG(a.st_mode):
     s.get(path+'/'+a.filename,str(dest));b=dest.read_bytes();records.append({'relative_path':nextrel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    else:raise RuntimeError('Unexpected nonregular recovery entry')
  walk(REMOTE)
  (R/'sync_manifest.json').write_text(json.dumps(records,indent=2))
  print(json.dumps({'files':len(records),'bytes':sum(x['bytes'] for x in records),'local':str(out)}))
 finally:t.close()
if __name__=='__main__':main()
