"""Build an isolated single-attempt adapter from frozen validated guards."""
import ast,difflib,hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent
F=R.parent/'20261022_formal/stage2'
REMOTE='/root/scilead/axcell/runs/20261022_parse_recovery'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=R/'attempt_2203_timeout600';assert not out.exists();out.mkdir()
 src=Path(r'E:\SCILEAD\axcell\source\axcell\axcell\scripts')
 shutil.copytree(src,out/'converter_scripts')
 f=out/'converter_scripts/latex2html.sh';before=f.read_bytes();needle=b'timeout -s KILL 300 engrafo';assert before.count(needle)==1
 after=before.replace(needle,b'timeout -s KILL 600 engrafo');f.write_bytes(after)
 (out/'timeout_only.diff').write_text(''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='original/latex2html.sh',tofile='RECOVERY_TIMEOUT_600/latex2html.sh')),encoding='utf-8')
 shutil.copy2(F/'policy.py',out/'policy.py')
 s=(F/'parse_one.py').read_text(encoding='utf-8')
 s=s.replace('/root/scilead/axcell/runs/20261022_formal/stage2',REMOTE+'/attempt_2203_timeout600')
 s=s.replace("with patch('docker.from_env',negotiated):extract=PaperExtractor(data)","with patch('docker.from_env',negotiated):\n        from axcell.helpers.latex_converter import LatexConverter\n        extract=PaperExtractor(data)\n        extract.latex=LatexConverter(scripts_path=ROOT/'converter_scripts')")
 s=s.replace('axcell-formal-convert','axcell-recovery-convert-2203').replace('axcell-formal-parse-20261022','axcell-parse-recovery-20261022')
 s=s.replace("'official_status':status", "'recovery_label':'RECOVERY_TIMEOUT_600','official_status':status")
 (out/'parse_one.py').write_text(s,encoding='utf-8')
 s=(F/'monitor.py').read_text(encoding='utf-8')
 s=s.replace('/root/scilead/axcell/runs/20261022_formal/stage2',REMOTE+'/attempt_2203_timeout600')
 s=s.replace('axcell-formal-parse-20261022','axcell-parse-recovery-20261022')
 s=s.replace("from pathlib import Path", "from pathlib import Path\nfrom observe import extra_snapshot")
 s=s.replace('rows.append(row)',"row.update(extra_snapshot(pid,d))\n            rows.append(row)")
 (out/'monitor.py').write_text(s,encoding='utf-8')
 for p in out.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
 q=json.loads((R/'selected_inputs.json').read_text(encoding='utf-8'));row=next(x for x in q if x['paper_id']=='2203.16804.pdf')
 row['frozen_remote_source']=row['remote_source'];row['remote_source']=REMOTE+'/attempt_2203_timeout600/parsed/sources/'+row['tex_version']
 (out/'queue.json').write_text(json.dumps([row],indent=2),encoding='utf-8')
 original=json.loads((F/'configuration.json').read_text(encoding='utf-8'))
 config={k:original[k] for k in ['axcell_commit','image','workers','container_memory_gib','container_cpus','network_disabled','threads','start_min_ram_gib','disk_reserve_gib','stop_low_ram_gib','sustained_seconds']}
 config.update(recovery_label='RECOVERY_TIMEOUT_600',official_converter_timeout_seconds=300,recovery_converter_timeout_seconds=600,outer_safety_watchdog_seconds=660,attempt_limit=1,automatic_retries=0,api_calls=0,model_loads=0,source_archive_unchanged=True,scientific_difference='latex2html.sh timeout 300 -> 600 only',observability_difference='read-only process CPU, cgroup, file descriptor positions and intermediate snapshots')
 config['configuration_sha256']=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
 (out/'configuration.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
 print(json.dumps({'converter_difference':(out/'timeout_only.diff').read_text(),'python_syntax':'passed','path':str(out)}))
if __name__=='__main__':main()
