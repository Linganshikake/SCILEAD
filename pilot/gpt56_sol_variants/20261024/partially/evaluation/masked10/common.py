import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024')
import variant_runtime as v
json, read, save, sha, REPO = v.json, v.read, v.save, v.sha, v.REPO
RUN = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024\\partially\\evaluation\\masked10')
BASE = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024')
GOLD = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024\\masking\\partially_masked_leaderboards.json')
NORMALIZED = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261024\\partially\\stage2\\leaderboard_normalized_output.json')
def boundary():
    def guard(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo'):
            raise RuntimeError('Evaluation is offline')
    sys.addaudithook(guard)
    v.setup()
def verify_frozen():
    return v.verify()
