import sys, json, hashlib, os
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode=True
ROOT=Path(r'D:\C++\SCILEAD'); OUT=Path(__file__).resolve().parent
P3=OUT.parent/'20261022_stage3_resume'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
previous=read(P3/'local_frozen_before.json')
paths={Path(p) for p in previous}
paths.update(p for p in P3.rglob('*') if p.is_file())
repo=ROOT/'emnlp2024-leaderboard-generation'
paths.update(p for p in repo.glob('*') if p.is_file() and p.suffix in ('.py','.json','.md','.txt','.yml'))
paths.add(ROOT/'pilot/gold/tdm_annotations.json')
paths.add(ROOT/'pilot/experiment_settings.json')
snapshot={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths) if p.is_file()}
with (OUT/'protected_files_before.json').open('x',encoding='utf-8') as f: json.dump(snapshot,f,indent=2)
diff=[p for p,v in previous.items() if p not in snapshot or snapshot[p]!=v]
manifest=read(P3/'extraction_manifest.json')
rows=manifest['rows']
rawtypes=[]
for r in rows:
    if r.get('raw_output_path'):
        raw=read(Path(r['raw_output_path']))
        rawtypes.extend([type(v.get('score')).__name__ for v in raw])
print(json.dumps({'snapshot_files':len(snapshot),'prior_freeze_mismatches':diff,'raw_score_types':sorted(set(rawtypes)),'p3_counts':read(P3/'stage3_verification.json'),'baseline_manifest_keys':list(read(ROOT/'pilot/full43_uncapped/manifest.json'))},ensure_ascii=True))
