"""Invoke pinned AxCell public entry points; only add execution guards and logging."""
import argparse,datetime,json,os,sys,time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import contextmanager

ROOT=Path('/root/scilead/axcell')
RUN=ROOT/'runs/20261022_single_paper'
PAPER='1511.08308.pdf'
SOURCE='1511.08308v5'

@contextmanager
def safe_empty_console_progress():
 from fastprogress.fastprogress import ConsoleProgressBar
 original=ConsoleProgressBar.on_update
 def render(bar,value,text):
  if bar.total==0:return
  return original(bar,value,text)
 with patch.object(ConsoleProgressBar,'on_update',render):yield

def save(name,data):
 p=RUN/name;p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_suffix(p.suffix+'.tmp')
 tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');tmp.replace(p)

def collection():
 from axcell.data.paper_collection import PaperCollection
 pc=PaperCollection.from_files(ROOT/'data/papers',jobs=1)
 assert len(pc)==1
 paper=pc.get_by_id('1511.08308');assert paper is not None
 return paper

def convert():
 assert not (ROOT/'data/papers'/SOURCE/'text.json').exists(),'Existing parsed result must not be overwritten'
 assert not (RUN/'conversion_attempt.json').exists(),'A previous conversion attempt must be preserved'
 save('conversion_attempt.json',{'paper':PAPER,'source':SOURCE,'time':datetime.datetime.now().astimezone().isoformat()})
 import docker
 from axcell.helpers.paper_extractor import PaperExtractor
 original_from_env=docker.from_env
 def negotiated_client(**kwargs):
  kwargs.setdefault('version','auto');return original_from_env(**kwargs)
 with patch('docker.from_env',negotiated_client):extract=PaperExtractor(ROOT/'data')
 containers=extract.latex.client.containers
 original=containers.run
 def guarded_run(image,command,**kwargs):
  assert image=='arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6'
  assert any(x.endswith('@sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e') for x in extract.latex.client.images.get(image).attrs.get('RepoDigests',[]))
  kwargs.update(name='axcell-single-convert',labels={'scilead.task':'axcell-single-20261022'},mem_limit='20g',memswap_limit='20g',nano_cpus=6000000000,network_disabled=True)
  save('conversion_container_config.json',{'image':image,'command':command,'name':kwargs['name'],'memory_bytes':20*2**30,'cpus':6,'network_disabled':True,'mounts':[{'host':str(k),'target':v} for k,v in kwargs['volumes'].items()],'remove':kwargs.get('remove')})
  return original(image,command,**kwargs)
 containers.run=guarded_run
 extract.latex.client=SimpleNamespace(containers=containers,images=extract.latex.client.images)
 start=time.monotonic();status=extract(ROOT/'data/sources'/SOURCE)
 save('conversion_result.json',{'paper_id':PAPER,'source_version':SOURCE,'official_status':status,'seconds':round(time.monotonic()-start,3)})
 if status!='success':raise RuntimeError('Original PaperExtractor returned '+status)
 paper=collection()
 tables=[]
 for table in paper.tables:
  tables.append({'name':table.name,'caption':table.caption,'rows':len(table.df),'columns':len(table.df.columns),'cells':[[{'raw_value':cell.raw_value,'value':cell.value} for cell in row] for row in table.df.values]})
 save('parsed_artifacts.json',{'paper_id':PAPER,'title':paper.text.title,'fragment_count':len(paper.text.fragments),'table_count':len(tables),'tables':tables,'html_bytes':(ROOT/'data/htmls'/SOURCE/'index.html').stat().st_size})
 assert len(paper.text.fragments)>0,'Parsed text is empty'
 assert len(tables)>0,'No tables parsed; stop before model extraction'
 print(json.dumps({'stage':'conversion','status':'PARSE_COMPLETE','tables':len(tables),'fragments':len(paper.text.fragments)}),flush=True)

