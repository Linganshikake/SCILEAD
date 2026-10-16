import json,hashlib,os,sys,time,importlib.metadata
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PILOT=ROOT.parent
REPO=PILOT.parent/'emnlp2024-leaderboard-generation'
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):
    path=Path(path);assert path.resolve().is_relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');tmp.replace(path)
def setup():
    sys.dont_write_bytecode=True;os.chdir(ROOT);sys.path.insert(0,str(REPO))
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING='false',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false')
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Offline audit: network forbidden')
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(os.fsdecode(args[0]));s=str(p).replace('\\','/').lower()
            if p.name.startswith('.env') or any(x in s for x in ('/.codex/','/.claude/','/.aws/')):raise RuntimeError('Credential/unrelated config access forbidden')
    sys.addaudithook(guard)
