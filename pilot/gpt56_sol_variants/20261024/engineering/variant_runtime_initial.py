"""Original SCILEAD mains, audited observers, GPT56 A1 transport only."""
import argparse,contextlib,copy,csv,ctypes,hashlib,importlib.metadata,importlib.util,json,logging,os,random,shutil,sys,time,types
from pathlib import Path
sys.dont_write_bytecode=True
TOP=Path(__file__).resolve().parent
ROOT=Path(r'D:\C++\SCILEAD');REPO=ROOT/'emnlp2024-leaderboard-generation'
PILOT=ROOT/'pilot';BASE=PILOT/'gpt56_sol_fully/20261024_A2_result_type_recovery'
MODEL='gpt-5.6-sol';URL='https://9527.codes/v1';KEY='';RUN_ID=''
A1=PILOT/'gpt56_sol_fully/20261024_A1_single_paper'
spec=importlib.util.spec_from_file_location('gpt56_frozen_transport',A1/'run_trial.py')
frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):frozen.save(Path(p),x)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False).encode()).hexdigest()
def immutable(p,x):
    if Path(p).exists():assert read(p)==x,'IMMUTABLE_ARTIFACT_MISMATCH: '+str(p)
    else:save(p,x)
def labels_state(labels):return {k:{'ordered_values':list(v),'serialized':str(v),'sha256':digest(str(v))} for k,v in labels.items()}
def wire(messages):return [{'role':{'system':'system','human':'user'}[m.type],'content':m.content} for m in messages]
def resources():
    class Mem(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('available_page',ctypes.c_ulonglong),('total_virtual',ctypes.c_ulonglong),('available_virtual',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
    m=Mem();m.length=ctypes.sizeof(m)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)),'MEMORY_PROBE_FAILED'
    return {'available_memory_bytes':m.available,'available_commit_bytes':m.available_page,'free_disk_bytes':shutil.disk_usage(TOP).free}
def setup():
    assert os.environ.get('PYTHONHASHSEED')=='0','PYTHONHASHSEED must be 0 before interpreter starts'
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING='false',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false')
    sys.path.insert(0,str(REPO));logging.disable(logging.CRITICAL)
def verify(full=False):
    manifest=read(TOP/'protected_hashes.json')
    if not full:
        critical=set(read(TOP/'critical_paths.json'))
        manifest={p:h for p,h in manifest.items() if p in critical}
    changed=[p for p,h in manifest.items() if not Path(p).is_file() or sha(p)!=h]
    assert not changed,'FROZEN_SOURCE_CHANGED: '+str(changed[:3])
    return {'files_checked':len(manifest),'changed':changed,'scope':'ALL_FROZEN' if full else 'CRITICAL_INPUTS_AND_METHOD'}
def durable_request(client,folder,messages,key):
    folder=Path(folder);req=frozen.payload(messages)
    if (folder/'attempt.lock').exists():
        assert (folder/'request.json').exists() and read(folder/'request.json')==req,'REPLAY_REQUEST_CHANGED'
        assert (folder/'accepted.json').exists(),'FAILED_OR_UNKNOWN_NO_AUTOMATIC_RESEND'
        accepted=read(folder/'accepted.json');assert sha(folder/'response.json')==accepted['response_sha256'],'REPLAY_RESPONSE_CHANGED'
        return frozen.validate(read(folder/'response.json'),False)
    body=frozen.one_request(client,folder,req,key,URL+'/chat/completions')
    answer=frozen.validate(body,False)
    save(folder/'accepted.json',{'status':'COMPLETE','response_sha256':sha(folder/'response.json'),'raw_answer':answer,'finish_reason':'stop','model':MODEL})
    return answer
def load_observer(cold):
    origin=PILOT/('full43_cold_start' if cold else 'full43_partially')/'engine.py'
    previous=sys.modules.get('common');sys.modules['common']=sys.modules[__name__]
    try:
        s=importlib.util.spec_from_file_location('frozen_observer_'+str(cold),origin)
        module=importlib.util.module_from_spec(s);s.loader.exec_module(module)
    finally:
        if previous is None:sys.modules.pop('common',None)
        else:sys.modules['common']=previous
    return module.Observer
