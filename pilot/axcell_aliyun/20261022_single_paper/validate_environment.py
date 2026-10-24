import json,sys,subprocess
from pathlib import Path
import torch,numpy,pandas,fastai,spacy,docker
from axcell.helpers.paper_extractor import PaperExtractor
from axcell.helpers.results_extractor import ResultsExtractor
assert sys.version_info[:3]==(3,7,1)
assert torch.__version__=='1.3.1+cpu' and not torch.cuda.is_available()
assert numpy.__version__=='1.18.1' and pandas.__version__=='0.25.3'
assert fastai.__version__=='1.0.55' and spacy.__version__=='2.2.3'
c=docker.from_env(version='auto');version=c.version();c.close()
r={'python':sys.version,'executable':sys.executable,'torch':torch.__version__,'cuda_available':torch.cuda.is_available(),'numpy':numpy.__version__,'pandas':pandas.__version__,'fastai':fastai.__version__,'spacy':spacy.__version__,'docker_sdk':docker.__version__,'docker_server':version.get('Version'),'docker_api':version.get('ApiVersion'),'PaperExtractor_import':True,'ResultsExtractor_import':True,'model_weights_loaded':False}
p=Path('/root/scilead/axcell/runs/20261022_single_paper/environment_validation.json');p.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
