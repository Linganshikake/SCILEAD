from offline_support import *
RUN = Path('D:\\C++\\SCILEAD\\pilot\\gpt56_sol_variants\\20261028_semantic_alignment_v1\\analysis\\baseline_evaluations\\cold_42_stage2\\leaderboard')
BASE = RUN / 'helper_view'
GOLD = Path('C:\\Users\\Administrator\\Desktop\\KG\\SCILEAD_DATA\\data\\leaderboards.json')
NORMALIZED = BASE / 'normalized_output.json'
def verify_frozen():
    return verify(read(RUN / 'source_hashes.json'))
