"""Offline protocol drift checks; no credentials, model loads or network."""
import json,hashlib,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'20261028'
def load(p):return json.loads(p.read_text(encoding='utf8'))
class PromptVariantTests(unittest.TestCase):
 def test_only_two_system_prompts_appended(self):
  before=load(ROOT/'prompts_original.json');after=load(ROOT/'prompts_semantic_v1.json');added=load(ROOT/'prompt_additions.json')
  self.assertEqual(set(before),set(after));self.assertEqual({k for k in before if before[k]!=after[k]},set(added))
  self.assertEqual(set(added),{'masked-normalization-system-prompt','leaderboard-normalization-system-prompt'})
  for k in added:self.assertEqual(after[k],before[k]+added[k]);self.assertNotIn('{',added[k]);self.assertNotIn('}',added[k])
 def test_new_requirement_has_no_dataset_examples_or_gold_values(self):
  text='\n'.join(load(ROOT/'prompt_additions.json').values())
  for blocked in ['ON5E','Ontonotes','CoNLL','90.32','2020.','SemEval','Gold','88.32']:self.assertNotIn(blocked,text)
  for required in ['not by literal string equality','not an exact-string membership test','ambiguous','verbatim']:self.assertIn(required,text)
 def test_frozen_inputs_orders_generation_and_initial_sets(self):
  v=ROOT/'variants';old=BASE/'variants'
  for f in ['inputs/output.json','inputs/gold.json','inputs/leaderboards.json','masking/initial_labels.json','references/cold_initial_labels.json']:
   self.assertEqual((v/f).read_bytes(),(old/f).read_bytes())
  self.assertEqual((ROOT/'generation_config.json').read_bytes(),(BASE/'generation_config.json').read_bytes())
  for b in ['partially','cold_default','cold_0','cold_42']:
   self.assertEqual((v/b/'paper_order.json').read_bytes(),(old/b/'paper_order.json').read_bytes())
   self.assertEqual(load(v/b/'config.json')['cold_start_seed'],load(old/b/'config.json')['cold_start_seed'])
 def test_runner_only_prompt_bindings_changed(self):
  expected=(BASE/'variants/variant_runtime.py').read_text(encoding='utf8').replace("TRANSPORT_PATH=TOP.parent/'transport.py'","TRANSPORT_PATH=TOP.parent/'transport.py'\nPROMPT_PATH=TOP.parent/'prompts_semantic_v1.json'").replace("read(REPO/'prompts.json')","read(PROMPT_PATH)").replace("prompt_file=str(REPO/'prompts.json')","prompt_file=str(PROMPT_PATH)")
  expected=expected.replace("origin=PILOT/('full43_cold_start' if cold else 'full43_partially')/'engine.py'","origin=(ADAPTER_ROOT/'cold_observer.py') if cold else PILOT/'full43_partially'/'engine.py'")
  self.assertEqual((ROOT/'variants/variant_runtime.py').read_text(encoding='utf8'),expected)
  observer=(BASE.parent.parent/'full43_cold_start/engine.py').read_text(encoding='utf8').split('class Transport:')[0].replace("read(REPO/'prompts.json')","read(PROMPT_PATH)")
  self.assertEqual((ROOT/'variants/cold_observer.py').read_text(encoding='utf8'),observer)
  self.assertEqual((ROOT/'transport.py').read_bytes(),(BASE/'transport.py').read_bytes())
if __name__=='__main__':unittest.main()
