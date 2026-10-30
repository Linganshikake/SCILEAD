"""Actual official mains, masks and orders; synthetic predictions, HTTP responses only."""
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest

import variant_runtime as v
import prepare_variants as p


class FrozenProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.setup()
        cls.root = Path(tempfile.mkdtemp(prefix='frozen_protocol_', dir=v.TOP / 'reproducibility'))
        cls.source = cls.root / 'fully/merged/output.json'
        cls.normalized = cls.root / 'fully/merged/normalized_output.json'
        cls.marker = cls.root / 'fully/verification.json'
        cls.out = cls.root / 'prepared'
        cls.order = v.read(p.REFERENCE / 'partially/paper_order.json')['papers']
        # One empty paper and two identical predictions: count unknown to the adapter.
        # Use reversed publication order so preparation must restore frozen order.
        row = {'Task': 'SyntheticTask', 'Dataset': 'SyntheticDataset', 'Metric': 'SyntheticMetric', 'Result': '1.00'}
        raw = {paper: {'output': json.dumps([row, row] if paper == cls.order[0] else []),
                       'source_documents': [{'content': 'offline only', 'metadata': {'paper': paper}}]}
               for paper in reversed(cls.order)}
        norm = {paper: {'normalized_output': json.loads(value['output']), 'source_documents': value['source_documents']}
                for paper, value in raw.items()}
        v.save(cls.source, raw)
        v.save(cls.normalized, norm)
        v.save(cls.marker, {'state': 'QUEUE_FINISHED', 'complete_papers': len(cls.order), 'records': 2,
                            'protected_files_changed': [], 'secret_scan_passed': True, 'stop': None})
        cls.manifest = p.prepare(cls.source, cls.normalized, cls.out,
                                  scope=v.TOP.parent / 'evaluation_scope.json', verification=cls.marker)

    def test_preparation_dynamic_counts_frozen_copies_and_idempotency(self):
        self.assertEqual(self.manifest['predictions'], 2)
        self.assertEqual(self.manifest['maximum_method_positions'], 32)
        self.assertFalse(self.manifest['model_loaded'])
        self.assertTrue(self.manifest['input_paper_reorder_only'])
        self.assertEqual(list(v.read(self.out / 'inputs/output.json')), self.order)
        self.assertEqual(v.read(self.out / 'inputs/output.json'), v.read(self.source))
        self.assertEqual(v.read(self.out / 'inputs/normalized_output.json'), v.read(self.normalized))
        cfg = v.read(self.out / 'fully_cs/config.json')
        self.assertEqual(cfg['raw_records'], 2)
        self.assertEqual(cfg['expected_exact_fields'] + cfg['expected_cs_fields'], 6)
        self.assertFalse(v.read(self.out / 'fully_cs/model_manifest.json')['current_run_model_hashes_verified'])
        self.assertEqual(v.read(self.out / 'fully_cs/resource_policy.json')['minimum_physical_GiB'], 4.0)
        self.assertEqual(p.prepare(self.source, self.normalized, self.out,
                                  scope=v.TOP.parent / 'evaluation_scope.json', verification=self.marker), self.manifest)

    def test_original_masking_matches_frozen_labels_and_file(self):
        import tdm_llm_masked_normalization as s1
        masks = self.root / 'actual_masks'
        labels = s1.sample_tdms(v.read(self.out / 'inputs/leaderboards.json'), v.read(self.out / 'inputs/gold.json'),
                                0, masks.as_posix() + '/', False, 'masking/')
        self.assertEqual(v.labels_state(labels), v.read(p.REFERENCE / 'masking/initial_labels.json'))
        self.assertEqual(v.sha(masks / 'masking/partially_masked_leaderboards.json'),
                         v.sha(p.REFERENCE / 'masking/partially_masked_leaderboards.json'))

    def test_official_cold_orders_results_and_replay(self):
        import tdm_llm_masked_normalization as s1
        for name, seed in p.BRANCHES[1:]:
            with self.subTest(branch=name):
                v.RUN_ID = name
                out = self.root / name
                cfg = v.read(self.out / name / 'config.json')
                self.assertEqual(cfg['cold_start_seed'], seed)
                if seed is not None:
                    self.assertIsInstance(cfg['cold_start_seed'], str)
                args = types.SimpleNamespace(seed=0, tdm_config_file=str(self.out / name / 'official_config.json'),
                    gold_tdm_file=cfg['gold_path'], gold_leaderboard_file=cfg['leaderboards_path'],
                    tdm_output_file=cfg['input_path'], prompt_file=str(v.REPO / 'prompts.json'), cold_start=True,
                    cold_start_seed=seed, normalization_output_path=out.as_posix() + '/', max_new_tokens=None)
                observer, transport = v.run_original(s1, 'stage1', args, out, mock=lambda e: e['original'])
                replay_observer, replay = v.run_original(s1, 'stage1', args, out, mock=lambda e: e['original'])
                sub = 'cold_start' + ('_' + seed if seed is not None else '')
                output = v.read(out / sub / 'cold_start_masked_normalized_output.json')
                self.assertEqual(list(output), v.read(p.REFERENCE / name / 'paper_order.json')['papers'])
                self.assertEqual([r['Result'] for r in output[self.order[0]]['normalized_output']], ['1.00', '1.00'])
                self.assertEqual(transport.mock_new, 3)
                self.assertEqual(replay.mock_new, 0)
                self.assertEqual(observer.events, replay_observer.events)

    def test_all_empty_branch_completes_without_http(self):
        empty_root = self.root / 'all_empty'
        source, normalized, marker = (empty_root / name for name in ('fully/merged/output.json',
                                      'fully/merged/normalized_output.json', 'fully/verification.json'))
        v.save(source, {paper: {'output': '[]', 'source_documents': []} for paper in self.order})
        v.save(normalized, {paper: {'normalized_output': [], 'source_documents': []} for paper in self.order})
        v.save(marker, {'state': 'QUEUE_FINISHED', 'complete_papers': len(self.order), 'records': 0,
                        'protected_files_changed': [], 'secret_scan_passed': True, 'stop': None})
        out = empty_root / 'prepared'
        p.prepare(source, normalized, out, verification=marker)
        v.save(out / 'reproducibility/offline_tests.json', {'status': 'PASS', 'synthetic_fixture_only': True})
        previous = v.TOP
        try:
            v.TOP = out
            def no_request(expected):
                raise AssertionError('Empty extraction must not issue HTTP')
            self.assertEqual(v.run_branch('cold_default', mock=no_request), 0)
            for stage in ('stage1', 'stage2'):
                summary = v.read(out / 'cold_default' / stage / 'summary.json')
                self.assertEqual(summary['status'], 'COMPLETE')
                self.assertEqual(summary['records'], 0)
                self.assertEqual(summary['api_calls'], 0)
        finally:
            v.TOP = previous


if __name__ == '__main__':
    unittest.main(verbosity=2)
