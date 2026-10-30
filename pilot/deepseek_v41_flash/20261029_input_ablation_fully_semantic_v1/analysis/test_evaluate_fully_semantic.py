"""Run offline with the existing scilead Python using -E -s -B -X utf8."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'evaluate_fully_semantic.py'


def load():
    if not SCRIPT.exists():
        raise AssertionError('Fully evaluator has not been implemented')
    spec = importlib.util.spec_from_file_location('fully_evaluator', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = load()
        cls.core = cls.e.load_core()
        cls.previous, cls.protected, cls.candidates = cls.e.verify_reference(cls.core)

    def inputs(self):
        source = self.e.PREVIOUS / self.e.ARMS['baseline_rag']
        return self.e.read(source/'output.json'), self.e.read(source/'normalized_output.json')

    def test_frozen_scope_and_original_board_memberships(self):
        boards = self.e.read(self.e.BOARDS)
        before = copy.deepcopy(boards)
        derived, scope = self.core.derive_boards(boards, self.e.SELECTED)
        self.assertEqual((len(derived), sum(len(b['Leaderboard']) for b in derived), scope['singleton_boards']), (10, 14, 6))
        self.assertEqual(boards, before)
        self.assertEqual(self.previous['scope']['selected_gold_tdmrs'], 28)
        self.assertEqual({k: len(v) for k,v in self.candidates.items()}, {'Task': 23, 'Dataset': 71, 'Metric': 26})

    def test_all_prior_arms_satisfy_fully_contract(self):
        for arm, folder in self.e.ARMS.items():
            raw = self.e.read(self.e.PREVIOUS/folder/'output.json')
            norm = self.e.read(self.e.PREVIOUS/folder/'normalized_output.json')
            with self.subTest(arm=arm):
                self.assertEqual(self.e.validate_inputs(raw, norm, self.core, self.candidates)['status'], 'COMPLETE')

    def test_partial_ids_never_claim_complete_and_extra_ids_fail(self):
        raw, norm = self.inputs()
        del norm[self.e.SELECTED[-1]]
        coverage = self.e.validate_inputs(raw, norm, self.core, self.candidates)
        self.assertEqual(coverage['status'], 'INCOMPLETE')
        self.assertEqual(coverage['missing_normalized_ids'], [self.e.SELECTED[-1]])
        norm['unexpected.pdf'] = next(iter(norm.values()))
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            self.e.validate_inputs(raw, norm, self.core, self.candidates)

    def test_result_rows_and_source_documents_are_immutable(self):
        raw, norm = self.inputs()
        paper = self.e.SELECTED[0]
        for mutation in ('result', 'rows', 'source', 'missing_source'):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(norm)
                entry = changed[paper]
                if mutation == 'result': entry['normalized_output'][0]['Result'] = '56'
                elif mutation == 'rows': entry['normalized_output'].pop()
                elif mutation == 'source': entry['source_documents'] = ['changed']
                else: entry.pop('source_documents')
                with self.assertRaises(ValueError): self.e.validate_inputs(raw, changed, self.core, self.candidates)

    def test_no_added_labels_and_existing_candidates_cannot_change(self):
        raw, norm = self.inputs()
        paper = self.e.SELECTED[0]
        for label in ('invented task', None, 'Machine Translation'):
            changed = copy.deepcopy(norm)
            changed[paper]['normalized_output'][0]['Task'] = label
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.e.validate_inputs(raw, changed, self.core, self.candidates)
        # PTB is not itself a candidate; original None fallback remains allowed.
        norm[paper]['normalized_output'][0]['Dataset'] = None
        self.assertEqual(self.e.validate_inputs(raw, norm, self.core, self.candidates)['status'], 'COMPLETE')

    def test_duplicate_keys_and_nonfinite_json_fail(self):
        for s in ('{"p":1,"p":2}', '{"p":NaN}', '{"p":Infinity}'):
            with self.subTest(s=s), self.assertRaises(ValueError): self.e.decode_json(s)

    def test_complete_only_comparison_reports_all_metrics(self):
        old = self.previous['arms']['baseline_rag']['stages']['fullyllm']
        new = copy.deepcopy(old)
        new['aggregate']['Task IIM']['F1'] = .5
        result = self.e.compare(old, new)
        self.assertEqual(result['delta']['tuple']['Task IIM']['F1'], -.5)
        self.assertEqual(len(result['delta']['tuple']), 7)
        self.assertEqual(len(result['delta']['per_paper']), 5)
        self.assertTrue(result['prompt_comparison_same_extraction'])
        new['status'] = 'INCOMPLETE'
        self.assertIsNone(self.e.compare(old, new)['delta'])

    def test_official_legacy_result_and_numeric_rbo_are_preserved(self):
        with self.core.official_modules() as (tdm, lb):
            row = {'Task': 'T', 'Dataset': 'D', 'Metric': 'M', 'Result': '1'}
            gold = {'p': {'TDMs': [dict(row, Result=10)]}}
            norm = {'p': {'normalized_output': [row]}}
            r,p = tdm.calculate_exact_match(gold, norm)
            self.assertEqual((r['p'],p['p']), (1,1))
            self.assertEqual(self.core.strict_metric([row], gold['p']['TDMs'])['F1'], 0)
            key = str(('T','D','M'))
            scores = lb.evaluate({key: {'q': 10}}, [{'Task':'T','Dataset':'D','Metric':'M','Leaderboard':{'p':10}}])
            self.assertEqual([scores[k][key] for k in ('Paper Coverage','Result Coverage','RBO')], [0,1,1])
            self.assertEqual(self.core.HELPERS['ao'](['p'], ['q'])[0], 0)

    def test_write_and_credentials_boundary(self):
        self.e.writable(ROOT/'evaluation/a.json')
        self.e.writable(ROOT/'analysis/a.json')
        for path in [self.e.PREVIOUS/'evaluation/a.json', ROOT/'runtime.py', ROOT/'evaluation/../../a.json']:
            with self.subTest(path=path), self.assertRaises(PermissionError): self.e.writable(path)
        for path in [ROOT/'.env', ROOT/'.env.local', ROOT/'.aws/credentials', ROOT/'credentials.json', ROOT/'id_rsa']:
            with self.subTest(path=path), self.assertRaises(PermissionError): self.e.check_read(path)


class IntegrationTests(unittest.TestCase):
    def python(self, *args):
        return subprocess.run([sys.executable,'-E','-s','-B','-X','utf8',*args], cwd=ROOT,
                              env={}, capture_output=True, text=True, encoding='utf-8')

    def test_fixture_matches_verified_metrics_and_preserves_pointers(self):
        e = load()
        paths = [e.PREVIOUS/'evaluation/report.json', e.PREVIOUS/'evaluation/latest.json',
                 ROOT/'evaluation/report.json', ROOT/'evaluation/latest.json']
        before = {str(p): p.read_bytes() if p.exists() else None for p in paths}
        proc = self.python(str(SCRIPT), '--fixture-prior-completed')
        self.assertEqual(proc.returncode, 0, proc.stdout+proc.stderr)
        info = json.loads(proc.stdout.splitlines()[-1])
        self.assertEqual(info['status'], 'FIXTURE_COMPLETE')
        report = e.read(info['report'])
        self.assertFalse(report['all_three_arms_complete'])
        self.assertTrue(report['fixture_parity_verified'])
        self.assertTrue(report['protected_files_unchanged'])
        for arm in e.ARMS:
            value = report['arm_results'][arm]
            for key in ('aggregate','per_paper','leaderboard','mean_per_paper_f1_SEPARATE'):
                self.assertEqual(value['old_fully'][key], value['enhanced_fully'][key], (arm,key))
            self.assertEqual(value['comparison']['delta']['tuple']['TDMR Exact Match']['F1'], 0)
        self.assertEqual(before, {str(p): p.read_bytes() if p.exists() else None for p in paths})

    def test_offline_guard_is_enforced(self):
        code = '''
import importlib.util,sys,os
s=importlib.util.spec_from_file_location('ev',sys.argv[1]);e=importlib.util.module_from_spec(s);s.loader.exec_module(e)
e.install_boundary()
assert os.getenv('HOME') is None
for event,args in [('socket.connect',(None,('127.0.0.1',1))),('subprocess.Popen',('x',[],None,None)),('os.putenv',('A','B'))]:
 try: sys.audit(event,*args)
 except PermissionError: pass
 else: raise AssertionError(event)
try: __import__('transformers')
except PermissionError: pass
else: raise AssertionError('model import')
try: (e.PREVIOUS/'evaluation/guard_probe.json').write_text('bad')
except PermissionError: pass
else: raise AssertionError('old write')
print('guard passed')
'''
        proc = self.python('-c', code, str(SCRIPT))
        self.assertEqual(proc.returncode, 0, proc.stdout+proc.stderr)
        self.assertIn('guard passed', proc.stdout)


if __name__ == '__main__': unittest.main(verbosity=2)
