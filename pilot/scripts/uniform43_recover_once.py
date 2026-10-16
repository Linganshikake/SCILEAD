"""Explicitly authorized, bounded recovery of the recorded connection failure only."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parents[1]/'full43_uncapped';PAPER='2020.emnlp-main.152.pdf'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--authorization',required=True);a=ap.parse_args();assert a.authorization.strip()
    m=read(RUN/'manifest.json');r=next(r for r in m['papers'] if r['id']==PAPER);folder=Path(r['normalization_dir']).resolve();archive=folder.with_name('normalization_failed_attempt_1')
    assert folder.is_relative_to(RUN.resolve()) and archive.is_relative_to(RUN.resolve()) and not archive.exists()
    states=list(folder.glob('api_calls/*/state.json'));assert len(states)==1
    state=read(states[0]);assert state['status']=='FAILED' and state['error_type']=='APIConnectionError' and not state.get('http_status')
    assert not (folder/'api_calls/0001/response.json').exists() and not (folder/'normalized_output.json').exists()
    hashes={str(f.relative_to(folder)):sha(f) for f in folder.rglob('*') if f.is_file()}
    # Both resolved paths checked above; archive by rename, without deleting or changing contents.
    folder.rename(archive)
    assert all(sha(archive/p)==h for p,h in hashes.items())
    save(RUN/'recovery_authorization.json',{'paper':PAPER,'user_authorization':a.authorization,'epoch':time.time(),'maximum_reissues':1,'failure_archive':str(archive),'failure_files_sha256':hashes,'reason':'Connection failure without HTTP response; possible prior billing explicitly acknowledged','extraction_unchanged_sha256':sha(Path(r['extraction_dir'])/'output.json')})
    m['failed_attempt_archives']=[{'paper':PAPER,'stage':'normalize','path':str(archive),'requests':1,'usage_unknown':True}];save(RUN/'manifest.json',m)
    folder.mkdir();env=dict(os.environ,SCILEAD_RUN_ROOT=str(RUN),PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1')
    with (folder/'run.log').open('a',encoding='utf-8') as f:
        p=subprocess.run([sys.executable,'-B','-X','utf8',str(Path(__file__).with_name('scilead_api.py')),'--paper',PAPER,'--stage','normalize'],env=env,stdout=f,stderr=subprocess.STDOUT)
    assert read(archive/'api_calls/0001/request.json')==read(folder/'api_calls/0001/request.json')
    m=read(RUN/'manifest.json');row=next(r for r in m['papers'] if r['id']==PAPER);row['status']='NORMALIZE_'+(read(folder/'summary.json')['status'] if (folder/'summary.json').exists() else 'FAILED');save(RUN/'manifest.json',m)
    save(RUN/'recovery_finished.json',{'epoch':time.time(),'exit_code':p.returncode,'status':row['status']});print(row['status'],flush=True);sys.exit(p.returncode)
if __name__=='__main__':main()
