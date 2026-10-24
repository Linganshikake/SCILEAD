"""Reuse the verified single-paper entry point unchanged; bind only ID/input/output."""
import sys, json, hashlib, importlib.util, resource, os, time
from pathlib import Path
ROOT=Path('/root/scilead/axcell')
BASE=ROOT/'runs/20261022_stage3'
paper_id=sys.argv[1]
item=next(x for x in json.loads((BASE/'queue.json').read_text()) if x['paper_id']==paper_id)
run=BASE/'papers'/paper_id
script=ROOT/'scripts/run_single.py'
assert hashlib.sha256(script.read_bytes()).hexdigest()=='074537f9041a8acff837c2a320c5f097c4b41e782a9d63bd3dd8ff36815ae27b'
spec=importlib.util.spec_from_file_location('verified_single',str(script)); original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
original.RUN=run;original.PAPER=paper_id;original.SOURCE=item['tex_version']
def collection():
 from axcell.data.paper_collection import PaperCollection
 pc=PaperCollection.from_files(run/'inputs',jobs=1)
 assert len(pc)==1
 paper=pc.get_by_id(item['tex_version'].rsplit('v',1)[0]);assert paper is not None
 assert len(paper.tables)==item['table_count'] and len(paper.text.fragments)==item['fragment_count']
 return paper
original.collection=collection
start=time.monotonic()
try:
 original.extract_results()
 original.save('worker_exit.json',{'exit_code':0,'seconds':time.monotonic()-start,'maxrss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024})
except Exception as e:
 original.save('extract_error.json',{'status':'FAILED','error_type':type(e).__name__,'message':str(e),'no_automatic_model_retry':True})
 original.save('worker_exit.json',{'exit_code':1,'seconds':time.monotonic()-start,'maxrss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024})
 raise
