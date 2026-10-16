from common import *
import subprocess
from concurrent.futures import ThreadPoolExecutor
def main():
    setup();assert not (ROOT/'freeze_before.json').exists()
    prev=PILOT/'full43_fewshot_both_prompts';f=read(prev/'freeze_before.json');dirs={}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for root,expected in f['directories'].items():
            paths=[str(p) for p in Path(root).rglob('*') if p.is_file()];assert set(paths)==set(expected)
            actual=dict(zip(paths,pool.map(sha,paths)));assert actual==expected,root;dirs[root]=actual
            print('FROZEN',Path(root).name,len(actual),flush=True)
        paths=[str(p) for p in prev.rglob('*') if p.is_file()];dirs[str(prev)]=dict(zip(paths,pool.map(sha,paths)))
    for rel,h in read(prev/'artifact_sha256.json').items():assert dirs[str(prev)][str(prev/rel)]==h
    sources=dict(f['sources_gold'])
    for p in REPO.iterdir():
        if p.is_file() and (p.suffix in ('.py','.json','.md','.txt') or p.name in ('LICENSE','NOTICE')):sources[str(p)]=sha(p)
    gold=Path(read(prev/'input_manifest.json')['gold_path'])
    for p in gold.parent.iterdir():
        if p.is_file():sources[str(p)]=sha(p)
    for name in ('2024.emnlp-main.453.data.zip','2024.emnlp-main.453.software.zip'):
        p=gold.parents[2]/name
        if p.exists():sources[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in f['sources_gold'].items())
    git=['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO)]
    commit=subprocess.check_output(git+['rev-parse','HEAD'],text=True).strip();assert commit=='8bf74b0a830feb7035c6166dce3394dc344ae532'
    save(ROOT/'freeze_before.json',{'directories':dirs,'sources_gold':sources,'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'commit':commit,'git_status':subprocess.check_output(git+['status','--porcelain'],text=True),'epoch':time.time()})
    print('FROZEN_TOTAL',sum(len(x) for x in dirs.values()),flush=True)
if __name__=='__main__':main()
