from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=R.parent/'20261021_formal42'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
pid='2105.03654.pdf';old=(OLD/'remote_snapshot/extraction/2105.03654/extraction/calls/000000/response.txt').read_text(encoding='utf-8');new=(R/'token2048_diagnostic/extraction/calls/000000/response.txt').read_text(encoding='utf-8')
before=read(R/'audit/papers/2105.03654/parse.json')['complete_record_spans'];after=read(R/'token2048_diagnostic/parse.json')['record_spans']
assert len(before)==31 and len(after)==49 and new.startswith(old)
for a,b in zip(before,after):assert old[a['span'][0]:a['span'][1]]==new[b['span'][0]:b['span'][1]]
rows=[]
for i,x in enumerate(after):
    a,b=x['span'];rows.append({'index_zero_based':i,'classification':'prior_complete_object_unchanged' if i<31 else ('previously_truncated_record_completed_by_new_generation' if i==31 else 'additional_new_generation_record'),'raw_object_text':new[a:b],'record':json.loads(new[a:b])})
proof={'previous_complete_objects':31,'new_complete_records':49,'first31_verbatim':True,'completed_previously_partial_records':1,'additional_after_that':17,'new_generated_tokens_beyond1024_including_eos':569,'rows':rows}
(R/'token2048_diagnostic/record_extension.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'token2048_diagnostic/diagnostic_report.md';text=p.read_text(encoding='utf-8')
if '## 新增内容核对' not in text:
    text+='\n## 新增内容核对\n\n原输出有31个完整对象和第32条的残缺前半段；新生成保留前31个对象的原始文本，完成第32条，随后又生成17条，总计49条。输出较旧上限多569个Tokens（含EOS）。逐条原文和分类保存于record_extension.json，没有拼接新旧响应。\n\n结构完整不等于抽取正确：独立单篇评价的Result IIM F1仅14.81%，TDMR F1为10.71%；未据此筛选、删除或重跑任何记录。\n'
    p.write_text(text,encoding='utf-8')
print(json.dumps({k:v for k,v in proof.items() if k!='rows'}))
