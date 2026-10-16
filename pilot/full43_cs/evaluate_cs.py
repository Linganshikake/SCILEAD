"""Official evaluation plus offline, paired diagnostics. No model initialization."""
import collections,contextlib,types
from decimal import Decimal,InvalidOperation
from cs_common import *

def metric(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0.0}
def number(x):
    try:
        d=Decimal(str(x));return d if d.is_finite() else None
    except InvalidOperation:return None
def strict(a,b):return number(a) is not None and number(a)==number(b)
def tdm(a,b):return all(a[k]==b[k] for k in ('Task','Dataset','Metric'))
def strict_metric(rows,g):
    pn={number(r['Result']) for r in rows};gn={number(r['Result']) for r in g};common=(pn&gn)-{None}
    pd=len(pn-{None})+len({r['Result'] for r in rows if number(r['Result']) is None});gd=len(gn-{None})+len({str(r['Result']) for r in g if number(r['Result']) is None})
    return metric(len(common)/pd if pd else 0,len(common)/gd if gd else 0)
def main():
    setup();verify();assert read(RUN/'normalization/summary.json')['status']=='COMPLETE'
    config=read(RUN/'config.json');gold=read(config['gold_path']);raw=read(BASE/'merged/output.json');old=read(BASE/'merged/normalized_output.json');new=read(RUN/'normalization/embedding_normalized_output.json');labels=read(RUN/'candidate_labels.json')['labels']
    assert list(raw)==list(old)==list(new) and len(new)==43
    out=RUN/'evaluation';out.mkdir(exist_ok=True)
    import tdm_eval
    args=types.SimpleNamespace(gold_data_path=config['gold_path'],normalized_tdm_output_path=str(RUN/'normalization/embedding_normalized_output.json'),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json'))
    save(out/'invocation.json',vars(args))
    with (out/'run.log').open('w',encoding='utf-8') as f,contextlib.redirect_stdout(f):tdm_eval.main(args)
    r=read(out/'eval_results.json');v=read(out/'eval_values.json');oldv=read(BASE/'evaluation/eval_values.json');oldm=read(BASE/'evaluation/metrics_with_f1.json')['aggregate']
    aggregate={k+' IIM':metric(x['Precision'],x['Recall']) for k,x in r['Individual'].items()};aggregate['TDM Exact Match']=metric(r['Exact Match Precision wo Results'],r['Exact Match Recall wo Results']);aggregate['TDMR Exact Match']=metric(r['Exact Match Precision'],r['Exact Match Recall'])
    per={};paired=[];goldrows=[];counts=collections.Counter();strict_per={}
    for p in new:
        a=json.loads(raw[p]['output']);b=old[p]['normalized_output'];c=new[p]['normalized_output'];g=gold[p]['TDMs']
        assert len(a)==len(b)==len(c) and raw[p]['source_documents']==old[p]['source_documents']==new[p]['source_documents']
        per[p]={k+' IIM':metric(x['Precision'][p],x['Recall'][p]) for k,x in v['Individual'].items()};per[p]['TDM Exact Match']=metric(v['Exact Match Recall wo Precision'][p],v['Exact Match Recall wo Results'][p]);per[p]['TDMR Exact Match']=metric(v['Exact Match Precision'][p],v['Exact Match Recall'][p])
        assert per[p]['Result IIM']==metric(oldv['Individual']['Result']['Precision'][p],oldv['Individual']['Result']['Recall'][p])
        strict_per[p]=strict_metric(c,g);assert strict_per[p]==strict_metric(b,g)
        for i,(ra,ll,cs) in enumerate(zip(a,b,c),1):
            assert isinstance(ra['Result'],str) and ra['Result']==ll['Result']==cs['Result']
            assert all(cs[k] in labels[k] for k in labels)
            llhit=[j+1 for j,z in enumerate(g) if tdm(ll,z) and strict(ll['Result'],z['Result'])];cshit=[j+1 for j,z in enumerate(g) if tdm(cs,z) and strict(cs['Result'],z['Result'])]
            category='both_strict_tdmr_match' if llhit and cshit else 'llm_only_strict_tdmr_match' if llhit else 'cs_only_strict_tdmr_match' if cshit else 'neither_strict_tdmr_match'
            counts[category]+=1
            comparisons={}
            for k in labels:
                kind='old_null_new_in_set' if ll[k] is None else 'same_name' if ll[k]==cs[k] else 'different_name';counts[k+':'+kind]+=1;comparisons[k]=kind
            paired.append({'paper':p,'record':i,'raw':ra,'llm':ll,'cs':cs,'field_comparison':comparisons,'llm_strict_gold_indices':llhit,'cs_strict_gold_indices':cshit,'category':category,'caveat':'Gold-supported tuple match is an offline diagnostic, not a semantic oracle for individual fields.'})
        for j,z in enumerate(g,1):
            numeric=[i+1 for i,x in enumerate(c) if strict(x['Result'],z['Result'])];lh=[i+1 for i,x in enumerate(b) if tdm(x,z) and strict(x['Result'],z['Result'])];ch=[i+1 for i,x in enumerate(c) if tdm(x,z) and strict(x['Result'],z['Result'])]
            goldrows.append({'paper':p,'gold_index':j,'gold':z,'strict_numeric_prediction_indices':numeric,'llm_strict_tdmr_prediction_indices':lh,'cs_strict_tdmr_prediction_indices':ch})
    strict_agg=metric(sum(x['Precision'] for x in strict_per.values())/43,sum(x['Recall'] for x in strict_per.values())/43)
    assert aggregate['Result IIM']==oldm['Result IIM'] and abs(strict_agg['F1']-0.5867817863240564)<1e-12
    save(out/'metrics_with_f1.json',{'aggregate':aggregate,'aggregation':'Unmodified official per-paper macro P/R; F1=2PR/(P+R), not mean per-paper F1','mean_per_paper_f1_SEPARATE':{k:sum(m[k]['F1'] for m in per.values())/43 for k in aggregate},'papers':43,'gold_tdmrs':295,'predicted_tdmrs':sum(len(x['normalized_output']) for x in new.values())})
    save(out/'per_paper_metrics.json',per);save(out/'strict_result_metrics.json',{'aggregate':strict_agg,'per_paper':strict_per,'unchanged_from_llm':True,'definition':'Finite Decimal equality, unique numeric values; distinct nonnumeric strings remain in denominators. Macro P/R then harmonic F1.'});save(out/'paired_records.json',paired);save(out/'paired_summary.json',dict(counts));save(out/'gold_alignment.json',goldrows)
    save(out/'comparison_with_llm_normalization.json',{k:{'LLM':oldm[k],'CS':x,'delta_F1':x['F1']-oldm[k]['F1']} for k,x in aggregate.items()})
    verify();print(json.dumps({'metrics':aggregate,'strict_result':strict_agg,'paired_counts':counts},ensure_ascii=False))
if __name__=='__main__':main()
