import hashlib, importlib.metadata, json, os, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[1]; REPO=ROOT/'emnlp2024-leaderboard-generation'; BASE=RUN.parent/'full43_uncapped'
MODEL='gpt-4.1-2025-04-14'; URL='https://9527.codes/v1'; KEY=''; RUN_ID='fewshot'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False).encode()).hexdigest()
def scrub(x):
    if isinstance(x,str):return x.replace(KEY,'[REDACTED]') if KEY else x
    if isinstance(x,list):return [scrub(v) for v in x]
    if isinstance(x,dict):return {k:('[REDACTED]' if k.lower() in ('authorization','api_key','x-api-key') else scrub(v)) for k,v in x.items()}
    return x
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');data=json.dumps(scrub(x),ensure_ascii=False,indent=2,allow_nan=False)
    for i in range(20):
        try:t.write_text(data,encoding='utf-8');t.replace(p);return
        except PermissionError:
            if i==19:raise
            time.sleep(min(.05*(i+1),.25))
def immutable(p,x):
    if Path(p).exists():assert read(p)==x,'Artifact changed: '+str(p)
    else:save(p,x)
def wire(messages):return [{'role':{'system':'system','human':'user'}[m.type],'content':m.content} for m in messages]
def setup(stage='offline'):
    temp=RUN/'runtime/tmp';temp.mkdir(parents=True,exist_ok=True)
    os.environ.update(HF_HOME=str(ROOT/'assets/huggingface'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING='false',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false',ANONYMIZED_TELEMETRY='False',TIKTOKEN_CACHE_DIR=str(ROOT/'assets/tiktoken'),TMP=str(temp),TEMP=str(temp))
    os.chdir(RUN);sys.path.insert(0,str(REPO))
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo') and stage=='offline':raise RuntimeError('Offline verification')
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(os.fsdecode(args[0]));s=str(p).replace('\\','/').lower()
            if any(v in s for v in ('/.codex/','/.claude/','/.aws/')):raise RuntimeError('Unrelated sensitive config')
            if p.name.startswith('.env') and (stage=='offline' or p.resolve()!=(ROOT/'SCILEAD_small_test/.env').resolve()):raise RuntimeError('Unauthorized dotenv')
            if stage=='extract' and p.name in ('tdm_annotations.json','leaderboards.json'):raise RuntimeError('Gold forbidden in extraction')
    sys.addaudithook(guard)
def verify(full=False):
    f=read(RUN/'freeze_before.json')
    for p,h in f['sources_gold'].items():assert sha(p)==h,p
    assert f['dependencies']=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    if full:
        for root,files in f['directories'].items():
            assert {str(p) for p in Path(root).rglob('*') if p.is_file()}==set(files),root
            for p,h in files.items():assert sha(p)==h,p
    return f
def estimate(messages):
    import tiktoken
    enc=tiktoken.encoding_for_model(MODEL)
    return 3+sum(3+len(enc.encode(m['role']))+len(enc.encode(m['content'])) for m in messages)
def validate(text):
    out={'json_valid':False,'schema_valid':False,'records':None}
    try:r=json.loads(text)
    except ValueError:return out
    out.update(json_valid=True,records=len(r) if isinstance(r,list) else None)
    out['schema_valid']=isinstance(r,list) and all(isinstance(x,dict) and set(x)=={'Task','Dataset','Metric','Result'} and all(isinstance(v,str) for v in x.values()) for x in r)
    if out['schema_valid']:out['duplicates']=len(r)-len({json.dumps(x,sort_keys=True) for x in r})
    return out
