from pathlib import Path
import json,subprocess,os,hashlib
r=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup')
env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
p=subprocess.run(['/root/autodl-tmp/scilead/envs/llama/bin/python','-B',str(r/'scripts/cs_repair_runner.py'),'probe'],env=env,capture_output=True,text=True)
print(json.dumps({'probe_exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr[-1000:]}));assert p.returncode==0
assert (r/'workflow_complete.json').exists(),'WAIT_FOR_ORIGINAL_WORKFLOW_TO_FINISH'
assert not (r/'cs_repair_launch.json').exists(),'ALREADY_LAUNCHED'
code="""from pathlib import Path
import subprocess,os,json
r=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup');out={}
for mode in ['v2','diagnostic']:
 if mode=='diagnostic' and not (r/'token2048_diagnostic/extraction/prepared_output.json').exists():continue
 p=subprocess.run(['/root/autodl-tmp/scilead/envs/llama/bin/python','-B',str(r/'scripts/cs_repair_runner.py'),mode]);out[mode]=p.returncode
(r/'cs_repair_complete.json').write_text(json.dumps(out))
"""
with (r/'cs_repair.log').open('ab') as log:p=subprocess.Popen(['/root/autodl-tmp/scilead/envs/llama/bin/python','-c',code],env=env,stdout=log,stderr=log,start_new_session=True)
(r/'cs_repair_launch.json').write_text(json.dumps({'pid':p.pid,'reason':'Verified fixed-code cache repair; prior failure preceded new CS mappings'}));print('CS_REPAIR_LAUNCHED',p.pid)