class SimulatedInterruption(Exception):pass
class Transport:
    def __init__(self,observer,out,cold,mock=None,interrupt_after=None):
        import httpx
        self.observer=observer;self.out=Path(out);self.cold=cold;self.mock=mock;self.cursor=0;self.mock_new=0;self.interrupt_after=interrupt_after
        self.out.mkdir(parents=True,exist_ok=True)
        if mock is None:
            global KEY
            from dotenv import dotenv_values
            env=dotenv_values(frozen.ENV,interpolate=False,encoding='utf-8-sig')
            KEY=next((env[k] for k in ('OPENAI_API_KEY','API_KEY','SK') if env.get(k)),None)
            base=next((env[k] for k in ('BASE_URL','OPENAI_BASE_URL','API_BASE','OPENAI_API_BASE','API_BASE_URL') if env.get(k)),None)
            assert KEY and base and base.rstrip('/') in ('https://9527.codes','https://9527.codes/v1'),'CREDENTIAL_CONFIG_INVALID'
            self.key=KEY
            self.client=httpx.Client(transport=httpx.HTTPTransport(retries=0),trust_env=False,follow_redirects=False,timeout=httpx.Timeout(connect=20,read=600,write=30,pool=20))
        else:
            self.key='synthetic-offline-key'
            def handler(request):
                self.mock_new+=1
                body={'model':MODEL,'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':mock(self.expected)}}],'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2}}
                return httpx.Response(200,json=body)
            self.client=httpx.Client(transport=httpx.MockTransport(handler))
    def summary(self):
        states=[]
        for p in sorted((self.out/'api_calls').glob('*/state.json')):
            s=read(p);s['accepted']=(p.parent/'accepted.json').exists();s['call']=p.parent.name;states.append(s)
        total={k:sum((s.get('usage') or {}).get(k,0) or 0 for s in states) for k in ('prompt_tokens','completion_tokens','total_tokens')}
        total.update(attempts=len(states),successful_responses=sum(s['accepted'] for s in states),failed_or_unknown=sum(not s['accepted'] for s in states),unknown_usage_attempts=sum(s.get('usage') is None for s in states),request_seconds=sum(s.get('elapsed_seconds',0) for s in states),mock=self.mock is not None,automatic_retries=0)
        save(self.out/'api_usage.json',total);return total
    def invoke(self,prompt):
        messages=wire(prompt.to_messages());expected=self.observer.expected(messages)
        prompts=read(REPO/'prompts.json')
        pk='leaderboard-normalization-system-prompt' if self.observer.stage=='stage2' else ('masked-normalization-system-prompt' if self.cold or expected['field'] in ('Task','Dataset') else 'normalization-system-prompt')
        assert messages[0]=={'role':'system','content':prompts[pk]}
        index=self.cursor+1;folder=self.out/'api_calls'/f'{index:04d}';immutable(folder/'expected.json',expected)
        self.expected=expected
        new=not (folder/'attempt.lock').exists()
        if new and self.mock is None:
            memory=resources()
            assert memory['available_memory_bytes']>=256*2**20 and memory['free_disk_bytes']>=2*2**30,'RESOURCE_GUARD'
            save(folder/'resource_before.json',memory)
        try:
            answer=durable_request(self.client,folder,messages,self.key)
            if new and self.interrupt_after==index:raise SimulatedInterruption('After durable response before official field update')
            self.cursor=index;self.observer.answer(answer,index)
            return types.SimpleNamespace(content=answer)
        finally:
            if new:
                total=self.summary()
                print(json.dumps({'run':RUN_ID,'stage':self.observer.stage,'call':index,'paper':expected['paper'],'field':expected['field'],'accepted':(folder/'accepted.json').exists(),'total_tokens':total['total_tokens']}),flush=True)
def run_original(module,stage,args,out,mock=None,interrupt_after=None):
    cold=bool(getattr(args,'cold_start',False)) if stage=='stage1' else RUN_ID.startswith('cold_')
    observer=load_observer(cold)(module,stage,out)
    transport=Transport(observer,out,cold,mock,interrupt_after)
    previous=module.utils.llm_init_langchain;module.utils.llm_init_langchain=lambda *a,**k:transport
    try:
        sys.settrace(observer.trace);module.main(args)
    finally:
        sys.settrace(None);module.utils.llm_init_langchain=previous;transport.client.close();transport.summary()
    save(Path(out)/'observer_summary.json',{'events':observer.event_index,'requests':transport.cursor,'mock_new_requests':transport.mock_new})
    return observer,transport

