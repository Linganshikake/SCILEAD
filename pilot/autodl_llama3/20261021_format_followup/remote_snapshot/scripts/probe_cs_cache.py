from pathlib import Path
import os,json
root=Path('/root/autodl-tmp/scilead');old=root/'runs/llama3/20261021_formal42'
for p in [old/'cache',root/'cache/huggingface',root/'models/bilingual-embedding-large']:
 print('ROOT',str(p),'EXISTS',p.exists())
 if p.exists():
  for f in p.rglob('*'):
   if f.is_file() and (f.suffix=='.py' or 'refs' in f.parts):print(str(f),f.stat().st_size)
print((old/'config/cs_model_transfer.json').read_text())
