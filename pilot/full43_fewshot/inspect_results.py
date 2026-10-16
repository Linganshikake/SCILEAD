"""Offline evidence pointers only; never edits predictions or assigns unsupported causes."""
from common import *
import re, collections
def main():
    setup();comparison=read(RUN/'evaluation/comparison.json');raw=read(RUN/'fewshot_output.json');gold=read(read(RUN/'manifest.json')['gold_path']);findings={}
    for change in comparison['papers']:
        p=change['paper'];docs=raw[p]['source_documents'];rows=json.loads(raw[p]['output']);items=[]
        for i,row in enumerate(rows,1):
            value=row['Result'];matches=[]
            for j,doc in enumerate(docs,1):
                loc=doc['content'].find(value) if value else -1
                if loc>=0:matches.append({'evidence_index':j,'metadata':doc['metadata'],'snippet':doc['content'][max(0,loc-350):loc+len(value)+350]})
            items.append({'record':i,'prediction':row,'new_vs_zero_shot':row in change['added_raw_records'],'literal_result_evidence':matches,'literal_missing_note':None if matches else 'Exact string not found; formatting, scaling or numeric errors require manual review, not proof of hallucination.'})
        findings[p]={'tdmr_f1_delta':change['tdmr_f1_delta'],'old_count':change['old_records'],'new_count':change['new_records'],'records':items}
    save(RUN/'inspection/evidence_pointers.json',findings)
    order=sorted(comparison['papers'],key=lambda r:r['tdmr_f1_delta'],reverse=True)
    lines=['# Few-shot 错误与变化核查','', '此文件只提供预测变化及冻结证据定位，不修正输出。Gold 对照见 evaluation/error_analysis.json。单凭数值未在 Gold 中出现不能认定为 Baseline；单凭字面字符串未命中证据也不能认定幻觉。','']
    for c in order[:4]+order[-4:]:
        p=c['paper'];lines+=['## '+p,'',f"TDMR F1 变化 {c['tdmr_f1_delta']:+.6f}；条数 {c['old_records']} → {c['new_records']}；null 字段 {c['old_null_fields']} → {c['new_null_fields']}。",'']
        for item in findings[p]['records']:
            if not item['new_vs_zero_shot']:continue
            lines+=['### 新预测 #'+str(item['record']),'```json',json.dumps(item['prediction'],ensure_ascii=False),'```']
            if not item['literal_result_evidence']:lines+=['结果字面值未在证据中找到，需结合格式/比例进行人工判断。']
            for match in item['literal_result_evidence'][:2]:lines+=['证据 #'+str(match['evidence_index'])+'；metadata='+json.dumps(match['metadata'],ensure_ascii=False),'```text',match['snippet'],'```']
    lines+=['','## 归因限制','Result 粒度、不同实验变体、Baseline 或 Dev/Test 混入仅在冻结证据有直接支持时作出判断。自动分析把无严格数值匹配、标准化 null、数值匹配但标签/绑定不同分别记录；不把这些类别互相等同。','原始 PDF 表格解析完全复用，因此本轮观察到的不同预测不意味着表格重新解析发生了变化。']
    (RUN/'inspection/findings.md').write_text('\n'.join(lines),encoding='utf-8');print('INSPECTION_POINTERS',len(findings))
if __name__=='__main__':main()
