"""Unchanged official evaluators, fixed42 failure accounting, separate strict diagnostics."""
from pathlib import Path
import sys,os,json,copy,math,types,hashlib,argparse,decimal,collections
R=Path(__file__).resolve().parents[1];P=R.parents[1];ROOT=P.parent;REPO=ROOT/'emnlp2024-leaderboard-generation'
sys.dont_write_bytecode=True
os.environ.update(HF_HOME=str(R/'cache/local_evaluation'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false')
sys.path.insert(0,str(REPO));sys.path.insert(0,str(P/'autodl_setup/20261021/stage/adapters'))
from evaluate import ranking,ao
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f1(p,r):return 2*p*r/(p+r) if p+r else 0
def metric(p,r):return {'Precision':p,'Recall':r,'F1':f1(p,r)}
def number(v):
    try:
        d=decimal.Decimal(str(v).strip());return d if d.is_finite() else None
    except decimal.InvalidOperation:return None
def strict(gold,pred):
    per={};comparisons=[]
    for pid,g in gold.items():
        rows=pred[pid]['normalized_output'];grows=g['TDMs'];gs={number(x['Result']) for x in grows};ps={number(x['Result']) for x in rows};gs.discard(None);ps.discard(None)
        match=len(gs&ps);invalid={x['Result'] for x in rows if number(x['Result']) is None}
        rc=match/len(gs) if gs else 0;pc=match/(len(ps)+len(invalid)) if ps or invalid else 0
        def keys(seq):return collections.Counter((x['Task'],x['Dataset'],x['Metric'],number(x['Result'])) for x in seq if number(x['Result']) is not None)
        count=sum((keys(rows)&keys(grows)).values())
        per[pid]={'Result strict numeric unique':metric(pc,rc),'TDMR strict numeric one-to-one':metric(count/len(rows) if rows else 0,count/len(grows)), 'unparseable_results':sorted(invalid),'predictions':len(rows)}
        for i,grow in enumerate(grows):
            equal=[j for j,x in enumerate(rows) if number(x['Result']) is not None and number(x['Result'])==number(grow['Result'])]
            exact=[j for j in equal if all(rows[j][k]==grow[k] for k in ['Task','Dataset','Metric'])]
            fuzzy=[j for j,x in enumerate(rows) if str(grow['Result']) in x['Result'] or x['Result'] in str(grow['Result'])]
            comparisons.append({'paper_id':pid,'gold_index':i,'gold':grow,'strict_value_prediction_indices':equal,'strict_tdmr_prediction_indices':exact,'official_string_value_indices':fuzzy,'classification':'STRICT_TDMR_MATCH' if exact else ('VALUE_PRESENT_NAMES_OR_BINDING_DIFFER' if equal else 'VALUE_NOT_PRESENT'),'matching_predictions':[{'prediction_index':j,'prediction':rows[j]} for j in sorted(set(equal+fuzzy))]})
    agg={k:metric(sum(v[k]['Precision'] for v in per.values())/len(per),sum(v[k]['Recall'] for v in per.values())/len(per)) for k in ['Result strict numeric unique','TDMR strict numeric one-to-one']}
    return {'definition':'Auxiliary only. Entire-string Decimal equality; no percent stripping/scaling. Result unique numeric sets; TDMR one-to-one multiset intersection. Does not replace official substring metrics.','aggregate':agg,'per_paper':per,'gold_row_comparison':comparisons}
def evaluate(name,source,masked=None):
    import tdm_eval,leaderboard_eval
    out=R/'evaluation'/name
    if (out/'complete.json').exists():
        assert read(out/'complete.json')['source_sha256']==sha(source);return
    out.mkdir(parents=True,exist_ok=True);gold=read(R/'evaluation/gold_subset.json');boards=read(R/'evaluation/gold_leaderboards_subset.json');norm=read(source)
    ids=read(R/'config/scope42.json')['eligible_ids'];assert len(ids)==42 and sum(len(x['TDMs']) for x in gold.values())==259
    missing=[p for p in ids if p not in norm];pred={p:norm[p] if p in norm else {'normalized_output':[],'source_documents':[]} for p in ids}
    for p,x in pred.items():
        for row in x['normalized_output']:assert set(row)=={'Task','Dataset','Metric','Result'} and isinstance(row['Result'],str)
    normalized=out/'evaluation_input_fixed42.json';save(normalized,pred)
    save(out/'coverage.json',{'target_papers':42,'source_completed_papers':42-len(missing),'failed_empty_for_evaluation_only':missing,'effective_coverage':(42-len(missing))/42,'evaluation_gold_tdmrs':259,'gold_tdmrs_with_completed_output':sum(len(gold[p]['TDMs']) for p in ids if p in norm),'original_source':str(source),'source_sha256':sha(source)})
    tdm_eval.main(types.SimpleNamespace(gold_data_path=str(R/'evaluation/gold_subset.json'),normalized_tdm_output_path=str(normalized),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json')))
    aggregate=read(out/'eval_results.json');values=read(out/'eval_values.json');metrics={k+' IIM':metric(v['Precision'],v['Recall']) for k,v in aggregate['Individual'].items()}
    metrics['TDM']=metric(aggregate['Exact Match Precision wo Results'],aggregate['Exact Match Recall wo Results']);metrics['TDMR']=metric(aggregate['Exact Match Precision'],aggregate['Exact Match Recall'])
    save(out/'metrics_with_f1.json',{'aggregate':metrics,'F1_definition':'2PR/(P+R) from official paper-macro Precision and Recall; not mean per-paper F1','fixed_denominator':42,'gold_tdmrs':259})
    per={p:{k+' IIM':metric(v['Precision'][p],v['Recall'][p]) for k,v in values['Individual'].items()} for p in ids}
    for p in ids:per[p].update(TDM=metric(values['Exact Match Recall wo Precision'][p],values['Exact Match Recall wo Results'][p]),TDMR=metric(values['Exact Match Precision'][p],values['Exact Match Recall'][p]))
    save(out/'per_paper_metrics.json',per)
    masked_path=''
    if masked:
        masked_boards=read(masked);scoped=[{**b,'Leaderboard':{p:v for p,v in b['Leaderboard'].items() if p in ids}} for b in masked_boards];save(out/'masked_leaderboards_scope42.json',scoped);masked_path=str(out/'masked_leaderboards_scope42.json')
    leaderboard_eval.main(types.SimpleNamespace(gold_leaderboards_file=str(R/'evaluation/gold_leaderboards_subset.json'),normalized_output_file=str(normalized),masked_leaderboards_file=masked_path,eval_results_file=str(out/'leaderboard_official.json'),eval_values_file=str(out/'leaderboard_values.json')))
    converted=copy.deepcopy(boards);generated=leaderboard_eval.construct_output_leaderboards(converted,pred);hits=set();details=[]
    for x in pred.values():
        for row in x['normalized_output']:
            key=str((row['Task'],row['Dataset'],row['Metric']))
            if key in generated:hits.add(key)
    for b in converted:
        key=str((b['Task'],b['Dataset'],b['Metric']));gr=ranking(b['Leaderboard'],b['Metric']);pr=ranking(generated[key],b['Metric']);score,depths=ao([x['paper_id'] for x in gr],[x['paper_id'] for x in pr]);details.append({'tdm':key,'gold_ranking':gr,'predicted_ranking':pr,'AO_paper_ids':score,'depths':depths,'nonempty_finite_result':bool(pr)})
    save(out/'generated_leaderboards.json',generated)
    supplement={'gold_leaderboards':27,'gold_entries':131,'LR_exact_tdm_hit':len(hits)/27,'LR_nonempty_finite_result':sum(bool(x) for x in generated.values())/27,'AO_paper_id_macro_all_gold_boards':sum(x['AO_paper_ids'] for x in details)/27,'definitions':'Reuse audited ranking/ao. Ties paper_id; empty0; k=min lengths. Official RBO ranks distinct result values and is separate.','per_board':details};save(out/'leaderboard_supplementary.json',supplement)
    extra=strict(gold,pred);save(out/'strict_numeric_auxiliary.json',extra)
    lines=['# 逐条 Gold 对照（离线诊断）','','预测索引从0开始。数值存在但名称或绑定不同，并不单凭该检查认定 Baseline 混入。','','|论文|Gold索引|Gold TDMR|严格数值对应预测|严格TDMR对应预测|分类|','|---|---:|---|---|---|---|']
    for x in extra['gold_row_comparison']:lines.append('|'+ '|'.join([x['paper_id'],str(x['gold_index']),json.dumps(x['gold'],ensure_ascii=False).replace('|','\\|'),str(x['strict_value_prediction_indices']),str(x['strict_tdmr_prediction_indices']),x['classification']])+'|')
    (out/'tdmr_comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    save(out/'complete.json',{'source_sha256':sha(source),'official_tdm_eval_sha256':sha(REPO/'tdm_eval.py'),'official_leaderboard_eval_sha256':sha(REPO/'leaderboard_eval.py'),'new_model_calls':0,'fixed_scope42':True})
    print(json.dumps({'evaluation':name,'TDMR_F1':metrics['TDMR']['F1'],'coverage':42-len(missing)}))
def main():
    a=argparse.ArgumentParser();a.add_argument('--gpt-only',action='store_true');args=a.parse_args()
    for name,path in [('gpt41_fully_llm',P/'full43_uncapped/merged/normalized_output.json'),('gpt41_fully_cs',P/'full43_cs/normalization/embedding_normalized_output.json'),('gpt41_partially_stage1',P/'full43_partially/stage1/normalized_output.json'),('gpt41_partially_stage2',P/'full43_partially/stage2/leaderboard_normalized_output.json')]:evaluate(name,path)
    if args.gpt_only:return
    S=R/'remote_snapshot'
    for name,path in [('llama3_fully_llm',S/'normalization/fully_llm/normalization/normalized_output.json'),('llama3_fully_cs',S/'normalization/fully_cs/normalized_output.json'),('llama3_partially_stage1',S/'normalization/partially/stage1/partially_masked_normalization/partially_masked_normalized_output.json'),('llama3_partially_stage2',S/'normalization/partially/stage2/leaderboard_normalized_output.json')]:
        if path.exists():evaluate(name,path, S/'normalization/partially/stage1/partially_masked_normalization/partially_masked_leaderboards.json' if 'partially' in name else None)
if __name__=='__main__':main()
