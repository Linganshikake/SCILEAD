import sys,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('partially_common',Path('D:\\C++\\SCILEAD\\pilot\\full43_cold_start\\common.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
json,read,save,sha,REPO=c.json,c.read,c.save,c.sha,c.REPO
RUN=Path(__file__).resolve().parent
BASE=c.BASE
GOLD=Path('D:\\C++\\SCILEAD\\pilot\\full43_cold_start\\references\\masked10.json')
NORMALIZED=c.RUN/'stage2/leaderboard_normalized_output.json'
def boundary():
    c.setup()
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Evaluation is offline')
    sys.addaudithook(guard)
def verify_frozen():return c.verify()
