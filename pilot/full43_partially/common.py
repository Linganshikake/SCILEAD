import hashlib,importlib.metadata,json,os,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[1];REPO=ROOT/'emnlp2024-leaderboard-generation';BASE=RUN.parent/'full43_uncapped';CS=RUN.parent/'full43_cs';LB=RUN.parent/'leaderboard_eval_full43_uncapped'
MODEL='gpt-4.1-2025-04-14';URL='https://9527.codes/v1';KEY=''
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def scrub(x):
    if isinstance(x,str):return x.replace(KEY,'[REDACTED]') if KEY else x
    if isinstance(x,list):return [scrub(v) for v in x]
    if isinstance(x,dict):return {k:('[REDACTED]' if k.lower() in ('authorization','api_key','x-api-key') else scrub(v)) for k,v in x.items()}
    return x
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');text=json.dumps(scrub(x),ensure_ascii=False,indent=2,allow_nan=False)
    # Bounded filesystem-only retries for transient Windows sharing conflicts.
    # Never retries model requests, changes the payload or discards a response.
    for attempt in range(20):
        try:t.write_text(text,encoding='utf-8');t.replace(p);return
        except PermissionError:
            if attempt==19:raise
            time.sleep(min(0.05*(attempt+1),0.25))
def immutable(p,x):
    if Path(p).exists():assert read(p)==x,'Existing artifact differs: '+str(p)
    else:save(p,x)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False).encode()).hexdigest()
def setup():
    temp=RUN/'runtime/tmp';temp.mkdir(parents=True,exist_ok=True)
    os.environ.update(HF_HOME=str(ROOT/'assets/hf_cache'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING='false',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false',TIKTOKEN_CACHE_DIR=str(ROOT/'assets/tiktoken'),TMP=str(temp),TEMP=str(temp))
    os.chdir(RUN);sys.path.insert(0,str(REPO))
def verify():
    f=read(RUN/'freeze_before.json')
    for root,files in f['directories'].items():
        assert {str(p) for p in Path(root).rglob('*') if p.is_file()}==set(files),root
        for p,h in files.items():assert sha(p)==h,p
    for p,h in f['sources_gold'].items():assert sha(p)==h,p
    assert f['dependencies']=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    return f
def labels_state(labels):return {k:{'ordered_values':list(v),'serialized':str(v),'sha256':digest(str(v))} for k,v in labels.items()}
def wire(messages):return [{'role':{'system':'system','human':'user'}[m.type],'content':m.content} for m in messages]
