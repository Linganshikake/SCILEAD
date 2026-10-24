set -eu
/root/scilead/axcell/envs/axcell-original/bin/python - <<'PY'
import json,sys,yaml,pkg_resources
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper';prefix=Path(sys.prefix)
prior=run/'dependency_pin_verification.json'
if prior.exists() and not (run/'dependency_pin_verification_before_name_normalization.json').exists():
 (run/'dependency_pin_verification_before_name_normalization.json').write_bytes(prior.read_bytes())
spec=yaml.safe_load((r/'source/axcell/environment.yml').read_text())
conda={d['name']:d['version'] for d in (json.loads(p.read_text()) for p in (prefix/'conda-meta').glob('*.json'))}
checks=[]
for requirement in spec['dependencies']:
 if isinstance(requirement,str):
  name,version=requirement.split('=',1)
  checks.append({'source':'official_conda_pin','name':name,'expected':version,'actual':conda.get(name.lower()),'match':conda.get(name.lower())==version})
 else:
  for item in requirement['pip']:
   if '==' not in item:continue
   name,expected=item.split('==');actual=pkg_resources.get_distribution(name).version
   match=actual==expected or name in ['torch','torchvision'] and actual==expected+'+cpu'
   checks.append({'source':'official_pip_pin','name':name,'expected':expected,'actual':actual,'match':match})
before={x['name'].lower():x['version'] for x in json.loads((run/'conda_python_packages_before_pip.json').read_text())}
after={d.project_name.lower():d.version for d in pkg_resources.working_set}
diff={name:{'before':version,'after':after.get(name)} for name,version in before.items() if after.get(name)!=version}
out={'all_explicit_original_pins_match_with_cpu_build_exception':all(x['match'] for x in checks),'checks':checks,'changes_to_preexisting_python_packages':diff,'cpu_build_exception':['torch==1.3.1+cpu','torchvision==0.4.2+cpu'],'original_environment_yml_modified':False}
(run/'dependency_pin_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='checks'}));assert out['all_explicit_original_pins_match_with_cpu_build_exception']
PY