def run_branch(branch):
    global RUN_ID
    RUN_ID=branch;setup();verify()
    assert read(TOP/'reproducibility/offline_tests.json')['status']=='PASS'
    conf=read(TOP/branch/'config.json');run=TOP/branch;raw=read(conf['input_path'])
    assert sha(conf['input_path'])==conf['input_sha256']
    import msvcrt
    lock=(run/'process.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    import tdm_llm_masked_normalization as s1
    import leaderboard_llm_normalization as s2
    try:
        for stage,module in [('stage1',s1),('stage2',s2)]:
            out=run/stage;work=run/'work'/stage;out.mkdir(exist_ok=True);work.mkdir(parents=True,exist_ok=True)
            if (out/'summary.json').exists() and read(out/'summary.json').get('status')=='COMPLETE':
                summary=read(out/'summary.json');assert sha(summary['output_path'])==summary['output_sha256'];continue
            if stage=='stage1':
                args=types.SimpleNamespace(seed=0,tdm_config_file=str(run/'official_config.json'),gold_tdm_file=conf['gold_path'],gold_leaderboard_file=conf['leaderboards_path'],tdm_output_file=conf['input_path'],prompt_file=str(REPO/'prompts.json'),cold_start=conf['cold_start'],cold_start_seed=conf['cold_start_seed'],normalization_output_path=work.as_posix()+'/',max_new_tokens=None)
                if conf['cold_start']:
                    sub='cold_start'+('_'+conf['cold_start_seed'] if conf['cold_start_seed'] is not None else '')
                    original=work/sub/'cold_start_masked_normalized_output.json'
                else:original=work/'partially_masked_normalization/partially_masked_normalized_output.json'
                final=out/'normalized_output.json'
            else:
                assert read(run/'stage1/summary.json')['status']=='COMPLETE'
                args=types.SimpleNamespace(seed=0,tdm_config_file=str(run/'official_config.json'),gold_leaderboard_file=conf['leaderboards_path'],masked_normalized_file=str(run/'stage1/normalized_output.json'),prompt_file=str(REPO/'prompts.json'),leaderboard_normalization_path=work.as_posix()+'/',max_new_tokens=None)
                original=work/'leaderboard_normalized_output.json';final=out/'leaderboard_normalized_output.json'
            immutable(out/'invocation.json',vars(args));start=time.monotonic()
            try:observer,transport=run_original(module,stage,args,out)
            except Exception as e:
                error=str(e).replace(KEY,'[REDACTED]') if KEY else str(e)
                save(out/'summary.json',{'status':'PAUSED_FAILED_OR_UNCERTAIN','error_type':type(e).__name__,'error':error[:300],'seconds_this_attempt':time.monotonic()-start})
                print(json.dumps({'run':branch,'stage':stage,'status':'PAUSED','error_type':type(e).__name__,'error':error[:300]}),flush=True);return 2
            result=read(original);assert list(result)==conf['paper_order'] and set(result)==set(raw)
            for p,x in raw.items():
                rows=json.loads(x['output']);nr=result[p]['normalized_output']
                assert len(nr)==len(rows) and result[p]['source_documents']==x['source_documents']
                assert [r['Result'] for r in rows]==[r['Result'] for r in nr]
            immutable(final,result)
            if stage=='stage1':
                expected=read(TOP/('references/cold_initial_labels.json' if conf['cold_start'] else 'masking/initial_labels.json'))
                assert read(out/'initial_labels.json')==expected
                immutable(out/'final_labels.json',observer.events[-1]['labels_after'])
            summary={'status':'COMPLETE','papers':len(result),'records':sum(len(x['normalized_output']) for x in result.values()),'null_fields':{k:sum(r[k] is None for x in result.values() for r in x['normalized_output']) for k in ('Task','Dataset','Metric')},'events':observer.event_index,'api_calls':transport.cursor,'seconds_this_attempt':time.monotonic()-start,'output_path':str(final),'output_sha256':sha(final)}
            if stage=='stage1':summary['label_additions']=sum(e['added_name'] is not None for e in observer.events)
            else:summary['changed_tdms']=sum(e['changed'] for e in observer.events)
            save(out/'summary.json',summary);checkpoint=read(out/'checkpoint.json');checkpoint['status']='COMPLETE';save(out/'checkpoint.json',checkpoint)
            print(json.dumps({'run':branch,'stage':stage,'summary':summary}),flush=True)
        save(run/'verification.json',{'status':'NORMALIZATION_COMPLETE','source_integrity':verify(),'generation_model':MODEL,'new_extraction_calls':0})
        return 0
    finally:lock.close()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--branch',required=True,choices=['partially','cold_default','cold_0','cold_42'])
    sys.exit(run_branch(parser.parse_args().branch))
