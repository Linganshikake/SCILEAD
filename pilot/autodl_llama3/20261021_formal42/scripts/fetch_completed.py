from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021\scripts')))
from remote_client import connect
rr='/root/autodl-tmp/scilead/runs/llama3/20261021_formal42';sources={'fully_llm':'normalization/fully_llm/normalization/normalized_output.json','fully_cs':'normalization/fully_cs/normalized_output.json'}
c=connect();s=c.open_sftp();proof=[]
try:
    for name,rel in sources.items():
        with s.open(rr+'/'+rel,'rb') as f:data=f.read()
        target=R/'fetched_completed'/name/'normalized_output.json';target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==data
        else:target.write_bytes(data)
        proof.append({'name':name,'remote_source':rr+'/'+rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    (R/'fetched_completed/transfer.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps({'completed_outputs_fetched':len(proof)}))
finally:s.close();c.close()
