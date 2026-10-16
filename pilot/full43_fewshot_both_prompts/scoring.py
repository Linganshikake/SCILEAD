from common import *
import argparse, collections, decimal, shutil
def metric(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0.0}
def number(x):
    try:
        n=decimal.Decimal(str(x));return n if n.is_finite() else None
    except decimal.InvalidOperation:return None
def numeric(a,b):return number(a) is not None and number(a)==number(b)
def same_tdm(a,b):return all(a[k]==b[k] for k in ('Task','Dataset','Metric'))
def score(norm,raw,gold,coverage,out):
    res=read(out/'eval_results.json');vals=read(out/'eval_values.json');agg={k+' IIM':metric(v['Precision'],v['Recall']) for k,v in res['Individual'].items()};agg['TDM Exact Match']=metric(res['Exact Match Precision wo Results'],res['Exact Match Recall wo Results']);agg['TDMR Exact Match']=metric(res['Exact Match Precision'],res['Exact Match Recall'])
    per={};analysis={}
    for p in norm:
        pm={k+' IIM':metric(v['Precision'][p],v['Recall'][p]) for k,v in vals['Individual'].items()};pm['TDM Exact Match']=metric(vals['Exact Match Recall wo Precision'][p],vals['Exact Match Recall wo Results'][p]);pm['TDMR Exact Match']=metric(vals['Exact Match Precision'][p],vals['Exact Match Recall'][p]);per[p]=pm
        predictions=norm[p]['normalized_output'];original=json.loads(raw[p]['output']);gg=gold[p]['TDMs'];pn={number(x['Result']) for x in predictions};gn={number(x['Result']) for x in gg};intersection=(pn&gn)-{None};pd=len(pn-{None})+len({x['Result'] for x in predictions if number(x['Result']) is None});gd=len(gn-{None})+len({str(x['Result']) for x in gg if number(x['Result']) is None})
        rows=[]
        for i,g in enumerate(gg,1):
            numeric_idx=[j+1 for j,r in enumerate(predictions) if numeric(r['Result'],g['Result'])];exact=[j+1 for j,r in enumerate(predictions) if numeric(r['Result'],g['Result']) and same_tdm(r,g)]
            cat='correct' if exact else ('numeric_result_missing_or_changed' if not numeric_idx else 'normalization_null' if any(any(predictions[j-1][k] is None for k in ('Task','Dataset','Metric')) for j in numeric_idx) else 'numeric_match_but_binding_or_label_mismatch')
            rows.append({'gold_index':i,'gold':g,'strict_numeric_indices':numeric_idx,'strict_tdmr_indices':exact,'category':cat,'matching_predictions':[{'index':j,'raw':original[j-1],'normalized':predictions[j-1]} for j in numeric_idx]})
        discrepancies=[{'prediction':i+1,'gold':j+1,'predicted_result':a['Result'],'gold_result':b['Result']} for i,a in enumerate(predictions) for j,b in enumerate(gg) if ((str(b['Result']) in a['Result']) or (a['Result'] in str(b['Result'])))!=numeric(a['Result'],b['Result'])]
        analysis[p]={'strict_result_iim':metric(len(intersection)/pd if pd else 0,len(intersection)/gd if gd else 0),'gold_rows':rows,'category_counts':dict(collections.Counter(x['category'] for x in rows)),'substring_vs_strict_discrepancies':discrepancies,'extra_numeric_values':[{'index':i+1,'raw':original[i],'normalized':x} for i,x in enumerate(predictions) if not any(numeric(x['Result'],g['Result']) for g in gg)]}
    for k,v in agg.items():
        for score in ('Precision','Recall'):assert abs(v[score]-sum(x[k][score] for x in per.values())/len(per))<1e-12
    strict=metric(sum(x['strict_result_iim']['Precision'] for x in analysis.values())/len(analysis),sum(x['strict_result_iim']['Recall'] for x in analysis.values())/len(analysis))
    save(out/'metrics_with_f1.json',{'scope':coverage,'aggregate':agg,'per_paper':per,'strict_result_iim_auxiliary':strict,'aggregation':'Official per-paper macro P/R; F1=2PR/(P+R), not mean per-paper F1','official_source_sha256':sha(REPO/'tdm_eval.py')});save(out/'per_paper_metrics.json',per);save(out/'error_analysis.json',analysis)
    return agg,per,strict,analysis
