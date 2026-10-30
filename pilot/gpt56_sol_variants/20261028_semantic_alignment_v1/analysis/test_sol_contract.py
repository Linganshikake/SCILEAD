"""Sol adaptations: flat layout, frozen 335-row extraction and completed-stage gates."""
import importlib
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class SolContractTests(unittest.TestCase):
    def fixture(self, folder):
        r = importlib.import_module('evaluation_contract')
        root = Path(folder)
        raw = root/'inputs/output.json'
        raw.parent.mkdir()
        raw.write_bytes(r.RAW.read_bytes())
        norm, summary = r.stage_paths(root, 'partially_stage2')
        norm.parent.mkdir(parents=True)
        old_norm, old_summary = r.stage_paths(r.BASELINE, 'partially_stage2')
        norm.write_bytes(old_norm.read_bytes())
        r.save(summary, {**r.read(old_summary), 'output_path':str(norm)})
        config = r.read(r.BASELINE/'partially/config.json')
        config.update(input_path=str(raw))
        r.save(root/'partially/config.json', config)
        return r, root, norm, summary, raw

    def test_flat_completed_stage_uses_335_predictions(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r, root, norm, summary, raw = self.fixture(tmp)
            state = r.ready_stage(root, 'partially_stage2')
            self.assertEqual(state['status'], 'READY')
            self.assertEqual(state['coverage']['predictions'], 335)
            self.assertEqual(state['coverage']['official_gold_tdmrs'], 295)
            self.assertIn(str(raw.resolve()), state['input_hashes'])
            self.assertIn(str(root/'partially/config.json'), state['input_hashes'])

    def test_incomplete_summary_is_pending_even_if_output_exists(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r, root, norm, summary, raw = self.fixture(tmp)
            r.save(summary, {**r.read(summary), 'status':'RUNNING'})
            self.assertEqual(r.ready_stage(root,'partially_stage2')['status'], 'PENDING')
            summary.write_text('{', encoding='utf-8')
            self.assertEqual(r.ready_stage(root,'partially_stage2')['status'], 'PENDING')

    def test_byte_identical_local_gold_snapshots_are_accepted_and_frozen(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r, root, norm, summary, raw = self.fixture(tmp)
            gold, boards = root/'inputs/gold.json', root/'inputs/leaderboards.json'
            gold.write_bytes(r.GOLD.read_bytes())
            boards.write_bytes(r.BOARDS.read_bytes())
            path = root/'partially/config.json'
            r.save(path, {**r.read(path), 'gold_path':str(gold), 'leaderboards_path':str(boards)})
            state = r.ready_stage(root, 'partially_stage2')
            self.assertEqual(state['status'], 'READY')
            self.assertIn(str(gold), state['input_hashes'])
            self.assertIn(str(boards), state['input_hashes'])
            gold.write_bytes(gold.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError, 'Gold.*byte-identical'):
                r.ready_stage(root, 'partially_stage2')

    def test_complete_summary_missing_output_is_error(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r, root, norm, summary, raw = self.fixture(tmp)
            norm.unlink()
            with self.assertRaisesRegex(ValueError, 'COMPLETE.*missing'):
                r.ready_stage(root, 'partially_stage2')

    def test_raw_byte_change_rejected_even_with_updated_config_hash(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r, root, norm, summary, raw = self.fixture(tmp)
            raw.write_bytes(raw.read_bytes()+b'\n')
            config_path = root/'partially/config.json'
            r.save(config_path, {**r.read(config_path), 'input_sha256':r.sha(raw)})
            with self.assertRaisesRegex(ValueError, 'byte-identical'):
                r.ready_stage(root, 'partially_stage2')

    def test_row_result_change_rejected_with_valid_summary_hash(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r, root, norm, summary, raw = self.fixture(tmp)
            data = r.read(norm)
            next(iter(data.values()))['normalized_output'][0]['Result'] = '999999'
            r.save(norm, data)
            r.save(summary, {**r.read(summary), 'output_sha256':r.sha(norm)})
            with self.assertRaisesRegex(ValueError, 'Result string changed'):
                r.ready_stage(root, 'partially_stage2')

    def test_config_order_or_gold_change_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r, root, norm, summary, raw = self.fixture(tmp)
            path = root/'partially/config.json'
            config = r.read(path)
            for key, value in [('paper_order',list(reversed(config['paper_order']))),
                               ('gold_path',str(root/'wrong-gold.json')),
                               ('input_sha256','0'*64)]:
                r.save(path, {**config, key:value})
                with self.subTest(field=key), self.assertRaises(ValueError):
                    r.ready_stage(root, 'partially_stage2')

    def test_duplicate_json_keys_are_rejected(self):
        r = importlib.import_module('evaluation_contract')
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            p = Path(tmp)/'duplicate.json'
            p.write_text('{"status":"RUNNING","status":"COMPLETE"}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                r.read(p)

    def test_guard_blocks_credentials_and_rename_escape(self):
        r = importlib.import_module('evaluation_contract')
        for event, args in [('open',(str(HERE/'.env'),'r',0)),
                            ('os.rename',(str(HERE/'ok'),str(HERE.parent/'bad'),-1,-1)),
                            ('import',('variant_runtime',None,[],[],[]))]:
            with self.subTest(event=event), self.assertRaises(RuntimeError):
                sys.audit(event,*args)

    def test_seal_rejects_changed_input_and_added_artifact(self):
        r = importlib.import_module('evaluation_contract')
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            root = Path(tmp)
            folder = root/'evaluation'
            folder.mkdir()
            artifact, source = folder/'status.json', root/'summary.json'
            r.save(artifact, {})
            r.save(source, {'status':'COMPLETE'})
            seal = {'status':'COMPLETE', 'artifacts':{'status.json':r.sha(artifact)},
                    'input_hashes':{str(source):r.sha(source)}}
            r.save(folder/'verified_complete.json', seal)
            r.save(source, {'status':'RUNNING'})
            with self.assertRaisesRegex(ValueError, 'changed'):
                r.verified_evaluation(folder, root/'unused')
            r.save(folder/'unexpected.json', {})
            with self.assertRaisesRegex(ValueError, 'inventory changed'):
                r.verified_evaluation(folder, root/'unused')

    def test_completed_stage_facade_rejects_arbitrary_output_without_writes(self):
        e = importlib.import_module('evaluate_offline')
        r = importlib.import_module('evaluation_contract')
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'known flat Sol'):
                e.evaluate(r.RAW, root/'partial.json', root/'scores')
            self.assertEqual(list(root.iterdir()), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
