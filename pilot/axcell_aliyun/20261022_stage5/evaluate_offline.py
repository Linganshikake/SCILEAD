"""Original official evaluation, scoped comparisons, separate strict diagnostics."""
import os,sys,json,hashlib,csv,copy,contextlib,importlib.util,statistics,subprocess
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
from datetime import datetime,timezone
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=Path(r'D:\C++\SCILEAD');REPO=ROOT/'emnlp2024-leaderboard-generation';P4=OUT.parent/'20261022_stage4_preparation';REF=ROOT/'pilot/leaderboard_eval_full43_uncapped'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LANGCHAIN_TRACING='false',LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false')
def guard(event,args):
    if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Evaluation is strictly offline')
    if event=='open' and isinstance(args[0],(str,bytes)):
        path=Path(os.fsdecode(args[0]));s=path.as_posix().lower()
        if path.name.lower().endswith('.env') or any(x in s for x in ('/.codex/','/.claude/','/.aws/')):raise RuntimeError('No credentials/config access during evaluation')
sys.addaudithook(guard)
sys.path.insert(0,str(REPO));import tdm_eval as official;import leaderboard_eval as board_official
sys.path.insert(0,str(REF));import evaluate_paper_metrics as existing_board_diagnostics
from diagnostics import diagnose,equal_number
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def md(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf-8')
def metrics(p,r):return {'Precision':p,'Recall':r,'F1':2*p*r/(p+r) if p+r else 0}
def tdm_eval(normpath,folder,goldpath):
    folder.mkdir(parents=True,exist_ok=True)
    args=SimpleNamespace(gold_data_path=str(goldpath),normalized_tdm_output_path=str(normpath),eval_results_path=str(folder/'eval_results.json'),eval_values_path=str(folder/'eval_values.json'))
    save(folder/'official_invocation.json',vars(args));official.main(args)
    r=read(folder/'eval_results.json');v=read(folder/'eval_values.json')
    agg={k+' IIM':metrics(x['Precision'],x['Recall']) for k,x in r['Individual'].items()}
    agg.update({'TDM Exact Match':metrics(r['Exact Match Precision wo Results'],r['Exact Match Recall wo Results']),'TDMR Exact Match':metrics(r['Exact Match Precision'],r['Exact Match Recall'])})
    per={}
    for pid in read(normpath):
        per[pid]={k+' IIM':metrics(x['Precision'][pid],x['Recall'][pid]) for k,x in v['Individual'].items()}
        per[pid].update({'TDM Exact Match':metrics(v['Exact Match Recall wo Precision'][pid],v['Exact Match Recall wo Results'][pid]),'TDMR Exact Match':metrics(v['Exact Match Precision'][pid],v['Exact Match Recall'][pid])})
    for k in agg:
        assert abs(agg[k]['Precision']-statistics.mean(p[k]['Precision'] for p in per.values()))<1e-12
        assert abs(agg[k]['Recall']-statistics.mean(p[k]['Recall'] for p in per.values()))<1e-12
    save(folder/'metrics_with_f1.json',{'aggregation':'Original per-paper Macro P and R; F1=2PR/(P+R), not average paper F1','papers':len(per),'aggregate':agg,'f1_source':'Additional arithmetic from official P/R'})
    save(folder/'per_paper_metrics.json',per);return agg,per
def leaderboard(normpath,folder,scoped_gold_path):
    folder.mkdir(parents=True,exist_ok=True)
    args=SimpleNamespace(gold_leaderboards_file=str(scoped_gold_path),masked_leaderboards_file='',normalized_output_file=str(normpath),eval_results_file=str(folder/'eval_results.json'),eval_values_file=str(folder/'eval_values.json'))
    save(folder/'official_invocation.json',vars(args));board_official.main(args)
    gold=read(scoped_gold_path);norm=read(normpath);pred=board_official.construct_output_leaderboards(gold,norm)
    assert board_official.evaluate(pred,gold)==read(folder/'eval_values.json')['gold_results']
    save(folder/'generated_leaderboards.json',pred);save(folder/'gold_after_official_conversion.json',gold)
    keys={str((g['Task'],g['Dataset'],g['Metric'])) for g in gold}
    hit={str((t['Task'],t['Dataset'],t['Metric'])) for paper in norm.values() for t in paper['normalized_output']} & keys
    ev=read(folder/'eval_results.json')['gold_results'];by=[]
    for g in gold:
        key=str((g['Task'],g['Dataset'],g['Metric']));pv=pred[key];gv=g['Leaderboard']
        gr=existing_board_diagnostics.ranking(gv,g['Metric']);pr=existing_board_diagnostics.ranking(pv,g['Metric'])
        ao,depths=existing_board_diagnostics.ao([r['paper_id'] for r in gr],[r['paper_id'] for r in pr])
        # Strict joint coverage uses exact same paper and official-converted numerical Result, separate from official RC.
        joint=sum(p in gv and equal_number(v,gv[p]) for p,v in pv.items())/len(gv)
        by.append({'tdm_key':key,'gold_entries':len(gv),'predicted_entries':len(pv),'exact_tdm_hit':key in hit,'valid_nonempty':bool(pv),'AO_paper_id':ao,'AO_depths':depths,'gold_ranking':gr,'predicted_ranking':pr,'strict_joint_paper_result_coverage':joint})
    agg={'gold_boards':len(gold),'gold_entries':sum(len(g['Leaderboard']) for g in gold),'LR_exact_TDM':len(hit)/len(gold),'valid_nonempty_board_rate':sum(bool(x) for x in pred.values())/len(gold),'PC_official':ev['Paper Coverage'],'RC_official':ev['Result Coverage'],'RBO_official_numeric_lists':ev['RBO'],'AO_paper_ID_supplementary':statistics.mean(x['AO_paper_id'] for x in by),'strict_joint_paper_result_coverage':statistics.mean(x['strict_joint_paper_result_coverage'] for x in by)}
    save(folder/'metrics.json',{'aggregate':agg,'official':['PC','RC','RBO'],'supplementary':['LR_exact_TDM','valid_nonempty_board_rate','AO_paper_ID_supplementary','strict_joint_paper_result_coverage'],'AO_definition':'Reuse frozen implementation: k=min(lengths), average top-d ID overlap/d, empty=0, tie by paperID lexicographic; all27 boards Macro','duplicate_policy':'Original per-paper dictionary assignment, last matching numeric tuple overwrites previous; no manual dedup or repair','by_leaderboard':by});return agg
def main():
    test_results=[]
    for name in ('test_ledger.py','test_diagnostics.py','test_integrity.py'):
        result=subprocess.run([sys.executable,'-B',str(OUT/name)],capture_output=True,text=True,encoding='utf-8',env=dict(os.environ,PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1'))
        test_results.append({'file':name,'sha256':sha(OUT/name),'returncode':result.returncode,'output':result.stdout+result.stderr})
    save(OUT/'evaluation/test_evidence.json',test_results)
    tests_passed=all(t['returncode']==0 for t in test_results);assert tests_passed
    finish=read(OUT/'execution_finished.json');assert finish['status']=='COMPLETE' and finish['completed_papers']==37
    normpath=OUT/'merged/normalized_output.json';norm=read(normpath);raw=read(OUT/'merged/output.json');assert len(norm)==37 and set(norm)==set(raw)
    from run_normalization import verified_output
    for pid in norm:
        folder=OUT/'papers'/pid;state=read(folder/'state.json');assert state['status']=='COMPLETE'
        assert norm[pid]==verified_output(folder,OUT/'normalized_outputs'/pid/'normalized_output.json',state)[pid]
    meta=read(ROOT/'pilot/full43_uncapped/manifest.json');goldpath=Path(meta['gold_path']);gold=read(goldpath);assert sha(goldpath)==meta['gold_sha256']
    boardspath=goldpath.with_name('leaderboards.json');goldboards=read(boardspath)
    baselinepath=ROOT/'pilot/full43_uncapped/merged/normalized_output.json';baseline=read(baselinepath)
    tracked=[goldpath,boardspath,baselinepath,REPO/'tdm_eval.py',REPO/'leaderboard_eval.py',REPO/'tdm_llm_normalization.py',REF/'evaluate_paper_metrics.py']
    before={str(p):sha(p) for p in tracked};save(OUT/'evaluation/frozen_sources_before.json',before)
    normalized_records=sum(len(v['normalized_output']) for v in norm.values());assert normalized_records==65
    for pid in norm:assert [r['Result'] for r in norm[pid]['normalized_output']]==[r['Result'] for r in json.loads(raw[pid]['output'])]
    agg,per=tdm_eval(normpath,OUT/'evaluation',goldpath)
    scopedboards=copy.deepcopy(goldboards)
    for b in scopedboards:b['Leaderboard']={p:v for p,v in b['Leaderboard'].items() if p in norm};assert b['Leaderboard']
    assert len(scopedboards)==27 and sum(len(b['Leaderboard']) for b in scopedboards)==119
    scopepath=OUT/'evaluation/gold_leaderboards_scoped37.json';save(scopepath,scopedboards)
    lb=leaderboard(normpath,OUT/'evaluation/leaderboard',scopepath)
    base_subset={p:baseline[p] for p in norm};basepath=OUT/'evaluation/comparison_gpt41_same37/normalized_input.json';save(basepath,base_subset)
    gpt_agg,gpt_per=tdm_eval(basepath,basepath.parent,goldpath);gpt_lb=leaderboard(basepath,basepath.parent/'leaderboard',scopepath)
    diagnostic={p:diagnose(json.loads(raw[p]['output']),norm[p]['normalized_output'],gold[p]['TDMs']) for p in norm}
    save(OUT/'evaluation/strict_diagnostics.json',diagnostic)
    strict={k:metrics(statistics.mean(d[k]['Precision'] for d in diagnostic.values()),statistics.mean(d[k]['Recall'] for d in diagnostic.values())) for k in ('strict_tdmr_one_to_one','strict_result_iim_one_to_one')}
    save(OUT/'evaluation/strict_metrics.json',{'scope':'same37, zero-prediction papers included','aggregate':strict,'definition':'Decimal exact finite numeric equality, no percent scaling or substring; maximum-cardinality one-to-one pairing per paper; original counts retained','official_metrics_replaced':False})
    counts=Counter(r['category'] for d in diagnostic.values() for r in d['gold_rows']);diffs=sum(len(d['official_substring_vs_strict_pairs']) for d in diagnostic.values());extra=sum(len(d['extra_numeric_predictions']) for d in diagnostic.values())
    coverage={'selected_available_tex_papers':39,'parsed_and_extracted':37,'normalized':37,'nonempty':28,'valid_empty':9,'normalized_records':65,'official_eval_papers':37,'evaluated_gold_tdmrs':sum(len(gold[p]['TDMs']) for p in norm),'selected39_gold':283,'full_dataset_papers':43,'full_dataset_gold':295,'author36_membership':'UNVERIFIED','parse_failed':['1905.03197.pdf','2203.16804.pdf'],'no_verified_tex':['128538.pdf','D19-1367.pdf','C18-1139.pdf','D18-1105.pdf'],'gold_leaderboards':27,'gold_leaderboard_entries':119,'no_rethreshold_after_paper_restriction':True,'boards_below_three_after_restriction':sum(len(b['Leaderboard'])<3 for b in scopedboards)}
    save(OUT/'evaluation/coverage.json',coverage)
    save(OUT/'metrics.json',{'scope':coverage,'official_tuple_metrics':agg,'leaderboard':lb,'strict_supplementary':strict,'gpt41_same37':{'tuple_metrics':gpt_agg,'leaderboard':gpt_lb}})
    lines=['# 逐条Gold与AxCell输出对照（标准化完成后离线分析）','','严格匹配采用一对一数值相等，官方包含匹配指标另存。标签/绑定不一致不自动等于标准化模型错误；抽取与命名歧义须结合来源判定。','', '| 论文 / Gold序号 | Gold T/D/M/R | 严格匹配预测序号(0基) | 数值对应预测：原始→标准化 | 分类 |','|---|---|---|---|---|']
    def cell(x):return json.dumps(x,ensure_ascii=False).replace('|','/').replace('\n',' ')
    for pid,d in diagnostic.items():
        for r in d['gold_rows']:lines.append('| '+' | '.join([pid+'/'+str(r['gold_index']),cell(r['gold']),str(r['matched_prediction_index']),cell({'indices':r['numeric_prediction_indices'],'raw':r['raw_candidates'],'normalized':r['normalized_candidates']}),r['category']])+' |')
    md(OUT/'evaluation/tdmr_comparison.md','\n'.join(lines))
    errors={'gold_diagnostic_categories':dict(counts),'substring_vs_strict_pair_disagreements':diffs,'extra_numeric_prediction_records':extra,'known_source_errors_preserved':read(P4/'record_provenance.json'),'scope_warning':'Heuristic categories, no manual correction, extra values do not automatically prove Baseline contamination; no percent scaling in strict tuple diagnostic'}
    save(OUT/'evaluation/error_analysis.json',errors)
    rows='\n'.join(f"| {k} | {v['Precision']*100:.4f} | {v['Recall']*100:.4f} | {v['F1']*100:.4f} |" for k,v in agg.items())
    comparison='\n'.join(f"| {k} | {v['F1']*100:.4f} | {gpt_agg[k]['F1']*100:.4f} | {(v['F1']-gpt_agg[k]['F1'])*100:+.4f} |" for k,v in agg.items())
    lbcompare='\n'.join(f"| {k} | {lb[k]*100:.4f} | {gpt_lb[k]*100:.4f} |" for k in lb if k not in ('gold_boards','gold_entries'))
    md(OUT/'comparison_with_gpt41.md',f'''# 同范围与冻结GPT-4.1结果比较

双方都使用同一37篇（含9篇AxCell零预测），相同完整候选名称集合和官方评价函数。GPT-4.1只读取冻结full43_uncapped预测，不重新调用模型。排行榜为原27榜按37paper IDs限制后的119条Gold记录，不重新应用>=3筛选（其中2榜剩2条），两种方法使用相同分母。

| 指标 | AxCell + GPT-4.1 Fully F1/% | GPT-4.1 Extraction + Fully F1/% | 差值/百分点 |
|---|---:|---:|---:|
{comparison}

| 排行榜指标 | AxCell/% | GPT-4.1/% |
|---|---:|---:|
{lbcompare}

这是同一当前可运行论文集合上的描述性比较；AxCell输入为既有特定TeX版本，GPT-4.1为先前PDF证据，输入模态/版本、抽取模型与原始覆盖均不同。不能把差值归因为单一标准化因素，也不能与GPT-4.1全43篇分数作相同分母比较。无重新抽取、无方法优化。
''')
    paper={'Task IIM':(68.98,58.52,63.32),'Dataset IIM':(63.66,33.87,44.22),'Metric IIM':(69.35,51.36,59.01),'Result IIM':(45.32,18.41,26.18),'TDM Exact Match':(55.08,25.78,35.12),'TDMR Exact Match':(32.59,13.67,19.26)}
    paperrows='\n'.join(f"| {k} | {v['Precision']*100:.2f}/{v['Recall']*100:.2f}/{v['F1']*100:.2f} | {paper[k][0]:.2f}/{paper[k][1]:.2f}/{paper[k][2]:.2f} |" for k,v in agg.items())
    md(OUT/'comparison_with_paper.md',f'''# 与原论文AxCell对照（非严格同范围）

来源：[EMNLP2024原论文](https://aclanthology.org/2024.emnlp-main.453.pdf)，Table3/4/5/12、Appendix C；本地冻结PDF/text在pilot/leaderboard_eval_full43_uncapped/reference。Table3是TDMR、Table4是IIM、Table12是TDM。

| 指标 | 本地P/R/F1 % | 作者P/R/F1 % |
|---|---|---|
{paperrows}

排行榜作者报告LR40.00%、PC25.78%、RC15.45%、AO11.93%；本地LR精确TDM {lb['LR_exact_TDM']*100:.4f}%、有效非空榜率{lb['valid_nonempty_board_rate']*100:.4f}%、PC{lb['PC_official']*100:.4f}%、RC{lb['RC_official']*100:.4f}%、AO论文ID{lb['AO_paper_ID_supplementary']*100:.4f}%。官方数值列表RBO {lb['RBO_official_numeric_lists']*100:.4f}%单独报告，不当成AO。

作者使用36篇TeX及GPT-4 Turbo(1106-preview) Fully标准化；本地37篇，GPT-4.1-2025-04-14，无客户端输出上限。作者36篇成员和具体TeX版本仍未核实，不能宣称严格复现其范围。作者Elasticsearch索引语料未核实；本地延续验收单篇的每篇空初始索引。当前27榜经37篇限制后有119条Gold，作者子集的实际榜成员/分母不可核对。

这些差异、9篇零预测、错误绑定与数量/维度误作分数、部分标签标准化null，都可能影响结果；没有控制实验，不能量化各因素贡献。保留官方重复预测与Result包含关系的异常行为，严格一对一诊断另列；不为提高分数改变模型、阈值或Prompt。
''')
    save(OUT/'evaluation/verification.json',{'official_tdm_main_executed':True,'official_leaderboard_main_executed':True,'original_source_unchanged':all(sha(Path(p))==h for p,h in before.items()),'baseline_unchanged':sha(baselinepath)==before[str(baselinepath)],'same37_scope_comparison':True,'all37_including9empty':True,'Gold_tdmrs':248,'boards':27,'board_entries':119,'tests_passed':tests_passed,'test_evidence_sha256':sha(OUT/'evaluation/test_evidence.json'),'merged_equals_verified_official_outputs':True,'paid_api_calls':0,'normalization_repeated':False,'F1_from_macro_P_R':True})
    assert all(sha(Path(p))==h for p,h in before.items())
    print(json.dumps({'tuple_metrics':agg,'leaderboard':lb,'strict':strict,'diagnostic_categories':dict(counts),'substring_disagreements':diffs},ensure_ascii=True))
if __name__=='__main__':main()
