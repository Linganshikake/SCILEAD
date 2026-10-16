"""Read-only compact progress; excludes all mock/replay directories."""
from common import *
for rid in ('order_default','order_0','order_42'):
    out={'run':rid}
    for stage in ('stage1','stage2'):
        p=TOP/rid/stage
        if not p.exists():continue
        u=read(p/'api_usage.json') if (p/'api_usage.json').exists() else {}
        ck=read(p/'checkpoint.json') if (p/'checkpoint.json').exists() else {}
        out[stage]={'calls':u.get('attempts',0),'success':u.get('successful_responses',0),'fail':u.get('failed_or_uncertain',0),'tokens':u.get('total_tokens',0),'event':ck.get('event'),'paper':ck.get('paper'),'status':ck.get('status')}
    print(json.dumps(out,ensure_ascii=False))
if (TOP/'execution_status.json').exists():print(json.dumps(read(TOP/'execution_status.json')))
