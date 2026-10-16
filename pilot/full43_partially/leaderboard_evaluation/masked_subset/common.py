import sys,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('partially_common',Path(__file__).resolve().parents[2]/'common.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
json,read,save,sha,REPO=c.json,c.read,c.save,c.sha,c.REPO
RUN=Path(__file__).resolve().parent
BASE=c.BASE
GOLD=Path('D:\\C++\\SCILEAD\\pilot\\full43_partially\\masking\\partially_masked_leaderboards.json')
NORMALIZED=c.RUN/'stage2/leaderboard_normalized_output.json'
def boundary():
    c.setup()
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Evaluation is offline')
    sys.addaudithook(guard)
def verify_frozen():return c.verify()
