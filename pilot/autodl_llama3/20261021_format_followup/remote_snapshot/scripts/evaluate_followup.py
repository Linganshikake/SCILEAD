from pathlib import Path
import sys,os,json,importlib.util,types,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=R.parent/'20261021_formal42';S=R/'remote_snapshot'
spec=importlib.util.spec_from_file_location('verified_evaluation',OLD/'scripts/evaluate_scope.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
os.environ['HF_HOME']=str(R/'cache/local_evaluation')
read=e.read;save=e.save
def main():
    base=R/'format_v2';e.R=base
    for dest,src in [('config/scope42.json','config/scope42.json'),('evaluation/gold_subset.json','evaluation/gold_subset.json'),('evaluation/gold_leaderboards_subset.json','evaluation/gold_leaderboards_subset.json')]:
        p=base/dest;p.parent.mkdir(parents=True,exist_ok=True);data=(OLD/src).read_bytes()
        if p.exists():assert p.read_bytes()==data
        else:p.write_bytes(data)
    masked=S/'format_v2/normalization/partially_stage1/partially_masked_normalization/partially_masked_leaderboards.json'
    for stage in ['fully_llm','fully_cs','partially_stage1','partially_stage2']:
        src=S/'format_v2/normalization'/stage/'normalized_output.json'
        if src.exists():e.evaluate(stage,src,masked if 'partially' in stage else None)
    # Diagnostic evaluation has only the one authorized paper; never merged into fixed42.
    import tdm_eval
    gold=read(OLD/'evaluation/gold_subset.json');pid='2105.03654.pdf'
    for stage in ['fully_llm','fully_cs']:
        src=S/'token2048_diagnostic/normalization'/stage/'normalized_output.json'
        if not src.exists():continue
        out=R/'token2048_diagnostic/evaluation'/stage
        if (out/'complete.json').exists():assert read(out/'complete.json')['source_sha256']==e.sha(src);continue
        save(out/'gold_single.json',{pid:gold[pid]});pred=read(src);assert list(pred)==[pid]
        tdm_eval.main(types.SimpleNamespace(gold_data_path=str(out/'gold_single.json'),normalized_tdm_output_path=str(src),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json')))
        agg=read(out/'eval_results.json');metrics={k+' IIM':e.metric(v['Precision'],v['Recall']) for k,v in agg['Individual'].items()};metrics['TDM']=e.metric(agg['Exact Match Precision wo Results'],agg['Exact Match Recall wo Results']);metrics['TDMR']=e.metric(agg['Exact Match Precision'],agg['Exact Match Recall'])
        save(out/'metrics_with_f1.json',metrics);save(out/'strict_numeric_auxiliary.json',e.strict({pid:gold[pid]},pred));save(out/'complete.json',{'source_sha256':e.sha(src),'paper_count':1,'separate_from_main42':True})
if __name__=='__main__':main()
