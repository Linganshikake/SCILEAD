import ctypes,hashlib,importlib.metadata,json,os,sys
from pathlib import Path
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parent;ROOT=Path(r'D:\C++\SCILEAD');REPO=ROOT/'emnlp2024-leaderboard-generation';BASE=RUN.parent.parent/'fully';LB=ROOT/'pilot/full43_cs/leaderboard_evaluation';CACHE=ROOT/'assets/hf_cache'
MODEL='Lajavaness/bilingual-embedding-large';REV='e83179d7a66e8aed1b3015e98bb5ae234ed89598';CODE='dangvantuan/bilingual_impl';CODE_REV='8079a782f9671d3696b5ab189781480fcca58d25'
SNAPSHOT=CACHE/'models--Lajavaness--bilingual-embedding-large'/'snapshots'/REV;CODE_PATH=CACHE/'models--dangvantuan--bilingual_impl'/'snapshots'/CODE_REV
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');tmp.replace(p)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False).encode()).hexdigest()
def memory():
    class M(ctypes.Structure):_fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(x,ctypes.c_ulonglong) for x in ('total','available','page_total','page_available','virtual_total','virtual_available','extended')]
    m=M();m.length=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    class P(ctypes.Structure):_fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(x,ctypes.c_size_t) for x in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    p=P();p.cb=ctypes.sizeof(p);ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p;ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(P),ctypes.c_ulong];ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(p),p.cb)
    return {'physical_available_GiB':m.available/2**30,'commit_available_GiB':m.page_available/2**30,'working_set_GiB':p.WorkingSetSize/2**30,'peak_working_set_GiB':p.PeakWorkingSetSize/2**30,'max_rss_bytes':p.PeakWorkingSetSize,'max_rss_GiB':p.PeakWorkingSetSize/2**30,'private_GiB':p.PrivateUsage/2**30,'peak_private_GiB':p.PeakPagefileUsage/2**30}

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
    # Source and input hashes only; no historical output directories are written.
    manifest=read(RUN.parent/'protected_hashes.json')
    for path,h in manifest.items():assert sha(path)==h,'FROZEN_SOURCE_CHANGED: '+path
    dependencies=read(RUN.parent/'reproducibility/dependency_versions.json')
    assert dependencies=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'ENVIRONMENT_CHANGED'
    mm=read(RUN/'model_manifest.json')
    assert str(SNAPSHOT)==mm['local_snapshot'] and REV==mm['weight_revision'] and CODE_REV==mm['code_revision']
    # Deferred to explicit CS execution. Preparation never opens model weights.
    for name,h in mm['model_files_sha256'].items():assert sha(SNAPSHOT/name)==h,'MODEL_FILE_CHANGED: '+name
    for name,h in mm['code_files_sha256'].items():assert sha(CODE_PATH/name)==h,'MODEL_CODE_CHANGED: '+name
    return manifest
