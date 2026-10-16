"""Read-only final verification; no model loading or network."""
from cs_common import *
def main():
    verify();inventory=read(RUN/'artifact_sha256.json')
    for p,h in inventory.items():assert sha(RUN/p)==h,p
    raw=read(BASE/'merged/output.json');norm=read(RUN/'normalization/embedding_normalized_output.json');labels=read(RUN/'candidate_labels.json')['labels'];audits=[json.loads(l) for l in (RUN/'normalization/mapping_audit.jsonl').read_text(encoding='utf-8').splitlines()]
    assert list(raw)==list(norm) and len(norm)==43 and len(audits)==852
    count=0
    for p in raw:
        r=json.loads(raw[p]['output']);n=norm[p]['normalized_output'];d=RUN/'normalization/papers'/Path(p).stem
        assert read(d/'output.json')=={p:norm[p]}
        assert read(d/'complete.json')['source_sha256']==digest(raw[p])
        assert read(d/'complete.json')['candidate_sha256']==digest(labels)
        assert len(r)==len(n) and norm[p]['source_documents']==raw[p]['source_documents']
        for x,y in zip(r,n):
            assert list(x)==list(y) and x['Result']==y['Result']
            for k in labels:
                assert y[k] in labels[k]
                if x[k] in labels[k]:assert x[k]==y[k]
        count+=len(r)
    assert count==284 and sum(x['exact_match'] for x in audits)==310
    metrics=read(RUN/'evaluation/metrics_with_f1.json');per=read(RUN/'evaluation/per_paper_metrics.json')
    for k,m in metrics['aggregate'].items():
        for item in ('Precision','Recall'):assert abs(m[item]-sum(v[k][item] for v in per.values())/43)<1e-12
        p,r=m['Precision'],m['Recall'];assert abs(m['F1']-(2*p*r/(p+r) if p+r else 0))<1e-12
    assert metrics['aggregate']['Result IIM']==read(BASE/'evaluation/metrics_with_f1.json')['aggregate']['Result IIM']
    print(json.dumps({'status':'PASS','artifacts_checked':len(inventory),'papers':43,'records':count,'frozen_inputs_and_dependencies_unchanged':True,'no_model_loaded':True}))
if __name__=='__main__':main()
