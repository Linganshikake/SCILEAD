import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cs_common as c
from cs_common import json,read,save,sha,REPO
RUN=Path(__file__).resolve().parent
BASE=c.RUN
GOLD=Path(read(BASE/'config.json')['gold_leaderboards_path'])
NORMALIZED=BASE/'normalization/embedding_normalized_output.json'
def boundary():
    c.setup()
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Evaluation is offline')
    sys.addaudithook(guard)
def verify_frozen():return c.verify()
