"""Read-only final artifact, metric, request and frozen-input checks."""
import statistics
from common import *

def main():
    assert RUN==TOP
    f=verify();manifest=read(TOP/'experiment_manifest.json');verification=read(TOP/'verification.json')
    assert manifest['status']=='THREE_RUNS_COMPLETE_VERIFIED' and verification['status']=='PASS'
    inventory=read(TOP/'artifact_sha256.json')
    actual={str(p.relative_to(TOP)) for p in TOP.rglob('*') if p.is_file() and p.name!='artifact_sha256.json' and 'runtime' not in p.parts}
    assert actual==set(inventory)
    for name,h in inventory.items():assert sha(TOP/name)==h,name
    runs=('order_default','order_0','order_42');counts={};total_tokens=0
    for rid in runs:
        counts[rid]={}
        assert read(TOP/rid/'verification.json')['status']=='PASS'
        for stage in ('stage1','stage2'):
            folders=sorted((TOP/rid/stage/'api_calls').iterdir());counts[rid][stage]=len(folders)
            for folder in folders:
                req=read(folder/'request.json');state=read(folder/'state.json');body=read(folder/'response.json');attempt=read(folder/'attempt.json')
                assert set(req)=={'messages','model','n','seed','stream','temperature'}
                assert req['model']==MODEL and req['seed']==0 and req['temperature']==0 and req['stream'] is False and req['n']==1
                assert state['status']=='COMPLETE' and state['http_status']==200 and state['finish_reason']=='stop' and state['returned_model']==MODEL and state['run_id']==rid
                assert attempt['attempt']==1 and digest(body)==state['response_sha256']
                assert state['usage']['total_tokens']==state['usage']['prompt_tokens']+state['usage']['completion_tokens']
                total_tokens+=state['usage']['total_tokens']
    usage=read(TOP/'api_usage_summary.json')['total'];assert sum(sum(v.values()) for v in counts.values())==usage['attempts']==usage['successful_responses']
    assert total_tokens==usage['total_tokens'] and usage['failed_or_uncertain']==usage['unknown_usage_attempts']==0
    for scope in ('all27','masked10'):
        summary=read(TOP/'summary'/f'{scope}_mean_std.json');assert summary['main_ddof']==1
        for name,row in summary['metrics'].items():
            values=list(row['values'].values());assert len(values)==3
            assert row['mean']==statistics.mean(values) and row['sample_std_ddof1']==statistics.stdev(values) and row['population_std_ddof0']==statistics.pstdev(values)
    audit=read(TOP/'reproducibility/adapter_audit.json')
    for name,h in audit['adapter_sha256'].items():assert sha(TOP/name)==h,name
    print(json.dumps({'status':'FINAL_DELIVERY_PASS','artifact_files':len(inventory),'historical_files_unchanged':sum(map(len,f['directories'].values())),'real_calls':counts,'total_requests':usage['attempts'],'total_tokens':total_tokens,'no_output_cap_or_extra_payload_keys':True,'all_http200_snapshot_stop':True,'all_statistics_recomputed':True,'final_hashes_verified':True},ensure_ascii=False))
if __name__=='__main__':main()
