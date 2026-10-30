"""Invoke unchanged official tuple evaluation on all 43 Fully+CS papers."""
import contextlib
from types import SimpleNamespace
from cs_common import *

def metric(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0.0}

def main():
    setup();verify()
    assert read(RUN/'normalization/summary.json')['status']=='COMPLETE'
    import tdm_eval as official
    config=read(RUN/'config.json');out=RUN/'evaluation'
    args=SimpleNamespace(gold_data_path=config['gold_path'],normalized_tdm_output_path=str(RUN/'normalization/embedding_normalized_output.json'),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json'))
    save(out/'invocation.json',vars(args))
    with (out/'run.log').open('w',encoding='utf-8') as f,contextlib.redirect_stdout(f):official.main(args)
    r=read(out/'eval_results.json');v=read(out/'eval_values.json')
    aggregate={k+' IIM':metric(x['Precision'],x['Recall']) for k,x in r['Individual'].items()}
    aggregate['TDM Exact Match']=metric(r['Exact Match Precision wo Results'],r['Exact Match Recall wo Results'])
    aggregate['TDMR Exact Match']=metric(r['Exact Match Precision'],r['Exact Match Recall'])
    raw=read(RUN/'merged/output.json');norm=read(args.normalized_tdm_output_path);gold=read(args.gold_data_path)
    assert list(raw)==list(norm) and len(norm)==43
    raw_as_norm={p:{'normalized_output':json.loads(x['output'])} for p,x in raw.items()}
    raw_r,raw_p=official.calculate_ind_match(gold,raw_as_norm,'Result')
    assert raw_r==v['Individual']['Result']['Recall'] and raw_p==v['Individual']['Result']['Precision']
    per={}
    for p in norm:
        per[p]={k+' IIM':metric(x['Precision'][p],x['Recall'][p]) for k,x in v['Individual'].items()}
        per[p]['TDM Exact Match']=metric(v['Exact Match Recall wo Precision'][p],v['Exact Match Recall wo Results'][p])
        per[p]['TDMR Exact Match']=metric(v['Exact Match Precision'][p],v['Exact Match Recall'][p])
    save(out/'metrics_with_f1.json',{'aggregate':aggregate,'aggregation':'Unmodified official per-paper macro Precision/Recall; F1=2PR/(P+R), not mean per-paper F1','mean_per_paper_f1_SEPARATE':{k:sum(x[k]['F1'] for x in per.values())/43 for k in aggregate},'papers':43,'gold_tdmrs':295,'predicted_tdmrs':335,'result_iim_unchanged_from_raw_input':True,'official_main_executed':True,'official_source_sha256':sha(REPO/'tdm_eval.py')})
    save(out/'per_paper_metrics.json',per)
    verify();print(json.dumps(aggregate),flush=True)

if __name__=='__main__':main()
