"""Final read-only verification of paid outputs, reports and immutable evidence."""
import json,csv,hashlib,ast,statistics,sys
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=Path(r'D:\C++\SCILEAD');P4=OUT.parent/'20261022_stage4_preparation';REPO=ROOT/'emnlp2024-leaderboard-generation'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def md(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf-8')
def table(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
plan=read(P4/'normalization_request_preview.json')['requests'];raw=read(P4/'normalization_input.json');norm=read(OUT/'merged/normalized_output.json');labels={k:ast.literal_eval(v) for k,v in read(P4/'candidate_sets.json').items()}
states={};requesthashes={};nulls=Counter();mapped=Counter();usage=Counter()
assert len(list((OUT/'api_calls').glob('*/attempt.json')))==len(plan)==123
for q in plan:
    folder=OUT/'api_calls'/q['request_id'];s=read(folder/'state.json');request=read(folder/'request.json');response=read(folder/'response.json')
    assert request==q['payload'] and s['checkpoint_cache_key']==q['checkpoint_cache_key']
    assert s['status']=='COMPLETE' and s['attempts']==1 and s['http_status']==200 and s['finish_reason']=='stop' and s['returned_model']=='gpt-4.1-2025-04-14'
    assert s['response_sha256']==sha(folder/'response.json') and s['raw_answer']==response['choices'][0]['message']['content']
    assert not any(k in request for k in ('max_tokens','max_completion_tokens','max_output_tokens','tools','response_format'))
    answer=s['raw_answer'];actual=norm[q['paper_id']]['normalized_output'][q['record_index']][q['field']]
    assert actual==(answer if answer in labels[q['field']] else None)
    (nulls if actual is None else mapped)[q['field']]+=1
    for k in ('prompt_tokens','completion_tokens','total_tokens'):usage[k]+=s['usage'][k]
    states[q['request_id']]=s
    for p in folder.iterdir():
        if p.is_file():requesthashes[str(p.relative_to(OUT))]=sha(p)
assert len(norm)==37 and sum(len(x['normalized_output']) for x in norm.values())==65
exact=0
for pid,data in raw.items():
    src=json.loads(data['output']);dst=norm[pid]['normalized_output'];assert len(src)==len(dst) and norm[pid]['source_documents']==data['source_documents']
    for a,b in zip(src,dst):
        assert a['Result']==b['Result']
        for k in labels:
            if a[k] in labels[k]:assert b[k]==a[k];exact+=1
assert exact==72 and sum(nulls.values())==39 and sum(mapped.values())==84
freeze=read(OUT/'protected_files_before.json');p4hist=read(P4/'historical_files_read_sha256.json')
for p,h in {**freeze,**p4hist}.items():assert Path(p).stat().st_size==h['bytes'] and sha(Path(p))==h['sha256'],p
# Verify previously frozen full43 baseline wholesale using its pre-existing manifest.
baselinefreeze=read(ROOT/'pilot/leaderboard_eval_full43_uncapped/freeze_before.json')
basefiles=baselinefreeze['all_baseline_files']
for p,h in basefiles.items():assert sha(Path(p))==h,p
assert set(basefiles)=={str(p) for p in (ROOT/'pilot/full43_uncapped').rglob('*') if p.is_file()}
for x in read(P4/'model_asset_verification.json')['files']:assert sha(Path(x['path']))==x['sha256']
start=read(OUT/'execution_started.json');finish=read(OUT/'execution_finished.json');seconds=(datetime.fromisoformat(finish['finished_utc'])-datetime.fromisoformat(start['started_utc'])).total_seconds()
summary=read(OUT/'normalization_usage.json');assert all(summary[k]==usage[k] for k in usage)
summary.update(batch_wall_seconds=seconds,valid_mappings=sum(mapped.values()),null_mappings=sum(nulls.values()),null_by_field=dict(nulls),valid_mapping_by_field=dict(mapped),direct_exact_fields=exact,wire_payload_verified_against_P4=True,all_finish_reason_stop=True,all_returned_model_matches=True,actual_provider_bill=None,seed_determinism_verified=False)
save(OUT/'normalization_usage.json',summary)
metrics=read(OUT/'metrics.json');agg=metrics['official_tuple_metrics'];lb=metrics['leaderboard'];strict=metrics['strict_supplementary'];per=read(OUT/'evaluation/per_paper_metrics.json');diagnostics=read(OUT/'evaluation/strict_diagnostics.json');records=read(P4/'record_provenance.json');papers=read(OUT/'normalization_manifest.json')['papers'];papermap={p['paper_id']:p for p in papers}
with (P4/'paper_scope_comparison.csv').open(encoding='utf-8-sig',newline='') as f:scope=list(csv.DictReader(f))
outrows=[]
for p in scope:
    pid=p['paper_id'];s=papermap.get(pid);m=per.get(pid)
    outrows.append({'paper_id':pid,'gold_count':p['gold_count'],'extraction_status':p['status'],'normalization_status':s['status'] if s else 'NOT_RUN_UPSTREAM_FAILURE_OR_NO_INPUT','records':s['records'] if s else None,'requests':s['completed_requests'] if s else 0,'null_fields':s['null_fields'] if s else None,'Result_IIM_F1':m['Result IIM']['F1'] if m else None,'TDM_F1':m['TDM Exact Match']['F1'] if m else None,'TDMR_F1':m['TDMR Exact Match']['F1'] if m else None,'author36_membership':'UNVERIFIED','normalized_output':str(OUT/'normalized_outputs'/pid/'normalized_output.json') if s else None})
table(OUT/'paper_output_index.csv',outrows)
known=[]
for r in records:
    if r['known_error']:
        known.append({**r,'normalized':norm[r['paper_id']]['normalized_output'][r['record_index']]})
save(OUT/'evaluation/known_error_followup.json',known)
cats=Counter(g['category'] for d in diagnostics.values() for g in d['gold_rows'])
diffs={p:d['official_substring_vs_strict_pairs'] for p,d in diagnostics.items() if d['official_substring_vs_strict_pairs']}
badanswers=[{'request_id':q['request_id'],'paper_id':q['paper_id'],'record_index':q['record_index'],'field':q['field'],'original_value':q['original_value'],'raw_response':states[q['request_id']]['raw_answer']} for q in plan if states[q['request_id']]['raw_answer'] not in labels[q['field']]]
save(OUT/'evaluation/null_mapping_cases.json',badanswers)
errorlines='\n'.join('| '+' | '.join([r['record_id'],r['cell_ext_id'],r['tdmr']['Result'],r['known_error'],json.dumps(r['normalized'],ensure_ascii=False)])+' |' for r in known)
md(OUT/'inspection/findings.md',f'''# AxCell错误记录（不修复预测）

标准化123次成功HTTP请求，84个回答精确属于候选集合，39个回答为原始字符串None并按官方规则变为null：Task4、Dataset17、Metric18。另72字段无需模型直接保留。API成功不表示语义标准化正确；null不按网络失败重试。

| 原始记录 | 来源单元格 | 原Result | 已核实错误类型 | 标准化后原样保留 |
|---|---|---|---|---|
{errorlines}

三例都属于AxCell原始抽取/绑定错误，标准化不读取表格上下文、不纠正Result或Metric语义。不存在根据Gold筛除错误样本。

严格逐Gold诊断共248条：{json.dumps(dict(cats),ensure_ascii=False)}。217条没有任何严格相等数值候选，仅能归为“遗漏、值错误或比例/格式差异”，不能进一步断言全部是抽取遗漏。15条有相等数值但候选出现null字段，5条有相等数值但标签/绑定未匹配；这些是对照分类，不自动证明唯一错误环节。11条通过严格TDMR一对一匹配。

官方字符串包含与严格相等不同的两对均在1809.08370.pdf：96.61对96.6，95.02对95.0。官方分数完整保留，严格诊断另报。官方TDMR F1={agg['TDMR Exact Match']['F1']*100:.4f}%，严格一对一F1={strict['strict_tdmr_one_to_one']['F1']*100:.4f}%。

其他现象：原始模型名含Oracle (Intent)、without transfer、Joint等变体的记录均保留，不按名称过滤。是否属于其他工作Baseline或Dev/Test混淆需逐论文正文复核，本轮不能仅据名称下结论。正文/表格输入未变，不开展修正规则或改进实验。
''')
rowstr='\n'.join(f"| {k} | {v['Precision']*100:.4f} | {v['Recall']*100:.4f} | {v['F1']*100:.4f} |" for k,v in agg.items())
lbstr='\n'.join(f"| {k} | {v*100:.4f}% |" for k,v in lb.items() if k not in ('gold_boards','gold_entries'))
paperstr='\n'.join('| '+' | '.join([r['paper_id'],r['gold_count'],str(r['records']) if r['records'] is not None else '—',str(r['requests']),str(r['null_fields']) if r['null_fields'] is not None else '—',f"{r['Result_IIM_F1']*100:.2f}" if r['Result_IIM_F1'] is not None else '—',f"{r['TDM_F1']*100:.2f}" if r['TDM_F1'] is not None else '—',f"{r['TDMR_F1']*100:.2f}" if r['TDMR_F1'] is not None else '—',r['normalization_status']])+' |' for r in outrows)
md(OUT/'final_axcell_report.md',f'''# AxCell Extraction + GPT-4.1 Fully Normalization：P5完成报告

本轮37/37可运行论文标准化及官方评价完成，28篇非空、9篇VALID_EMPTY，65条原始记录无增删。P4获用户“同意，可以进入下一阶段”后执行。123/123请求HTTP200，返回模型均为gpt-4.1-2025-04-14、finish_reason均stop；无失败、无重试、无用量未知请求。API成功不代表预测正确。

## 设置与实际调用

直接复用P3 AxCell结果，未重新解析、抽取或加载AxCell模型。原Prompt和23 Task/71 Dataset/26 Metric集合及顺序不变；官方tdm_llm_normalization.main逐字段处理，仅在独立适配层替换模型初始化。temperature=0、seed=0、n=1、stream=false；123个实际HTTP payload逐项等于P4清单，均没有max_tokens/max_completion_tokens/max_output_tokens、tools、response_format。固定seed已接受，不声称服务端完全确定性。

123次中84个有效集合映射，39个null（Task4/Dataset17/Metric18），另外72字段精确命中原样保留。重复名称没有缓存去重。Result字符串、顺序、65条来源及9篇空输出全部保留。来源原表另有可追溯索引，不加入标准化请求。

实际输入{usage['prompt_tokens']:,}、输出{usage['completion_tokens']:,}、总计{usage['total_tokens']:,} Tokens；标准化批次墙钟{seconds:.3f}秒（{seconds/60:.2f}分钟），请求耗时合计{summary['call_seconds_sum']:.3f}秒。按P4核实的OpenAI公开参考价计算${summary['openai_reference_usd']:.6f}；9527.codes实际账单/价格仍未知，不能称为实际已扣费。官方callback生成的成本文件不作为中转站账单。所有状态、请求ID（服务端未提供时为null）、响应ID、模型、usage和原始回答均保留。

## 官方tuple指标

范围为37篇/248条Gold，9篇零预测进入分母。使用完整43篇Gold文件、官方函数按输出37篇计算Macro P/R；F1额外由聚合P/R计算，不是逐篇F1算术平均。

| 指标 | Precision/% | Recall/% | F1/% |
|---|---:|---:|---:|
{rowstr}

## Leaderboard

原27个Gold榜限制到同37paper IDs后剩119条；其中两榜剩2条，不重复应用>=3阈值。官方PC/RC/数值列表RBO保持原实现和重复预测最后赋值行为；LR、有效非空榜率、论文ID AO为复用既有辅助实现，AO并列按paper ID字典序，空榜0，全部27榜Macro。

| 指标 | 结果 |
|---|---:|
{lbstr}

## 严格诊断与比较

严格数值一对一Result IIM F1={strict['strict_result_iim_one_to_one']['F1']*100:.4f}%，严格TDMR F1={strict['strict_tdmr_one_to_one']['F1']*100:.4f}%，仅补充诊断，不替代官方分数。不缩放、不去百分号、不将字符串包含视为数值相等；65条原记录保留。

同37篇冻结GPT-4.1 Extraction + Fully：Result IIM F1={metrics['gpt41_same37']['tuple_metrics']['Result IIM']['F1']*100:.4f}%，TDM F1={metrics['gpt41_same37']['tuple_metrics']['TDM Exact Match']['F1']*100:.4f}%，TDMR F1={metrics['gpt41_same37']['tuple_metrics']['TDMR Exact Match']['F1']*100:.4f}%。只离线复算既有预测，没有新GPT抽取。详细P/R及排行榜对照见comparison_with_gpt41.md及对应JSON。

原论文AxCell TDMR F1=19.26%、TDM F1=35.12%、Result IIM F1=26.18%，使用作者36篇和GPT-4 Turbo；本地范围/TeX版本/标准化模型/客户端上限/索引语料等不能确认完全一致，因此只作描述性比较，不做严格因果归因。见comparison_with_paper.md。

三例已知错误（Recall91.85误绑F1、实体数4696、向量维度300误作分数）保留。官方包含匹配的两对差异及逐Gold类别见inspection/findings.md、evaluation/tdmr_comparison.md和strict_diagnostics.json。此处不计算完整Baseline混入率或Dev/Test错误率。

## 论文范围及逐篇结果

作者原36篇成员仍UNVERIFIED；不将本地37篇称为作者36篇严格复现。39篇TeX中两篇解析失败1905.03197.pdf与2203.16804.pdf保留未运行；另4篇尚无已核实TeX。37/39输入流程覆盖与37/43数据集覆盖单独报告；未静默删除失败项，未给它们编造标准化结果。

| 论文 | Gold | 预测数 | 请求数 | null字段 | Result IIM F1/% | TDM F1/% | TDMR F1/% | 标准化状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
{paperstr}

## 完整性与工程记录

P3/P4及此前受保护文件{len(freeze)}份、历史用量参考文件{len(p4hist)}份哈希保持一致；冻结full43_uncapped共{len(basefiles)}文件及清单核验一致；7个E盘模型/词表匹配冻结值。未修改官方源码、Prompt、Gold、原解析产物或既有实验。无SSH、Docker或模型实验启动。

独立代码复核发现两个编排校验缺口：合并副本需与已校验官方输出比较；测试通过状态须来自实际执行记录。已补齐并经测试验证，未发现输出损坏，未重跑任何API。最终三组离线测试共11项通过（网络mock、严格诊断、合并一致性）。历史版运行入口与最终版的差异仅为输出一致性保护，不涉及方法或请求参数。

官方评价导入依赖时有HF缓存路径权限提示和LangChain旧入口警告，评价退出码0；无网络模型下载、未升级依赖。保持原结果，未为警告重跑付费请求。

输出根目录 `{OUT}`；E盘同步目标 `E:\\SCILEAD\\axcell\\reports\\20261022_stage5`，以sync_verification.json为准。后续只可读取已有成功请求检查点，禁止再次生成挑选结果。批次已完成并停止，不自动进入其他实验。
''')
save(OUT/'request_files_sha256.json',requesthashes)
save(OUT/'manifest.json',{'experiment':'AxCell Extraction + GPT-4.1 Fully Normalization','stage':'P5_COMPLETE','source_p3':str(OUT.parent/'20261022_stage3_resume'),'approved_p4':str(P4),'gold_scope':metrics['scope'],'papers':outrows,'model':'gpt-4.1-2025-04-14','params':{'temperature':0,'seed':0,'n':1,'stream':False,'output_limit_parameters':'omitted','max_retries':0},'original_algorithm':'tdm_llm_normalization.main and tdm_eval.main, leaderboard_eval.main unmodified; initializer and argument adapters only','candidate_sets_sha256':sha(P4/'candidate_sets.json'),'prompts_sha256':sha(REPO/'prompts.json'),'actual_calls':123,'automatic_retries':0,'requests_with_null':39,'dependency_changes':False})
verification={'status':'P5_COMPLETE','utc':datetime.now(timezone.utc).isoformat(),'processed_papers':37,'records':65,'raw_predictions_unchanged':True,'result_strings_unchanged':True,'planned_requests':123,'actual_attempts':123,'successful_requests':123,'all_HTTP_200':True,'all_finish_stop':True,'all_exact_response_model':True,'all_exact_P4_payload':True,'no_output_limit_parameters_sent':True,'retry_count':0,'null_mappings':39,'direct_exact_fields':72,'protected_files_verified':len(freeze),'history_files_verified':len(p4hist),'frozen_full43_files_verified':len(basefiles),'all_frozen_unchanged':True,'evaluation':read(OUT/'evaluation/verification.json'),'paid_calls_for_evaluation':0,'secrets_written':False,'remote_access':False,'official_core_changes':False,'author36_scope':'UNVERIFIED','provider_bill':'UNVERIFIED','batch_wall_seconds':seconds}
save(OUT/'verification.json',verification)
md(OUT/'review_resolution.md','''# 独立复核与修复

审核者Plato只读检查：未发现正常执行路径的重复收费、payload偏差或官方算法改动。指出两项Important编排问题。

1. 原先跳过已完成任务时核验官方输出，而合并读取另一份交付副本：新增verified_output同时核验原文件哈希和副本内容，合并返回原文件；评价入口再次逐篇核对merged。test_integrity从缺函数失败到2项通过。实际37篇副本与原文件全部相等，没有预测改动，也没有重跑API。
2. 原评价验证报告无条件写strict_tests_passed=True：改为运行三组离线测试，记录退出码、输出、测试文件SHA；最终字段根据实际退出码计算。实际11项通过，证据在evaluation/test_evidence.json。

最终修复只限独立编排与证据记录，官方算法、数据、Prompt和请求配置不变。审核过程没有调用API或改文件。
''')
print(json.dumps({'verification':'PASS','protected_files':len(freeze),'baseline_files':len(basefiles),'requests':123,'nulls':dict(nulls),'tokens':dict(usage),'seconds':seconds},ensure_ascii=True))
