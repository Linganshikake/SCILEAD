"""Offline, non-generating final delivery checks."""
import csv
from variant_runtime import *

def main():
    def no_network(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('OFFLINE_DELIVERY')
    sys.addaudithook(no_network)
    check=read(TOP/'verification.json')
    assert check['status']=='PASS_COMPLETE' and check['all_logical_requests_resolved'] and not check['changed_frozen_files']
    with (TOP/'request_audit.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    u=read(TOP/'api_usage_summary.json');assert len(rows)==3052==u['actual_requests']
    success=[x for x in rows if x['accepted']=='True']
    assert len(success)==3048 and all(x['response_model']==MODEL and x['finish_reason']=='stop' and x['http_status']=='200' for x in success)
    assert sum(int(x['total_tokens'] or 0) for x in rows)==u['total_tokens']==1336690
    assert sum(x['authorized_retry']=='True' for x in rows)==4
    names=('实验结果汇总.md','report.md','README.md','experiment_manifest.json','generation_config.json','metrics_summary.json','verification.json','api_usage_summary.json','request_audit.csv','summary/variant_comparison.json','summary/cold_statistics.json','fully_cs/report.md','fully_cs/verification.json','fully_cs/evaluation/metrics_with_f1.json','fully_cs/normalization/embedding_normalized_output.json','inspection/candidate_scope_example.md','engineering/authorization_ledger.md')
    paths=[TOP/n for n in names]
    for b in ('partially','cold_default','cold_0','cold_42'):
        for st,name in [('stage1','normalized_output.json'),('stage2','leaderboard_normalized_output.json')]:
            p=TOP/b/st/name;out=read(p)
            assert len(out)==43 and sum(len(x['normalized_output']) for x in out.values())==335
            paths.extend([p,TOP/b/st/'summary.json',TOP/b/'evaluation'/st/'metrics_with_f1.json',TOP/b/'evaluation'/st/'per_paper_metrics.json'])
        for scope in ('all27','masked10'):paths.append(TOP/b/'evaluation'/scope/'paper_metrics/leaderboard_metrics.json')
    for n in ('variant_runtime.py','evaluate_variants.py','summarize_variants.py','finalize_experiment.py','test_transport.py','verify_delivery.py'):
        p=TOP/n;compile(p.read_text('utf-8'),str(p),'exec');paths.append(p)
    for n in ('实验结果汇总.md','inspection/candidate_scope_example.md','engineering/authorization_ledger.md','finalize_experiment.py'):
        assert '???' not in (TOP/n).read_text('utf-8'),'DAMAGED_TEXT: '+n
    save(TOP/'delivery_manifest.json',{'status':'PASS','files':{str(p.relative_to(TOP)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths},'request_count':len(rows),'all_successful_responses_model_and_stop_verified':True,'api_calls_during_delivery_check':0})
    print(json.dumps({'status':'PASS','delivery_files':len(paths),'successes':len(success),'requests':len(rows),'tokens':u['total_tokens'],'all43_per_variant':True}))

if __name__=='__main__':main()
