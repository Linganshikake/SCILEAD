"""Supplementary strict diagnostics; never replaces official evaluation."""
from decimal import Decimal,InvalidOperation
def strict_number(value):
    try:
        x=Decimal(str(value));return x if x.is_finite() else None
    except (InvalidOperation,ValueError):return None
def equal_number(a,b):return strict_number(a) is not None and strict_number(a)==strict_number(b)
def maximum_matching(pred,gold,compatible):
    edges=[[j for j,g in enumerate(gold) if compatible(p,g)] for p in pred];owner={}
    def augment(i,seen):
        for j in edges[i]:
            if j in seen:continue
            seen.add(j)
            if j not in owner or augment(owner[j],seen):owner[j]=i;return True
        return False
    for i in range(len(pred)):augment(i,set())
    return sorted((i,j) for j,i in owner.items())
def fields_equal(a,b):return all(a[k]==b[k] for k in ('Task','Dataset','Metric'))
def metric(matches,np,ng):
    p=matches/np if np else 0;r=matches/ng if ng else 0
    return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0,'matches':matches,'prediction_denominator':np,'gold_denominator':ng}
def diagnose(raw,pred,gold):
    strict_pairs=maximum_matching(pred,gold,lambda a,b:fields_equal(a,b) and equal_number(a['Result'],b['Result']))
    mapped={j:i for i,j in strict_pairs}
    unique_pred=list(dict.fromkeys(p['Result'] for p in pred));unique_gold=list(dict.fromkeys(str(g['Result']) for g in gold))
    result_pairs=maximum_matching(unique_pred,unique_gold,equal_number)
    rows=[]
    for j,g in enumerate(gold):
        numeric=[i for i,p in enumerate(pred) if equal_number(p['Result'],g['Result'])]
        correct_fields=[i for i in numeric if fields_equal(pred[i],g)]
        cat='STRICT_TDMR_MATCH' if j in mapped else 'DUPLICATE_ONE_TO_ONE_CONFLICT' if correct_fields else 'RESULT_MISSING_OR_VALUE_SCALE_ERROR' if not numeric else 'NUMERIC_MATCH_WITH_NULL_LABEL' if any(any(pred[i][k] is None for k in ('Task','Dataset','Metric')) for i in numeric) else 'NUMERIC_MATCH_LABEL_OR_BINDING_MISMATCH'
        rows.append({'gold_index':j,'gold':g,'matched_prediction_index':mapped.get(j),'numeric_prediction_indices':numeric,'category':cat,'raw_candidates':[raw[i] for i in numeric],'normalized_candidates':[pred[i] for i in numeric]})
    differences=[{'prediction_index':i,'gold_index':j,'predicted_result':p['Result'],'gold_result':str(g['Result']),'official_contains_match':str(g['Result']) in p['Result'] or p['Result'] in str(g['Result']),'strict_numeric_equal':equal_number(p['Result'],g['Result'])} for i,p in enumerate(pred) for j,g in enumerate(gold) if (str(g['Result']) in p['Result'] or p['Result'] in str(g['Result']))!=equal_number(p['Result'],g['Result'])]
    return {'strict_tdmr_one_to_one':metric(len(strict_pairs),len(pred),len(gold)),'strict_result_iim_one_to_one':metric(len(result_pairs),len(unique_pred),len(unique_gold)),'pairs':strict_pairs,'gold_rows':rows,'official_substring_vs_strict_pairs':differences,'extra_numeric_predictions':[{'prediction_index':i,'raw':raw[i],'normalized':p} for i,p in enumerate(pred) if not any(equal_number(p['Result'],g['Result']) for g in gold)],'duplicate_prediction_count':len(pred)-len({tuple(p.items()) for p in pred})}
