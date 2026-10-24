"""Build P4 reports and independently verify saved request data; no API clients."""
import json,hashlib,csv,ast,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=Path(r'D:\C++\SCILEAD');REPO=ROOT/'emnlp2024-leaderboard-generation';E=Path(r'E:\SCILEAD\axcell')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def md(n,s):(OUT/n).write_text(s.strip()+'\n',encoding='utf-8')
summary=read(OUT/'estimation.json');m=read(OUT/'normalization_request_manifest.json');p=read(OUT/'normalization_request_preview.json')['requests'];records=read(OUT/'record_provenance.json');inputs=read(OUT/'normalization_input.json');config=read(OUT/'config.json');sets=read(OUT/'candidate_sets.json');prompt=read(OUT/'prompt_snapshot.json')
assert len(p)==123 and len(records)==65 and len(inputs)==37
assert sum(not json.loads(v['output']) for v in inputs.values())==9
request_by={(x['paper_id'],x['record_index'],x['field']):x for x in p}
assert len(request_by)==123
for rec in records:
    t=rec['tdmr'];raw=rec['raw_prediction']
    assert t=={'Task':raw['task'],'Dataset':raw['dataset'],'Metric':raw['metric'],'Result':str(raw['score'])}
    for field in ('Task','Dataset','Metric'):
        key=(rec['paper_id'],rec['record_index'],field)
        if t[field] in ast.literal_eval(sets[field]):assert key not in request_by
        else:
            q=request_by[key];payload=q['payload']
            assert payload=={'model':'gpt-4.1-2025-04-14','temperature':0,'seed':0,'stream':False,'n':1,'messages':[{'role':'system','content':prompt['system']},{'role':'user','content':'\n\nItem list: '+sets[field]+'\n\nInput: '+t[field]+'\n\nAnswer: '}]}
            # The wire payload contains only the official names and one AxCell field; no paper/Result/provenance/Gold tuples.
            assert not set(payload)&{'max_tokens','max_output_tokens','max_completion_tokens','tools','response_format'}
expected=read(OUT.parent/'20261022_formal/experiment_manifest.json')
assets=[]
for x in expected['models']:
    path=E/x['path'];actual=sha(path);assert actual==x['expected_sha256'] and path.stat().st_size==x['expected_bytes']
    assets.append({'path':str(path),'sha256':actual,'bytes':path.stat().st_size,'matches_frozen_model_manifest':True})
