import contextlib,importlib.util,subprocess,types
from decimal import Decimal,InvalidOperation
from common import *
def metric(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0.0}
def number(x):
    try:
        d=Decimal(str(x));return d if d.is_finite() else None
    except InvalidOperation:return None
def strict_metric(rows,g):
    pn={number(r['Result']) for r in rows};gn={number(r['Result']) for r in g};common=(pn&gn)-{None}
    pd=len(pn-{None})+len({r['Result'] for r in rows if number(r['Result']) is None});gd=len(gn-{None})+len({str(r['Result']) for r in g if number(r['Result']) is None})
    return metric(len(common)/pd if pd else 0,len(common)/gd if gd else 0)
def evaluate_tdm(stage,path,conf):
    import tdm_eval
    out=RUN/'evaluation'/stage;out.mkdir(parents=True,exist_ok=True);gold=read(conf['gold_path']);norm=read(path);raw=read(conf['input_path']);assert set(norm)==set(raw) and list(norm)==read(RUN/'paper_order.json')['papers'] and len(norm)==43
    args=types.SimpleNamespace(gold_data_path=conf['gold_path'],normalized_tdm_output_path=str(path),eval_results_path=str(out/'eval_results.json'),eval_values_path=str(out/'eval_values.json'));save(out/'invocation.json',vars(args))
    with (out/'run.log').open('w',encoding='utf-8') as f,contextlib.redirect_stdout(f):tdm_eval.main(args)
    r=read(out/'eval_results.json');v=read(out/'eval_values.json');oldv=read(BASE/'evaluation/eval_values.json')
    aggregate={k+' IIM':metric(x['Precision'],x['Recall']) for k,x in r['Individual'].items()};aggregate['TDM Exact Match']=metric(r['Exact Match Precision wo Results'],r['Exact Match Recall wo Results']);aggregate['TDMR Exact Match']=metric(r['Exact Match Precision'],r['Exact Match Recall'])
    per={};strict_per={}
    for p in norm:
        rows=norm[p]['normalized_output'];assert [x['Result'] for x in rows]==[x['Result'] for x in json.loads(raw[p]['output'])] and norm[p]['source_documents']==raw[p]['source_documents']
        per[p]={k+' IIM':metric(x['Precision'][p],x['Recall'][p]) for k,x in v['Individual'].items()};per[p]['TDM Exact Match']=metric(v['Exact Match Recall wo Precision'][p],v['Exact Match Recall wo Results'][p]);per[p]['TDMR Exact Match']=metric(v['Exact Match Precision'][p],v['Exact Match Recall'][p])
        assert per[p]['Result IIM']==metric(oldv['Individual']['Result']['Precision'][p],oldv['Individual']['Result']['Recall'][p]);strict_per[p]=strict_metric(rows,gold[p]['TDMs'])
    strict_agg=metric(sum(x['Precision'] for x in strict_per.values())/43,sum(x['Recall'] for x in strict_per.values())/43)
    assert all(abs(aggregate['Result IIM'][k]-read(BASE/'evaluation/metrics_with_f1.json')['aggregate']['Result IIM'][k])<1e-14 for k in ('Precision','Recall','F1'))
    assert all(abs(strict_agg[k]-read(CS/'evaluation/strict_result_metrics.json')['aggregate'][k])<1e-14 for k in ('Precision','Recall','F1')) and strict_per==read(CS/'evaluation/strict_result_metrics.json')['per_paper']
    save(out/'metrics_with_f1.json',{'stage':stage,'input_path':str(path),'input_sha256':sha(path),'papers':43,'gold_tdmrs':295,'predictions':284,'aggregate':aggregate,'aggregation':'Official per-paper macro P/R. Additional F1 = harmonic mean of aggregate P/R, not arithmetic mean of per-paper F1.','mean_per_paper_f1_SEPARATE':{k:sum(x[k]['F1'] for x in per.values())/43 for k in aggregate}})
    save(out/'per_paper_metrics.json',per);save(out/'strict_result_metrics.json',{'aggregate':strict_agg,'per_paper':strict_per,'same_evaluator_definition_as_frozen_cs':True,'unchanged':True});print(stage,json.dumps(aggregate),flush=True)
def prepare_lb(scope,gold_path):
    out=RUN/'evaluation'/scope;out.mkdir(parents=True,exist_ok=True)
    for name in ('official','paper_metrics','leaderboards','reference'):(out/name).mkdir(exist_ok=True)
    changes=[]
    for name in ('run_official_leaderboard_eval.py','evaluate_paper_metrics.py'):
        origin=CS/'leaderboard_evaluation'/name;s=origin.read_text(encoding='utf-8')
        # Scope labels only. The audited formula code is not modified.
        s=s.replace('supplied 27 gold boards','supplied target gold boards').replace('all 27 gold boards','all target gold boards')
        s=s.replace('At least one exact normalized TDM match with finite numeric Result under original conversion. Exact-TDM-only alternative reported separately. No >=3 prediction filter is added.', 'LR is exact normalized TDM hit before numeric conversion. Finite-result nonempty-board rate is separately reported. No >=3 prediction filter is added.')
        (out/name).write_text(s,encoding='utf-8');changes.append({'file':name,'source_sha256':sha(origin),'copy_sha256':sha(out/name),'changes':'scope wording and LR primary label only; all formulas unchanged'})
    code=f'''import sys,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('partially_common',Path({str(TOP/'common.py')!r}))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
json,read,save,sha,REPO=c.json,c.read,c.save,c.sha,c.REPO
RUN=Path(__file__).resolve().parent
BASE=c.BASE
GOLD=Path({str(gold_path)!r})
NORMALIZED=c.RUN/'stage2/leaderboard_normalized_output.json'
def boundary():
    c.setup()
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Evaluation is offline')
    sys.addaudithook(guard)
def verify_frozen():return c.verify()
'''
    (out/'common.py').write_text(code,encoding='utf-8');save(out/'adapter_audit.json',{'copies':changes,'gold_path':str(gold_path),'target_boards':len(read(gold_path)),'predictions':'stage2','scope':'All 43 papers retained; only Gold leaderboard denominator restricted for masked_subset'})
    for name in ('run_official_leaderboard_eval.py','evaluate_paper_metrics.py'):
        with (out/(name+'.log')).open('w',encoding='utf-8') as f:r=subprocess.run([sys.executable,'-B','-X','utf8',str(out/name)],stdout=f,stderr=subprocess.STDOUT)
        assert r.returncode==0,f'{scope}/{name} failed; inspect log'
    print(scope,json.dumps(read(out/'paper_metrics/leaderboard_metrics.json')['aggregate']),flush=True)
def main():
    setup();verify();conf=read(RUN/'config.json')
    for stage,path in [('stage1',RUN/'stage1/normalized_output.json'),('stage2',RUN/'stage2/leaderboard_normalized_output.json')]:
        assert read(RUN/stage/'summary.json')['status']=='COMPLETE';evaluate_tdm(stage,path,conf)
    prepare_lb('all27',conf['leaderboards_path']);prepare_lb('masked10',TOP/'references/masked10.json')
    verify()
if __name__=='__main__':main()
