from offline_support import *
RUN = Path('D:\\C++\\SCILEAD\\pilot\\deepseek_v41_flash\\20261028\\analysis\\offline_test\\regression_y7mlqxwd\\sol_masked\\leaderboard')
BASE = RUN / 'helper_view'
GOLD = Path('D:\\C++\\SCILEAD\\pilot\\full43_partially\\masking\\partially_masked_leaderboards.json')
NORMALIZED = BASE / 'normalized_output.json'
def verify_frozen():
    return verify(read(RUN / 'source_hashes.json'))
