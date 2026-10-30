"""Offline regression tests; fixtures and temporary files stay under reporting."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import copy
import statistics

HERE = Path(__file__).resolve().parent


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf8')


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((HERE / 'audit_and_report.py').exists(), 'offline audit implementation missing')
        spec = importlib.util.spec_from_file_location('audit', HERE / 'audit_and_report.py')
        self.a = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.a)
        self.temp = tempfile.TemporaryDirectory(dir=HERE, prefix='test_fixture_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prompts = {k: k for k in ('normalization-system-prompt', 'masked-normalization-system-prompt', 'leaderboard-normalization-system-prompt')}
        self.folder = self.root / 'partially/stage1/api_calls/0001'
        self.expected = {'paper': 'p', 'record': 1, 'field': 'Task', 'original': 'X', 'candidate_serialized': "{'X'}"}
        self.expected['messages'] = [{'role': 'system', 'content': self.prompts['masked-normalization-system-prompt']}, {'role': 'user', 'content': "\n\nItem list: {'X'}\n\nInput: X\n\nAnswer: "}]
        self.request = dict(self.a.GENERATION, messages=self.expected['messages'])
        put(self.folder / 'expected.json', self.expected)
        put(self.folder / 'request.json', self.request)

    def scan(self):
        audit = self.a.Audit()
        result = self.a.audit_calls(self.folder.parent, 'partially', 'stage1', self.prompts, audit)
        return result, audit

    def response(self, folder=None):
        folder = folder or self.folder
        put(folder / 'request.json', self.request)
        response = {'model': 'gpt-5.6-sol', 'choices': [{'finish_reason': 'stop', 'message': {'content': 'X'}}], 'usage': {'prompt_tokens': 7, 'completion_tokens': 3, 'total_tokens': 10}}
        put(folder / 'response.json', response)
        put(folder / 'state.json', {'status': 'RECEIVED', 'post_calls': 1, 'automatic_retries': 0, 'http_status': 200, 'usage': response['usage'], 'elapsed_seconds': 2, 'started_utc': '2026-10-28T16:01:00+00:00'})
        put(self.folder / 'accepted.json', {'status': 'COMPLETE', 'response_relative_path': (folder / 'response.json').relative_to(self.folder).as_posix(), 'response_sha256': self.a.sha(folder / 'response.json'), 'model': 'gpt-5.6-sol', 'finish_reason': 'stop', 'raw_answer': 'X'})

    def test_unknown_attempt_is_counted_without_stage_summary(self):
        put(self.folder / 'state.json', {'status': 'UNKNOWN_TRANSPORT_ERROR', 'post_calls': 1, 'automatic_retries': 0})
        result, audit = self.scan()
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['logical_accepted'], 0)
        self.assertIsNone(result['rows'][0]['total_tokens'])
        self.assertEqual(self.a.usage_summary(result['rows'], [result])['unknown_usage_attempts'], 1)

    def test_request_without_state_is_unknown_send_not_zero(self):
        result, audit = self.scan()
        usage = self.a.usage_summary(result['rows'], [result])
        self.assertEqual(usage['attempt_records'], 1)
        self.assertEqual(usage['unknown_send_attempts'], 1)
        self.assertIsNone(usage['actual_model_requests'])

    def test_failed_original_and_authorized_retry_both_count(self):
        put(self.folder / 'state.json', {'status': 'RECEIVED', 'http_status': 524, 'post_calls': 1, 'automatic_retries': 0})
        put(self.folder / 'retry_authorization.json', {'max_additional_attempts': 1, 'original_request_sha256': self.a.sha(self.folder / 'request.json'), 'original_http_status': 524})
        self.response(self.folder / 'retry_1')
        result, audit = self.scan()
        self.assertEqual(result['logical_accepted'], 1)
        usage = self.a.usage_summary(result['rows'], [result])
        self.assertEqual(usage['actual_model_requests'], 2)
        self.assertEqual(usage['unknown_usage_attempts'], 1)
        self.assertEqual(usage['totals']['total_tokens'], 10)
        self.assertEqual(usage['authorized_additional_attempts'], 1)
        self.assertEqual(audit.errors, [])

    def test_changed_parameters_and_accepted_hash_fail(self):
        self.response()
        put(self.folder / 'request.json', dict(self.request, reasoning_effort='high'))
        acc = json.loads((self.folder / 'accepted.json').read_text())
        acc['response_sha256'] = '0' * 64
        put(self.folder / 'accepted.json', acc)
        result, audit = self.scan()
        self.assertEqual(result['logical_accepted'], 0)
        self.assertTrue(any('generation' in x['check'] for x in audit.errors))
        self.assertTrue(any('accepted' in x['check'] for x in audit.errors))

    def test_accepted_reference_cannot_escape(self):
        self.response()
        acc = json.loads((self.folder / 'accepted.json').read_text())
        acc['response_relative_path'] = '../response.json'
        put(self.folder / 'accepted.json', acc)
        result, audit = self.scan()
        self.assertEqual(result['logical_accepted'], 0)
        self.assertTrue(audit.errors)

    def test_unknown_retry_without_authorization_never_passes(self):
        put(self.folder / 'state.json', {'status': 'UNKNOWN_TRANSPORT_ERROR', 'post_calls': 1, 'automatic_retries': 0})
        self.response(self.folder / 'retry_1')
        result, audit = self.scan()
        self.assertTrue(any('authorization' in x['check'] for x in audit.errors))
        self.assertEqual(len(result['rows']), 2)

    def test_authorized_unknown_retry_keeps_both_attempts(self):
        put(self.folder / 'state.json', {'status': 'UNKNOWN_TRANSPORT_ERROR', 'error_type': 'RemoteProtocolError', 'post_calls': 1, 'automatic_retries': 0})
        helper = self.root / 'authorized_resume.py'
        helper.write_text('# synthetic helper, never executed\n', encoding='utf8')
        put(self.folder / 'manual_recovery_authorization.json', {'authorized': True, 'max_additional_attempts': 1, 'request_sha256': self.a.sha(self.folder / 'request.json'), 'original_state_sha256': self.a.sha(self.folder / 'state.json'), 'helper_sha256': self.a.sha(helper)})
        self.response(self.folder / 'retry_1')
        result, audit = self.scan()
        self.assertEqual(audit.errors, [])
        self.assertEqual(result['logical_accepted'], 1)
        usage = self.a.usage_summary(result['rows'], [result])
        self.assertEqual(usage['actual_model_requests'], 2)
        self.assertEqual(usage['authorized_additional_attempts'], 1)
        self.assertEqual(usage['unknown_usage_attempts'], 1)

    def test_actual_manual_authorization_without_helper_pin(self):
        put(self.folder / 'state.json', {'status': 'UNKNOWN_TRANSPORT_ERROR', 'error_type': 'RemoteProtocolError', 'post_calls': 1, 'automatic_retries': 0})
        (self.root / 'authorized_resume.py').write_text('# test only\n', encoding='utf8')
        put(self.folder / 'manual_recovery_authorization.json', {'authorized': True, 'max_additional_attempts': 1, 'request_sha256': self.a.sha(self.folder / 'request.json'), 'original_state_sha256': self.a.sha(self.folder / 'state.json')})
        self.response(self.folder / 'retry_1')
        self.assertFalse((self.folder / 'retry_1/accepted.json').exists())
        result, audit = self.scan()
        self.assertEqual(audit.errors, [])
        self.assertEqual(result['logical_accepted'], 1)
        self.assertFalse(result['rows'][1]['recovery_helper_hash_pinned_in_authorization'])
        usage = self.a.usage_summary(result['rows'], [result])
        self.assertEqual(usage['physical_http200_attempts'], 1)
        self.assertEqual(usage['physical_valid_model_stop_responses'], 1)
        self.assertEqual(usage['logical_accepted'], 1)

    def test_regression_example_uses_actual_changed_event(self):
        import report_render
        before = {'Task': 'T', 'Dataset': 'D', 'Metric': 'M', 'Result': '1'}
        after = dict(before, Dataset='Other D')
        changes = []
        for i in range(3):
            changes.append({'paper': 'p' + str(i), 'record': 1, 'field': 'TDM', 'raw_extraction': before,
                            'before': before, 'after': after, 'baseline_call': None, 'variant_call': None,
                            'baseline_event': {'path': 'synthetic_old', 'sha256': 'fixture'}, 'variant_event': {'path': 'synthetic_new', 'sha256': 'fixture'}})
        comparison = {'stage2_paper_changes': [{'case': 'partially_stage2', 'metric': 'TDMR Exact Match',
                       'top_regressions': [{'paper_id': 'p0', 'baseline_F1': 0.5, 'variant_F1': 0, 'delta_F1': -0.5}],
                       'top_improvements': [{'paper_id': 'p1', 'baseline_F1': 0, 'variant_F1': 0.5, 'delta_F1': 0.5}, {'paper_id': 'p2', 'baseline_F1': 0, 'variant_F1': 0.5, 'delta_F1': 0.5}]}]}
        examples = report_render.select_examples(comparison, {'partially_stage2': {'changes': changes}}, {c['paper']: {'TDMs': [before]} for c in changes}, self.root)
        self.assertEqual(len(examples), 3)
        self.assertEqual(examples[0]['direction'], 'regression')
        self.assertTrue(examples[0]['before_exact_gold_tdm'])
        self.assertFalse(examples[0]['after_exact_gold_tdm'])

    def test_reordered_records_or_changed_source_fail(self):
        raw = {'p': {'output': json.dumps([{'Result': '1'}, {'Result': '2'}]), 'source_documents': ['evidence']}}
        output = {'p': {'normalized_output': [{'Result': '2'}, {'Result': '1'}], 'source_documents': ['changed']}}
        audit = self.a.Audit()
        self.a.check_output(output, raw, ['p'], audit, 'stage')
        self.assertEqual(len(audit.errors), 2)

    def test_report_pending_and_timezone_use_actual_date(self):
        stamps = self.a.timestamps('2026-10-28T16:01:00+00:00')
        self.assertTrue(stamps['checked_shanghai'].startswith('2026-10-29T00:01'))
        self.assertEqual(self.a.final_status('PASS', 'PENDING'), 'PENDING')
        self.assertEqual(self.a.final_status('INCOMPLETE', 'COMPLETE'), 'INCOMPLETE')

    def test_empty_comparison_marked_complete_is_rejected(self):
        p = self.root / 'comparison.json'
        put(p, {'status': 'COMPLETE', 'local_rows': [], 'paired_differences': [], 'cold_three_order_summaries': [], 'stage2_paper_changes': []})
        status, _, issues = self.a.load_comparison(p, self.root, self.root, {})
        self.assertEqual(status, 'FAILED')
        self.assertTrue(issues)

    def test_output_outside_reporting_rejected(self):
        with self.assertRaises(ValueError):
            self.a.resolve_output(HERE.parent / 'analysis')

    def test_nested_billing_usage_is_not_added(self):
        self.response()
        response = json.loads((self.folder / 'response.json').read_text())
        response['usage']['billing_usage'] = {'openai_usage': {'total_tokens': 10000}}
        put(self.folder / 'response.json', response)
        state = json.loads((self.folder / 'state.json').read_text())
        state['usage'] = response['usage']
        put(self.folder / 'state.json', state)
        acc = json.loads((self.folder / 'accepted.json').read_text())
        acc['response_sha256'] = self.a.sha(self.folder / 'response.json')
        put(self.folder / 'accepted.json', acc)
        result, audit = self.scan()
        self.assertEqual(self.a.usage_summary(result['rows'], [result])['totals']['total_tokens'], 10)

    def test_stream_numeric_zero_is_not_boolean_false(self):
        put(self.folder / 'request.json', dict(self.request, stream=0))
        result, audit = self.scan()
        self.assertTrue(any('generation' in e['check'] for e in audit.errors))

    def test_quota_rejection_without_usage_remains_unaccepted(self):
        put(self.folder / 'state.json', {'status': 'HTTP_ERROR', 'http_status': 403, 'post_calls': 1, 'automatic_retries': 0})
        put(self.folder / 'response.json', {'error': {'code': 'insufficient_user_quota'}})
        result, audit = self.scan()
        self.assertEqual(result['logical_accepted'], 0)
        self.assertEqual(result['rows'][0]['attempt_outcome'], 'rejected_http')
        self.assertEqual(result['rows'][0]['error_code'], 'insufficient_user_quota')
        self.assertIsNone(result['rows'][0]['total_tokens'])
        self.assertEqual(audit.errors, [])

    def test_complete_summary_without_events_fails(self):
        directory = self.root / 'partially/stage1'
        raw = {'p': {'output': json.dumps([{'Task': 'X', 'Result': '1'}]), 'source_documents': []}}
        output = {'p': {'normalized_output': [{'Task': 'X', 'Result': '1'}], 'source_documents': []}}
        audit = self.a.Audit()
        self.a.inspect_events(directory, self.root / 'baseline', 'stage1', raw, ['p'], output, None, {'accepted': {}, 'expected': {}}, audit, True)
        self.assertTrue(any(x['check'] == 'all_record_events_present' for x in audit.errors))

    def comparison_fixture(self):
        data = {'status': 'COMPLETE', 'scope': {'papers': 43, 'predictions': 335, 'gold_annotations': 295, 'gold_boards': 27},
                'local_rows': [], 'paired_differences': [], 'cold_three_order_summaries': [], 'stage2_paper_changes': []}
        for branch in self.a.BRANCHES:
            for stage in self.a.STAGES:
                case = branch + '_' + stage
                for model in self.a.MODELS:
                    root = self.root / model
                    path = root / branch / stage / self.a.OUTPUTS[stage]
                    put(path, {'synthetic_fixture_only': case})
                    row = {'model': model, 'case': case, 'status': 'COMPLETE', 'role': 'primary' if stage == 'stage2' else 'diagnostic',
                           'normalized': str(path), 'input_sha256': self.a.sha(path),
                           'coverage': {'status': 'COMPLETE', 'evaluated_papers': 43, 'tuple_macro_denominator': 43, 'predictions': 335, 'evaluated_gold_tdmrs': 295, 'gold_leaderboards': 27},
                           'tuple': {m: {k: 0.5 for k in self.a.PRF} for m in self.a.METRICS}, 'leaderboard': {k: 0.5 for k in self.a.LB}}
                    row['per_paper'] = {'p' + str(i): copy.deepcopy(row['tuple']) for i in range(43)}
                    data['local_rows'].append(row)
                data['paired_differences'].append({'case': case, 'metrics': {k: 0.0 for k in self.a.SCALARS}})
                if stage == 'stage2':
                    for metric in self.a.METRICS[-2:]:
                        data['stage2_paper_changes'].append({'case': case, 'metric': metric, 'paired_papers': 43, 'improved': 0, 'regressed': 0, 'unchanged': 43, 'top_improvements': [], 'top_regressions': []})
        for stage in self.a.STAGES:
            for model in (*self.a.MODELS, 'paired_delta'):
                data['cold_three_order_summaries'].append({'model': model, 'stage': stage, 'status': 'COMPLETE', 'orders_present': list(self.a.BRANCHES[1:]), 'metrics': {k: {'n': 3, 'mean': 0 if model == 'paired_delta' else 0.5, 'sample_sd': 0.0} for k in self.a.SCALARS}})
        path = self.root / 'comparison.json'
        put(path, data)
        return path, data

    def test_complete_comparison_contract_and_stale_hash(self):
        path, data = self.comparison_fixture()
        status, comparison, issues = self.a.load_comparison(path, self.root / 'prompt_improvement_variant', self.root / 'baseline', {})
        self.assertEqual((status, issues), ('COMPLETE', []))
        data['local_rows'][0]['input_sha256'] = '0' * 64
        put(path, data)
        self.assertEqual(self.a.load_comparison(path, self.root / 'prompt_improvement_variant', self.root / 'baseline', {})[0], 'FAILED')

    def test_full_chinese_report_renders_all_metrics(self):
        import report_render
        path, data = self.comparison_fixture()
        verification = {'status': 'PASS', 'report_status': 'COMPLETE', 'comparison_status': 'COMPLETE', **self.a.timestamps(),
                        'prompt_sha256': 'fixture', 'protected_file_count': 83, 'protected_changes': [], 'protected_changes_during_audit': [], 'stage_checks': {},
                        'issues': [], 'comparison_issues': [], 'comparison_path': str(path), 'comparison_sha256': self.a.sha(path)}
        usage = self.a.usage_summary([], [])
        usage['branches'] = {b: self.a.usage_summary([], []) for b in self.a.BRANCHES}
        events = {b + '_stage2': {'changes': []} for b in self.a.BRANCHES}
        report, examples = report_render.render(verification, usage, data, events, {}, self.root, self.root)
        self.assertIn('第二阶段：主要结果', report)
        self.assertIn('第一阶段：诊断结果', report)
        for metric in self.a.METRICS:
            self.assertIn(metric, report)
        self.assertEqual(examples, [])
        self.assertNotIn('2026-10-28（', report)

    def test_offline_guard_blocks_network_credentials_and_external_writes(self):
        from offline_guard import Guard
        guard = Guard()
        for event, args in [('socket.connect', ()), ('subprocess.Popen', ()), ('open', (str(HERE.parent / '.env'), 'r', 0)), ('open', (str(HERE.parent / 'illegal.txt'), 'w', 1))]:
            with self.assertRaises(PermissionError):
                guard(event, args)
        self.assertEqual(len(guard.blocked), 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
