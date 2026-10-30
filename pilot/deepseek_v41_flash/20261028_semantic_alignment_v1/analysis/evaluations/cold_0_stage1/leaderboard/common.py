from offline_support import *
RUN = Path('D:\\C++\\SCILEAD\\pilot\\deepseek_v41_flash\\20261028_semantic_alignment_v1\\analysis\\evaluations\\cold_0_stage1\\leaderboard')
BASE = RUN / 'helper_view'
GOLD = Path('C:\\Users\\Administrator\\Desktop\\KG\\SCILEAD_DATA\\data\\leaderboards.json')
NORMALIZED = BASE / 'normalized_output.json'
def verify_frozen():
    return verify(read(RUN / 'source_hashes.json'))
