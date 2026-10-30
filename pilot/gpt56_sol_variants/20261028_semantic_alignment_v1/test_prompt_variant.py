import json,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261024'
REFERENCE=ROOT.parents[1]/'deepseek_v41_flash/20261028_semantic_alignment_v1'
def read(p):return json.loads(p.read_text(encoding='utf8'))
class Protocol(unittest.TestCase):
 def test_exact_prompt(self):
  self.assertTrue((ROOT/'prompts_semantic_v1.json').is_file(),'Prepared independent Prompt is missing')
  self.assertEqual((ROOT/'prompts_semantic_v1.json').read_bytes(),(REFERENCE/'prompts_semantic_v1.json').read_bytes())
  old=read(ROOT/'prompts_original.json');new=read(ROOT/'prompts_semantic_v1.json');adds=read(ROOT/'prompt_additions.json')
  self.assertEqual({k for k in old if old[k]!=new[k]},set(adds))
  for k,v in adds.items():self.assertEqual(new[k],old[k]+v)
 def test_frozen_sol_input_and_settings(self):
  self.assertTrue((ROOT/'inputs/output.json').is_file(),'Prepared Sol input is missing')
  self.assertEqual((ROOT/'inputs/output.json').read_bytes(),(BASE/'inputs/output.json').read_bytes())
  raw=read(ROOT/'inputs/output.json');self.assertEqual(len(raw),43);self.assertEqual(sum(len(json.loads(v['output'])) for v in raw.values()),335)
  self.assertEqual(read(ROOT/'generation_config.json'),read(BASE/'generation_config.json'))
  for b in ['partially','cold_default','cold_0','cold_42']:
   a=read(ROOT/b/'config.json');o=read(BASE/b/'config.json')
   for k in ['generation','model','paper_order','cold_start','cold_start_seed','masking_seed','python_hash_seed','input_sha256']:self.assertEqual(a[k],o[k])
 def test_runtime_only_scoped_diff(self):
  self.assertTrue((ROOT/'adapter_changes.json').is_file(),'Adaptation record missing')
  audit=read(ROOT/'adapter_changes.json');src=(BASE/'variant_runtime.py').read_text(encoding='utf8')
  for change in audit['exact_replacements']:
   self.assertEqual(src.count(change['before']),change['count']);src=src.replace(change['before'],change['after'])
  self.assertEqual((ROOT/'variant_runtime.py').read_text(encoding='utf8'),src)
  self.assertEqual(hashlib.sha256(Path(audit['transport_path']).read_bytes()).hexdigest(),audit['transport_sha256'])
if __name__=='__main__':unittest.main()
