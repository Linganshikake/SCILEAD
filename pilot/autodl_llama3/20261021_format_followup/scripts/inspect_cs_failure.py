from pathlib import Path
import json
r=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup')
print((r/'v2_cs.log').read_text(errors='replace')[-6500:])
for p in (r/'format_v2/normalization/fully_cs').rglob('*.json'):
 if p.name in ['model_validation.json','complete.json']:print(str(p.relative_to(r)))
