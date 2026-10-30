import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024')
import variant_runtime as v
json, read, save, sha, REPO = v.json, v.read, v.save, v.sha, v.REPO
RUN = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024\\evaluation_references\\gpt56_fully\\all27')
BASE = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024')
GOLD = Path('C:\\Users\\Administrator\\Desktop\\KG\\SCILEAD_DATA\\data\\leaderboards.json')
NORMALIZED = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_fully\\20261024_A2_result_type_recovery\\merged\\normalized_output.json')
def boundary():
    def guard(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo'):
            raise RuntimeError('Evaluation is offline')
    sys.addaudithook(guard)
    v.setup()
def verify_frozen():
    return v.verify()
