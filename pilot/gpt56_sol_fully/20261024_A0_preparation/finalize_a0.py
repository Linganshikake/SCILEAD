"""Offline A0 proposal/report finalization; contains no paid execution entry point."""
from pathlib import Path
import json,csv,hashlib,sys,os
O=Path(__file__).resolve().parent;ROOT=Path(r'D:\C++\SCILEAD')
def guard(e,a):
    if e in ('socket.connect','socket.getaddrinfo','socket.bind'):raise RuntimeError('A0_NETWORK_FORBIDDEN')
    if e=='open' and isinstance(a[0],(str,bytes)):
        p=Path(os.fsdecode(a[0]));mode=a[1];flags=a[2]
        write=isinstance(mode,str) and any(c in mode for c in 'wax+') or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        if write and not p.resolve().is_relative_to(O):raise RuntimeError('ONLY_A0_OUTPUT_WRITABLE')
sys.addaudithook(guard)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,d):(O/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(name,text):(O/name).write_text(text,encoding='utf-8')
def field(value,source,status='PROPOSED'):
    return {'value':value,'source':source,'status':status}
model_url='https://developers.openai.com/api/docs/models/gpt-5.6-sol'
reason_url='https://developers.openai.com/api/docs/guides/reasoning'
api_url='https://developers.openai.com/api/reference/resources/responses/methods/create'
chat_url='https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create'
save('generation_config_proposal.json',{
    'document_type':'A0_PROPOSAL_NOT_EXECUTED','model_api_calls_authorized':0,'ready_to_execute':False,
    'model':field('gpt-5.6-sol','user + '+model_url,'OFFICIAL_ID_PROVIDER_MAPPING_UNVERIFIED'),
    'provider':field('9527.codes','user + designated local config','PROVIDER_UNVERIFIED'),
    'api_type':field('Chat Completions','proposal: minimal change to original GPT message roles; historical provider route'),
    'api_base_url':field('https://9527.codes/v1','proposal derived from configured root https://9527.codes and historical adapter'),
    'request_path':field('/v1/chat/completions','historical GPT-4.1 adapter; '+model_url),
    'reasoning_effort':field('medium',model_url+' documents default; fixed for both stages'),
    'reasoning_mode':field('standard','default documented in '+reason_url+'; no pro mode; Chat request omits unsupported mode field'),
    'extraction_output_budget':field({'field':'max_completion_tokens','tokens':32768},'proposal: historical visible max996, general reasoning guide initial reserve>=25000; '+chat_url),
    'normalization_output_budget':field({'field':'max_completion_tokens','tokens':32768},'proposal: historical visible max11 does not bound hidden reasoning; same initial reserve policy'),
    'temperature':field('OMIT','model-specific medium compatibility not confirmed; do not inherit GPT-4.1'),
    'seed':field('OMIT','generic Chat documentation is not model-specific determinism support'),
    'do_sample':field('OMIT','not a field in proposed OpenAI-compatible request'),
    'stream':field(False,'historical single-response logging protocol'),
    'structured_output':field('Plain text; omit response_format and schema enforcement','proposal: preserve original Prompt-only baseline; support exists officially but adds generation constraints'),
    'tools':field('OMIT','user prohibits agent tools; no web/file/code/shell/model fallback'),
    'history':field('Independent requests; omit previous_response_id/conversation/replayed reasoning','original per-paper/per-field method; no cross-paper context'),
    'timeout_seconds':field({'connect':20,'read':600,'write':30,'pool':20},'connect/write/pool from existing transport; read600 proposed for reasoning; no trial performed'),
    'automatic_retries':field(0,'user constraints and unknown-billing failure history'),
    'recovery':field('Persist attempt before send; never resend unknown/failed status without explicit bounded recovery authorization; retain all successes','existing checkpoint protocol'),
    'termination_validation':field('HTTP200, expected model mapping, stop, nonempty complete JSON and four fields for Extraction; exact candidate membership for Normalization','official task + existing validation'),
    'responses_alternative_documentation_only':{'api':'/v1/responses','input':'same system/user text as input items','reasoning':{'effort':'medium','mode':'standard'},'max_output_tokens':32768,'truncation':'disabled','store':False,'status_check':'completed; incomplete_details must be absent; reject budget exhaustion','source':api_url,'auto_fallback':False,'provider_supported':None},
    'fee_approval':field('NOT_REQUIRED_BY_USER; no fee report; record actual tokens if future execution authorized','latest user instruction; does not override A0 no-model-API rule'),
    'next_stage_gate':'User accepts A0 and separately authorizes A1; confirm provider alias/parameter routing and freeze proposal before any call'
})
credential=read(O/'credential_presence_audit.json');credential.update(configured_base_url_sanitized='https://9527.codes',configured_root_matches_expected_provider=True,configured_base_includes_v1=False,proposal_api_base='https://9527.codes/v1',base_difference='Historical adapter appends v1 independently; no credential/config edit performed')
save('credential_presence_audit.json',credential)
save('tokenizer_mapping_audit.json',{'library':'tiktoken','version':'0.14.0','target':'gpt-5.6-sol','encoding_name_for_model':'o200k_base','exact_model_mapping':None,'matched_prefix':'gpt-5','target_provider_tokenizer_verified':False,'message_overhead':'Existing Chat estimate, not proven target serialization','method':'Recomputed all actual messages locally, no token-count API or tokenizer download'})
write('request_count_estimate.md','''# 请求量估算

按用户最新指示，仅估算请求量，不制作费用报告或发起费用审批。

|阶段|预计请求数|依据|
|---|---:|---|
|Extraction|43|43篇输入完整，每篇一次；尚未确认服务商限制|
|Fully Normalization|约542|历史GPT-4.1的284条真实预测逐字段映射，共542次；新模型结果未知|
|合计|约585|历史规模参考，不是授权任务或固定实际次数|

若仍产生284条记录且三个名称字段均未精确命中，则最多852次Normalization、合计895次。它只是固定记录数下的上界；新模型记录数变化会改变请求数。一般规则为0≤Normalization≤3×新有效记录数，重复字段不合并，Result不请求名称映射。

历史真实记录：Extraction输入175935、输出12127 Tokens，最大单次可见输出996；Normalization输入173352、输出2021，最大单次可见输出11。完整来源和哈希见historical_token_records.json，不混入较早被替代或失败的请求。

本次重新构造43篇原始GPT消息并离线估算，输入仍为175935 Tokens，最长54504。tiktoken0.14.0将gpt-5前缀映射到o200k_base，但无该模型精确映射；消息开销和服务商分词尚未证明。因此数字一致有计算依据，不代表新模型的实际账单一定相同。

新模型隐藏推理用量、输出长度、格式失败率无法由GPT-4.1可靠预测。上述585条历史成功记录为筛选后的正式基线，不能用其零失败率预测新模型。近期服务错误也不能当作稳定的目标模型失败概率。不为故障预置额外收费重试。人工核查计划覆盖43篇全部状态、所有异常/null和至少每篇输出一次；实际失败数量届时报告。

可复用：证据、Prompt、候选集合、评价代码与对照结果。不可复用为新模型结果：任何历史Extraction或Normalization答案。A0新增模型请求数0。
''')
write('unresolved_questions.md','''# A0待确认事项

1. 9527.codes是否支持gpt-5.6-sol，是否锁定底层版本，返回model标识如何对应；官方ID不能证明转发后模型身份。
2. 该通道是否接受Chat Completions的reasoning_effort=medium和max_completion_tokens=32768，是否存在更小服务端默认限制。
3. 账户/令牌额度、模型分组与上游通道是否由控制台或客服核实；get_channel_failed根因仍未知。
4. 目标模型的实际tokenizer/Chat开销、请求限制与参数兼容，需资料及获准单篇试跑确认。
5. 用户验收A0并决定是否按提案进入A1。首篇建议2020.emnlp-main.152.pdf；无试跑授权前不生成请求。

费用不再要求审批或详细报告；无需重新提供密钥。A0的零模型调用边界不变。
''')
write('README.md','''# SCILEAD实验A — GPT-5.6 Sol Fully LLM A0

本目录是2026-10-24的正式A0交付：43篇、295 Gold TDMR、27榜，目标模型gpt-5.6-sol，计划服务商9527.codes。Extraction与Fully LLM Normalization均换用目标模型，其余原版流程保持。

**A0资料与输入准备完成；PROVIDER_UNVERIFIED；真实模型API调用0。** 不允许直接运行单篇测试、模型探测或历史请求重试。下一阶段是用户验收并明确授权后的单篇A1。

先读A0_summary.md、generation_config_proposal.json和provider_compatibility_audit.md。配置是提案，不是已经执行的请求参数。按最新指示不制作费用报告，只给请求量参考；官方价格文档作为资料保留。

核心文件：input_manifest.csv、input_token_estimate.csv、normalization_request_estimate.json、request_count_estimate.md、model_specification.md、official_pricing_reference.md、experiment_design.md、error_handling_plan.md、unresolved_questions.md、verification.json。

inputs/只有原样证据与两条Extraction消息；Gold计数仅位于审计manifest，不作为消息传入。official_docs/是公开文档离线副本，抓取没有认证也不是模型API请求。scripts均为离线核验或公开文档下载，没有模型调用入口。

相邻a0_20261024是收到完整后半段要求前的草稿，保留不覆盖；以本目录最终交付为准。此前统一GPT-4.1标准化中断任务没有继续运行。
''')
write('A0_summary.md','''# A0验收摘要

日期：2026-10-24。**A0准备完成，服务商兼容性保持PROVIDER_UNVERIFIED，停在A0。** 本轮模型API调用0，模型探测0，未运行试跑、推理、Normalization或评价。公开文档读取不携带密钥；本地凭据仅核查存在性与安全的基础URL。

1. **模型规格**：官方gpt-5.6-sol，1050000上下文、922000最大输入、128000最大输出；推理强度none/low/medium/high/xhigh/max，medium为默认。官方标准参考价格输入4、缓存输入0.40、输出20美元/百万Tokens；>272K输入时需用长上下文价格。详情及离线原件已保存，非服务商报价。
2. **服务商**：未确认支持目标模型、固定快照或参数。附件BASE_URL为https://9527.codes，历史接口为/v1/chat/completions；建议base_url带/v1，未改.env。密钥没有输出、复制或提交Git。
3. **通道故障**：get_channel_failed尚无服务商根因确认。历史24次成功与10次失败并存，不能认为已恢复。没有在A0重试。
4. **输入范围**：43篇、172个检索正文块、301个表格文档，证据内容与顺序不变；295 Gold、27榜。独立重构的完整消息代理估算175935 Tokens，最长54504；按官方限制有充足余量，但目标分词/中转限制仍需试跑验证，不沿用Llama的上下文阻塞规则。
5. **请求量**：约43次Extraction＋542次Normalization＝585次；542来自历史284条预测，新模型实际调用数取决于新有效字段。按最新指示不做费用情景报告或审批。不得把585条当成已获准自动执行的任务。
6. **单篇提案**：gpt-5.6-sol、medium、单轮Chat Completions、两阶段总输出预算各32768、stream=false；不传旧seed/temperature/do_sample、工具或JSON schema强制参数。原Prompt不变。预算包括隐藏推理；不足时记录截断/不完整，不补写。完整参数来源及Responses差异见配置提案和兼容审计。
7. **待确认**：服务商模型映射、通道恢复、参数转发与限制；用户验收A0并授权A1。建议首篇2020.emnlp-main.152.pdf基于输入追溯完整、规模适中，未根据得分挑选。未确认前不调用模型。

输出全部位于独立目录。旧GPT-4.1、Llama-3、Llama-2、AxCell、官方源码、Prompt、Gold均未写入；本次读取的冻结证据、调用记录及配置均做前后哈希检查。新报告不声称强模型已经解决任何错误，也不生成伪实验分数。
''')
sources=read(O/'read_source_hashes.json');assert all(sha(Path(p))==h for p,h in sources.items())
docs=read(O/'official_docs/retrieval_manifest.json');assert all(next(d for d in docs if d['title']==n).get('http_status')==200 for n in ['model','pricing','responses','reasoning'])
for d in docs:
    if d.get('sha256'):assert sha(Path(d['file']))==d['sha256']
man=read(O/'input_manifest.json');assert len(man)==43 and sum(r['text_blocks'] for r in man)==172 and sum(r['table_documents'] for r in man)==301
prompts=read(O/'frozen_prompts.json')
for r in man:
    ds=read(O/'inputs'/r['paper_id']/'source_documents.json');ms=read(O/'inputs'/r['paper_id']/'extraction_messages.json')
    assert ms==[{'role':'system','content':prompts['tdm-extraction-system-prompt'].format()},{'role':'user','content':prompts['query']+'\n\nRetrieved document contents:\n\n'+'\n\n'.join(d['content'] for d in ds)+'.\n\n Output json:\n\n'}]
# Exact-value local leakage check; never emit, hash or copy the credential contents.
from dotenv import dotenv_values
v=dotenv_values(ROOT/'SCILEAD_small_test/.env',interpolate=False,encoding='utf-8-sig');secrets=[v[k].encode() for k in ['OPENAI_API_KEY','API_KEY','SK'] if v.get(k) and len(v[k])>=16]
assert secrets
for p in O.rglob('*'):
    if p.is_file():assert not any(secret in p.read_bytes() for secret in secrets),'SECRET_LEAK'
del v,secrets
save('verification.json',{'status':'A0_COMPLETE_PROVIDER_UNVERIFIED','ready_for_model_call':False,'date':'2026-10-24','papers':43,'gold_tdmrs':295,'leaderboards':27,'text_blocks':172,'table_documents':301,'all_inputs_complete':True,'all_messages_exact_original_gpt_template':True,'gold_predictions_and_taxonomy_excluded_from_extraction':True,'source_hash_checks_passed':len(sources),'write_scope':'Only independent A0 directory; earlier draft retained','frozen_results_modified':False,'official_docs_saved_and_hashed':4,'model_api_requests':0,'model_probe_requests':0,'provider_network_requests':0,'public_document_gets_only':True,'paid_calls':0,'credentials_file_read_only':True,'secret_value_scan_passed':True,'candidate_counts':{'Task':23,'Dataset':71,'Metric':26},'target_model':'gpt-5.6-sol','provider_status':'PROVIDER_UNVERIFIED','no_executable_model_request_job':True,'fee_report_omitted_per_latest_user_instruction':True,'request_count_reference':585,'no_new_prediction_or_evaluation':True,'a0_conditions':'Input, documentation, configuration proposal and request estimate completed; provider questions explicitly recorded; awaiting A0 acceptance'})
save('delivery_manifest.json',{str(p.relative_to(O)):sha(p) for p in O.rglob('*') if p.is_file() and p.name!='delivery_manifest.json'})
print(json.dumps({'status':'A0_COMPLETE_PROVIDER_UNVERIFIED','papers':43,'files_checked':len(sources),'model_api_requests':0,'reference_requests':585,'directory':str(O)}))
