"""Reuse audited evaluator; change paths and permit documented official RC > 1."""
from cs_common import *
def main():
    verify();target=RUN/'leaderboard_evaluation';target.mkdir(exist_ok=True)
    for d in ('official','paper_metrics','leaderboards','reference'):(target/d).mkdir(exist_ok=True)
    changes=[]
    for name in ('run_official_leaderboard_eval.py','evaluate_paper_metrics.py'):
        s=(LB/name).read_text(encoding='utf-8');before=sha(LB/name)
        if name=='evaluate_paper_metrics.py':
            old='assert all(math.isfinite(v) and 0<=v<=1 for v in (pc,rc,rbo_score,score,joint))'
            new='assert all(math.isfinite(v) and 0<=v<=1 for v in (pc,rbo_score,score,joint));assert math.isfinite(rc) and rc>=0'
            assert s.count(old)==1;s=s.replace(old,new)
        (target/name).write_text(s,encoding='utf-8');changes.append({'file':name,'source_sha256':before,'copy_sha256':sha(target/name),'changes':'Only RC validation upper bound removed; no metric formula change' if name=='evaluate_paper_metrics.py' else 'None; entry point copied unchanged'})
    (target/'common.py').write_text('''import sys
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
''',encoding='utf-8')
    save(target/'adapter_audit.json',{'source_directory':str(LB),'changes':changes,'common':'Paths redirected to CS output; existing hash verifier; network-only guard, no global filesystem interception','formulas_unchanged':True})
if __name__=='__main__':main()
