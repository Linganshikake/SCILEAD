"""All test fixtures/results stay inside analysis/offline_test. No network."""
import copy
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import evaluate_offline as e


class Contracts(unittest.TestCase):
    def setUp(self):
        self.row = {'Task': 'T', 'Dataset': 'D', 'Metric': 'M', 'Result': '1.0'}
        self.gold = {'p': {'TDMs': [dict(self.row, Result=1)]},
                     'q': {'TDMs': [dict(self.row, Result=2)]}}
        self.raw = {'p': {'output': json.dumps([self.row]), 'source_documents': []}}
        self.norm = {'p': {'normalized_output': [self.row], 'source_documents': []}}

    def test_partial_is_explicit_and_not_fixed43(self):
        c = e.validate_inputs(self.raw, self.norm, self.gold)
        self.assertEqual((c['status'], c['evaluated_papers'], c['official_papers']), ('INCOMPLETE', 1, 2))
        self.assertEqual(c['missing_normalized_ids'], ['q'])
        self.assertEqual(c['predictions'], 1)

    def test_empty_coverage_has_no_scores(self):
        c = e.validate_inputs({}, {}, self.gold)
        self.assertEqual(c['evaluated_papers'], 0)
        self.assertEqual(c['status'], 'INCOMPLETE')

    def test_numeric_compatibility_and_string_preservation(self):
        self.raw['p']['output'] = '[{"Task":"T","Dataset":"D","Metric":"M","Result":1.000}]'
        self.assertEqual(e.validate_inputs(self.raw, self.norm, self.gold)['numeric_result_to_string_rows'], 1)
        self.raw['p']['output'] = json.dumps([dict(self.row, Result='1')])
        with self.assertRaisesRegex(ValueError, 'Result'):
            e.validate_inputs(self.raw, self.norm, self.gold)

    def test_changed_result_row_count_documents_unknown_and_nonstring_fail(self):
        for alter in ('result', 'count', 'documents', 'unknown', 'nonstring'):
            with self.subTest(alter=alter):
                n = copy.deepcopy(self.norm)
                if alter == 'result': n['p']['normalized_output'][0]['Result'] = '7'
                if alter == 'count': n['p']['normalized_output'].append(self.row)
                if alter == 'documents': n['p']['source_documents'] = ['changed']
                if alter == 'unknown': n['outside'] = n.pop('p')
                if alter == 'nonstring': n['p']['normalized_output'][0]['Result'] = 1
                with self.assertRaises(ValueError): e.validate_inputs(self.raw, n, self.gold)

    def test_strict_numeric_is_not_substring_or_percent_cleaning(self):
        pred = [{'Result': x} for x in ['1', '1.0', '12', 'N/A', 'NaN', '50%']]
        gold = [{'Result': x} for x in [1, 2, 50]]
        self.assertEqual(e.strict_metric(pred, gold), e.metric(1/5, 1/3))

    def test_duplicate_raw_keys_rejected(self):
        self.raw['p']['output'] = '[{"Task":"T","Task":"X","Dataset":"D","Metric":"M","Result":"1.0"}]'
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            e.validate_inputs(self.raw, self.norm, self.gold)


