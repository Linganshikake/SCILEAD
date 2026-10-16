"""Read-only evaluation boundary: no network, credentials, or writes outside this run."""
import hashlib,json,os,sys
from pathlib import Path
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[1];BASE=RUN.parent/'full43_uncapped';REPO=ROOT/'emnlp2024-leaderboard-generation'
GOLD=Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\leaderboards.json');TDM=GOLD.with_name('tdm_annotations.json');NORMALIZED=BASE/'merged/normalized_output.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):
    p=Path(p);assert p.resolve().is_relative_to(RUN);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def boundary():
    temporary=RUN/'runtime_cache/tmp';temporary.mkdir(parents=True,exist_ok=True)
    os.environ.update(TMP=str(temporary),TEMP=str(temporary),TMPDIR=str(temporary))
    os.environ.update(HF_HOME=str(RUN/'runtime_cache/huggingface'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',LANGCHAIN_TRACING_V2='false',LANGCHAIN_TRACING='false',LANGSMITH_TRACING='false',ANONYMIZED_TELEMETRY='False',PYTHONDONTWRITEBYTECODE='1')
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Evaluation is offline; network forbidden')
        if event=='open' and isinstance(args[0],(str,bytes)):
            if os.fsdecode(args[0]).lower()==os.devnull.lower():return
            p=Path(os.fsdecode(args[0])).resolve();s=p.as_posix().lower()
            if p.name.startswith('.env') or any(x in s for x in ('/.codex/','/.claude/','/.aws/')):raise RuntimeError('Sensitive configuration forbidden')
            mode=args[1];flags=args[2] if len(args)>2 else 0
            writing=(isinstance(mode,str) and any(v in mode for v in ('w','a','x','+'))) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
            if writing and not p.is_relative_to(RUN):raise RuntimeError('Write outside evaluation directory forbidden: '+str(p))
        if event in ('os.remove','os.rmdir','os.mkdir','os.rename'):
            targets=args[:2] if event=='os.rename' else args[:1]
            for item in targets:
                if isinstance(item,(str,bytes)) and not Path(os.fsdecode(item)).resolve().is_relative_to(RUN):raise RuntimeError('Mutation outside evaluation directory forbidden')
    sys.addaudithook(guard);os.chdir(RUN);sys.path.insert(0,str(REPO))
def verify_frozen():
    snap=read(RUN/'freeze_before.json')
    for path,h in snap['all_baseline_files'].items():assert sha(path)==h,path
    assert set(snap['all_baseline_files'])=={str(p) for p in BASE.rglob('*') if p.is_file()},'Baseline file inventory changed'
    for path,h in snap['sources_and_gold'].items():assert sha(path)==h,path
    return snap
