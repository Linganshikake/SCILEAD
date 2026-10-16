"""Unmodified official CS main with local CPU loading, diagnostic hooks and checkpoints."""
import argparse,inspect,time,types
from cs_common import *
def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0';verify();config=read(RUN/'config.json');start=time.monotonic()
    # Only prevent network during this local-only stage; no global filesystem interception.
    def network_guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Local CS inference must remain offline')
    sys.addaudithook(network_guard)
    import torch
    from sentence_transformers import SentenceTransformer,util
    torch.set_num_threads(4);torch.manual_seed(0)
    assert inspect.signature(util.semantic_search).parameters['score_function'].default is util.cos_sim
    print('LOAD_CPU_FP32',memory(),flush=True)
    encoder=SentenceTransformer(str(SNAPSHOT),device='cpu',trust_remote_code=True,local_files_only=True,model_kwargs={'torch_dtype':torch.float32,'code_revision':CODE_REV},config_kwargs={'code_revision':CODE_REV},tokenizer_kwargs={'code_revision':CODE_REV})
    assert str(encoder.device)=='cpu' and {str(p.dtype) for p in encoder.parameters()}=={'torch.float32'}
    load_seconds=time.monotonic()-start;probe=encoder.encode(['Named Entity Recognition','Accuracy','CoNLL-2003 - English'],convert_to_tensor=True);assert tuple(probe.shape)==(3,1024) and torch.isfinite(probe).all();sim=util.cos_sim(probe,probe);assert torch.isfinite(sim).all() and torch.allclose(sim.diag(),torch.ones(3),atol=1e-5)
    save(RUN/'model_load_validation.json',{'status':'PASS','device':str(encoder.device),'dtype':str(probe.dtype),'shape':list(probe.shape),'finite':True,'similarity_diagonal':sim.diag().tolist(),'load_seconds':load_seconds,'memory':memory(),'tokenizer_class':type(encoder.tokenizer).__name__,'module_classes':[type(m).__name__ for m in encoder],'config_class_module':type(encoder[0].auto_model.config).__module__,'model_class_module':type(encoder[0].auto_model).__module__,'prompts':encoder.prompts,'default_prompt_name':encoder.default_prompt_name,'environment_changed':False})
    print('LOAD_AND_SMOKE_PASS',load_seconds,memory(),flush=True)
    import tdm_embedding_normalization as official
    raw=read(RUN/'work/output.json');gold=read(Path(config['gold_path']));expected={k:list({t[k] for x in gold.values() for t in x['TDMs']}) for k in ('Task','Dataset','Metric')};audit_current={};original_search=util.semantic_search
    def factory(name,trust_remote_code):
        assert name==MODEL and trust_remote_code is True
        actual=inspect.currentframe().f_back.f_locals['labels_dict'];assert actual==expected
        if (RUN/'candidate_labels.json').exists():assert read(RUN/'candidate_labels.json')['labels']==actual
        save(RUN/'candidate_labels.json',{'python_hash_seed':0,'labels':actual,'sha256':{k:digest(v) for k,v in actual.items()},'source':'Actual labels_dict after original set-to-list conversion'})
        return encoder
    def traced_search(query,corpus,**kwargs):
        assert kwargs=={'top_k':1};frame=inspect.currentframe().f_back;loc=frame.f_locals;field=loc['key'];paper=loc['paper'];record=len(loc['normalized_tdms'])+1;labels=loc['labels_dict'][field]
        result=original_search(query,corpus,**kwargs);best=result[0][0];scores=util.cos_sim(query,corpus)[0];assert abs(float(scores[best['corpus_id']])-best['score'])<1e-6
        tied=torch.where(scores==scores.max())[0].tolist();assert best['corpus_id'] in tied
        audit_current[(paper,record,field)]={'paper_id':paper,'record':record,'field':field,'original':loc['tdm'][field],'exact_match':False,'selected':labels[best['corpus_id']],'top1_score':best['score'],'corpus_id':best['corpus_id'],'top1_tied_corpus_ids':tied,'candidate_sha256':digest(labels)}
        return result
    def progress(sequence,**kwargs):
        frame=inspect.currentframe().f_back
        def iterate():
            for paper in sequence:
                yield paper
                value=frame.f_locals['normalized_output'][paper];rows=json.loads(raw[paper]['output']);assert len(rows)==len(value['normalized_output']) and value['source_documents']==raw[paper]['source_documents'];records=[]
                for i,(r,n) in enumerate(zip(rows,value['normalized_output']),1):
                    assert r['Result']==n['Result']
                    for field in expected:
                        key=(paper,i,field)
                        if r[field] in expected[field]:
                            assert n[field]==r[field];item={'paper_id':paper,'record':i,'field':field,'original':r[field],'exact_match':True,'selected':n[field],'top1_score':None,'corpus_id':None,'top1_tied_corpus_ids':[],'candidate_sha256':digest(expected[field])}
                        else:item=audit_current[key];assert n[field]==item['selected']
                        records.append(item)
                folder=RUN/'normalization/papers'/Path(paper).stem;save(folder/'output.json',{paper:value});save(folder/'mapping.json',records);save(folder/'complete.json',{'status':'COMPLETE','records':len(rows),'source_sha256':digest(raw[paper]),'candidate_sha256':digest(expected),'memory':memory()})
                print('PAPER_COMPLETE',paper,len(rows),flush=True)
        return iterate()
    official.SentenceTransformer=factory;official.util=types.SimpleNamespace(semantic_search=traced_search);official.tqdm=types.SimpleNamespace(tqdm=progress)
    def completed(p):
        d=RUN/'normalization/papers'/Path(p).stem
        if not (d/'complete.json').exists():return False
        s=read(d/'complete.json');assert s['source_sha256']==digest(raw[p]) and s['candidate_sha256']==digest(expected);return True
    pending=[p for p in raw if not completed(p)]
    batches=[pending[:1],pending[1:]] if not (RUN/'pilot_pass.json').exists() else [pending]
    for bi,papers in enumerate(batches):
        if not papers:continue
        work=RUN/'work'/('pilot' if not (RUN/'pilot_pass.json').exists() else 'remaining');work.mkdir(exist_ok=True);save(work/'output.json',{p:raw[p] for p in papers})
        official.main(types.SimpleNamespace(seed=0,gold_tdm_path=config['gold_path'],tdm_output_path=work.as_posix()+'/'))
        if not (RUN/'pilot_pass.json').exists():
            sample=read(RUN/'normalization/papers'/Path(papers[0]).stem/'mapping.json');assert any(x['exact_match'] for x in sample) and any(not x['exact_match'] for x in sample);save(RUN/'pilot_pass.json',{'paper':papers[0],'status':'PASS','original_main_executed':True,'exact_and_cs_branches_tested':True,'top1_scores_and_selections_checked':True});print('PILOT_PASS_CONTINUE_ALL',flush=True)
    output={};audits=[]
    for paper in raw:
        assert completed(paper);d=RUN/'normalization/papers'/Path(paper).stem;output.update(read(d/'output.json'));audits+=read(d/'mapping.json')
    save(RUN/'normalization/embedding_normalized_output.json',output)
    with (RUN/'normalization/mapping_audit.jsonl').open('w',encoding='utf-8') as f:
        for x in audits:f.write(json.dumps(x,ensure_ascii=False)+'\n')
    verify();save(RUN/'normalization/summary.json',{'status':'COMPLETE','papers':len(output),'records':sum(len(x['normalized_output']) for x in output.values()),'exact_fields':sum(x['exact_match'] for x in audits),'cs_fields':sum(not x['exact_match'] for x in audits),'top1_tie_cases':sum(len(x['top1_tied_corpus_ids'])>1 for x in audits),'seconds':time.monotonic()-start,'memory':memory(),'new_llm_requests':0,'official_main_source_sha256':sha(REPO/'tdm_embedding_normalization.py')});print('ALL_COMPLETE',flush=True)
if __name__=='__main__':main()
