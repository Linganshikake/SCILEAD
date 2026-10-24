"""Offline scope preparation and unchanged official evaluation of existing GPT predictions."""
from pathlib import Path
import json,subprocess,hashlib,sys,os
R=Path(__file__).resolve().parents[1];PILOT=Path(r'D:\C++\SCILEAD\pilot');SOURCE=Path(r'D:\C++\SCILEAD\emnlp2024-leaderboard-generation')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    manifest=read(R/'experiment_manifest.json');ids=[x['paper_id'] for x in manifest['papers'] if x['eligible']]
    gold=read(PILOT/'autodl_setup/20261021/stage/data/gold/tdm_annotations.json');boards=read(PILOT/'autodl_setup/20261021/stage/data/gold/leaderboards.json')
    derived={p:gold[p] for p in ids};scoped=[{**b,'Leaderboard':{p:v for p,v in b['Leaderboard'].items() if p in ids}} for b in boards]
    assert len(ids)==42 and sum(len(x['TDMs']) for x in derived.values())==259
    assert len(scoped)==27 and min(len(b['Leaderboard']) for b in scoped)>=3
    out=R/'evaluation/gpt41_reference_scope42';save(out/'gold_subset.json',derived);save(out/'gold_leaderboards_subset.json',scoped)
    norm=read(PILOT/'full43_uncapped/merged/normalized_output.json');save(out/'normalized_output.json',{p:norm[p] for p in ids})
    args=[str(SOURCE/'tdm_eval.py'),'--gold_data_path',str(out/'gold_subset.json'),'--normalized_tdm_output_path',str(out/'normalized_output.json'),'--eval_results_path',str(out/'eval_results.json'),'--eval_values_path',str(out/'eval_values.json')]
    env=os.environ.copy();env.update(PYTHONUTF8='1',HF_HOME=str(R/'cache/huggingface'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    p=subprocess.run([sys.executable,'-X','utf8',*args],text=True,encoding='utf-8',capture_output=True,env=env);assert p.returncode==0,p.stderr
    save(out/'invocation.json',{'argv':args,'official_script_sha256':hashlib.sha256((SOURCE/'tdm_eval.py').read_bytes()).hexdigest(),'new_llm_requests':0,'is_llama_evaluation':False})
    values=read(out/'eval_results.json');metrics={}
    for k,v in values['Individual'].items():metrics[k+' IIM']=v
    metrics['TDM Exact Match']={'Precision':values['Exact Match Precision wo Results'],'Recall':values['Exact Match Recall wo Results']}
    metrics['TDMR Exact Match']={'Precision':values['Exact Match Precision'],'Recall':values['Exact Match Recall']}
    for x in metrics.values():x['F1']=2*x['Precision']*x['Recall']/(x['Precision']+x['Recall']) if x['Precision']+x['Recall'] else 0
    save(out/'metrics_with_f1.json',{'scope':'existing GPT-4.1 Fully LLM predictions on exactly 42 eligible papers; not Llama results','papers':42,'gold_tdmrs':259,'aggregate':metrics,'F1':'2PR/(P+R) on official macro P/R'})
    changes=[{'Task':b['Task'],'Dataset':b['Dataset'],'Metric':b['Metric'],'before':len(b['Leaderboard']),'after':len(s['Leaderboard'])} for b,s in zip(boards,scoped) if len(b['Leaderboard'])!=len(s['Leaderboard'])]
    save(R/'config/scope42.json',{'eligible_ids':ids,'blocked_ids':['1912.08777.pdf'],'gold_tdmrs':259,'excluded_gold_tdmrs':36,'normalization_candidates_source':'FULL original 43 papers, 23 Task / 71 Dataset / 26 Metric','evaluation_gold_source':'derived scope only; original Gold unchanged','leaderboards':27,'leaderboard_entries_original':140,'leaderboard_entries_scoped':131,'all_scoped_boards_still_at_least_three':True,'changed_leaderboards':changes,'formal_scope_approved':False})
    print(json.dumps({'gpt_reference_scope':42,'gold':259,'tdmr_f1':metrics['TDMR Exact Match']['F1'],'new_model_calls':0}))
if __name__=='__main__':main()
