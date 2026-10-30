"""Offline regression tests. Never run a credential loader or a model factory."""
import inspect
import json
import tempfile
import unittest
import sys
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parents[2] / 'gpt56_sol_variants/20261024'


class Adapters(unittest.TestCase):
    def setUp(self):
        self.assertTrue((HERE / 'variant_runtime.py').is_file(), 'DeepSeek adapter not implemented')
        import variant_runtime as v
        self.v = v
        self.temp = tempfile.TemporaryDirectory(dir=HERE)
        self.root = Path(self.temp.name)

    def tearDown(self):
        if hasattr(self, 'temp'):
            self.temp.cleanup()

    def test_original_observer_paths_and_no_model_import(self):
        for cold, name in ((False, 'full43_partially'), (True, 'full43_cold_start')):
            cls = self.v.load_observer(cold)
            self.assertEqual(Path(inspect.getfile(cls.__init__)).resolve(), self.v.PILOT / name / 'engine.py')

    def test_cs_launcher_import_does_not_load_model(self):
        sys.path.insert(0, str(HERE / 'fully_cs'))
        try:
            spec = importlib.util.spec_from_file_location('owned_cs_launcher', HERE / 'fully_cs/run_cs.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual(module.RUN, HERE / 'fully_cs')
            self.assertEqual(module.SNAPSHOT, self.v.ROOT / 'assets/hf_cache/models--Lajavaness--bilingual-embedding-large/snapshots/e83179d7a66e8aed1b3015e98bb5ae234ed89598')
            self.assertNotIn('sentence_transformers', sys.modules)
            self.assertNotIn('torch', sys.modules)
            self.assertTrue(hasattr(module, 'configure_output'), 'CS launcher must support prepared --output-dir')
            try:
                module.configure_output(self.root)
                self.assertEqual(module.RUN, self.root / 'fully_cs')
                self.assertEqual(module.resource_preflight.__globals__['RUN'], self.root / 'fully_cs')
                with self.assertRaisesRegex(ValueError, 'outside variants'):
                    module.configure_output(HERE.parent)
            finally:
                if hasattr(module, 'configure_output'):
                    module.configure_output(HERE)
        finally:
            sys.path.pop(0)

    def test_cs_resource_failure_checkpoints_peak_rss_without_loading(self):
        spec = importlib.util.spec_from_file_location('cs_resource_probe', HERE / 'fully_cs/cs_common.py')
        cs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cs)
        cs.RUN = self.root
        self.v.save(self.root / 'resource_policy.json', {'minimum_physical_GiB': 2**30, 'minimum_commit_GiB': 7.5})
        with self.assertRaisesRegex(RuntimeError, 'no model load attempted'):
            cs.resource_preflight('test_probe')
        state = self.v.read(self.root / 'blocked_resources.json')
        self.assertEqual(state['status'], 'BLOCKED_RESOURCES')
        self.assertFalse(state['model_loaded'])
        self.assertGreater(state['actual']['max_rss_bytes'], 0)
        self.assertGreater(state['actual']['max_rss_GiB'], 0)

    def test_missing_and_partial_inputs_do_not_prepare(self):
        import prepare_variants as p
        self.assertIsNone(p.completed_inputs(self.root / 'raw.json', self.root / 'normalized.json', ['b', 'a']))
        self.v.save(self.root / 'raw.json', {'b': {'output': '[]', 'source_documents': []}})
        self.v.save(self.root / 'normalized.json', {'b': {'normalized_output': [], 'source_documents': []}})
        self.assertIsNone(p.completed_inputs(self.root / 'raw.json', self.root / 'normalized.json', ['b', 'a']))

    def fixture(self):
        row = {'Task': 'T', 'Dataset': 'D', 'Metric': 'M', 'Result': '1.00'}
        raw = {'a': {'output': json.dumps([row, row]), 'source_documents': ['a']},
               'b': {'output': '[]', 'source_documents': ['b']}}
        normalized = {'a': {'normalized_output': [row, row], 'source_documents': ['a']},
                      'b': {'normalized_output': [], 'source_documents': ['b']}}
        self.v.save(self.root / 'raw.json', raw)
        self.v.save(self.root / 'normalized.json', normalized)
        return raw, normalized

    def test_variable_counts_preserve_duplicate_rows_result_and_documents(self):
        import prepare_variants as p
        raw, normalized = self.fixture()
        result = p.completed_inputs(self.root / 'raw.json', self.root / 'normalized.json', ['b', 'a'])
        self.assertEqual(list(result[0]), ['b', 'a'])
        self.assertEqual(list(result[1]), ['b', 'a'])
        self.assertEqual(result[0]['a'], raw['a'])
        self.assertEqual(result[1]['a'], normalized['a'])
        self.assertEqual(sum(len(json.loads(x['output'])) for x in result[0].values()), 2)

    def test_misaligned_normalized_input_is_not_ready(self):
        import prepare_variants as p
        raw, normalized = self.fixture()
        normalized['a']['normalized_output'].pop()
        self.v.save(self.root / 'normalized.json', normalized)
        self.assertIsNone(p.completed_inputs(self.root / 'raw.json', self.root / 'normalized.json', ['b', 'a']))

    def test_numeric_results_are_rejected_without_repair(self):
        import prepare_variants as p
        raw, normalized = self.fixture()
        rows = json.loads(raw['a']['output'])
        rows[0]['Result'] = 1.0
        raw['a']['output'] = json.dumps(rows)
        self.v.save(self.root / 'raw.json', raw)
        with self.assertRaisesRegex(ValueError, 'string'):
            p.completed_inputs(self.root / 'raw.json', self.root / 'normalized.json', ['b', 'a'])

    def test_frozen_orders_use_string_seeds(self):
        import prepare_variants as p
        order = self.v.read(REFERENCE / 'partially/paper_order.json')['papers']
        for name, seed in (('partially', None), ('cold_default', None), ('cold_0', '0'), ('cold_42', '42')):
            self.assertEqual(p.paper_order(order, seed), self.v.read(REFERENCE / name / 'paper_order.json')['papers'])

    def test_preparation_waits_for_main_completion_marker(self):
        import prepare_variants as p
        raw, normalized = self.fixture()
        # Even complete files cannot publish a prepared run before main's marker.
        reference = self.root / 'reference'
        self.v.save(reference / 'partially/paper_order.json', {'papers': ['b', 'a']})
        result = p.prepare(self.root / 'raw.json', self.root / 'normalized.json',
                           self.root / 'prepared', reference, verification=self.root / 'verification.json')
        self.assertIsNone(result)
        self.assertFalse((self.root / 'prepared/experiment_manifest.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
