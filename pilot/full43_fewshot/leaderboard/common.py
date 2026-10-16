import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import importlib.util
spec=importlib.util.spec_from_file_location('few_common',Path(__file__).resolve().parents[1]/'common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
json=c.json;read=c.read;save=c.save;sha=c.sha;REPO=c.REPO
RUN=Path(__file__).resolve().parent;BASE=c.RUN;GOLD=Path(read(BASE/'manifest.json')['gold_leaderboards_path']);NORMALIZED=BASE/'fewshot_normalized_output.json'
def boundary():c.setup('offline')
def verify_frozen():return c.verify()