class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (HERE/'offline_test').mkdir(exist_ok=True)
        cls.root = Path(tempfile.mkdtemp(prefix='regression_', dir=HERE/'offline_test'))

    def run_cli(self, raw, normalized, name, boards=None):
        out = self.root/name
        cmd = [sys.executable, '-B', '-X', 'utf8', str(HERE/'evaluate_offline.py'),
               '--raw', str(raw), '--normalized', str(normalized), '--out', str(out)]
        if boards: cmd += ['--boards', str(boards)]
        r = subprocess.run(cmd,
                           capture_output=True, text=True, encoding='utf-8')
        return r, out

    def test_historical_gpt41_exact_parity(self):
        base = e.PILOT/'full43_uncapped'
        r, out = self.run_cli(base/'merged/output.json', base/'merged/normalized_output.json', 'gpt41')
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        got = e.read(out/'metrics_with_f1.json')
        self.assertEqual(got['aggregate'], e.read(base/'evaluation/metrics_with_f1.json')['aggregate'])
        lb = e.read(out/'leaderboard/paper_metrics/leaderboard_metrics.json')['aggregate']
        self.assertEqual(lb, e.read(e.PILOT/'leaderboard_eval_full43_uncapped/paper_metrics/leaderboard_metrics.json')['aggregate'])
        self.assertEqual(got['coverage']['predictions'], 284)

    def test_sol_fully_cs_and_masked10_parity(self):
        import compare_results as c
        cases = [
            ('sol_fully', c.SOL/'merged/normalized_output.json', c.SOL/'evaluation/metrics_with_f1.json', c.VAR/'evaluation_references/gpt56_fully/all27/paper_metrics/leaderboard_metrics.json', None),
            ('sol_cs', c.VAR/'fully_cs/normalization/embedding_normalized_output.json', c.VAR/'fully_cs/evaluation/metrics_with_f1.json', c.VAR/'fully_cs/leaderboard_evaluation/paper_metrics/leaderboard_metrics.json', None),
            ('sol_masked', c.VAR/'partially/stage2/leaderboard_normalized_output.json', c.VAR/'partially/evaluation/stage2/metrics_with_f1.json', c.VAR/'partially/evaluation/masked10/paper_metrics/leaderboard_metrics.json', c.MASK)]
        for name, np, mp, lp, boards in cases:
            with self.subTest(name=name):
                r, out = self.run_cli(c.SOL/'merged/output.json', np, name, boards)
                self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
                self.assertEqual(e.read(out/'metrics_with_f1.json')['aggregate'], c.tuple_metrics(e.read(mp)))
                lb = e.read(out/'leaderboard/paper_metrics/leaderboard_metrics.json')['aggregate']
                self.assertEqual(lb, e.read(lp)['aggregate'])
                if name=='sol_cs': self.assertEqual(lb['LR_exact_tdm_hit'], 24/27)
                if boards: self.assertEqual(lb['gold_leaderboards'], 10)
                # Exercise the new-result reader in memory only; historical
                # fixtures are never published as DeepSeek experiment results.
                if name=='sol_fully':
                    got, missing = c.load_new(c.Sources(), self.root/'absent_suite', {'fully':out})
                    self.assertEqual(len(got),1)
                    self.assertEqual(len(missing),9)
                    self.assertEqual(got[0]['tuple'],c.tuple_metrics(e.read(mp)))
                    # Both supported live directory layouts, using historical
                    # fixtures strictly inside offline_test.
                    for layout in ('direct','nested'):
                        suite = self.root/('layout_'+layout)
                        target = suite/'fully' if layout=='direct' else suite/'fully/all27'
                        shutil.copytree(out,target)
                        autodetected, absent = c.load_new(c.Sources(),suite,{})
                        self.assertEqual(len(autodetected),1)
                        self.assertEqual(len(absent),9)
                        self.assertEqual(autodetected[0]['case'],'fully')
                if boards:
                    with self.assertRaisesRegex(ValueError,'Cannot label'):
                        c.load_new(c.Sources(), self.root/'absent_suite', {'fully':out})

    def test_boundary_no_network_credentials_external_writes_or_model_imports(self):
        code = '''import socket, sys
from pathlib import Path
from offline_support import boundary, bind_official, ANALYSIS
boundary()
for action in [lambda: socket.getaddrinfo('example.invalid', 443),
               lambda: Path('blocked.env').read_text(),
               lambda: sys.audit('subprocess.Popen', 'blocked', [], None, None),
               lambda: sys.audit('os.system', 'blocked'),
               lambda: sys.audit('_winapi.CreateProcess', 'blocked', None, None, None, False, 0, None, None, None),
               lambda: (ANALYSIS.parent/'forbidden_test_output.txt').write_text('no')]:
    try: action()
    except RuntimeError: pass
    else: raise AssertionError('Boundary did not block action')
bind_official()
assert not any(n in sys.modules for n in ('model_init','transformers','langchain','openai','httpx','dotenv','variant_runtime'))
print('PASS')
'''
        r = subprocess.run([sys.executable,'-B','-X','utf8','-c',code], cwd=HERE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        self.assertFalse((HERE.parent/'forbidden_test_output.txt').exists())

    def test_comparison_complete_history_stage2_primary_and_all_papers_csv(self):
        out = self.root/'comparison'
        r = subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'compare_results.py'),
                            '--evaluations',str(self.root/'no_current_results'),'--out',str(out)], capture_output=True,text=True)
        self.assertEqual(r.returncode, 2, r.stdout+r.stderr)
        report = e.read(out/'comparison.json')
        self.assertEqual(len(report['local_rows']), 20)
        self.assertEqual(len(report['missing']), 10)
        for model in ('GPT-4.1','Sol'):
            primary = next(x for x in report['local_rows'] if x['model']==model and x['case']=='partially_stage2')
            self.assertEqual(primary['role'], 'primary')
            self.assertEqual(set(primary['leaderboards']), {'all27','masked10'})
        with (out/'per_paper_comparison.csv').open(encoding='utf-8-sig', newline='') as f:
            csvrows = list(csv.DictReader(f))
        self.assertEqual(len(csvrows), sum(len(r['per_paper'])*7 for r in report['local_rows']))
        self.assertTrue(all(len(r['per_paper'])==43 for r in report['local_rows']))
        self.assertNotEqual(report['provenance']['original_repository_HEAD'], report['provenance']['frozen_outer_archive_commit'])

    def test_malformed_input_fails_and_zero_scores_are_not_fabricated(self):
        raw, norm = self.root/'bad_raw.json', self.root/'bad_norm.json'
        raw.write_text('{bad json', encoding='utf-8'); norm.write_text('{}', encoding='utf-8')
        r, out = self.run_cli(raw,norm,'malformed')
        self.assertEqual(r.returncode,1)
        self.assertEqual(e.read(out/'status.json')['status'],'FAILED')
        self.assertFalse((out/'metrics_with_f1.json').exists())

    def test_inspector_has_all_ten_cases_and_does_not_claim_file_presence_complete(self):
        out = self.root/'inspection'
        r = subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'inspect_runs.py'),
                            '--out',str(out)],capture_output=True,text=True)
        self.assertEqual(r.returncode,2,r.stdout+r.stderr)
        report=e.read(out/'inspection.json')
        self.assertEqual(report['status'],'INCOMPLETE')
        self.assertEqual(len(report['jobs']),10)
        self.assertTrue(all(j['evaluations']=={} for j in report['jobs']))

    def test_nonfinite_board_result_is_explicit_failure(self):
        board=e.read(e.BOARDS)[0]; paper=next(iter(board['Leaderboard']))
        row={k:board[k] for k in ('Task','Dataset','Metric')}; row['Result']='NaN'
        raw={paper:{'output':json.dumps([row]),'source_documents':[]}}
        norm={paper:{'normalized_output':[row],'source_documents':[]}}
        rp,np=self.root/'nonfinite_raw.json',self.root/'nonfinite_norm.json'
        rp.write_text(json.dumps(raw),encoding='utf-8');np.write_text(json.dumps(norm),encoding='utf-8')
        r,out=self.run_cli(rp,np,'nonfinite')
        self.assertEqual(r.returncode,1)
        self.assertIn('Nonfinite',e.read(out/'status.json')['error'])

    def test_partial_empty_and_missing_cli(self):
        base = e.PILOT/'full43_uncapped/merged'
        raw, norm = e.read(base/'output.json'), e.read(base/'normalized_output.json')
        paper = next(iter(norm))
        for name, rr, nn in [('partial', raw, {paper:norm[paper]}), ('empty', {}, {})]:
            rp, np = self.root/(name+'_raw.json'), self.root/(name+'_norm.json')
            rp.write_text(json.dumps(rr), encoding='utf-8'); np.write_text(json.dumps(nn), encoding='utf-8')
            r, out = self.run_cli(rp, np, name)
            self.assertEqual(r.returncode, 2, r.stdout+r.stderr)
            status = e.read(out/'status.json')
            self.assertEqual(status['status'], 'INCOMPLETE')
            self.assertEqual(status['coverage']['evaluated_papers'], len(nn))
            if nn:
                lb = e.read(out/'leaderboard/paper_metrics/leaderboard_metrics.json')['aggregate']
                self.assertEqual(lb['gold_leaderboards'], 27)
            else: self.assertFalse((out/'metrics_with_f1.json').exists())
        r, out = self.run_cli(self.root/'absent.json', self.root/'missing.json', 'missing')
        self.assertEqual(r.returncode, 2, r.stdout+r.stderr)
        self.assertEqual(e.read(out/'status.json')['status'], 'INCOMPLETE')


if __name__ == '__main__':
    program = unittest.main(verbosity=2, exit=False)
    result = program.result
    e.save(HERE/'offline_test/verification_latest.json', {
        'status':'PASS' if result.wasSuccessful() else 'FAIL', 'tests_run':result.testsRun,
        'failures':len(result.failures), 'errors':len(result.errors),
        'artifacts':str(getattr(Integration,'root',HERE/'offline_test')), 'python':sys.executable, 'new_api_requests':0,
        'utility_hashes': {str(p):e.sha(p) for p in HERE.glob('*.py')},
        'checks': ['GPT41 Fully exact tuple/leaderboard parity', 'Sol Fully and Fully CS exact parity',
                   'Sol Partially stage2 masked10 exact parity', '43/295/all27 and explicit partial/empty coverage',
                   '20 historical configurations; all-paper CSV; Partially stage2 primary',
                   'Network, credentials, external writes and child-process boundary']})
    sys.exit(0 if result.wasSuccessful() else 1)
