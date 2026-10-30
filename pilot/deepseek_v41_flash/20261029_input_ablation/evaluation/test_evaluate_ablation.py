"""Offline scope, denominator and F1 regression tests; no model imports."""
import copy
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'evaluate_ablation.py'
spec = importlib.util.spec_from_file_location('evaluate_ablation', SCRIPT)
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


def item(rows):
    return {'normalized_output': rows, 'source_documents': []}


class EvaluationTests(unittest.TestCase):
    def test_membership_intersection_preserves_singletons_and_source(self):
        original = [
            {'Task': 'a', 'Dataset': 'd', 'Metric': 'm', 'Leaderboard': {'p': 1, 'q': 2, 'outside': 3}},
            {'Task': 'b', 'Dataset': 'd', 'Metric': 'm', 'Leaderboard': {'q': 4}},
            {'Task': 'c', 'Dataset': 'd', 'Metric': 'm', 'Leaderboard': {'outside': 5}},
        ]
        before = copy.deepcopy(original)
        boards, scope = ev.derive_boards(original, ['p', 'q'])
        self.assertEqual(original, before)
        self.assertEqual([b['Leaderboard'] for b in boards], [{'p': 1, 'q': 2}, {'q': 4}])
        self.assertEqual(scope['boards_retained'], 2)
        self.assertEqual(scope['boards_ge2'], 1)
        self.assertEqual(scope['singleton_boards'], 1)
        self.assertEqual(scope['boards_dropped_empty'], 1)

    def test_f1_is_harmonic_of_macro_pr_not_mean_paper_f1(self):
        score = ev.metric(.75, .75)
        mean_f1 = (ev.metric(1, .5)['F1'] + ev.metric(.5, 1)['F1']) / 2
        self.assertEqual(score['F1'], .75)
        self.assertAlmostEqual(mean_f1, 2/3)
        self.assertNotEqual(score['F1'], mean_f1)
        self.assertEqual(ev.metric(0, 0)['F1'], 0)

    def test_strict_numeric_no_substring_or_percent_cleaning(self):
        pred = [{'Result': x} for x in ['1.0', '1', '10%', 'NaN', 'NaN', 'bad']]
        gold = [{'Result': x} for x in [1, 10]]
        result = ev.strict_metric(pred, gold)
        self.assertEqual(result['Precision'], .25)
        self.assertEqual(result['Recall'], .5)
        self.assertAlmostEqual(result['F1'], 1/3)
        self.assertEqual(ev.strict_metric([{'Result': '12'}], [{'Result': 2}])['F1'], 0)

    def test_missing_papers_are_not_completed_or_zero_filled(self):
        raw = {'p': {'output': '[]', 'source_documents': []}}
        selected, coverage = ev.scope_inputs(raw, {'p': item([])}, ['p', 'q'])
        self.assertEqual(set(selected), {'p'})
        self.assertEqual(coverage['status'], 'INCOMPLETE')
        self.assertEqual(coverage['tuple_macro_denominator'], 1)
        self.assertEqual(coverage['missing_normalized_ids'], ['q'])

    def test_empty_valid_prediction_counts_as_observed(self):
        raw = {'p': {'output': '[]', 'source_documents': []}}
        _, coverage = ev.scope_inputs(raw, {'p': item([])}, ['p'])
        self.assertEqual(coverage['status'], 'COMPLETE')

    def test_result_change_is_rejected(self):
        row = {'Task': 't', 'Dataset': 'd', 'Metric': 'm', 'Result': '1'}
        import json
        raw = {'p': {'output': json.dumps([row]), 'source_documents': []}}
        altered = dict(row, Result='2')
        with self.assertRaises(ValueError):
            ev.scope_inputs(raw, {'p': item([altered])}, ['p'])

    def test_original_ao_and_tie_order(self):
        funcs = ev.load_pure_helpers()
        self.assertEqual(funcs['ao'](['a', 'b'], ['a', 'c'])[0], .75)
        self.assertEqual(funcs['ao'](['a'], [])[0], 0)
        ranks = funcs['ranking']({'b': 2, 'a': 2}, 'Accuracy')
        self.assertEqual([x['paper_id'] for x in ranks], ['a', 'b'])

    def test_numeric_compatibility_and_string_preservation(self):
        import json
        row = {'Task': 't', 'Dataset': 'd', 'Metric': 'm', 'Result': 1}
        raw = {'p': {'output': json.dumps([row]), 'source_documents': []}}
        _, coverage = ev.scope_inputs(raw, {'p': item([dict(row, Result='1.0')])}, ['p'])
        self.assertEqual(coverage['status'], 'COMPLETE')
        raw['p']['output'] = json.dumps([dict(row, Result='1')])
        with self.assertRaises(ValueError):
            ev.scope_inputs(raw, {'p': item([dict(row, Result='1.0')])}, ['p'])

    def test_no_primary_delta_for_incomplete_scope(self):
        arm = {'status': 'INCOMPLETE', 'stages': {}}
        result = ev.compare_arms({'baseline_rag': arm, 'parsed_full': arm}, ['p'])
        pair = result['pairs']['parsed_full_minus_baseline_rag']
        self.assertFalse(pair['comparable_complete_scope'])
        self.assertIsNone(pair['delta'])

    def test_complete_pair_deltas_cover_both_stages(self):
        def arm(value):
            scores = {m: {'Precision': value, 'Recall': value, 'F1': value} for m in ev.METRICS}
            stage = {'evaluated_ids': ['p'], 'aggregate': scores, 'per_paper': {'p': scores},
                     'leaderboard': {'aggregate': {'PC': value, 'AO': value}}}
            return {'status': 'COMPLETE', 'stages': {'raw_pre_normalization': stage, 'fullyllm': stage}}
        comparison = ev.compare_arms({'baseline_rag': arm(.25), 'parsed_full': arm(.75)}, ['p'])
        pair = comparison['pairs']['parsed_full_minus_baseline_rag']
        self.assertTrue(pair['comparable_complete_scope'])
        for stage in ('raw_pre_normalization', 'fullyllm'):
            self.assertEqual(pair['delta'][stage]['tuple']['TDMR Exact Match']['F1'], .5)
            self.assertEqual(pair['delta'][stage]['leaderboard']['AO'], .5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
