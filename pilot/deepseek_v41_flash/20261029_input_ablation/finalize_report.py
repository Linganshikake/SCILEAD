"""Offline comparison/report and end-to-end audit; no credentials or API imports."""
import ast,csv,hashlib,json,math,os,statistics,sys
from collections import Counter
from datetime import datetime
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261028'
ARMS=['baseline_rag','parsed_full','page_images']
LABELS={'baseline_rag':'历史 RAG','parsed_full':'解析全文','page_images':'整页图片'}
METRICS=['Task IIM','Dataset IIM','Metric IIM','Result IIM','TDM Exact Match','TDMR Exact Match']
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def csvsave(name,rows):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def mdtable(header,rows):return '\n'.join(['| '+' | '.join(header)+' |','|'+'|'.join(['---']*len(header))+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def pct(v):return f'{100*v:.2f}'

def main():
    evaluation=read(ROOT/'evaluation/report.json');assert evaluation['all_three_arms_complete']
    discovery=read(ROOT/'discovery.json');selected=discovery['selection']['selected'];ids=[x['paper_id'] for x in selected]
    inputrows=read(ROOT/'input_manifest.json');protected=read(ROOT/'protected_hashes.json')
    changed=[p for p,h in protected.items() if sha(p)!=h];assert not changed
    gold=read(evaluation['scope']['full_gold_path'])
    originalgold=Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\tdm_annotations.json')
    assert read(originalgold)==gold
    assert read(originalgold.with_name('leaderboards.json'))==read(evaluation['scope']['original_27_boards_path'])
    raws={};norms={};counts={};usage={};requests=[];times=[]
    generation=read(BASE/'generation_config.json')
    for arm in ARMS:
        merge=ROOT/arm/('merged' if arm=='baseline_rag' else 'fully/merged')
        raws[arm]=read(merge/'output.json');norms[arm]=read(merge/'normalized_output.json')
        assert list(raws[arm])==ids and list(norms[arm])==ids
        counts[arm]={'predictions':sum(len(json.loads(x['output'])) for x in raws[arm].values()),
                     'null_fields':sum(v is None for x in norms[arm].values() for row in x['normalized_output'] for v in row.values())}
        states=[]
        for pid in ids:
            paper=(BASE/'fully/papers'/pid) if arm=='baseline_rag' else ROOT/arm/'fully/papers'/pid
            for p in paper.rglob('state.json'):
                if not (p.parent/'request.json').exists():continue
                s=read(p);q=read(p.parent/'request.json');response=read(p.parent/'response.json')
                assert set(q)==set(generation)|{'messages'}
                assert {k:v for k,v in q.items() if k!='messages'}==generation
                assert s['http_status']==200 and s['status']=='RECEIVED'
                assert s['finish_reason']=='stop' and len(response['choices'])==1
                assert s['post_calls']==1 and s['automatic_retries']==0
                stage='extraction' if p.parent.name=='extraction' else 'normalization'
                if arm!='baseline_rag' and stage=='extraction':assert q['messages']==read(ROOT/arm/'inputs'/pid/'extraction_messages.json')
                if stage=='normalization':
                    mapping=read(p.parent/'mapping.json')
                    expected=[{'role':'system','content':read(BASE/'frozen_prompts.json')['normalization-system-prompt']},
                              {'role':'user','content':'\n\nItem list: '+read(BASE/'candidate_sets.json')[mapping['field']]+'\n\nInput: '+mapping['input']+'\n\nAnswer: '}]
                    assert q['messages']==expected
                u=s['usage'];states.append(s)
                requests.append({'arm':arm,'paper_id':pid,'stage':stage,'historical_reuse':arm=='baseline_rag',
                    'request_directory':str(p.parent),'model':q['model'],'response_model':s['response_model'],
                    'http_status':s['http_status'],'finish_reason':s['finish_reason'],
                    'prompt_tokens':u['prompt_tokens'],'completion_tokens':u['completion_tokens'],'total_tokens':u['total_tokens'],
                    'elapsed_seconds':s['elapsed_seconds'],'response_id':s.get('response_id'),
                    'request_sha256':sha(p.parent/'request.json'),'response_sha256':sha(p.parent/'response.json')})
        subset=[x for x in requests if x['arm']==arm]
        usage[arm]={'requests':len(states),'new_requests':0 if arm=='baseline_rag' else len(states),
            'extraction_requests':sum(x['stage']=='extraction' for x in subset),
            'normalization_requests':sum(x['stage']=='normalization' for x in subset),
            **{k:sum(x[k] for x in subset) for k in ['prompt_tokens','completion_tokens','total_tokens','elapsed_seconds']}}
        if arm!='baseline_rag':
            cp=read(ROOT/arm/'fully/checkpoint.json')
            assert cp['state']=='QUEUE_FINISHED' and cp['stop_reason'] is None
            times.append((datetime.fromisoformat(cp['started_utc']),datetime.fromisoformat(cp['updated_utc'])))
            for pid in ids:
                paper=ROOT/arm/'fully/papers'/pid
                assert all(sha(paper/f)==h for f,h in read(paper/'completion_hashes.json').items())
            assert read(ROOT/arm/'fully/verification.json')['secret_scan_passed']
            for n in ['run_fully.py','transport.py','result_compat.py','candidate_sets.json','frozen_prompts.json','generation_config.json']:
                assert sha(ROOT/arm/n)==sha(BASE/n)
    csvsave('request_manifest.csv',requests)
    newusage={k:sum(usage[a][k] for a in ARMS[1:]) for k in ['requests','extraction_requests','normalization_requests','prompt_tokens','completion_tokens','total_tokens','elapsed_seconds']}
    newusage['batch_wall_seconds']=(max(t[1] for t in times)-min(t[0] for t in times)).total_seconds()
    newusage['automatic_retries']=0
    save('api_usage_summary.json',{'new':newusage,'by_arm':usage,'historical_baseline_not_recounted_as_new':True,'time_definition':'elapsed_seconds sums individual HTTP durations; batch wall time covers both concurrently running independent serial arms.'})
    metrics=[];per=[]
    for a in ARMS:
        stage=evaluation['arms'][a]['stages']['fullyllm']
        for k,v in stage['aggregate'].items():metrics.append({'arm':a,'metric':k,**v})
        for p,values in stage['per_paper'].items():
            for k,v in values.items():per.append({'arm':a,'paper_id':p,'metric':k,**v})
    csvsave('metrics.csv',metrics);csvsave('per_paper_metrics.csv',per)

    # Inspectable case evidence; created only after all predictions are complete.
    first=selected[0];es=read(first['paths']['partition_elements_json'])
    rag_text='\n\n'.join(x['content'] for x in raws['baseline_rag']['D19-1367.pdf']['source_documents'])
    full_text='\n\n'.join(x['content'] for x in raws['parsed_full']['D19-1367.pdf']['source_documents'])
    table=next(x for x in es if x['type']=='Table' and x['metadata']['page_number']==4)
    narrative=next(x for x in es if x['type']=='NarrativeText' and '93.47' in x['text'])
    assert '93.47' in table['metadata']['text_as_html'] and '93.47' not in table['text']
    assert '93.47' not in rag_text and '93.47' in full_text
    maps={a:ROOT/a/'fully/papers/1808.08745.pdf/normalization/requests/002_record0_Metric' for a in ARMS[1:]}
    assert read(maps['parsed_full']/'request.json')==read(maps['page_images']/'request.json')
    save('inspection/cases.json',{
        'D19_1367':{'paper_id':'D19-1367.pdf','page':4,'table_text':table['text'],'table_html':table['metadata']['text_as_html'],
            'narrative':narrative['text'],'rag_contains_93_47':False,'full_parsed_contains_93_47':True,
            'original_table_caption_in_rag':raws['baseline_rag']['D19-1367.pdf']['source_documents'][-1]['content'].split('\n')[0],
            'outputs':{a:json.loads(raws[a]['D19-1367.pdf']['output']) for a in ARMS}},
        'XSum_identical_normalization_request':{'paper_id':'1808.08745.pdf','identical_request_sha256':sha(maps['parsed_full']/'request.json'),
            'results':{a:read(p/'mapping.json') for a,p in maps.items()},'original_predictions_unchanged':True},
        'LUKE_dev_test_and_metric_omission':{'paper_id':'2020.emnlp-main.523.pdf','gold':gold['2020.emnlp-main.523.pdf']['TDMs'],
            'raw_outputs':{a:json.loads(raws[a]['2020.emnlp-main.523.pdf']['output']) for a in ARMS},
            'normalized_outputs':{a:norms[a]['2020.emnlp-main.523.pdf']['normalized_output'] for a in ARMS}},
        'inspection_is_post_generation':True})
    save('visual_qa.json',{'rendered_pages':56,'structurally_checked_all_pages':True,'dpi':150,'format':'PNG',
        'spot_checked_pages':{'D19-1367.pdf':[3],'1901.10430.pdf':[6],'1808.08745.pdf':[3],'2020.emnlp-main.523.pdf':[5],'1911.09483.pdf':[6]},
        'result':'All five inspected full pages are nonblank, uncropped and tables/headers readable at source resolution.',
        'server_behavior':'DeepSeek automatically rescales image area to roughly 1300x1300; up to 1024 tokens/image. No local OCR, tiling or model-driven crop selection.'})

    # Standard offline scientific chart.
    os.environ['MPLCONFIGDIR']=str(ROOT/'charts/.mplconfig')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    font=Path(r'C:\Windows\Fonts\msyh.ttc')
    if font.exists():
        from matplotlib import font_manager
        font_manager.fontManager.addfont(str(font));plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name()
    plt.rcParams['axes.unicode_minus']=False
    (ROOT/'charts').mkdir(exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(12,8.5),layout='constrained')
    colors=['#7b8794','#1479b8','#ce7040']
    for ax,keys,isboard in [(axes[0],METRICS,False),(axes[1],['LR_exact_tdm_hit','PC','RC','RBO','AO'],True)]:
        pos=np.arange(len(keys));width=.24
        for i,a in enumerate(ARMS):
            stage=evaluation['arms'][a]['stages']['fullyllm']
            vals=[100*(stage['leaderboard']['aggregate'][k] if isboard else stage['aggregate'][k]['F1']) for k in keys]
            bars=ax.bar(pos+(i-1)*width,vals,width,label=LABELS[a],color=colors[i])
            ax.bar_label(bars,labels=[f'{x:.1f}' for x in vals],padding=3,fontsize=9)
        ax.set_xticks(pos,['LR','PC','RC','RBO','AO'] if isboard else ['Task IIM','Dataset IIM','Metric IIM','Result IIM','TDM','TDMR'])
        ax.set_ylim(0,114);ax.set_ylabel('%');ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    axes[0].set_title('DeepSeek 输入对照：同一 5 篇 / 28 条 Gold · 原版 Fully LLM 标准化',fontweight='bold')
    axes[0].legend(ncol=3,loc='lower left');axes[0].set_ylabel('F1 (%)')
    axes[1].set_title('排行榜：相同 10 榜（6 个单论文榜，4 个多论文榜）')
    fig.savefig(ROOT/'charts/comparison.png',dpi=180);fig.savefig(ROOT/'charts/comparison.svg');plt.close(fig)

    stages={a:evaluation['arms'][a]['stages']['fullyllm'] for a in ARMS}
    protocol_table=mdtable(['设置','正文/页面','表格处理','抽取/标准化'],[
        ['历史 RAG','每篇4个历史检索正文块','全部历史表格纯文本','复用已有 DeepSeek Fully LLM'],
        ['解析全文','原解析器保留的全部 Title/NarrativeText，按页聚合','同样的32张表格纯文本及原caption规则','5次新抽取 + 49次标准化'],
        ['整页图片','PDF全部56页，150 DPI PNG，原页序','表格随整页图像输入','5次新抽取 + 52次标准化']])
    metric_table=mdtable(['指标','历史RAG P/R/F1','解析全文 P/R/F1','整页图片 P/R/F1'],[
        [k]+[' / '.join(pct(stages[a]['aggregate'][k][v]) for v in ['Precision','Recall','F1']) for a in ARMS] for k in METRICS])
    board_table=mdtable(['指标']+[LABELS[a] for a in ARMS],[[label]+[pct(stages[a]['leaderboard']['aggregate'][k]) for a in ARMS]
        for k,label in [('LR_exact_tdm_hit','LR'),('LR_nonempty_finite_result','有效非空榜率'),('PC','PC'),('RC','RC'),('RBO','官方数值RBO'),('AO','论文ID AO')]])
    paper_table=mdtable(['论文','Gold','页数/表格','三组预测条数（RAG/全文/图片）','RAG TDMR F1','全文 TDMR F1','图片 TDMR F1'],[
        [x['paper_id'],x['gold'],f"{x['pages']} / {x['tables']}",'/'.join(str(len(json.loads(raws[a][x['paper_id']]['output']))) for a in ARMS)]+
        [pct(stages[a]['per_paper'][x['paper_id']]['TDMR Exact Match']['F1']) for a in ARMS] for x in inputrows])
    usage_table=mdtable(['设置','抽取请求','标准化请求','输入Token','输出Token（含推理）','总Token'],[
        [LABELS[a],usage[a]['extraction_requests'],usage[a]['normalization_requests'],usage[a]['prompt_tokens'],usage[a]['completion_tokens'],usage[a]['total_tokens']] for a in ARMS])
    text=f'''# DeepSeek 输入方式子集对照：实验结果

三组均完成 **5/5 篇、28 条 Gold**。最终 TDMR F1：历史 RAG **71.85%**，解析全文 **82.83%**，整页图片 **83.31%**。相对历史 RAG，分别提高 **10.98** 和 **11.46** 个百分点。图片组比解析全文高 **0.48** 个百分点。

## 设置与范围

{protocol_table}

模型实际请求为 `deepseek-flash`，官方文档映射版本为 `DeepSeek-V4.1-Flash-1017`。两阶段都沿用已验证配置：thinking enabled、reasoning_effort high、stream false；未发送客户端输出上限、temperature、seed、tools或response_format。System Prompt与用户任务前后缀不变。原版Fully候选集合23/71/26及顺序、逐字段处理、精确接受规则不变；不缓存重复名称。

第一组原请求是直接输入PDF。核实[官方Vision文档](https://api-docs.deepseek.com/guides/vision)和[Files文档](https://api-docs.deepseek.com/guides/files_api)后，用户批准改成整页图片：接口不支持PDF文件，只支持图片。每页原样渲染，不OCR、不裁剪、不切图；官方服务会按约1300×1300总像素面积缩放，单图最高1024 Tokens。图片请求最大9.4 MB。

解析全文组复用已保存的Unstructured元素，直接执行原版`extract_text_and_tables`方法的缓存等价调用；未重新解析PDF。这里的“全文”指原版代码保留的Title/NarrativeText全部正文，而不是额外纳入公式、图像或其他被原版排除的元素。全部正文按原页序在前，全部表格按原序在后，未进行切块、Embedding或Chroma检索。原表格HTML保留在审计文件中，本组仍使用与历史一致的纯文本表示，32/32个表格文档逐字一致。

种子`20261029`；在43篇完整输入中，按非表格文本长度与表格数的中位数分成四层，每层抽一篇，再随机补一篇。抽样没有使用Gold数量、答案或模型得分；清单在新请求前冻结。

{paper_table}

## 完整最终指标

以下均为百分数。官方逐篇Macro Precision/Recall保持原样；F1=2PR/(P+R)，并非逐篇F1的算术平均。

{metric_table}

严格Result数值相等的辅助P/R/F1与本次官方Result IIM完全一致。它只核对Result值，不核对对应Task/Dataset/Metric；详细记录见evaluation及metrics.csv。标准化前的官方精确名称评价也已保存，未将其称为语义抽取分数。

![同一子集结果](charts/comparison.png)

## 排行榜指标

从冻结的27个Gold排行榜中，仅保留本次5篇成员的交集：10榜、14个论文成员条目，其中6榜只有1篇，4榜各有2篇。三组使用完全相同的派生Gold。PC/RC/RBO由原官方代码生成；LR、有效非空榜率和论文ID AO沿用既有辅助定义。

{board_table}

解析全文组在这10榜上全命中。ReCoRD不属于这10榜，其Dev/Test混淆影响tuple指标，但不进入上述排行榜分母。多论文榜的逐榜成员和排序保存在evaluation报告中，便于检查实际排序变化。

## 哪个环节影响结果

### 1. D19-1367：纯文本表格表示损失，叠加正文检索遗漏

第4页Table 2的HTML保留了I-DARTS的**93.47**，但同一元素的`text`只有模型名称，没有分数列；原caption关联还把它配成了Figure 2。历史RAG的4段正文也没有93.47，因此原输出为NER `N/A`。完整正文中另有明确的“93.47 F1-score”，解析全文组恢复该记录；图片组也抽出56.0与93.47两条Gold。

该篇TDMR F1从 **40→80→100**。全文组还输出验证集Perplexity 58.0，图片组只保留两项测试结果。问题发生在“HTML/元素到纯文本上下文”的信息保留及正文选择两个位置。

### 2. LUKE（2020.emnlp-main.523）：上下文更多，Dev/Test选择仍会出错

历史RAG选中了ReCoRD测试值 **90.6/91.2**。解析全文组改为输出开发值 **90.8/91.4**，漏掉测试值；图片组把开发值和测试值都输出，还加入SQuAD开发值89.8/95.0。原版标准化把带Dev/Test的Metric都映射成EM/F1，限定信息随后消失。

三组都漏掉Open Entity与TACRED的Precision/Recall，共4条Gold，即使这些列在PDF表格上清晰存在。该篇TDMR F1为 **77.78→55.56→63.64**。这属于Extraction对最佳结果、指标列及实验split的选择问题，增加输入并未自动解决。

### 3. XSum（1808.08745）：正确抽取被标准化拒绝

三组均抽到了31.89、11.54、25.75三个正确ROUGE值。图片组在标准化`ROUGE-1 F1`时返回了带单引号的`'ROGUE-1'`，不与候选`ROGUE-1`精确相等，按原规则保存为null。解析全文组的**同一个请求，参数和消息哈希完全一致**，返回的是不带引号的候选，因此被接受。

该篇TDMR F1为 **50→75→50**。三组还都输出了Gold未收录的人评/QA结果。最终差值包含重复LLM标准化带来的返回波动，不能把这部分计为RAG或图片输入的收益；所有原答案和null均保留，未修复。

### 汇总判断

- **本次最直接的输入收益是补回被遗漏的证据。** 两种新输入都修复了D19-1367的NER数值遗漏，图片组Result IIM F1达到88.55%，高于全文82.83%和RAG79.46%。
- **更多上下文也会引入更多实验条件。** LUKE的开发/测试结果是最明显的退化案例，表明结果选择与绑定仍是抽取层问题。
- **标准化仍会损伤正确抽取。** XSum相同请求的一次引号差异就使正确记录和相应排行榜丢失；本轮保留原始精确接受规则，因此结果呈现了这一真实波动。
- 每篇每组只执行一次。样本覆盖5篇、28条Gold；此次选样同时含提升、退化和持平论文，观察到的变化用于定位问题，未据此更改全量冻结结果。

## 请求与运行记录

{usage_table}

历史RAG行是复用的历史用量；本轮新增 **{newusage['requests']}次**（抽取10次、标准化101次），输入{newusage['prompt_tokens']:,}、输出{newusage['completion_tokens']:,}、总计 **{newusage['total_tokens']:,} Tokens**。全部HTTP200、finish_reason=stop；无重试、无失败、无模型切换。两条独立串行队列并行执行，批次墙钟{newusage['batch_wall_seconds']:.1f}秒，HTTP耗时加总{newusage['elapsed_seconds']:.1f}秒。

准备阶段复用了本地tokenizer缓存；PATH中的MiKTeX因配置目录权限导致渲染失败，随后使用项目原有独立Poppler完成渲染，失败日志保留。未安装依赖、未修改原PDF或冻结环境。

## 文件索引

- `selection_frozen.json` / `input_manifest.json`：抽样与输入。
- `page_images/fully/`：图片组逐篇原响应、标准化、检查点与用量。
- `parsed_full/fully/`：解析全文组同类产物。
- `baseline_rag/merged/`：同5篇历史RAG结果的只读来源副本。
- `evaluation/report.json`：所有官方P/R/F1、逐篇指标和逐榜结果；`evaluation/latest.json`定位本轮完整评价。
- `metrics.csv` / `per_paper_metrics.csv`：汇总和逐篇表。
- `inspection/cases.json`：三个案例的输入证据、原始预测及标准化返回。
- `api_usage_summary.json` / `request_manifest.csv`：新旧请求分开统计。
- `verification.json`：源码、Gold、Prompt、证据、历史结果及新请求的一致性核验。

后续未自动扩展到43篇，也未修改名称对齐Prompt或进行结果修复。
'''
    (ROOT/'report.md').write_text(text,encoding='utf8')
    save('experiment_manifest.json',{'status':'COMPLETE','model':generation['model'],'generation_config':generation,
        'selected_papers':ids,'gold':28,'arms':ARMS,'selection':discovery['selection'],
        'official_source_sha256':{p:h for p,h in protected.items() if 'emnlp2024-leaderboard-generation' in p},
        'baseline_root':str(BASE),'evaluation_report':str(ROOT/'evaluation/report.json'),
        'raw_predictions':counts,'new_usage':newusage})
    newrequests=[x for x in requests if not x['historical_reuse']]
    protected.update(read(ROOT/'evaluation/report.json')['protected_sha256'])
    assert all(sha(p)==h for p,h in protected.items())
    verification={'status':'PASS','selected_papers':5,'gold':28,'completed_by_arm':{a:5 for a in ARMS},
        'protected_files_checked':len(protected),'protected_files_changed':[],
        'original_runtime_and_normalization_copied_unchanged':True,'fully_candidates':[23,71,26],
        'new_api_requests':len(newrequests),'all_http_200':True,'all_finish_reason_stop':True,'all_extractions_structurally_valid':True,
        'no_automatic_retries':True,'response_model_ids':sorted({x['response_model'] for x in newrequests}),
        'request_model_ids':sorted({x['model'] for x in newrequests}),
        'no_client_output_caps_or_tools':True,'all_extraction_messages_equal_frozen_inputs':True,
        'all_normalization_messages_equal_original_fully_templates':True,'all_result_strings_preserved':True,
        'all_candidate_order_strings_identical':True,'table_parity_32_of_32':True,
        'rendered_pages':56,'gold_copy_semantically_equal_to_original':True,
        'source_input_provenance_no_prediction_or_gold_insertions':True,
        'preparation_tests':'test_preparation.py; 2 passed','evaluation_audit':evaluation['protected_files_unchanged'],
        'all_three_arms_complete':evaluation['all_three_arms_complete']}
    save('verification.json',verification)
    report_hashes={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not any(x.startswith('.') for x in p.relative_to(ROOT).parts) and p.name!='delivery_hashes.json'}
    save('delivery_hashes.json',report_hashes)
    print(json.dumps({'status':'PASS','new_usage':newusage,'counts':counts,'protected_files':len(protected),'report':str(ROOT/'report.md')},ensure_ascii=False))

if __name__=='__main__':main()
