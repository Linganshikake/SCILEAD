"""Synthetic responses exercise original mains and real replay observer, no API."""
import copy,shutil,types
from common import *
from engine import run_original,SimulatedInterruption
def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0'
    import tdm_llm_masked_normalization as s1
    import leaderboard_llm_normalization as s2
    test=RUN/'reproducibility/offline_test';assert not test.exists();test.mkdir()
    labels={'Task':{'KnownTask'},'Dataset':{'KnownDataset'},'Metric':{'KnownMetric'}}
    raw={'synthetic.pdf':{'output':json.dumps([
        {'Task':'KnownTask','Dataset':'KnownDataset','Metric':'KnownMetric','Result':'1.00'},
        {'Task':'TaskAlias','Dataset':'NewDataset','Metric':'NewMetric','Result':'2.00'},
        {'Task':'OtherTask','Dataset':'Quoted','Metric':'MetricAlias','Result':'3.00'},
        {'Task':'KnownTask','Dataset':'NewDataset','Metric':'KnownMetric','Result':'4.00'},
        {'Task':'NewTask','Dataset':'KnownDataset','Metric':'KnownMetric','Result':'5.00'}]),'source_documents':[{'content':'synthetic only','metadata':{}}]}}
    responses={'TaskAlias':'KnownTask','NewDataset':'NewDataset','NewMetric':'NewMetric','OtherTask':'UnlistedAnswer','Quoted':'"Quoted"','MetricAlias':'KnownMetric','NewTask':'NewTask'}
    save(test/'raw.json',raw);save(test/'config.json',{'model_type':'gpt4-turbo-128k'});save(test/'gold.json',{});save(test/'boards.json',[])
    sample=s1.sample_tdms;s1.sample_tdms=lambda *a:copy.deepcopy(labels)
    def args(out):return types.SimpleNamespace(seed=0,tdm_config_file=str(test/'config.json'),gold_tdm_file=str(test/'gold.json'),gold_leaderboard_file=str(test/'boards.json'),tdm_output_file=str(test/'raw.json'),prompt_file=str(REPO/'prompts.json'),cold_start=False,cold_start_seed=None,normalization_output_path=out.as_posix()+'/',max_new_tokens=None)
    for name in ('continuous','resumed'):(test/name/'partially_masked_normalization').mkdir(parents=True)
    try:
        observer,t=run_original(s1,'stage1',args(test/'continuous'),test/'continuous',mock=lambda e:responses[e['original']])
        try:run_original(s1,'stage1',args(test/'resumed'),test/'resumed',mock=lambda e:responses[e['original']],interrupt_after=2)
        except SimulatedInterruption:pass
        else:raise AssertionError('Interruption not exercised')
        resumed,rt=run_original(s1,'stage1',args(test/'resumed'),test/'resumed',mock=lambda e:responses[e['original']])
        a=read(test/'continuous/partially_masked_normalization/partially_masked_normalized_output.json');b=read(test/'resumed/partially_masked_normalization/partially_masked_normalized_output.json');assert a==b and observer.events==resumed.events and t.cursor==7 and rt.mock_new==5
        rows=a['synthetic.pdf']['normalized_output'];assert rows[0]['Task']=='KnownTask' and rows[1]['Task']=='KnownTask' and rows[1]['Dataset']=='NewDataset' and rows[1]['Metric'] is None and rows[2]['Task'] is None and rows[2]['Dataset'] is None and rows[3]['Dataset']=='NewDataset' and rows[4]['Task']=='NewTask'
        assert [x['Result'] for x in rows]==['1.00','2.00','3.00','4.00','5.00'] and a['synthetic.pdf']['source_documents']==raw['synthetic.pdf']['source_documents']
    finally:s1.sample_tdms=sample
    # Stage2: null skip, exact skip, accepted tuple, unmatched preservation.
    stage2raw={'synthetic.pdf':{'normalized_output':[rows[0],rows[1],{'Task':'Alias','Dataset':'KnownDataset','Metric':'KnownMetric','Result':'6.0'},{'Task':'Unmatched','Dataset':'KnownDataset','Metric':'KnownMetric','Result':'7.0'}],'source_documents':raw['synthetic.pdf']['source_documents']}}
    save(test/'stage2_input.json',stage2raw);save(test/'boards.json',[{'Task':'KnownTask','Dataset':'KnownDataset','Metric':'KnownMetric','Leaderboard':{}}]);out=test/'stage2';out.mkdir()
    args2=types.SimpleNamespace(seed=0,tdm_config_file=str(test/'config.json'),gold_leaderboard_file=str(test/'boards.json'),masked_normalized_file=str(test/'stage2_input.json'),prompt_file=str(REPO/'prompts.json'),leaderboard_normalization_path=out.as_posix()+'/',max_new_tokens=None)
    o,t2=run_original(s2,'stage2',args2,out,mock=lambda e:'(KnownTask, KnownDataset, KnownMetric)' if 'Alias' in e['original'] else '(Unknown, Unknown, Unknown)')
    n=read(out/'leaderboard_normalized_output.json')['synthetic.pdf']['normalized_output'];assert t2.cursor==2 and n[2]['Task']=='KnownTask' and n[3]['Task']=='Unmatched' and read(test/'stage2_input.json')==stage2raw
    save(RUN/'reproducibility/offline_tests.json',{'status':'PASS','checks':['original exact skip','map existing candidate','original new Task/Dataset added','other and quoted answers null','Metric cannot extend','Result/source documents unchanged','new dynamic member later exact skipped','interrupt after raw response then replay without duplicate request','serialized candidate order and complete event state identical after replay','stage2 null/exact skipped','stage2 accepted tuple mapped','stage2 unmatched preserved','stage1 input not mutated by stage2'],'new_remote_requests':0,'mock_stage1_calls':7,'resumed_new_calls':5,'mock_stage2_calls':2})
    print('OFFLINE_TESTS_PASS')
if __name__=='__main__':main()
