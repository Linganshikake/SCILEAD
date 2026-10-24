from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];OLD=R.parent/'20261021_formal42';S=OLD/'remote_snapshot'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    target=R/'audit/protected_before.json'
    if not target.exists():
        records={str(p):{'path':str(p),'sha256':sha(p)} for p in OLD.rglob('*') if p.is_file()}
        for x in read(OLD/'integrity_before.json')+read(OLD/'protected_diagnostics.json'):
            assert sha(Path(x['path']))==x['sha256'];records[x['path']]=x
        save(target,list(records.values()))
    for x in read(target):assert sha(Path(x['path']))==x['sha256']
    ids=read(OLD/'config/scope42.json')['eligible_ids'];raw=read(S/'extraction/raw_output.json');diagnosis={}
    for pid in ['1901.10430.pdf','2105.03654.pdf']:
        d=S/'extraction'/pid.removesuffix('.pdf')/'extraction/calls/000000'
        req=read(d/'request.json');complete=read(d/'complete.json');text=(d/'response.txt').read_text(encoding='utf-8')
        assert text==raw[pid]['output']
        diagnosis[pid]={'position_zero_based':ids.index(pid),'request':req,'complete':complete,'raw_sha256':sha(d/'response.txt'),'raw_tail':text[-600:],'files':[p.name for p in d.iterdir() if p.is_file()]}
    save(R/'audit/raw_failure_records.json',diagnosis)
    print(json.dumps({'protected_files':len(read(target)),'failure_records':{p:{'position':x['position_zero_based'],'generation':x['complete']['actual_generation'],'files':x['files']} for p,x in diagnosis.items()}}))
if __name__=='__main__':main()
