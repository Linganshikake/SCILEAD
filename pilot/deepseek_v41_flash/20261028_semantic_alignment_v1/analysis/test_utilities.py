"""Offline behavior tests. Every temporary file stays below this analysis directory."""
import copy
import importlib
import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class UtilityTests(unittest.TestCase):
    def module(self, name):
        self.assertIsNotNone(importlib.util.find_spec(name), f'{name} has not been implemented')
        return importlib.import_module(name)

    def test_output_path_rejects_parent_and_sibling(self):
        s = self.module('offline_support')
        for p in (HERE, HERE.parent/'predictions.json', HERE/'..'/'escape.json', HERE.with_name('analysis_other')/'x'):
            with self.subTest(path=p), self.assertRaises(ValueError):
                s.require_output(p)
        self.assertEqual(s.require_output(HERE/'verification'/'ok.json'), HERE/'verification'/'ok.json')

    def test_summary_requires_complete_matching_counts_path_and_hash(self):
        r = self.module('evaluation_contract')
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            p = Path(tmp)/'normalized_output.json'
            p.write_text('{}', encoding='utf-8')
            summary = {'status':'COMPLETE', 'papers':43, 'records':295, 'output_path':str(p), 'output_sha256':r.sha(p)}
            self.assertEqual(r.validate_summary(summary, p), r.sha(p))
            for field, value in [('status','RUNNING'), ('papers',42), ('records',294), ('output_path',str(p.parent/'other.json')), ('output_sha256','0'*64)]:
                bad = {**summary, field:value}
                with self.subTest(field=field), self.assertRaises(ValueError):
                    r.validate_summary(bad, p)

    def test_macro_f1_is_harmonic_of_macro_pr(self):
        e = self.module('evaluate_offline')
        value = {'Individual':{k:{'Precision':0.5,'Recall':0.25} for k in ('Task','Dataset','Metric','Result')},
                 'Exact Match Precision wo Results':0.5,'Exact Match Recall wo Results':0.25,
                 'Exact Match Precision':0.5,'Exact Match Recall':0.25}
        got = e.aggregate_results(value)
        for metric in got.values():
            self.assertAlmostEqual(metric['F1'], 1/3)
            self.assertNotAlmostEqual(metric['F1'], 0.25)

    def test_cold_stats_use_sample_sd_and_require_exact_three_orders(self):
        c = self.module('compare_results')
        runs = {name:{'x':v} for name,v in zip(('cold_default','cold_0','cold_42'), (0.1,0.2,0.3))}
        stats = c.three_order_stats(runs)
        self.assertAlmostEqual(stats['x']['mean'],0.2)
        self.assertAlmostEqual(stats['x']['sample_sd'],0.1)
        with self.assertRaises(ValueError): c.three_order_stats(dict(list(runs.items())[:2]))
        with self.assertRaises(ValueError): c.three_order_stats({**runs,'extra':{'x':0.4}})
        bad = copy.deepcopy(runs); bad['cold_0']['x'] = math.nan
        with self.assertRaises(ValueError): c.three_order_stats(bad)

    def test_differences_are_variant_minus_baseline(self):
        c = self.module('compare_results')
        self.assertEqual(c.scalar_differences({'x':0.75,'y':0.25}, {'x':0.25,'y':0.75}), {'x':0.5,'y':-0.5})
        with self.assertRaises(ValueError): c.scalar_differences({'x':0.5}, {'y':0.2})

    def test_pinned_helpers_and_baseline_contract(self):
        r = self.module('evaluation_contract')
        self.assertGreater(r.verify_audit()['files_checked'], 10)
        norm, summary = r.stage_paths(r.BASELINE, 'partially_stage2')
        r.validate_summary(r.read(summary), norm)
        row = r.load_evaluation(r.BASELINE/'analysis/evaluations/partially_stage2', norm)
        self.assertEqual(row['coverage']['evaluated_papers'],43)
        self.assertEqual(row['coverage']['predictions'],295)
        self.assertEqual(row['leaderboard']['gold_leaderboards'],27)
        self.assertEqual(len(row['per_paper']),43)

    def test_missing_stage_is_pending_without_creating_outputs(self):
        r = self.module('evaluation_contract')
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            state = r.ready_stage(Path(tmp), 'cold_42_stage2')
            self.assertEqual(state['status'],'PENDING')
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_audit_events_block_writes_network_processes_and_models(self):
        r = self.module('evaluation_contract')
        # Synthetic audit events exercise the guard without a network call/process/file write.
        events = [('open',(str(HERE.parent/'forbidden.txt'),'w',0)),
                  ('socket.connect',(None,('example.invalid',443))),
                  ('subprocess.Popen',('unused',[],None,None)),
                  ('import',('transformers',None,[],[],[]))]
        for name,args in events:
            with self.subTest(event=name), self.assertRaises(RuntimeError):
                sys.audit(name,*args)

    def test_changed_or_escaping_sealed_artifacts_are_rejected(self):
        r = self.module('evaluation_contract')
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            root=Path(tmp)
            artifact=root/'status.json'
            artifact.write_text('{}',encoding='utf-8')
            seal={'status':'COMPLETE','input_hashes':{},'artifacts':{'status.json':r.sha(artifact)}}
            r.save(root/'verified_complete.json',seal)
            artifact.write_text('{"changed":true}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'changed'):
                r.verified_evaluation(root,root/'unused')
            seal['artifacts']={'../outside.json':'0'*64}
            r.save(root/'verified_complete.json',seal)
            with self.assertRaisesRegex(ValueError,'escapes'):
                r.verified_evaluation(root,root/'unused')

    def test_missing_variant_differences_remain_none(self):
        c = self.module('compare_results')
        scores={m:{'Precision':0.5,'Recall':0.25,'F1':1/3} for m in c.METRICS}
        base={'model':'baseline','case':'partially_stage2','role':'primary','per_paper':{'paper-a':scores}}
        rows=list(c.per_paper_rows({'local_rows':[base]}))
        self.assertEqual(len(rows),6)
        self.assertEqual(rows[0]['baseline_Precision'],0.5)
        self.assertIsNone(rows[0]['variant_Precision'])
        self.assertIsNone(rows[0]['delta_Precision'])
        self.assertEqual(rows[0]['status'],'VARIANT_UNAVAILABLE')

    def test_paper_changes_report_both_gains_and_regressions(self):
        c = self.module('compare_results')
        rows=[{'case':'cold_0_stage2','metric':'TDMR Exact Match','status':'PAIRED_COMPLETE',
               'paper_id':p,'baseline_F1':0.5,'variant_F1':0.5+d,'delta_F1':d}
              for p,d in [('gain',0.2),('loss',-0.1),('same',0)]]
        item=c.paper_change_summary(rows)[0]
        self.assertEqual((item['improved'],item['regressed'],item['unchanged']),(1,1,1))
        self.assertEqual(item['top_improvements'][0]['paper_id'],'gain')
        self.assertEqual(item['top_regressions'][0]['paper_id'],'loss')
        self.assertEqual(c.paper_change_summary([]),[])


if __name__ == '__main__':
    unittest.main(verbosity=2)
