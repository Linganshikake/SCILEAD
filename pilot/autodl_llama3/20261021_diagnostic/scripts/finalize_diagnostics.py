from pathlib import Path
import json,hashlib,shutil,csv,collections,subprocess,sys
from format_candidate import audit
R=Path(__file__).resolve().parents[1];PILOT=Path(r'D:\C++\SCILEAD\pilot');PRE=PILOT/'autodl_setup/20261021';RR='/root/autodl-tmp/scilead/runs/llama3/20261021_diagnostic'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(name,text):(R/name).write_text(text,encoding='utf-8')
def gib(n):return n/1024**3
def main():
    state=read(R/'remote_snapshot/batch_status.json');assert state['status']=='DIAGNOSTIC_COMPLETE_FORMAL_BLOCKED' and state['actual_generation_calls']==3
    pre=read(R/'preflight.json');manifest=read(R/'experiment_manifest.json');scope=read(R/'config/scope42.json')
    shutil.copytree(R/'remote_snapshot/extraction',R/'extraction',dirs_exist_ok=True)
    records=[];candidate_files=[]
    sources=[(x['paper_id'],R/'extraction'/x['paper_id'].removesuffix('.pdf')/'extraction',False,x) for x in state['papers']]
    sources.append(('2020.findings-emnlp.378.pdf',PRE/'remote_snapshot/runs/smoke/llama3-20261021/extraction',True,None))
    for pid,folder,historical,item in sources:
        call=folder/'calls/000000';response=(call/'response.txt').read_text(encoding='utf-8');request=read(call/'request.json');usage=read(call/'complete.json');raw=read(call/'pipeline_raw_response.json')
        assert raw[0][0]['generated_text']==request['prompt']+response
        expected=next(x for x in pre['audit'] if x['paper_id']==pid);assert request['prompt_sha256']==expected['prompt_sha256']
        output=read(folder/'output.json');docs=read(PRE/'stage/data/evidence'/(pid+'.json'))[pid];assert output[pid]['source_documents']==docs and output[pid]['output']==response
        runtime=read(folder/'calls/model_runtime.json');assert runtime['pipeline_forward_params']=={'max_new_tokens':1024,'do_sample':False}
        assert runtime['device_map']=={'':'0'} and runtime['quantization']['bnb_4bit_quant_type']=='fp4'
        a=audit(response);assert a['candidate_eligible'] and a['record_values_unchanged']
        candidate=a.pop('candidate_text');start,end=a['span'];assert candidate==response[start:end]
        # The original Result numeric lexemes, duplicates and every row stay byte-for-byte.
        candidate_path=R/'diagnostics/candidates'/(pid+'.candidate.json');candidate_path.write_text(candidate,encoding='utf-8');candidate_files.append(candidate_path)
        rows=json.loads(candidate);duplicate_count=len(rows)-len({json.dumps(x,sort_keys=True) for x in rows})
        rec={'paper_id':pid,'historical':historical,'source_output':str(folder/'output.json'),'source_output_sha256':sha(folder/'output.json'),'response_sha256':sha(call/'response.txt'),'raw_pipeline_sha256':sha(call/'pipeline_raw_response.json'),'prompt_sha256':request['prompt_sha256'],'format_audit':a,'candidate_path':str(candidate_path),'candidate_sha256':sha(candidate_path),'duplicate_records_retained':duplicate_count,'usage':usage,'wall_seconds':item['wall_seconds'] if item else None,'candidate_not_used_for_normalization_or_evaluation':True}
        records.append(rec)
        entry=next(x for x in manifest['papers'] if x['paper_id']==pid)
        entry.update(generation_status='COMPLETE',parse_status='COMPLETE' if a['raw_schema_acceptable'] else 'FAILED',candidate_format_status='ELIGIBLE_PENDING_USER_APPROVAL' if not a['raw_json_valid'] else 'NO_CORRECTION_NEEDED',normalization_status='BLOCKED',evaluation_status='BLOCKED',output_index=str(folder/'output.json'),historical_generation_reused_for_diagnosis=historical)
    manifest.update(status='DIAGNOSTICS_COMPLETE_AWAITING_USER_PROTOCOL_APPROVAL',new_extraction_calls=3,historical_extraction_examined=1,paid_api_calls=0,formal_scope_approval=False,custom_format_policy_approval=False)
    save(R/'experiment_manifest.json',manifest);save(R/'diagnostics/format_audit.json',records);save(R/'extraction/output_index.json',records)
    current=[x for x in records if not x['historical']];calls=[x['usage']['actual_generation'] for x in current]
    usage={'new_extraction_calls':3,'new_normalization_calls':0,'paid_api_calls':0,'automatic_retries':0,'input_tokens':sum(x['input_tokens'] for x in calls),'output_tokens':sum(x['output_tokens'] for x in calls),'generation_seconds':sum(x['generation_seconds'] for x in calls),'batch_wall_seconds':state['seconds'],'peak_gpu_allocated_bytes':max(x['peak_allocated_bytes'] for x in calls),'peak_process_rss_bytes':max(x['usage']['process_peak_rss_bytes'] for x in current),'final_gpu':state['final_gpu'],'historical_extraction_examined_not_regenerated':1}
    save(R/'generation_usage.json',usage)
    table='\n'.join(f"| {x['paper_id']} | {x['usage']['actual_generation']['input_tokens']} | {x['usage']['actual_generation']['output_tokens']} | {x['usage']['actual_generation']['finish_reason']} | {'是' if x['format_audit']['raw_json_valid'] else '否'} | {x['format_audit']['records']} | {','.join(sorted(set(x['format_audit']['result_types'])))} | {x['duplicate_records_retained']} |" for x in records)
    write('format_audit.md',f'''# Llama-3 格式诊断（尚未批准正式处理）

结论：不是重复 Prompt 或包装器误切分。历史与新增每次 pipeline 原始文本都严格等于完整请求 Prompt + 作者包装后的响应；四个实例中的三个由模型自行生成说明性前缀。新增三篇均 EOS，未触及 1024 上限。

## 作者依据与边界

[冻结 README 第145行](https://github.com/UKPLab/emnlp2024-leaderboard-generation/blob/8bf74b0a830feb7035c6166dce3394dc344ae532/README.md#L145) 允许标准化前使用格式纠正后的输出，但未规定算法、白名单或人工修改界限。官方 tdm_extraction.py 原样保存模型字符串；tdm_llm_normalization.py 直接 json.loads，然后对 Result 使用 str()。因此数字 Result 不必在适配层手动转换。原 Prompt 的示例使用字符串，但源码能接受有限 JSON 数值。

已有 author_hf_pipeline.py 是作者固定 community 0.0.20 模块的逐字节副本，SHA256 为 6716e012f55d006674dc320b4204015024a5f776fdaefbfe6c55fbbff3136d7c。它只恢复原版对返回输入 Prompt 的移除，不删除生成的说明前缀。已实测完整文本等式，未重复套 chat template。

43 个实际 RetrievalQA Prompt 与独立渲染一致；每篇仅一个 begin_of_text、三段 header。实际 pipeline add_special_tokens=False，Llama-3 tokenizer 的 BOS=128000、EOS=128009；作者加载后添加 pad=128256。生成的 EOS 配置为 [128001,128009]，实际 do_sample=False、max_new_tokens=1024、seed=0。原模型配置中采样默认值被 pipeline 参数覆盖；没有改变原配置。

## 实际输出

| 论文（最后一行为历史 smoke） | 输入 Tokens | 输出 Tokens | 结束 | 原文可直接解析 | 唯一数组内候选条数 | Result 类型 | 重复条数（保留） |
|---|---:|---:|---|---|---:|---|---:|
{table}

候选条数只描述数组结构，不代表结果正确或已经通过正式标准化。全部原始输出仍保留，重复记录未删除。

## 提交确认的候选规则 v1

1. 原始完整响应能直接 json.loads 且字段可接受时直接使用原响应，不改写。
2. 否则必须存在唯一完整的最外层 JSON 数组；只允许移除空白、精确前缀 `Here are the extracted tuples in JSON format:` 以及成对的完整 Markdown JSON 代码围栏。
3. 数组内部逐字符保留，不改 Task/Dataset/Metric/Result，不改变数值字面形式、顺序、重复项和条数，不在这里把数字转字符串。Result 的 str() 仅由官方标准化源码完成。
4. 多个数组、截断、未知前后缀、解释性后缀、重复 JSON 键、NaN/Infinity、缺字段、额外字段、非标量 Result 均保留失败。不得选取一个看似较好的片段、补括号、补字段或调用模型修复。
5. 即使语法可解析，非 EOS/异常结束也必须单独标记，不能据此宣称生成完整。本轮三个新增样本均 EOS。

三个带前缀实例都恰好只删除数组外49个字符；候选文件中的数组内部与原响应片段完全相同。所有字段和值保持一致，包括 `89.80` 这样的原始数值文本。候选文件仅在 diagnostics/candidates/，**没有作为正式 output.json、Normalization 或评价输入**。

具体例子（仅展示一个条目，完整候选文件保留全部13条）：原响应为说明前缀后接数组，其中包含 `{{"Task": "Abstractive Summarization", "Dataset": "CNNDM", "Metric": "ROUGE-1", "Result": 44.29}}`。候选处理只移除数组之前的前缀；这个条目原样保留，不把 CNNDM 改成 Gold 名称，不更换44.29。

13项边界测试通过。该具体规则不是作者定义的算法，按本次用户附件第三节要求，正式使用前仍须确认。
''')
    listing='\n'.join(f"| {x['paper_id']} | {x['input_tokens']} | {x['evidence_count']} | {x['tables']} | {x['gold_count_for_scope_only']} |" for x in manifest['papers'] if x['eligible'])
    write('context_scope.md',f'''# 输入长度与拟定42篇评价口径（待确认）

固定模型原生上下文8192；预留官方1024新 Tokens，完整输入允许7168 Tokens。43篇按同一官方 Prompt、tokenizer 与实际 pipeline 统计；42篇合规，1篇 `1912.08777.pdf` 输入55324、48条证据，其中44条表格，另需1024输出。它的36条 Gold 不在拟定子集内。

42篇合计 **259条 Gold TDMR**。最长合规输入 `1511.08308.pdf` 为4661，加预算共5685，不是真正接近8192。三个诊断样本由最短输入、最多表格、最长合规输入确定，未根据模型表现选择。

原论文4.1节给出文本分块和相关文本+全部表格拼接；pdf_loader.py 使用2000字符/200重叠，原 CustomRetriever 返回语义文本与全部表格。本次已复用冻结证据。在冻结源码及论文所查部分未找到超长输入截断、RoPE调整、再分段生成或删表规则，因此不得替超长论文添加新处理。

## 拟定评测与失败处理

- 保留原始43篇 Gold；只在本目录生成42篇评测派生副本。Normalization 候选及 Partially 隐藏规则仍从完整43篇构建，不改变23/71/26名称集合。
- 27个原始 Gold 排行榜都保留；仅删除其1912.08777.pdf条目，共140→131个榜内条目，9个榜受影响，所有榜仍至少3篇。GPT配对比较也须用同一42篇/131条目范围。
- 元组指标调用未经修改的官方脚本，逐篇 Macro P/R；F1=2PR/(P+R)，不取逐篇F1算术平均。
- 建议将42篇设为固定评价分母。不能解析或标准化失败的论文保留 FAILED 状态，并在独立“评价输入”中记空预测以避免静默剔除；原始响应不改写、不伪称成功。同时报告有效输出覆盖率和仅成功样本的附加分数。此失败输入策略尚未执行，也需随42篇口径确认。
- 超长论文属于事先排除的输入阻塞，不计入42篇成功或失败分母；43篇覆盖仍明确为最多42/43。不能称完整43篇复现，也不与论文43篇分数计算正式差值。
- 官方数值列表 RBO 与独立论文ID AO 分别保留。原论文表5名为 AO 的列与代码 RBO 定义差异仍须标注，不能互换命名。

| 论文 | 输入 Tokens | 证据数 | Table数 | Gold条数（仅范围统计） |
|---|---:|---:|---:|---:|
{listing}
''')
    gpt43=read(PILOT/'full43_uncapped/evaluation/metrics_with_f1.json')['aggregate'];gpt42=read(R/'evaluation/gpt41_reference_scope42/metrics_with_f1.json')['aggregate']
    paper={'Fully LLM':{'Task IIM':[87.33,92.17,89.68],'Dataset IIM':[92.09,87.75,89.87],'Metric IIM':[94.90,89.48,92.11],'Result IIM':[39.50,49.56,43.96],'TDM Exact Match':[77.13,72.56,74.77],'TDMR Exact Match':[27.11,35.60,30.78]},'Fully CS':{'TDMR Exact Match':[23.22,29.54,26.00],'TDM Exact Match':[62.02,58.07,59.98]},'Partially':{'TDMR Exact Match':[15.70,18.75,17.09],'TDM Exact Match':[50.75,45.30,47.87]}}
    save(R/'references/paper_metrics.json',{'source':'https://aclanthology.org/2024.emnlp-main.453.pdf','column_order':'P/R/F1 (paper tables order R/P/F1 explicitly converted)','unit':'percent','metrics':paper,'paper_table5':{'Fully LLM':{'LR':96.30,'PC':79.18,'RC':29.30,'AO_as_named_in_paper':25.49},'Fully CS':{'LR':81.48,'PC':60.15,'RC':22.65,'AO_as_named_in_paper':21.45},'Partially':{'LR':92.59,'PC':61.90,'RC':19.01,'AO_as_named_in_paper':19.52}},'full43_paper_pdf_sha256':sha(PRE/'references/scilead_emnlp_2024.pdf')})
    paper_table='\n'.join(f"| {metric} | {' / '.join(f'{v:.2f}' for v in values)} | 未评价 | {gpt43[metric]['Precision']*100:.2f} / {gpt43[metric]['Recall']*100:.2f} / {gpt43[metric]['F1']*100:.2f} |" for metric,values in paper['Fully LLM'].items())
    write('comparison_with_paper.md',f'''# 原论文参考值与可比性

[论文 Table 3、4、12](https://aclanthology.org/2024.emnlp-main.453.pdf)。下表百分制列顺序统一为 P/R/F1；原文表格为 R/P/F1。本轮没有新的 Llama 评价分数，不计算正式差值。

| Fully LLM 指标 | 原论文 Llama-3（43篇） | 本地 Llama-3 | 冻结 GPT-4.1（43篇） |
|---|---|---|---|
{paper_table}

原论文 Llama-3 + CS 的 TDM/TDMR F1 为59.98/26.00；Partially 为47.87/17.09。表5 Fully LLM 的 LR/PC/RC/原文AO 为96.30/79.18/29.30/25.49。完整参考数值与来源哈希见 references/paper_metrics.json。

本地当前仅三篇诊断，拟定正式范围42篇；不能将这些参考值相减后声称复现差距。硬件 A800 对原文 A100、Windows冻结证据、兼容依赖版本与具体格式整理协议都必须记录；没有实验依据时不能将差异归因于其中任一项。

原论文还报告 Llama-3 Cold Start（表5、6、17、18等），本轮仅列为待确认，未启动；不扩展到Cold Start、threshold=2或其他模型。
''')
    compare='\n'.join(f"| {k} | {v['Precision']*100:.4f} | {v['Recall']*100:.4f} | {v['F1']*100:.4f} | 未评价 |" for k,v in gpt42.items())
    write('comparison_with_gpt41.md',f'''# 同范围 GPT-4.1 离线参考

为后续配对比较，已对冻结 GPT-4.1 Fully LLM 的同一42篇预测，使用派生42篇 Gold，实际调用未修改 tdm_eval.py。没有重新抽取、标准化或请求模型。原始 full43_uncapped 未改动。

| 指标 | GPT-4.1 P(%) | R(%) | F1(%) | 本地 Llama-3 |
|---|---:|---:|---:|---|
{compare}

F1由官方聚合P/R另外计算。42篇259条Gold，TDMR F1={gpt42['TDMR Exact Match']['F1']:.6f}；冻结43篇为{gpt43['TDMR Exact Match']['F1']:.6f}。这两者的变化来自评价范围，不能称模型进步。本轮没有可配对的正式 Llama 分数，不计算模型差值。

原始官方JSON、逐篇值、调用参数、脚本哈希见 evaluation/gpt41_reference_scope42/。该目录全是 GPT 参考，不是 Llama 评价。后续排行榜比较也必须重算同42篇/27榜/131榜内条目；当前未将43篇排行榜分数冒充该范围结果。
''')
    save(R/'evaluation/llama_evaluation_status.json',{'status':'BLOCKED','reason':'Await formal 42-paper scope and candidate formatting protocol approval','official_metrics':None,'not_zero_score':True})
    for branch in ['fully_llm','fully_cs','partially']:save(R/'normalization'/branch/'status.json',{'status':'BLOCKED','reason':'Formal protocol not approved; no new Llama normalization calls','actual_calls':0})
    elapsed=state['seconds']/60;remaining_minutes=state['seconds']/3*38/60
    write('formal_protocol_proposal.md',f'''# 待确认的正式协议

1. 采用 format_audit.md 的保守语法规则v1。只移除已明确白名单的外层文本/完整围栏；数组内逐字节不变。数字Result由原官方标准化执行str()。未知、截断、重复键等情况继续失败。
2. 范围为42篇、259条Gold；排除超长1912.08777.pdf。候选名称仍完整43篇23/71/26。排行榜27个、131榜内条目；失败处理按context_scope.md固定分母方案，必须同时报有效覆盖率。
3. 建议直接复用本轮3篇和历史2020.findings-emnlp.378.pdf的原始生成（输入/参数已核对），不重生成以改善格式或得分；剩余38篇各一次。若某记录不能依协议整理则保留失败，不挑选其他样本。
4. 原参数不变：revision固定、作者FP4/bfloat16/greedy、seed0，Extraction1024、名称标准化15、排行榜对齐100。Fully LLM、CS、Partially分别保存，Cold Start仍不在本轮范围。
5. 不安装新依赖、不下载Llama权重；CS本地10个文件约2.11GiB与冻结SHA一致，既有CPU前向记录可追溯，但本轮未做新CS推理/远端迁移。后续需复用这些权重，不能拿GPT映射充当Llama结果。

## 时间与资源估算

三篇实测{elapsed:.2f}分钟（各自加载模型），纯生成{usage['generation_seconds']:.2f}秒。按相同编排线性外推，剩余38篇Extraction约{remaining_minutes:.1f}分钟；样本非随机、输出长短不同，保守预留0.5–2小时。若使用保持相同模型参数的进程内复用可减少重复加载，但不能据此承诺耗时。

Fully与Partially第一阶段各最多3×预测记录数的名称调用；第二阶段还依唯一TDM数追加调用。15/100输出预算保持不变。尚无本轮标准化吞吐测量，不能给出精确总时长；A–E建议预留约2–6小时，作为工程预算而非实测结果。CS迁移/验证如需要另计。峰值GPU allocated已测约{gib(usage['peak_gpu_allocated_bytes']):.2f}GiB，进程RSS约{gib(usage['peak_process_rss_bytes']):.2f}GiB，未发生OOM。

确认前不启动正式42篇，不把候选数组送入模型。服务器继续保持现有计费模式，不关机、不重启。
''')
    integrity=read(R/'integrity_before.json');assert all(sha(Path(x['path']))==x['sha256'] for x in integrity)
    requests=list((R/'extraction').rglob('request.json'));assert len(requests)==3
    verify={'status':'PASS_FOR_DIAGNOSTIC_SCOPE','protected_files_unchanged':len(integrity),'remote_source_and_evidence_hashes_verified':pre['source_hash_files'],'prompt_capture_matches':43,'new_extraction_calls':3,'new_normalization_calls':0,'paid_api_calls':0,'raw_pipeline_equals_prompt_plus_output_all_four_cases':True,'raw_prompt_hashes_match_frozen_audit':True,'candidate_array_spans_verbatim':True,'candidate_policy_tests':13,'official_source_prompt_gold_unchanged':True,'raw_outputs_unmodified':True,'formal_protocol_approved':False,'formal_experiment_started':False,'all_new_generations_eos':True,'original_adapter_direct_valid_papers':1,'new_candidate_arrays_total_records':27,'gpu_released':state['final_gpu'],'official_llama_evaluation_run':False,'official_gpt_scope42_reference_evaluation_run':True,'CS_new_embedding_calls':0}
    save(R/'verification.json',verify)
    speedtable='\n'.join(f"| {x['paper_id']} | {x['usage']['actual_generation']['generation_seconds']:.2f} | {x['wall_seconds']:.2f} | {gib(x['usage']['actual_generation']['peak_allocated_bytes']):.2f} | {gib(x['usage']['process_peak_rss_bytes']):.2f} |" for x in current)
    write('run_report.md',f'''# SCILEAD Llama-3 70B 本轮执行报告

**已完成三篇单次诊断，正式实验尚未启动。** 3/3成功生成并EOS，1/3原响应可直接作为JSON输入；另2篇的唯一完整数组可按候选规则保留，但该规则等待用户确认。生成成功、语法有效、完成评价、达到原论文性能分别记录，不能等同。

## 真实输出

| 论文（末行为历史） | 输入 | 输出 | 结束 | 原始JSON有效 | 数组候选条数 | Result类型 | 保留重复条数 |
|---|---:|---:|---|---|---:|---|---:|
{table}

| 本轮论文 | 纯生成秒 | 子进程总秒 | GPU allocated峰值GiB | RSS峰值GiB |
|---|---:|---:|---:|---:|
{speedtable}

本轮合计输入{usage['input_tokens']}、输出{usage['output_tokens']} Tokens；总运行{state['seconds']:.2f}秒；3次本地生成、0次重试、0次付费API。结束GPU状态：{state['final_gpu']}（used/free）。实例未关机或改计费模式。

## 结论与停止点

格式问题已定位为模型生成的49字符外层前缀；未发现Prompt重复、错误chat包装或1024截断。作者README允许格式纠正但没有具体算法；官方Result本来会str()。保守候选已在独立目录测试，数组内部、数值、重复项均未改动，未送入标准化或计分。

当前42篇合规、259条Gold；1912.08777.pdf输入55324，含36条Gold，保持BLOCKED。正式42篇范围、失败评价口径和格式规则均须用户确认；依据来自本次附件第三、五节。所需最小规则、实例与时间预算详见formal_protocol_proposal.md。

Extraction：新增3次完成；Fully LLM/CS/Partially：未执行；Llama IIM/TDM/TDMR与排行榜P/R/F1、LR/PC/RC/RBO/AO：**N/A，尚未评价，不能记为0**。只完成了同范围GPT-4.1的免费离线官方评价，TDMR F1={gpt42['TDMR Exact Match']['F1']:.6f}，明确不计作Llama结果。

## 工程记录与完整性

复用原环境和30片权重；本轮未下载/安装。69个远端源码/证据哈希一致；本地{len(integrity)}个受保护文件哈希未变。CS已有10个模型文件SHA再次通过，没有重复嵌入计算。

仅修正诊断工程问题：历史pipeline日志为嵌套批次列表，按实际结构读取；Windows官方评价子进程启用UTF-8并使用任务内离线缓存路径；初次扩大历史文件扫描耗时，停止本任务扫描后改用明确214个保护文件清单。没有修改模型、Prompt、官方算法或预测。

本地：`{R}`；远端：`{RR}`。原始输出在extraction/，候选在diagnostics/candidates/，逐条哈希与判据在diagnostics/format_audit.json；execution状态见experiment_manifest.json。正式入口沿用原 adapters/run_llama.py，但确认前不得启动。恢复时先检查request/complete，不能删除失败检查点来重跑。
''')
    plan=(R/'plan.md').read_text(encoding='utf-8')
    for i in range(1,7):plan=plan.replace(f'- [ ] {i}.',f'- [x] {i}.')
    (R/'plan.md').write_text(plan,encoding='utf-8')
    print(json.dumps({'new_generations':3,'raw_json_valid':1,'candidate_records':27,'historical_candidate_records':6,'scope42_gold':259,'protected_files_unchanged':len(integrity),'formal_started':False}))
if __name__=='__main__':main()
