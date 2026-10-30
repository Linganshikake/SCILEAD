"""Prepare this owned offline branch from frozen full43_cs adapters."""
import ast
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
RUN = Path(__file__).resolve().parent
ROOT = Path(r'D:\C++\SCILEAD')
OLD = ROOT / 'pilot/full43_cs'
REPO = ROOT / 'emnlp2024-leaderboard-generation'
INPUT = ROOT / 'pilot/gpt56_sol_fully/20261024_A2_result_type_recovery/merged/output.json'
sys.path.insert(0, str(OLD))
import cs_common as original

def write(name, text):
    p = RUN / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def main():
    assert not (RUN / 'freeze_before.json').exists(), 'Preparation already frozen'
    cfg = original.read(OLD / 'config.json')
    mm = original.read(OLD / 'model_manifest.json')
    raw = original.read(INPUT)
    gold = original.read(cfg['gold_path'])
    boards = original.read(cfg['gold_leaderboards_path'])
    assert len(raw) == len(gold) == 43 and set(raw) == set(gold)
    assert sum(len(x['TDMs']) for x in gold.values()) == 295
    assert len(boards) == 27 and sum(len(b['Leaderboard']) for b in boards) == 140
    rows = [r for x in raw.values() for r in json.loads(x['output'])]
    assert len(rows) == 335
    assert all(set(r) == {'Task', 'Dataset', 'Metric', 'Result'} for r in rows)
    assert all(isinstance(v, str) for r in rows for v in r.values())
    labels = {k: {t[k] for g in gold.values() for t in g['TDMs']} for k in ('Task', 'Dataset', 'Metric')}
    for folder in ('work', 'merged', 'runtime/tmp', 'runtime/huggingface/hub', 'runtime/huggingface/modules', 'evaluation', 'normalization', 'reproducibility'):
        (RUN / folder).mkdir(parents=True, exist_ok=True)
    for folder in ('work', 'merged'):
        shutil.copy2(INPUT, RUN / folder / 'output.json')
    # Only small cached implementation code is copied. Model weights remain read-only.
    code_repo = original.CACHE / 'models--dangvantuan--bilingual_impl'
    shutil.copytree(code_repo, RUN / 'runtime/huggingface/hub' / code_repo.name, dirs_exist_ok=True)
    shutil.copytree(original.CACHE / 'modules', RUN / 'runtime/huggingface/modules', dirs_exist_ok=True)
    shutil.copy2(OLD / 'candidate_labels.json', RUN / 'candidate_labels.json')
    shutil.copy2(OLD / 'report.md', RUN / 'reproducibility/original_full43_cs_report.md')
    shutil.copy2(OLD / 'config.json', RUN / 'reproducibility/original_full43_cs_config.json')
    changes = []
    common = (OLD / 'cs_common.py').read_text(encoding='utf-8')
    common = common[:common.index('def setup():')]
    old_paths = "RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[1];REPO=ROOT/'emnlp2024-leaderboard-generation';BASE=RUN.parent/'full43_uncapped';LB=RUN.parent/'leaderboard_eval_full43_uncapped';CACHE=ROOT/'assets/hf_cache'"
    new_paths = "RUN=Path(__file__).resolve().parent;ROOT=Path(r'D:\\C++\\SCILEAD');REPO=ROOT/'emnlp2024-leaderboard-generation';BASE=ROOT/'pilot/gpt56_sol_fully/20261024_A2_result_type_recovery';LB=ROOT/'pilot/full43_cs/leaderboard_evaluation';CACHE=ROOT/'assets/hf_cache'"
    assert common.count(old_paths) == 1
    common = common.replace(old_paths, new_paths)
    common += '''
_guard_installed=False
def resource_preflight(phase):
    policy=read(RUN/'resource_policy.json');actual=memory()
    result={'phase':phase,'actual':actual,'policy':policy}
    save(RUN/('memory_'+phase+'.json'),result)
    if actual['physical_available_GiB']<policy['minimum_physical_GiB'] or actual['commit_available_GiB']<policy['minimum_commit_GiB']:
        save(RUN/'blocked_resources.json',dict(result,status='BLOCKED_RESOURCES',model_loaded=False))
        raise RuntimeError('Insufficient conservative memory headroom; no model load attempted')
    return actual

def setup():
    global _guard_installed
    tmp=RUN/'runtime/tmp';tmp.mkdir(parents=True,exist_ok=True)
    hf=RUN/'runtime/huggingface'
    os.environ.update(HF_HOME=str(hf),HF_HUB_CACHE=str(hf/'hub'),HF_MODULES_CACHE=str(hf/'modules'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',TMP=str(tmp),TEMP=str(tmp),TMPDIR=str(tmp),LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false',ANONYMIZED_TELEMETRY='False',PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(RUN/'runtime/xdg'),MPLCONFIGDIR=str(RUN/'runtime/matplotlib'),TORCH_HOME=str(RUN/'runtime/torch'))
    os.environ.pop('TRANSFORMERS_CACHE',None)
    sys.path.insert(0,str(REPO));os.chdir(RUN)
    if _guard_installed:return
    def allowed(path):
        if isinstance(path,int) or path is None:return True
        if os.fsdecode(path).lower()=='nul':return True  # Windows null device, not a filesystem write.
        p=Path(os.fsdecode(path)).resolve()
        return p.is_relative_to(RUN)
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):
            raise RuntimeError('Offline-only branch: network prohibited')
        if event=='open':
            path,mode,flags=args
            if not isinstance(path,int):
                p=Path(os.fsdecode(path))
                if p.name.lower() in ('.env','token','stored_tokens','credentials') or p.suffix.lower()=='.env':
                    raise RuntimeError('Credential file access prohibited: '+str(p))
            writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
            if writing and not allowed(path):raise RuntimeError('Write outside owned branch prohibited: '+str(path))
        elif event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.utime'):
            if not allowed(args[0]):raise RuntimeError('Mutation outside owned branch prohibited: '+str(args[0]))
        elif event in ('os.rename','os.link','os.symlink'):
            if not all(allowed(p) for p in args[:2]):raise RuntimeError('Mutation outside owned branch prohibited')
    sys.addaudithook(guard);_guard_installed=True

def verify():
    f=read(RUN/'freeze_before.json')
    for root,files in f['directories'].items():
        actual={str(p) for p in Path(root).rglob('*') if p.is_file()}
        assert actual==set(files),root
        for path,h in files.items():assert sha(path)==h,path
    for path,h in f['sources_gold'].items():assert sha(path)==h,path
    assert f['dependencies']=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    return f
'''
    write('cs_common.py', common)
    run = (OLD / 'run_cs.py').read_text(encoding='utf-8')
    needle = "    encoder=SentenceTransformer(str(SNAPSHOT),device='cpu',trust_remote_code=True,local_files_only=True,"
    assert run.count(needle) == 1
    run = run.replace(needle, "    before_load=resource_preflight('before_model_load')\n    save(RUN/'memory_before_model_load.json',before_load)\n    encoder=SentenceTransformer(str(SNAPSHOT),device='cpu',trust_remote_code=True,local_files_only=True,token=False,")
    run = run.replace('    import torch\n',"    resource_preflight('before_torch_import')\n    import torch\n")
    run = run.replace('# Only prevent network during this local-only stage; no global filesystem interception.','# Owned-path filesystem and credential guards are installed by setup().')
    write('run_cs.py', run)
    for name in ('run_official_leaderboard_eval.py','evaluate_paper_metrics.py','common.py'):
        s=(OLD/'leaderboard_evaluation'/name).read_text(encoding='utf-8')
        write('leaderboard_evaluation/'+name,s)
        changes.append({'source':str(OLD/'leaderboard_evaluation'/name),'destination':'leaderboard_evaluation/'+name,'changes':'none; common imports the adapted cs_common'})
    for folder in ('official','paper_metrics','leaderboards','reference'):
        (RUN/'leaderboard_evaluation'/folder).mkdir(exist_ok=True)
    for name in ('cs_common.py','run_cs.py'):
        changes.append({'source':str(OLD/name),'destination':name,'changes':'Owned paths, offline/write/credential guards, local cache and resource check; model token=False; no normalization algorithm changes' if name=='cs_common.py' else 'Memory preflight and token=False only'})
    sources = [p for p in REPO.iterdir() if p.is_file() and (p.suffix in ('.py','.md','.json') or p.name in ('requirements.txt','LICENSE','NOTICE'))]
    sources += [INPUT,Path(cfg['gold_path']),Path(cfg['gold_leaderboards_path'])]
    sources += [p for p in code_repo.rglob('*') if p.is_file()]
    commit=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'rev-parse','HEAD'],cwd=REPO,text=True).strip()
    status=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'status','--porcelain'],cwd=REPO,text=True,capture_output=True)
    assert commit=='8bf74b0a830feb7035c6166dce3394dc344ae532'
    original.save(RUN/'freeze_before.json',{'directories':{str(OLD):{str(p):original.sha(p) for p in OLD.rglob('*') if p.is_file()}},'sources_gold':{str(p):original.sha(p) for p in sources},'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'commit':commit,'git_status_before':status.stdout,'git_status_stderr':status.stderr,'timestamp_epoch':time.time(),'input_path':str(INPUT),'input_sha256':original.sha(INPUT)})
    actual_model={name:original.sha(Path(mm['local_snapshot'])/name) for name in mm['model_files_sha256']}
    assert actual_model==mm['model_files_sha256']
    assert {name:original.sha(original.CODE_PATH/name) for name in mm['code_files_sha256']}==mm['code_files_sha256']
    mm.pop('actual_runtime',None)
    mm['current_run_model_hashes_verified']=True
    mm['embedding_cache_reused']=False
    mm['model_downloads']=0
    original.save(RUN/'model_manifest.json',mm)
    cs=sum(r[k] not in labels[k] for r in rows for k in labels)
    cfg.update(input_path=str(INPUT),input_sha256=original.sha(INPUT),raw_records=len(rows),expected_cs_fields=cs,expected_exact_fields=3*len(rows)-cs,started_epoch=time.time(),memory_before=original.memory(),disk_free=shutil.disk_usage(RUN).free,algorithm='Unmodified official tdm_embedding_normalization.main; same full43_cs CPU FP32 local model adapter; no similarity threshold in official source',embedding_cache_reused=False,scope='ONLY offline Fully+CS',gold_leaderboards=27,gold_leaderboard_records=140)
    original.save(RUN/'config.json',cfg)
    original.save(RUN/'resource_policy.json',{'minimum_physical_GiB':4.5,'minimum_commit_GiB':7.5,'cs_physical_budget_GiB':3.5,'cs_commit_budget_GiB':6.5,'concurrent_parent_api_reserve_GiB':1.0,'basis':'Conservative operational gate: prior CPU FP32 peak working set 3.047 GiB and peak private commit 5.459 GiB, plus safety margins and one parent API process; not a proven exact OOM boundary.'})
    original.save(RUN/'reproducibility/adapter_audit.json',{'adapters':changes,'official_main_modified':False,'threshold':None,'threshold_note':'Official source always takes cosine top-1 for nonexact labels; no threshold introduced','candidate_order':'Official set insertion and list conversion, PYTHONHASHSEED=0, checked against frozen full43_cs candidate_labels.json','preprocessing':'Unchanged encoder.encode inputs/defaults; each original encode call retained; no embedding reuse or batching changes'})
    original.save(RUN/'reproducibility/versions.json',{'python':sys.version,'executable':sys.executable,'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()}})
    for p in RUN.rglob('*.py'):
        if 'runtime' in p.relative_to(RUN).parts:continue
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
    print(json.dumps({'prepared':str(RUN),'papers':43,'records':335,'cs_fields':cs,'exact_fields':1005-cs,'memory':original.memory(),'input_sha256':original.sha(INPUT)},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
