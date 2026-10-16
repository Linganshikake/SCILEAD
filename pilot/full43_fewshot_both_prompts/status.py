from common import *
import collections
m=read(RUN/'input_manifest.json');s=collections.Counter();calls=collections.Counter();failures=[];active=None;tokens=0
for row in m['papers']:
    out=Path(row['normalization_dir']);summary=read(out/'summary.json') if (out/'summary.json').exists() else {'status':'PENDING'};s[summary['status']]+=1
    if summary['status']=='FAILED':failures.append({'paper':row['id'],'type':summary.get('error_type')})
    files=sorted(Path(row['calls_dir']).glob('*/state.json'))
    for file in files:
        state=read(file);calls[state['status']]+=1;tokens+=(state.get('usage') or {}).get('total_tokens',0) or 0
    if files and summary['status']=='PENDING':active={'paper':row['id'],'last_call':len(files),'planned':row['expected_normalization_requests']}
print(json.dumps({'papers':dict(s),'calls':dict(calls),'known_tokens':tokens,'active':active,'failed':failures}),flush=True)
