"""Fresh original-main replay of all saved successful responses, no live API."""
import collections,shutil,subprocess,types
from common import *
from engine import run_original
def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0';f=verify();conf=read(RUN/'config.json');raw=read(conf['input_path']);assert list(raw)==read(RUN/'paper_order.json')['papers'] and sha(conf['input_path'])==conf['input_sha256']
    replay=RUN/'reproducibility/replay_validation';replay.mkdir(exist_ok=True)
    import tdm_llm_masked_normalization as s1
    import leaderboard_llm_normalization as s2
    original_files={str(p):sha(p) for d in ('stage1','stage2') for p in (RUN/d).rglob('*') if p.is_file()}
    results={};all_states=[]
    def forbid_new(expected):raise AssertionError('A saved response was missing: no live request allowed')
    for stage,module in [('stage1',s1),('stage2',s2)]:
        out=RUN/stage;summary=read(out/'summary.json');assert summary['status']=='COMPLETE';target=replay/stage;target.mkdir(exist_ok=True)
        shutil.copytree(out/'api_calls',target/'api_calls',dirs_exist_ok=True)
        inv=read(out/'invocation.json')
        if stage=='stage1':inv['normalization_output_path']=target.as_posix()+'/';final=out/'normalized_output.json';replayed=target/'partially_masked_normalization/partially_masked_normalized_output.json'
        else:inv['leaderboard_normalization_path']=target.as_posix()+'/';final=out/'leaderboard_normalized_output.json';replayed=target/'leaderboard_normalized_output.json'
        observer,transport=run_original(module,stage,types.SimpleNamespace(**inv),target,mock=forbid_new)
        assert transport.mock_new==0 and read(replayed)==read(final)
        original_events=[read(p) for p in sorted((out/'events').glob('*.json'))];assert original_events==observer.events
        states=[]
        for folder in sorted((out/'api_calls').iterdir()):
            state=read(folder/'state.json');expected=read(folder/'expected.json');req=read(folder/'request.json');resp=read(folder/'response.json')
            assert state['status']=='COMPLETE' and state['http_status']==200 and state['returned_model']==MODEL and state['finish_reason']=='stop'
            assert state['response_sha256']==digest(resp) and state['raw_answer']==resp['choices'][0]['message']['content']
            assert req['messages']==expected['messages']
            # SDK serializes message object keys as content,role; prompt hash uses
            # the adapter's role,content order. Preserve message/content order and
            # normalize only object-key serialization for this hash comparison.
            prompt_messages=[{'role':m['role'],'content':m['content']} for m in req['messages']]
            assert digest(prompt_messages)==expected['prompt_sha256'] and digest(expected['candidate_serialized'])==expected['candidate_sha256']
            assert req['model']==MODEL and req['temperature']==0 and req['seed']==0 and req['stream'] is False
            assert not set(req)&{'max_tokens','max_completion_tokens','max_output_tokens','tools','response_format'}
            states.append(state)
        results[stage]={'original_main_replay_matches':True,'events_and_dynamic_order_match':True,'mock_new_requests':transport.mock_new,'calls':len(states),'records':sum(len(x['normalized_output']) for x in read(final).values()),'output_sha256':sha(final)};all_states+=states
        assert results[stage]['records']==284
    for path,h in original_files.items():assert sha(path)==h,path
    f=verify();git=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'status','--porcelain'],cwd=REPO,text=True,capture_output=True,check=True);assert not git.stdout.strip()
    usage={}
    for stage in ('stage1','stage2'):
        u=read(RUN/stage/'api_usage.json');usage[stage]={k:u[k] for k in ('attempts','successful_responses','failed_or_uncertain','unknown_usage_attempts','prompt_tokens','completion_tokens','total_tokens','request_seconds')}
    usage['total']={k:sum(usage[s][k] for s in ('stage1','stage2')) for k in usage['stage1']};usage['actual_invoice_cost']='UNKNOWN; third-party billing not inferred from LangChain callback';usage['wall_seconds_since_preparation']=time.time()-conf['started_epoch'];usage['mock_tests_and_replay_excluded']=True;save(RUN/'api_usage_summary.json',usage)
    verify_data={'status':'PASS','stages':results,'papers':43,'gold_tdmrs':295,'predictions':284,'all_http_200':True,'all_finish_reason_stop':True,'all_returned_models_fixed_snapshot':True,'all_requests_omit_output_limits':True,'dynamic_resume_original_main_verified':True,'frozen_directories':{p:{'file_count':len(v),'file_list_and_hashes_unchanged':True} for p,v in f['directories'].items()},'sources_prompts_gold_unchanged':True,'dependencies_unchanged':True,'git_clean':True,'record_order_results_sources_unchanged':True,'official_sample_tdms':True,'cold_start':False,'new_pdf_parsing_retrieval_embedding_extraction':0,'official_result_iim_unchanged_both_stages':True,'strict_result_unchanged_both_stages':True,'new_remote_requests_during_validation':0}
    for stage in ('stage1','stage2'):
        assert read(RUN/'evaluation'/stage/'metrics_with_f1.json')['aggregate']['Result IIM']==read(BASE/'evaluation/metrics_with_f1.json')['aggregate']['Result IIM']
        assert read(RUN/'evaluation'/stage/'strict_result_metrics.json')['aggregate']==read(CS/'evaluation/strict_result_metrics.json')['aggregate']
    save(RUN/'verification.json',verify_data);print(json.dumps({'verification':verify_data,'usage':usage},ensure_ascii=False))
if __name__=='__main__':main()
