from offline_support import *
RUN = Path('D:\\C++\\SCILEAD\\pilot\\deepseek_v41_flash\\20261028\\analysis\\offline_test\\regression_oih2dl_j\\sol_fully\\leaderboard')
BASE = RUN / 'helper_view'
GOLD = Path('C:\\Users\\Administrator\\Desktop\\KG\\SCILEAD_DATA\\data\\leaderboards.json')
NORMALIZED = BASE / 'normalized_output.json'
def verify_frozen():
    return verify(read(RUN / 'source_hashes.json'))
