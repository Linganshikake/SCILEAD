import argparse,types,traceback
import common as c
from common import *
from engine import run_original
def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0';verify();assert read(RUN/'reproducibility/offline_tests.json')['status']=='PASS'
    conf=read(RUN/'config.json');raw=read(conf['input_path']);assert sha(conf['input_path'])==conf['input_sha256']
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['stage1','stage2','all'],default='all');stage=parser.parse_args().stage
    import tdm_llm_masked_normalization as s1
    import leaderboard_llm_normalization as s2
    for selected in (['stage1','stage2'] if stage=='all' else [stage]):
        out=RUN/selected;out.mkdir(exist_ok=True)
        if (out/'summary.json').exists() and read(out/'summary.json')['status']=='COMPLETE':print('SKIP_COMPLETE',selected,flush=True);continue
        work=RUN/'work'/selected;work.mkdir(exist_ok=True)
        if selected=='stage1':
            args=types.SimpleNamespace(seed=0,tdm_config_file=str(RUN/'work/official_config.json'),gold_tdm_file=conf['gold_path'],gold_leaderboard_file=conf['leaderboards_path'],tdm_output_file=conf['input_path'],prompt_file=str(REPO/'prompts.json'),cold_start=False,cold_start_seed=None,normalization_output_path=work.as_posix()+'/',max_new_tokens=None)
            module=s1;original_path=work/'partially_masked_normalization/partially_masked_normalized_output.json';final=out/'normalized_output.json'
        else:
            assert read(RUN/'stage1/summary.json')['status']=='COMPLETE';stage1_sha=sha(RUN/'stage1/normalized_output.json')
            args=types.SimpleNamespace(seed=0,tdm_config_file=str(RUN/'work/official_config.json'),gold_leaderboard_file=conf['leaderboards_path'],masked_normalized_file=str(RUN/'stage1/normalized_output.json'),prompt_file=str(REPO/'prompts.json'),leaderboard_normalization_path=work.as_posix()+'/',max_new_tokens=None)
            module=s2;original_path=work/'leaderboard_normalized_output.json';final=out/'leaderboard_normalized_output.json'
        save(out/'invocation.json',vars(args));start=time.monotonic()
        try:observer,transport=run_original(module,selected,args,out)
        except Exception as e:
            save(out/'summary.json',{'status':'PAUSED_FAILED_OR_UNCERTAIN','error_type':type(e).__name__,'error':c.scrub(str(e)),'seconds_this_attempt':time.monotonic()-start});print('PAUSED',selected,type(e).__name__,c.scrub(str(e)),flush=True);return 2
        result=read(original_path);assert list(result)==list(raw)
        for p in raw:
            assert result[p]['source_documents']==raw[p]['source_documents'] and len(result[p]['normalized_output'])==len(json.loads(raw[p]['output']))
            assert [x['Result'] for x in result[p]['normalized_output']]==[x['Result'] for x in json.loads(raw[p]['output'])]
        immutable(final,result)
        if selected=='stage1':
            assert read(out/'initial_labels.json')==read(RUN/'masking/initial_labels.json')
            immutable(out/'final_labels.json',observer.events[-1]['labels_after'])
            events=[x for x in observer.events if x['added_name'] is not None]
            with (out/'label_update_events.jsonl').open('w',encoding='utf-8') as f:
                for x in events:f.write(json.dumps(x,ensure_ascii=False)+'\n')
        else:assert sha(RUN/'stage1/normalized_output.json')==stage1_sha
        nulls={k:sum(x[k] is None for y in result.values() for x in y['normalized_output']) for k in ('Task','Dataset','Metric')}
        save(out/'summary.json',{'status':'COMPLETE','papers':43,'records':284,'null_fields':nulls,'events':observer.event_index,'api_calls':transport.cursor,'seconds_this_run':time.monotonic()-start,'output_sha256':sha(final),'label_additions':len(events) if selected=='stage1' else None,'changed_tdms':sum(x['changed'] for x in observer.events) if selected=='stage2' else None})
        checkpoint=read(out/'checkpoint.json');checkpoint['status']='COMPLETE';save(out/'checkpoint.json',checkpoint);verify();print('STAGE_COMPLETE',selected,json.dumps(read(out/'summary.json')),flush=True)
    return 0
if __name__=='__main__':sys.exit(main())
