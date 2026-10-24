from pathlib import Path
import sys,json,hashlib,subprocess,datetime
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=R.parent/'20261021_formal42';S=OLD/'remote_snapshot';sys.path.insert(0,str(R/'parser_v2'))
from parser import parse
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    test=subprocess.run([sys.executable,'-B',str(R/'parser_v2/test_parser.py')],capture_output=True,text=True);(R/'parser_v2/test_results.txt').write_text(test.stdout+test.stderr,encoding='utf-8');assert test.returncode==0
    version={'version':'2.0','frozen_before_scoring_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{p.name:sha(p) for p in [R/'parser_v2/parser.py',R/'parser_v2/rules.md',R/'parser_v2/test_parser.py',R/'parser_v2/test_results.txt']}}
    path=R/'parser_v2/parser_version.json'
    raw=read(S/'extraction/raw_output.json');prior=read(S/'extraction/prepared_output.json');ids=read(OLD/'config/scope42.json')['eligible_ids'];prepared={};manifest=[]
    for pid in ids:
        v=parse(raw[pid]['output']);row={'paper_id':pid,'position':ids.index(pid),'raw_sha256':hashlib.sha256(raw[pid]['output'].encode()).hexdigest(),'source_documents_sha256':hashlib.sha256(json.dumps(raw[pid]['source_documents'],ensure_ascii=False).encode()).hexdigest(),**v};save(R/'audit/papers'/pid.removesuffix('.pdf')/'parse.json',row)
        if v['ok']:
            prepared[pid]={**raw[pid],'output':v['text']}
            if pid in prior:
                before=json.loads(prior[pid]['output']);after=json.loads(v['text']);assert before==after
                assert [str(x['Result']) for x in before]==[str(x['Result']) for x in after]
                assert v['text']==prior[pid]['output'],'Original40 array bytes changed'
        manifest.append({k:x for k,x in row.items() if k not in ['text','record_spans','groups']})
    if path.exists():assert read(path)['files']==version['files']
    else:save(path,version)
    save(R/'format_v2/extraction/prepared_output.json',prepared);save(R/'format_v2/recovery_manifest.json',{'papers':manifest,'valid_papers':len(prepared),'records':sum(len(json.loads(x['output'])) for x in prepared.values()),'original40_record_and_array_bytes_unchanged':True,'newly_recovered':[p for p in prepared if p not in prior],'remaining_failed':[p for p in ids if p not in prepared]})
    print(json.dumps(read(R/'format_v2/recovery_manifest.json')|{'papers':'omitted'}))
if __name__=='__main__':main()
