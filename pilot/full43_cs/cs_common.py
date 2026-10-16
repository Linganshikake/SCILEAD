import ctypes,hashlib,importlib.metadata,json,os,sys
from pathlib import Path
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[1];REPO=ROOT/'emnlp2024-leaderboard-generation';BASE=RUN.parent/'full43_uncapped';LB=RUN.parent/'leaderboard_eval_full43_uncapped';CACHE=ROOT/'assets/hf_cache'
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
    return {'physical_available_GiB':m.available/2**30,'commit_available_GiB':m.page_available/2**30,'working_set_GiB':p.WorkingSetSize/2**30,'peak_working_set_GiB':p.PeakWorkingSetSize/2**30,'private_GiB':p.PrivateUsage/2**30,'peak_private_GiB':p.PeakPagefileUsage/2**30}
def setup():
    tmp=RUN/'runtime/tmp';tmp.mkdir(parents=True,exist_ok=True)
    os.environ.update(HF_HOME=str(CACHE),HF_HUB_CACHE=str(CACHE),HF_MODULES_CACHE=str(CACHE/'modules'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',TMP=str(tmp),TEMP=str(tmp),LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false',ANONYMIZED_TELEMETRY='False')
    sys.path.insert(0,str(REPO));os.chdir(RUN)
def verify():
    f=read(RUN/'freeze_before.json')
    for root,files in f['directories'].items():
        assert {str(p) for p in Path(root).rglob('*') if p.is_file()}==set(files)
        for path,h in files.items():assert sha(path)==h,path
    for path,h in f['sources_gold'].items():assert sha(path)==h,path
    assert f['dependencies']=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    return f
