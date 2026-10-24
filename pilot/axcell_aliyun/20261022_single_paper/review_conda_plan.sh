set -eu
python3 - <<'PY'
from pathlib import Path
import json
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
s=(r/'conda_dry_run.log').read_text();d,end=json.JSONDecoder().raw_decode(s)
assert d['success'] and d['dry_run']
packages=d['actions']['LINK'];pins={p['name']:p['version'] for p in packages}
expected={'python':'3.7.1','pip':'21.0.1','fire':'0.1.3','html5lib':'1.0.1','beautifulsoup4':'4.7.1','lxml':'4.3.4','pandas':'0.25.3','numpy':'1.18.1','pyahocorasick':'1.4.0','unidecode':'1.0.23','elasticsearch-dsl':'6.3.1','ipython':'7.5.0','joblib':'0.13.2','python-magic':'0.4.15','docker-py':'4.1.0','seaborn':'0.9.0','docker-compose':'1.25.5','freetype':'2.10.1','numba':'0.48.0','spacy':'2.2.3'}
for k,v in expected.items():assert pins[k]==v,(k,pins.get(k),v)
summary={'success':True,'all_original_conda_pins_match':True,'package_count':len(packages),'download_bytes':sum(x.get('size',0) for x in d['actions'].get('FETCH',[])),'original_pins':expected,'sample_package':packages[0],'prefix':d['prefix']}
(r/'conda_solve_plan.json').write_text(json.dumps(d,indent=2))
(r/'conda_plan_review.json').write_text(json.dumps(summary,indent=2))
explicit='@EXPLICIT\n'+'\n'.join(p['url']+'#'+p['md5'] for p in packages)+'\n'
(r/'conda-explicit.txt').write_text(explicit)
print(json.dumps(summary,indent=2))
PY
