"""Read the verified saved output through the original entry point, without inference."""
import importlib.util, json, resource, socket, time
from pathlib import Path
from unittest.mock import patch

ROOT=Path('/root/scilead/axcell')
OUT=ROOT/'runs/20261022_formal/stage1'
OLD=ROOT/'runs/20261022_single_paper'
ATT=OLD/'attempts/console_progress_compat'
start=time.monotonic()

def read(p): return json.loads(p.read_text())
def forbidden(*args, **kwargs): raise RuntimeError('Stage1 prohibits network or model-weight loading')

with patch.object(socket.socket,'connect',forbidden), patch.object(socket.socket,'connect_ex',forbidden):
    import torch
    import pandas as pd
    with patch.object(torch,'load',forbidden):
        spec=importlib.util.spec_from_file_location('previous_single_entry',ROOT/'scripts/run_single.py')
        entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
        paper=entry.collection()
        assert paper.paper_id=='1511.08308v5' and paper.arxiv_no_version=='1511.08308'
        old=read(OLD/'parsed_artifacts.json')
        tables=[{'name':t.name,'caption':t.caption,'rows':len(t.df),'columns':len(t.df.columns),
                 'cells':[[{'raw_value':c.raw_value,'value':c.value} for c in row] for row in t.df.values]}
                for t in paper.tables]
        actual={'paper_id':'1511.08308.pdf','title':paper.text.title,
                'fragment_count':len(paper.text.fragments),'table_count':len(tables),'tables':tables,
                'html_bytes':(ROOT/'data/htmls/1511.08308v5/index.html').stat().st_size}
        assert actual==old, 'Saved parsed content differs from original conversion report'
        assert len(tables)==11 and len(paper.text.fragments)==154
        raw=read(ATT/'raw_outputs/records.json')
        frame=pd.read_pickle(ATT/'raw_outputs/records.pkl')
        assert json.loads(frame.to_json(orient='records',double_precision=15))==raw
        csv=pd.read_csv(ATT/'raw_outputs/records.csv')
        assert json.loads(csv.to_json(orient='records',double_precision=15))==raw
        mapped=read(ATT/'scilead_compatible_outputs/output.json')
        assert list(mapped)==['1511.08308.pdf']
        expected=[{'Task':r['task'],'Dataset':r['dataset'],'Metric':r['metric'],'Result':str(r['score'])} for r in frame.to_dict('records')]
        assert json.loads(mapped['1511.08308.pdf']['output'])==expected
        assert mapped['1511.08308.pdf']['source_documents']==[]
        assert len(raw)==2 and raw[0]['score']==91.85 and raw[1]['score']==4696.0
        provenance=read(ATT/'raw_outputs/provenance.json')
        assert provenance==[{'output_index':0,'cell_ext_id':'1511.08308v5/table_06.csv/6.2'},
                            {'output_index':1,'cell_ext_id':'1511.08308v5/table_11.csv/2.4'}]
        events=read(ATT/'raw_outputs/pipeline_events.json')
        final=[e for e in events if e['step']=='filtering::compound_filtering::filtered'][-1]
        assert final['kept_ids']==[p['cell_ext_id'] for p in provenance]
        table6=paper.table_by_name('table_06.csv'); table11=paper.table_by_name('table_11.csv')
        assert table6.df.values[6][2].value=='91.85'
        assert table6.df.values[1][2].value=='Recall'
        assert table11.df.values[2][4].value=='4,696'
        assert table11.df.values[2][0].value=='Test set size (# entities)'
        result=read(ATT/'extraction_result.json')
        assert result['status']=='EXTRACTION_COMPLETE' and result['record_count']==2
        assert result['paid_api_calls']==0 and result['normalization_status']=='NOT_EXECUTED'
        checks={'status':'PASSED','paper_id':'1511.08308.pdf','source_version':paper.paper_id,
                'entry_point':'Existing scripts/run_single.py collection() -> original PaperCollection.from_files(jobs=1)',
                'parsed_content_equal':True,'fragment_count':154,'table_count':11,'raw_records':raw,
                'csv_pickle_json_equal':True,'scilead_wrapper_and_id_equal':True,
                'pipeline_events':len(events),'provenance':provenance,'final_filter_provenance_matches':True,
                'known_errors_preserved':['Recall 91.85 labeled F1','Test-set entity count 4696 labeled F1'],
                'network_connections_blocked_in_child':True,'torch_load_blocked_in_child':True,
                'model_generations':0,'paid_api_calls':0,'elapsed_seconds':time.monotonic()-start,
                'child_max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
        (OUT/'saved_artifact_verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
        print(json.dumps({k:v for k,v in checks.items() if k not in ['raw_records','provenance']}),flush=True)
