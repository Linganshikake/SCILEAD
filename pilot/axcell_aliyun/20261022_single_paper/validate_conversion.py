import docker,json,sys,numpy,pandas,html5lib,lxml,requests,urllib3
from pathlib import Path
from axcell.helpers.paper_extractor import PaperExtractor
from axcell.data.paper_collection import PaperCollection
assert sys.version_info[:3]==(3,7,1)
assert numpy.__version__=='1.18.1' and pandas.__version__=='0.25.3'
assert requests.__version__=='2.31.0' and urllib3.__version__=='1.26.20'
c=docker.from_env(version='auto');v=c.version();c.close()
d={'status':'PASS','scope':'TeX conversion and parsed artifact inspection only','python':sys.version,'numpy':numpy.__version__,'pandas':pandas.__version__,'docker_sdk':docker.__version__,'docker_server':v['Version'],'docker_api':v['ApiVersion'],'PaperExtractor_import':True,'PaperCollection_import':True,'torch_imported':'torch' in sys.modules,'model_loaded':False}
Path('/root/scilead/axcell/runs/20261022_single_paper/conversion_environment_validation.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