def extract_results():
 assert not (RUN/'raw_outputs').exists(),'Existing attempt artifacts must not be overwritten'
 (RUN/'raw_outputs').mkdir()
 import torch,fastai
 assert not torch.cuda.is_available()
 assert torch.__version__=='1.3.1+cpu' and fastai.__version__=='1.0.55'
 from axcell.pipeline_logger import pipeline_logger
 from axcell.helpers.results_extractor import ResultsExtractor
 paper=collection();events=[];final_kept=[]
 def observer(step,**kw):
  seq=len(events);entry={'sequence':seq,'step':step,'time':datetime.datetime.now().astimezone().isoformat()}
  if step=='type_prediction::predicted':
   entry['tables']=[{'table':t.name,'prediction':p.name} for t,p in zip(kw['tables'],kw['predictions'])]
  if 'proposals' in kw:
   path='raw_outputs/events/{:03d}_proposals.json'.format(seq)
   (RUN/path).parent.mkdir(parents=True,exist_ok=True)
   kw['proposals'].to_json(str(RUN/path),orient='split',double_precision=15)
   entry.update(proposals_path=path,proposal_count=len(kw['proposals']))
  if 'which' in kw:
   entry['kept_ids']=[str(x) for x in kw['proposals'].index[kw['which']]]
   entry['removed_reasons']=json.loads(kw['reason'].to_json())
   if step=='filtering::compound_filtering::filtered':final_kept[:]=[kw['proposals'][kw['which']].copy()]
  events.append(entry);save('raw_outputs/pipeline_events.json',events)
  print(json.dumps({'stage_event':step,'sequence':seq}),flush=True)
 pipeline_logger.register('.*',observer)
 save('progress_display_adapter.json',{'fastprogress':'0.1.21','change':'Skip console on_update rendering only when total==0','iteration_tokens_models_weights_thresholds_unchanged':True})
 with safe_empty_console_progress():
  start=time.monotonic();extract=ResultsExtractor(ROOT/'models')
  loaded=time.monotonic();results=extract(paper,in_place=True);finish=time.monotonic()
 raw=json.loads(results.to_json(orient='records',double_precision=15))
 save('raw_outputs/records.json',raw)
 results.to_pickle(RUN/'raw_outputs/records.pkl')
 results.to_csv(RUN/'raw_outputs/records.csv',index=False)
 if final_kept:
  kept=final_kept[-1]
  expected=kept[['dataset','metric','task','model','parsed']].reset_index(drop=True).rename(columns={'parsed':'score'})
  assert expected.equals(results),'Provenance does not match original returned results'
  provenance=[{'output_index':i,'cell_ext_id':str(x)} for i,x in enumerate(kept.index)]
 else:
  assert len(results)==0
  provenance=[]
 save('raw_outputs/provenance.json',provenance)
 tdms=[{'Task':row['task'],'Dataset':row['dataset'],'Metric':row['metric'],'Result':str(row['score'])} for row in results.to_dict('records')]
 save('scilead_compatible_outputs/output.json',{PAPER:{'output':json.dumps(tdms,ensure_ascii=False,allow_nan=False),'source_documents':[]}})
 save('extraction_result.json',{'status':'EXTRACTION_COMPLETE' if tdms else 'VALID_EMPTY','paper_id':PAPER,'record_count':len(tdms),'table_count':len(paper.tables),'model_load_seconds':round(loaded-start,3),'inference_seconds':round(finish-loaded,3),'device':'cpu','torch':torch.__version__,'fastai':fastai.__version__,'paid_api_calls':0,'normalization_status':'NOT_EXECUTED','source_documents_note':'AxCell table/cell provenance is retained separately; no PDF retriever is introduced'})
 print(json.dumps({'status':'EXTRACTION_COMPLETE' if tdms else 'VALID_EMPTY','records':len(tdms)}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['convert','extract']);p.add_argument('--attempt',choices=['console_progress_compat']);a=p.parse_args()
 if a.attempt:
  assert a.stage=='extract';RUN=RUN/'attempts'/a.attempt;RUN.mkdir(parents=True,exist_ok=True)
 try:convert() if a.stage=='convert' else extract_results()
 except Exception as e:
  if not (RUN/(a.stage+'_error.json')).exists():save(a.stage+'_error.json',{'status':'FAILED','error_type':type(e).__name__,'message':str(e),'no_automatic_model_retry':True})
  raise