save('model_asset_verification.json',{'files':assets,'all_match':True,'models_loaded':False,'note':'Read-only streaming hash; no torch/model deserialization or remote execution'})
# Check all fixed-revision source blobs, allowing only Git CRLF checkout conversion.
tree=read(OUT/'public_sources/fixed_tree.json');source_checks=[]
for item in tree['tree']:
    if item['type']!='blob':continue
    path=REPO/item['path'];data=path.read_bytes()
    def gitsha(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    exact=gitsha(data)==item['sha'];crlf=gitsha(data.replace(b'\r\n',b'\n'))==item['sha']
    source_checks.append({'file':item['path'],'expected_git_blob':item['sha'],'exact_bytes_or_checkout_line_endings':exact or crlf,'sha256':sha(path)})
assert all(v['exact_bytes_or_checkout_line_endings'] for v in source_checks)
save('official_source_verification.json',{'commit':tree['sha'],'files':source_checks,'all_match':True})
protected=read(OUT/'protected_files_before.json');history=read(OUT/'historical_files_read_sha256.json')
changed=[]
for path,entry in {**protected,**history}.items():
    f=Path(path)
    if not f.is_file() or f.stat().st_size!=entry['bytes'] or sha(f)!=entry['sha256']:changed.append(path)
assert not changed
with (OUT/'paper_scope_comparison.csv').open(encoding='utf-8-sig',newline='') as f:scope=list(csv.DictReader(f))
assert len(scope)==43 and len({r['paper_id'] for r in scope})==43
assert sum(r['status']=='FAILED' for r in scope)==2 and sum(r['status']=='TEX_UNAVAILABLE' for r in scope)==4
known=[r for r in records if r['known_error']];assert len(known)==3
public={'retrieved_utc':datetime.now(timezone.utc).isoformat(),'paper':{'url':'https://aclanthology.org/2024.emnlp-main.453.pdf','section':'Appendix C, Experimental Details','printed_page':7974,'pdf_page_1_based':12,'facts':'AxCell uses 36 downloaded TeX sources from43; evaluation restricted to those36 Gold papers; fully predefined normalization used GPT-4 Turbo. No member list found in inspected text.','prior_report_reference_correction':'Earlier scope report said Appendix B; new audit locates paragraph in Appendix C; frozen report unchanged.'},'github':{'fixed_tree_url':'https://api.github.com/repos/UKPLab/emnlp2024-leaderboard-generation/git/trees/8bf74b0a830feb7035c6166dce3394dc344ae532?recursive=1','tracked_files':len(source_checks),'dedicated_axcell_subset_manifest_present':False,'release_list':read(OUT/'public_sources/releases.json')},'attachments':{'attempted_urls':['https://aclanthology.org/2024.emnlp-main.453.software.zip','https://aclanthology.org/2024.emnlp-main.453.data.zip'],'status':'HTTP404; cannot inspect via these URLs. Not proof no author list exists elsewhere.'},'local_data_readme':str(Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\README.md')),'pricing':{'url':'https://developers.openai.com/api/docs/models/gpt-4.1','checked_utc':summary['pricing']['checked_utc'],'usd_per_million_input':2,'usd_per_million_output':8,'usage':'Reference calculation only, cached input discount not assumed'},'provider':{'url':'https://9527.codes/','public_text':'JavaScript-only shell, no verifiable price obtained','price':'UNVERIFIED','paid_or_authenticated_endpoints_queried':False}}
save('source_evidence.json',public)
costrows='\n'.join(f"| {title} | {x['input_tokens']:,} | {x['output_tokens']:,} | {x['total_tokens']:,} | ${x['openai_reference_usd']:.6f} |" for title,x in [('历史均值',summary['cost_scenarios']['historical_mean']),('逐字段历史P95情景',summary['cost_scenarios']['historical_per_field_p95']),('每请求128输出Token规划情景（不是上限）',summary['cost_scenarios']['planning_128_tokens_each_NOT_A_CAP'])])
md('normalization_cost_estimate.md',f'''# P4 标准化请求量、Token与费用估算

计算时间（UTC）：{summary['created_utc']}。状态：仅准备，实际GPT请求0次，实际本轮API费用0；尚未批准收费执行。

模型固定 `gpt-4.1-2025-04-14`，服务 `https://9527.codes/v1`。65条原始预测来自28篇；9篇VALID_EMPTY不产生请求。195个Task/Dataset/Metric字段中72个精确命中而跳过。预计新增 **123次请求**：Task50、Dataset45、Metric28。27篇实际需要调用，另一篇非空论文2020.emnlp-main.523.pdf的六个名称字段全精确命中。

核验可复用AxCell检查点0个，新增请求123；123个位置对应40种不同payload，83个重复位置仍逐次处理，不增加名称缓存。官方逐字段实现没有跨记录缓存；未来只恢复同一输入/位置/完整请求的已成功检查点，不以历史GPT预测替换AxCell。

输入估算 **41,714 Tokens**，单次最大535。使用已有tiktoken的o200k_base与冻结适配器相同消息开销公式；不是服务端实际usage。历史542个同模型、同Fully Prompt、同候选序列、无客户端输出上限、HTTP200且finish_reason=stop的成功请求用于输出/耗时统计，原回答不复用。

| 情景 | 输入Token | 输出Token | 总Token | OpenAI公开参考费用/USD |
|---|---:|---:|---:|---:|
{costrows}

价格依据：[OpenAI GPT-4.1模型页](https://developers.openai.com/api/docs/models/gpt-4.1)，文本输入$2/百万Token，输出$8/百万Token；未假定缓存折扣。费用公式=(输入×2+输出×8)/1,000,000。核对时间：{summary['pricing']['checked_utc']}。

**这不是9527.codes的实际报价。** 其公开页面只返回需要JavaScript的壳，未获得该快照可核实价目、充值折算或账单规则，因此中转站单价和真实总费用保持UNVERIFIED/null，不推测美元与平台额度或人民币的换算。不登录收费接口做探测。

输出Token情景只是预算，不是请求参数或保证：请求不传max_tokens/max_completion_tokens/max_output_tokens；服务端可能产生更长响应，以上金额不是费用硬上限。128 Tokens/次也不会写入实际请求。若审批需硬金额上限，应先提供服务商价目/可接受预算，由后续独立执行保护在请求之间暂停，不能偷偷截断输出。

串行时间：历史均值加权约{summary['serial_time_estimate_seconds']['mean_seconds']/60:.2f}分钟；逐字段中位数加权约{summary['serial_time_estimate_seconds']['p50_seconds']/60:.2f}分钟，逐字段P95加权约{summary['serial_time_estimate_seconds']['p95_seconds']/60:.2f}分钟。规划5–15分钟含日志落盘；不是统计意义的全批P95或时限保证，不含网络中断和人工恢复等待。失败不自动重试。

本次请求范围为本地37篇已完成流程（248条Gold覆盖）中的65条真实预测；作者36篇成员仍未核实。需批准这一独立范围、123次新请求及中转站费用不确定性后才能执行。
''')
scope_lines='\n'.join('| '+' | '.join([r['paper_id'],r['gold_count'],r['status'],r['raw_records'] or '—',r['author36_membership']])+' |' for r in scope)
md('scope_and_gold_audit.md',f'''# P4 论文范围核查

已核实：完整Gold43篇/295条；既有TeX39篇/283条；当前流程完成37篇/248条Gold覆盖，其中28篇非空65条原始预测，9篇VALID_EMPTY。所有paper_id均与Gold完全对应；无缺Gold、无无法匹配ID。

作者36篇的确切成员与TeX版本仍**UNVERIFIED**。能确认“属于作者36篇且完成”的论文为0篇，是缺少成员证据，不表示与作者集合不相交。37篇成功论文全部标为“已完成、作者子集身份未核实”。禁止按抽取得分从39/37篇中挑36篇。

[原论文Appendix C](https://aclanthology.org/2024.emnlp-main.453.pdf)（PDF第12页，印刷页7974）说明取得36份TeX，针对这些论文的Gold评价，并用GPT-4 Turbo做Fully标准化，但检查文本未见成员名单。旧报告定位为Appendix B，此处纠正引用位置，旧文件保留。

本次成功读取固定GitHub树（21个文件）、Release列表（空），核验固定版源码与本地官方数据README/Gold结构；未见独立AxCell36成员清单。ACL页面列出的software.zip/data.zip URL本次直接GET均404，无法检查其内容，不能据此声称作者从未公开名单。证据与访问结果见source_evidence.json、public_sources/。

建议待确认的评价口径：后续主要报告“本地可解析37篇AxCell范围”，保留9篇有效空预测；另外报告39篇可用TeX的失败覆盖和43篇全数据集覆盖，不能把37篇分数当作作者36篇严格复现。39篇中的1905.03197.pdf（26 Gold）和2203.16804.pdf（9 Gold）继续FAILED，未纳入模型/标准化队列。4篇无已核实TeX：128538.pdf、D19-1367.pdf、C18-1139.pdf、D18-1105.pdf。P4不执行任何分数计算。

后续公平比较需要在同一论文范围复算已有模型；Llama-3缺1912.08777.pdf，若做三模型共同范围，则37篇与Llama的交集为36篇，但**这36篇只是本地比较交集，不等于作者AxCell36篇**。正式范围需P4审批，不能静默删除零预测或失败记录后声称全范围。

| paper_id | Gold数量 | 当前状态 | 原始预测数 | 作者36篇成员 |
|---|---:|---|---:|---|
{scope_lines}
''')
errorrows='\n'.join('| '+' | '.join([r['record_id'],r['tdmr']['Metric'],r['tdmr']['Result'],r['cell_ext_id'],r['known_error']])+' |' for r in known)
md('normalization_preflight.md',f'''# AxCell Extraction + GPT-4.1 Fully Normalization：P4预检查

**P3已由用户验收；P4请求准备完成，未执行标准化和评价，等待明确费用授权。**

输入来自20261022_stage3_resume的原始records.json及既有SCILEAD兼容output.json，不读取历史GPT预测替代AxCell。37篇包含28篇非空、9篇有效空；65条全部保留。37篇对应248条Gold仅用于覆盖计数，不是结果命中数。两篇解析失败原样保留。

候选集合由完整43篇/295条Gold构建：23 Task、71 Dataset、26 Metric。使用原str(set)、PYTHONHASHSEED=0，保存候选实际顺序与序列，字节级匹配冻结Fully候选文件。只将名称集合及当前AxCell单个字段值放入请求；不放入paper_id、Result、原表/单元格、其他字段或Gold答案绑定。

Prompt来自未修改的prompts.json中的normalization-system-prompt；调用未修改的NormalizationPrompt GPT分支生成system/user消息。gpt4-turbo-128k仅是官方模板分支标识，计划wire payload固定gpt-4.1-2025-04-14，temperature=0、seed=0、stream=false。不设置任何客户端输出Token上限、工具或response_format。未实例化API客户端；真正发送参数须在P5执行时再次核验，不能把本阶段计划当作已发送证据。

名称已精确命中时原样保留；不命中时逐字段调用，官方回答精确属于候选集合才接受，否则保存null，不strip、不去引号、不改缩写。Result保持P3字符串：AxCell已有float分数仅沿用P3的str(score)，不补单位、不缩放百分数、不纠正错误含义。来源表格文本另存record_provenance.json，不成为GPT上下文。

123个待调用位置（Task50/Dataset45/Metric28），72字段直接保留，0缓存命中，83个重复位置不去重。2020.emnlp-main.523.pdf虽非空但六个字段精确命中，0请求；9篇空输出也为0请求。未来只可复用同一实验位置、输入、Prompt、候选顺序、模型及完整参数均一致的成功检查点。

输入估算41,714 Tokens，输出历史均值估算474 Tokens；OpenAI公开参考约$0.087220，保守规划情景约$0.209380，但服务商价格未知且不设置输出上限，不能把这些数当报价或费用封顶。细节见normalization_cost_estimate.md。

以下已知错误全部保留，不做人工修复、不剔除：

| 记录ID | 原指标 | Result字符串 | 来源 | 错误类型 |
|---|---|---|---|---|
{errorrows}

来源核验：65条均保留paper_id、原模型名、record_index、原始JSON哈希、cell_ext_id、表格路径/哈希/原单元格。1511.08308v5的源表位于原单篇parsed_paper目录，其余位于正式stage2目录；这是索引路径差异，无重解析、无输入修改。

完整性：本轮3809个既有受保护文件哈希不变；7个E盘模型/词表文件匹配冻结模型manifest；固定Git提交的21个跟踪文件与官方Git blob一致（允许检出CRLF）。历史542个已完成请求仅用于Token/耗时统计，1626个相关文件只读核验。

生成器禁止socket连接、DNS及监听，并拒绝读取.env/私钥。依赖导入期间urllib3尝试探测本机IPv6监听(::1,0)，被拒绝并记录；没有外网连接尝试，更没有GPT请求。未读取或检查任何凭据的内容，后续授权执行才安全复用指定认证。

当前未验证项：作者36篇成员、9527.codes实际价目及当前服务可用性。没有用收费请求探测服务。已完成技术请求准备，但付费执行就绪状态仍为false，必须由用户批准范围和调用。

待P4确认：是否按“本地已完成37篇（保留9篇空输出）”独立口径，对65条预测执行123次标准化请求，并接受服务商账单与OpenAI参考价可能不同。即使获批，失败仍保存并停止该请求，不自动重试或换模型。
''')
md('report.md',f'''# AxCell P4准备交付

已完成离线核查及请求准备；实际GPT调用0、标准化0、评价0。停止在P4，未经批准不得收费执行。

- 原始范围：37篇完成，28篇非空，9篇VALID_EMPTY，65条预测；2篇解析失败保留。
- 123次拟新增请求：Task50、Dataset45、Metric28；72字段精确命中，缓存命中0。
- 41,714输入Tokens；历史均值474输出Tokens，参考费用$0.087220；每请求128输出Tokens规划情景$0.209380，不是上限。中转站实际价格UNVERIFIED。预计串行5–15分钟。
- 官方36篇成员仍未核实。当前范围仅能称“本地37篇可解析范围”，并另报39/43覆盖；完整43篇标准名称集合保持不变。
- 保留91.85误绑F1、4696实体数量、300向量维度这三类错误，未修正。
- 候选与Prompt、65条来源与Result、冻结文件通过核验；无模型、Docker、SSH或其他实验启动。

主要交付：normalization_request_manifest.json（123位置清单）、normalization_request_preview.json（全部精确payload）、normalization_input.json（37篇含空输出）、record_provenance.json、paper_scope_comparison.csv、normalization_preflight.md、normalization_cost_estimate.md、verification.json。

D盘目录：`{OUT}`。
E盘镜像目标：`E:\\SCILEAD\\axcell\\reports\\20261022_stage4_preparation`；镜像实际结果以sync_verification.json为准。文件中的D盘来源索引保留原值，不伪造E盘源文件；本轮不复制模型或重新下载数据。
''')
save('verification.json',{'status':'P4_PREPARED_AWAITING_EXPLICIT_APPROVAL','timestamp':datetime.now(timezone.utc).isoformat(),'processed_papers':37,'raw_records':65,'nonempty_papers':28,'valid_empty':9,'parse_failed':2,'planned_requests':123,'paid_api_calls':0,'cache_hits':0,'new_requests':123,'protected_local_files':len(protected),'historical_reference_files':len(history),'changed_files':changed,'models_verified':len(assets),'official_tracked_files_verified':len(source_checks),'all_results_preserved':True,'all_source_links_verified':True,'all_expected_messages_independently_reconstructed':True,'forbidden_output_limits_or_tools_in_payload':False,'no_source_model_or_prompt_changes':True,'remote_connected':False,'remote_assets_rehash_this_round':False,'remote_note':'No SSH/container/model operation this round; prior P3 remote integrity report retained, not represented as a new remote measurement','normalization_executed':False,'evaluation_executed':False,'scope_author36':'UNVERIFIED','provider_actual_price':'UNVERIFIED','normalized_output_file_created':False,'P4_approval_required':True})
print(json.dumps({'verification':'PASS','protected':len(protected),'historical_reference_files':len(history),'models':len(assets),'tracked_source':len(source_checks),'requests':len(p),'actual_calls':0}))
