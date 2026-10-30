"""Read-only progress view; counts model attempts, never sends requests."""
from variant_runtime import *

def main():
    result={}
    for branch in ('partially','cold_default','cold_0','cold_42'):
        stages={}
        for stage in ('stage1','stage2'):
            root=TOP/branch/stage
            summary=read(root/'summary.json') if (root/'summary.json').exists() else {}
            checkpoint=read(root/'checkpoint.json') if (root/'checkpoint.json').exists() else {}
            usage=read(root/'api_usage.json') if (root/'api_usage.json').exists() else {}
            attempts=sorted((root/'api_calls').glob('*/state.json'))
            latest=read(attempts[-1]) if attempts else {}
            stages[stage]={'status':summary.get('status',latest.get('status','PENDING')),'attempts':len(attempts),'accepted':usage.get('successful_responses',0),'tokens':usage.get('total_tokens',0),'last_paper':checkpoint.get('paper'),'last_field':checkpoint.get('field'),'events':checkpoint.get('event',0),'last_http':latest.get('http_status'),'last_seconds':latest.get('elapsed_seconds'),'error':summary.get('error')}
        result[branch]=stages
    print(json.dumps({'resources':resources(),'branches':result},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
