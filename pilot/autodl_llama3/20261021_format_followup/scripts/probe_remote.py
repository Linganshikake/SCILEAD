from pathlib import Path
import subprocess,json,hashlib
root=Path('/root/autodl-tmp/scilead');old=root/'runs/llama3/20261021_formal42';r=root/'runs/llama3/20261021_format_followup'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
print(json.dumps({'new_directory_exists':r.exists(),'gpu':subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout,'gpu_processes':subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],capture_output=True,text=True).stdout,'memory':Path('/proc/meminfo').read_text().splitlines()[:3],'old_complete':(old/'formal_remote_complete.json').exists(),'adapter_sha256':sha(root/'adapters/run_llama.py')}))
print((root/'adapters/run_llama.py').read_text())
