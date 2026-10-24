"""Original CS main with pinned local CPU loader and observational checkpoints."""
from pathlib import Path
import os,sys,json,time,inspect,types,hashlib,resource
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead');OUT=R/'normalization/fully_cs'
sys.dont_write_bytecode=True
os.environ.update(HF_HOME=str(R/'cache'),HF_HUB_CACHE=str(R/'cache/hub'),HF_MODULES_CACHE=str(R/'cache/modules'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1')
sys.path.insert(0,str(ROOT/'source'))
def read(p):return json.loads(p.read_text())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2));t.replace(p)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False).encode()).hexdigest()
def main():
    assert os.environ['PYTHONHASHSEED']=='0';OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'complete.json').exists():print('SKIP_COMPLETE');return
    assert (R/'normalization/fully_llm/stage_complete.json').exists(),'Fully LLM must precede CS'
    t=time.monotonic();ref=read(R/'config/cs_reference.json');manifest=read(R/'config/cs_model_transfer.json')
    for x in manifest:assert sha(Path(x['path']))==x['sha256']
    def deny_network(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('OFFLINE_CS_ONLY')
    sys.addaudithook(deny_network)
    import torch
    from sentence_transformers import SentenceTransformer,util
    import tdm_embedding_normalization as official
    torch.set_num_threads(4);torch.manual_seed(0)
    rev=ref['model']['code_revision'];encoder=SentenceTransformer(str(ROOT/'models/bilingual-embedding-large'),device='cpu',trust_remote_code=True,local_files_only=True,model_kwargs={'torch_dtype':torch.float32,'code_revision':rev},config_kwargs={'code_revision':rev},tokenizer_kwargs={'code_revision':rev})
    assert {p.dtype for p in encoder.parameters()}=={torch.float32} and str(encoder.device)=='cpu'
    probes=[]
    for x in ref['probes']:
        labels=ref['candidate_labels'][x['field']];corpus=encoder.encode(labels,convert_to_tensor=True);query=encoder.encode(x['original'],convert_to_tensor=True);best=util.semantic_search(query,corpus,top_k=1)[0][0]
        observed=labels[best['corpus_id']];delta=abs(best['score']-x['top1_score']);assert observed==x['selected'] and delta<=ref['score_tolerance'],'CS_REFERENCE_MISMATCH'
        probes.append({'field':x['field'],'original':x['original'],'selected':observed,'prior_score':x['top1_score'],'actual_score':best['score'],'absolute_delta':delta})
    save(OUT/'model_validation.json',{'status':'PASS','model_revision':ref['model']['weight_revision'],'code_revision':rev,'device':'cpu','dtype':'float32','compared_existing_cpu_outputs':probes,'seconds':time.monotonic()-t})
    raw=read(R/'extraction/prepared_output.json');gold=read(ROOT/'data/gold/tdm_annotations.json');labels={k:list({row[k] for v in gold.values() for row in v['TDMs']}) for k in ['Task','Dataset','Metric']};save(OUT/'candidate_labels.json',labels)
    assert [len(labels[k]) for k in ['Task','Dataset','Metric']]==[23,71,26]
    def factory(name,trust_remote_code):
        assert name==ref['model']['model'] and trust_remote_code
        assert inspect.currentframe().f_back.f_locals['labels_dict']==labels
        return encoder
    original_search=util.semantic_search;events=[]
    def search(q,c,**kw):
        assert kw=={'top_k':1};loc=inspect.currentframe().f_back.f_locals;result=original_search(q,c,**kw);best=result[0][0];k=loc['key']
        events.append({'paper_id':loc['paper'],'record':len(loc['normalized_tdms']),'field':k,'original':loc['tdm'][k],'selected':loc['labels_dict'][k][best['corpus_id']],'top1_score':best['score'],'corpus_id':best['corpus_id']})
        return result
    def progress(sequence,**kw):
        frame=inspect.currentframe().f_back
        def iterator():
            for p in sequence:
                yield p
                normalized=frame.f_locals['normalized_output'][p];rows=json.loads(raw[p]['output']);assert len(rows)==len(normalized['normalized_output'])
                for a,b in zip(rows,normalized['normalized_output']):assert str(a['Result'])==b['Result']
                save(OUT/'papers'/p.removesuffix('.pdf')/'normalized_output.json',{p:normalized})
                save(OUT/'papers'/p.removesuffix('.pdf')/'mapping.json',[x for x in events if x['paper_id']==p])
                save(OUT/'papers'/p.removesuffix('.pdf')/'complete.json',{'input_sha256':digest(raw[p]),'candidate_sha256':digest(labels),'records':len(rows)})
                print('CS_PAPER_COMPLETE',p,len(rows),flush=True)
        return iterator()
    official.SentenceTransformer=factory;official.util=types.SimpleNamespace(semantic_search=search);official.tqdm=types.SimpleNamespace(tqdm=progress)
    pending={}
    for p,v in raw.items():
        marker=OUT/'papers'/p.removesuffix('.pdf')/'complete.json'
        if marker.exists():assert read(marker)['input_sha256']==digest(v) and read(marker)['candidate_sha256']==digest(labels)
        else:pending[p]=v
    work=OUT/'work';save(work/'output.json',pending)
    if pending:official.main(types.SimpleNamespace(seed=0,gold_tdm_path=str(ROOT/'data/gold/tdm_annotations.json'),tdm_output_path=str(work)+'/'))
    merged={}
    for p in raw:merged.update(read(OUT/'papers'/p.removesuffix('.pdf')/'normalized_output.json'))
    save(OUT/'normalized_output.json',merged);save(OUT/'complete.json',{'status':'COMPLETE','papers':len(merged),'records':sum(len(v['normalized_output']) for v in merged.values()),'seconds':time.monotonic()-t,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'paid_api_calls':0,'method':'unchanged official tdm_embedding_normalization.main'})
if __name__=='__main__':main()
