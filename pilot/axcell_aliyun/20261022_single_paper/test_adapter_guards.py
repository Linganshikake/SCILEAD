import tempfile,sys,types,importlib.util,json
from pathlib import Path
from unittest.mock import patch
base=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('run_single',base/'run_single.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
calls=[]
class Collection:
 def run(self,image,command,**kwargs):calls.append(kwargs);return b''
class ImageCollection:
 def get(self,image):return types.SimpleNamespace(attrs={'RepoDigests':['x@sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e']})
class VolatileClient:
 @property
 def containers(self):return Collection()
 @property
 def images(self):return ImageCollection()
class FakeExtractor:
 def __init__(self,root):self.latex=types.SimpleNamespace(client=sys.modules['docker'].from_env())
 def __call__(self,source):
  self.latex.client.containers.run('arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6',['/files/latex2html.sh','index.html'],remove=True,volumes={})
  return 'test-stop-before-parsing'
with tempfile.TemporaryDirectory() as tmp:
 m.ROOT=Path(tmp);m.RUN=Path(tmp)/'run';m.RUN.mkdir()
 fake=types.ModuleType('axcell.helpers.paper_extractor');fake.PaperExtractor=FakeExtractor
 fake_docker=types.ModuleType('docker')
 def client_factory(**kwargs):
  assert kwargs.get('version')=='auto'
  return VolatileClient()
 fake_docker.from_env=client_factory
 with patch.dict(sys.modules,{'axcell.helpers.paper_extractor':fake,'docker':fake_docker}):
  try:m.convert()
  except RuntimeError as e:assert 'test-stop-before-parsing' in str(e)
 assert len(calls)==1
 assert calls[0].get('mem_limit')=='20g','Guard lost when Docker collection property returns a fresh instance'
 assert calls[0].get('network_disabled') is True
 assert calls[0].get('labels')=={'scilead.task':'axcell-single-20261022'}
 print('Volatile Docker collection guard and API auto negotiation: PASS')
 existing=m.RUN/'raw_outputs';existing.mkdir();(existing/'pipeline_events.json').write_text('[{"existing":true}]')
 try:m.extract_results()
 except (AssertionError,FileExistsError):pass
 else:raise AssertionError('Existing failed-attempt artifacts must block rerun')
 assert (existing/'pipeline_events.json').read_text()=='[{"existing":true}]'
 print('Failed-attempt output preservation: PASS')
