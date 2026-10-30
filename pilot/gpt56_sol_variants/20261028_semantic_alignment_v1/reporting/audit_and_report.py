"""Offline, read-only source audit. Only reporting artifacts are written.

No runtime/evaluator imports, credentials, subprocesses, network or model calls.
Exit codes: 0 final complete; 2 incomplete/pending; 1 audit/schema failure.
"""
import argparse
import collections
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT.parent / '20261024'
DEEPSEEK = ROOT.parents[1] / 'deepseek_v41_flash/20261028_semantic_alignment_v1'
BRANCHES = ('partially', 'cold_default', 'cold_0', 'cold_42')
STAGES = ('stage1', 'stage2')
MODELS = ('baseline', 'prompt_improvement_variant')
GENERATION = {'model': 'gpt-5.6-sol', 'reasoning_effort': 'medium', 'max_completion_tokens': 32768, 'stream': False}
METRICS = ('Task IIM', 'Dataset IIM', 'Metric IIM', 'Result IIM', 'TDM Exact Match', 'TDMR Exact Match')
PRF = ('Precision', 'Recall', 'F1')
LB = ('LR_exact_tdm_hit', 'LR_nonempty_finite_result', 'PC_official', 'RC_official', 'RBO_official_value_rankings', 'AO_paper_id_macro_all_gold_boards')
SCALARS = tuple(m + '/' + k for m in METRICS for k in PRF) + LB
OUTPUTS = {'stage1': 'normalized_output.json', 'stage2': 'leaderboard_normalized_output.json'}
TOKENS = ('prompt_tokens', 'completion_tokens', 'total_tokens', 'reasoning_tokens')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False).encode()).hexdigest()


def generation_matches(value):
    return isinstance(value, dict) and value == GENERATION and all(type(value[k]) is type(v) for k, v in GENERATION.items())


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON key: ' + key)
        out[key] = value
    return out


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_pairs)


def timestamps(value=None):
    now = datetime.fromisoformat(value) if value else datetime.now(timezone.utc)
    return {'checked_utc': now.astimezone(timezone.utc).isoformat(),
            'checked_shanghai': now.astimezone(timezone(timedelta(hours=8), 'Asia/Shanghai')).isoformat(),
            'local_timezone': 'Asia/Shanghai'}


class Audit:
    def __init__(self):
        self.errors = []
        self.pending = []
        self.sources = {}

    def check(self, condition, check, path):
        if not condition:
            self.errors.append({'check': check, 'path': str(path)})
        return bool(condition)

    def wait(self, check, path):
        self.pending.append({'check': check, 'path': str(path)})

    def get(self, path, required=False):
        path = Path(path)
        if not path.exists():
            if required:
                self.check(False, 'missing_required_file', path)
            return None
        try:
            data = path.read_bytes()
            self.sources[str(path)] = hashlib.sha256(data).hexdigest()
            return json.loads(data.decode('utf-8-sig'), object_pairs_hook=unique_pairs)
        except (ValueError, OSError, UnicodeError) as exc:
            self.check(False, 'unreadable_json:' + type(exc).__name__, path)
            return None


def valid_response(response):
    if not isinstance(response, dict) or response.get('model') != GENERATION['model']:
        return False
    choices = response.get('choices') or []
    if not choices or not isinstance(choices[0], dict):
        return False
    content = choices[0].get('message', {}).get('content')
    return choices[0].get('finish_reason') == 'stop' and isinstance(content, str) and bool(content.strip())


def accepted_response(folder, audit):
    acc = audit.get(folder / 'accepted.json')
    if acc is None:
        return None
    start = len(audit.errors)
    relative = acc.get('response_relative_path', 'response.json')
    if not audit.check(isinstance(relative, str) and bool(re.fullmatch(r'(?:retry_[1-9][0-9]*/)*response\.json', relative)), 'accepted_response_path', folder):
        return None
    path = folder / relative
    if not audit.check(path.resolve().is_relative_to(folder.resolve()), 'accepted_response_containment', path):
        return None
    response = audit.get(path, required=True)
    state = audit.get(path.parent / 'state.json', required=True) or {}
    audit.check(path.is_file() and sha(path) == acc.get('response_sha256'), 'accepted_response_hash', path)
    audit.check(valid_response(response) and state.get('http_status') == 200, 'accepted_response_http200_model_stop_content', path)
    if valid_response(response):
        audit.check(acc.get('status') == 'COMPLETE' and acc.get('model') == GENERATION['model'] and acc.get('finish_reason') == 'stop' and acc.get('raw_answer') == response['choices'][0]['message']['content'], 'accepted_metadata', folder)
    if len(audit.errors) != start:
        return None
    return {'path': str(path), 'sha256': sha(path), 'content': response['choices'][0]['message']['content']}


def audit_calls(api_dir, branch, stage, prompts, audit):
    rows, accepted, expected_by_call = [], {}, {}
    folders = sorted(p for p in api_dir.iterdir() if p.is_dir()) if api_dir.exists() else []
    for folder in folders:
        if not audit.check(folder.name.isdigit(), 'logical_call_directory_name', folder):
            continue
        number = int(folder.name)
        exp = audit.get(folder / 'expected.json', required=True) or {}
        expected_by_call[number] = exp
        accepted_item = accepted_response(folder, audit)
        parent_request = audit.get(folder / 'request.json')
        paths = {p.parent for name in ('request.json', 'state.json', 'response.json', 'attempt.lock') for p in folder.rglob(name)}
        for attempt in sorted(paths):
            begin = len(audit.errors)
            req = audit.get(attempt / 'request.json', required=True)
            state = audit.get(attempt / 'state.json') or {}
            response = audit.get(attempt / 'response.json')
            relative = attempt.relative_to(folder).as_posix()
            is_retry = attempt != folder
            helper_hash = None
            helper_pinned = None
            if is_retry:
                manual_path = attempt.parent / 'manual_recovery_authorization.json'
                auth_path = manual_path if manual_path.exists() else attempt.parent / 'retry_authorization.json'
                auth = audit.get(auth_path) or {}
                original_state = audit.get(attempt.parent / 'state.json') or {}
                original_request = attempt.parent / 'request.json'
                if auth_path == manual_path:
                    experiment_root = folder.parents[3]
                    helper = Path(auth.get('helper_path', experiment_root / 'authorized_resume.py'))
                    helper_hash = sha(helper) if helper.is_file() and helper.resolve().is_relative_to(experiment_root.resolve()) else None
                    helper_pinned = 'helper_sha256' in auth
                    helper_tests_path = experiment_root / 'recovery_offline_tests.json'
                    if helper_tests_path.exists():
                        helper_tests = audit.get(helper_tests_path, required=True) or {}
                        audit.check(helper_tests.get('status') == 'PASS' and helper_tests.get('files', {}).get(helper.name) == helper_hash, 'recovery_helper_matches_tested_bytes', helper_tests_path)
                    authorized = (attempt == folder / 'retry_1' and auth.get('authorized') is True and auth.get('max_additional_attempts') == 1
                                  and original_request.is_file() and auth.get('request_sha256') == sha(original_request)
                                  and auth.get('original_state_sha256') == sha(attempt.parent / 'state.json')
                                  and original_state.get('status') == 'UNKNOWN_TRANSPORT_ERROR' and original_state.get('post_calls') == 1
                                  and original_state.get('automatic_retries') == 0
                                  and helper.resolve().is_relative_to(experiment_root.resolve()) and helper.is_file()
                                  and (not helper_pinned or auth['helper_sha256'] == helper_hash))
                else:
                    authorized = (attempt.name == 'retry_1' and auth.get('max_additional_attempts') == 1
                                  and original_request.is_file() and auth.get('original_request_sha256') == sha(original_request)
                                  and auth.get('original_http_status') == original_state.get('http_status')
                                  and original_state.get('http_status') in (524, 403))
                if auth_path != manual_path and original_state.get('http_status') == 403:
                    old_response = audit.get(attempt.parent / 'response.json') or {}
                    authorized = authorized and auth.get('balance_replenished_confirmed') is True and auth.get('original_error_code') == 'insufficient_user_quota' and old_response.get('error', {}).get('code') == 'insufficient_user_quota'
                if 'original_state_sha256' in auth:
                    authorized = authorized and auth['original_state_sha256'] == sha(attempt.parent / 'state.json')
                if auth.get('earliest_retry_utc') and state.get('started_utc'):
                    authorized = authorized and datetime.fromisoformat(state['started_utc']) >= datetime.fromisoformat(auth['earliest_retry_utc'])
                audit.check(authorized, 'retry_authorization', auth_path)
                audit.check(req == parent_request, 'retry_identical_request', attempt)
            else:
                authorized = False
            if isinstance(req, dict):
                audit.check(generation_matches({k: v for k, v in req.items() if k != 'messages'}), 'actual_request_generation', attempt)
                key = 'leaderboard-normalization-system-prompt' if stage == 'stage2' else ('masked-normalization-system-prompt' if branch.startswith('cold_') or exp.get('field') in ('Task', 'Dataset') else 'normalization-system-prompt')
                messages = [{'role': 'system', 'content': prompts.get(key)}, {'role': 'user', 'content': '\n\nItem list: ' + str(exp.get('candidate_serialized', '')) + '\n\nInput: ' + str(exp.get('original', '')) + '\n\nAnswer: '}]
                audit.check(req.get('messages') == exp.get('messages') == messages, 'actual_request_expected_and_template', attempt)
                for name, value in [('candidate_sha256', exp.get('candidate_serialized')), ('prompt_sha256', exp.get('messages'))]:
                    if name in exp:
                        audit.check(exp[name] == digest(value), 'expected_' + name, folder)
            posts = state.get('post_calls')
            audit.check(posts in (None, 1), 'one_post_per_attempt', attempt)
            audit.check(state.get('automatic_retries') in (None, 0), 'no_automatic_retries', attempt)
            if state.get('http_status') == 200 and response is not None:
                audit.check(response.get('model') == GENERATION['model'], 'actual_response_model', attempt)
            if response is not None and response.get('usage') is not None and state.get('usage') is not None:
                audit.check(response['usage'] == state['usage'], 'state_response_usage_equality', attempt)
            # Only top-level usage. billing_usage repeats these fields and is not added.
            usage = response.get('usage') if isinstance(response, dict) and isinstance(response.get('usage'), dict) else state.get('usage')
            usage = usage if isinstance(usage, dict) else {}
            values = {k: usage.get(k) for k in TOKENS[:3]}
            values['reasoning_tokens'] = (usage.get('completion_tokens_details') or {}).get('reasoning_tokens')
            for key, value in values.items():
                audit.check(value is None or (type(value) is int and value >= 0), 'usage_nonnegative_integer:' + key, attempt)
            known = all(values[k] is not None for k in TOKENS[:3])
            choice = (response.get('choices') or [{}])[0] if isinstance(response, dict) else {}
            http = state.get('http_status')
            outcome = ('received_http200' if http == 200 else 'rejected_http' if isinstance(http, int) and 400 <= http < 500
                       else 'gateway_error_completion_unknown' if isinstance(http, int) and http >= 500 else 'transport_or_send_unknown')
            row = {'branch': branch, 'stage': stage, 'call': number, 'attempt': relative if is_retry else 'original',
                   'paper_id': exp.get('paper'), 'record': exp.get('record'), 'field': exp.get('field'),
                   'status': state.get('status', 'UNKNOWN_NO_STATE'), 'http_status': state.get('http_status'), 'error_type': state.get('error_type'),
                   'attempt_outcome': outcome, 'error_code': (response.get('error') or {}).get('code') if isinstance(response, dict) and isinstance(response.get('error'), dict) else None,
                   'post_calls': posts, 'automatic_retries': state.get('automatic_retries'), 'retry_authorized': authorized,
                   'recovery_helper_sha256': helper_hash, 'recovery_helper_hash_pinned_in_authorization': helper_pinned,
                   'request_model': req.get('model') if req else None, 'response_model': response.get('model') if response else None,
                   'finish_reason': choice.get('finish_reason'), 'usage_known': known, **values,
                   'valid_model_stop_response': valid_response(response),
                   'seconds': state.get('elapsed_seconds'), 'started_utc': state.get('started_utc'),
                   'request_sha256': sha(attempt / 'request.json') if (attempt / 'request.json').exists() else None,
                   'response_sha256': sha(attempt / 'response.json') if (attempt / 'response.json').exists() else None,
                   'request_verified': len(audit.errors) == begin,
                   'accepted_response': bool(accepted_item and Path(accepted_item['path']).parent == attempt), 'path': str(attempt)}
            rows.append(row)
        if accepted_item and all(r['request_verified'] for r in rows if r['call'] == number):
            accepted[number] = accepted_item
        if not paths:
            audit.wait('expected_saved_no_attempt_yet', folder)
    return {'rows': rows, 'logical_requests': len(folders), 'logical_accepted': len(accepted), 'accepted': accepted, 'expected': expected_by_call}


def usage_summary(rows, calls):
    known_posts = sum(r['post_calls'] or 0 for r in rows)
    unknown_send = sum(r['post_calls'] is None for r in rows)
    result = {'attempt_records': len(rows), 'known_post_calls': known_posts, 'unknown_send_attempts': unknown_send,
              'actual_model_requests': None if unknown_send else known_posts,
              'logical_normalization_requests': sum(c['logical_requests'] for c in calls),
              'logical_accepted': sum(c['logical_accepted'] for c in calls),
              'physical_http200_attempts': sum(r['http_status'] == 200 for r in rows),
              'physical_valid_model_stop_responses': sum(r['valid_model_stop_response'] and r['http_status'] == 200 for r in rows),
              'retry_attempt_records': sum(r['attempt'] != 'original' for r in rows),
              'authorized_additional_attempts': sum(r['retry_authorized'] for r in rows),
              'automatic_retries': None if any(r['automatic_retries'] is None for r in rows) else sum(r['automatic_retries'] for r in rows),
              'unknown_usage_attempts': sum(not r['usage_known'] for r in rows),
              'totals': {k: sum(r[k] for r in rows if r[k] is not None) for k in TOKENS},
              'known_usage_fields': {k: sum(r[k] is not None for r in rows) for k in TOKENS},
              'http_counts': dict(collections.Counter(str(r['http_status']) for r in rows)),
              'status_counts': dict(collections.Counter(r['status'] for r in rows)),
              'attempt_outcomes': dict(collections.Counter(r['attempt_outcome'] for r in rows)),
              'unknown_usage_http_counts': dict(collections.Counter(str(r['http_status']) for r in rows if not r['usage_known'])),
              'token_totals_are_known_usage_only': True, 'billing_usage_nested_fields_excluded': True,
              'audit_generated_api_requests': 0, 'new_extraction_requests': 0}
    intervals = [(datetime.fromisoformat(r['started_utc']), r['seconds']) for r in rows if r['started_utc'] and isinstance(r['seconds'], (int, float))]
    if intervals:
        first = min(t for t, _ in intervals)
        last = max(t + timedelta(seconds=s) for t, s in intervals)
        result.update(first_request_utc=first.isoformat(), last_observed_attempt_end_utc=last.isoformat(), observed_wall_seconds=(last - first).total_seconds())
    return result


def check_output(output, raw, order, audit, path):
    audit.check(list(output) == order and set(output) == set(raw), 'paper_order_and_ids', path)
    for paper in raw:
        original = json.loads(raw[paper]['output'])
        new = output.get(paper, {})
        records = new.get('normalized_output', [])
        audit.check(new.get('source_documents') == raw[paper]['source_documents'], 'source_documents_unchanged:' + paper, path)
        audit.check(len(records) == len(original) and [r.get('Result') for r in records] == [r['Result'] for r in original], 'record_count_order_and_Result:' + paper, path)


def inspect_events(directory, baseline_dir, stage, raw, order, output, stage1_output, calls, audit, complete):
    files = sorted((directory / 'events').glob('*.json'))
    events = [(p, audit.get(p, required=True)) for p in files]
    events = [(p, e) for p, e in events if isinstance(e, dict)]
    positions = [(paper, i, field) for paper in order for i, record in enumerate(json.loads(raw[paper]['output']), 1) for field in (record if stage == 'stage1' else ['TDM'])]
    observed = [(e.get('paper'), e.get('record'), e.get('field', 'TDM')) for _, e in events]
    audit.check(observed == positions[:len(observed)], 'event_record_order_prefix', directory)
    if complete:
        audit.check(observed == positions, 'all_record_events_present', directory)
        audit.check(sorted(e['call'] for _, e in events if 'call' in e) == sorted(calls['accepted']), 'accepted_calls_consumed_once', directory)
    old_events = {}
    for path in sorted((baseline_dir / 'events').glob('*.json')):
        event = audit.get(path, required=True)
        if event:
            old_events[event['paper'], event['record'], event.get('field', 'TDM')] = (path, event)
    changes = []
    for index, (path, event) in enumerate(events, 1):
        paper, record, field = event.get('paper'), event.get('record'), event.get('field', 'TDM')
        audit.check(event.get('event') == index, 'event_sequence_number', path)
        if (paper, record, field) not in positions:
            continue
        original = json.loads(raw[paper]['output'])[record - 1]
        if stage == 'stage1':
            audit.check(event.get('original') == original[field], 'event_original_record_identity', path)
        elif stage1_output:
            audit.check(event.get('original') == stage1_output[paper]['normalized_output'][record - 1], 'stage2_input_stage1_record_identity', path)
        if output:
            expected_normalized = output[paper]['normalized_output'][record - 1]
            audit.check(event.get('normalized') == (expected_normalized[field] if stage == 'stage1' else expected_normalized), 'event_normalized_output_identity', path)
        if 'call' in event:
            call = event['call']
            accepted = calls['accepted'].get(call)
            exp = calls['expected'].get(call, {})
            if not complete and not accepted:
                audit.wait('event_beyond_call_snapshot_rerun_when_stable', path)
                continue
            audit.check(bool(accepted) and event.get('raw_answer') == accepted['content'], 'event_accepted_response_content', path)
            audit.check((exp.get('paper'), exp.get('record'), exp.get('field')) == (paper, record, field), 'event_expected_position', path)
            serial = event.get('labels_before', {}).get(field, {}).get('serialized') if stage == 'stage1' else event.get('candidate_serialized')
            input_text = event.get('original') if stage == 'stage1' else '(' + ', '.join(str(event['original'][k]) for k in ('Task', 'Dataset', 'Metric')) + ')'
            audit.check(exp.get('candidate_serialized') == serial and exp.get('original') == input_text, 'event_expected_input_and_candidates', path)
        old = old_events.get((paper, record, field))
        if old and event.get('normalized') != old[1].get('normalized'):
            changes.append({'paper': paper, 'record': record, 'field': field, 'raw_extraction': original,
                            'before': old[1].get('normalized'), 'after': event.get('normalized'),
                            'before_branch': old[1].get('branch'), 'after_branch': event.get('branch'),
                            'baseline_event': {'path': str(old[0]), 'sha256': sha(old[0])},
                            'variant_event': {'path': str(path), 'sha256': sha(path)},
                            'baseline_call': old[1].get('call'), 'variant_call': event.get('call'),
                            'variant_accepted_response': calls['accepted'].get(event.get('call'))})
    return {'before_events': dict(collections.Counter(e['branch'] for _, e in old_events.values())),
            'after_events': dict(collections.Counter(e['branch'] for _, e in events)),
            'observed_event_count': len(events), 'expected_event_count': len(positions),
            'status': 'COMPLETE' if complete else 'PARTIAL', 'changed_event_count': len(changes), 'changes': changes}


def audit_stage(root, baseline, branch, stage, raw, config, prompts, audit, stage1_output):
    directory, old = root / branch / stage, baseline / branch / stage
    start = len(audit.errors)
    calls = audit_calls(directory / 'api_calls', branch, stage, prompts, audit)
    summary = audit.get(directory / 'summary.json') or {}
    checkpoint = audit.get(directory / 'checkpoint.json') or {}
    declared_complete = summary.get('status') == 'COMPLETE'
    output_path = directory / OUTPUTS[stage]
    output = audit.get(output_path)
    if output:
        check_output(output, raw, config['paper_order'], audit, output_path)
    invariant = 'initial_labels.json' if stage == 'stage1' else 'candidates.json'
    if (directory / invariant).exists():
        audit.check(audit.get(directory / invariant) == audit.get(old / invariant, required=True), 'baseline_' + invariant, directory)
    elif declared_complete:
        audit.check(False, 'missing_' + invariant, directory)
    if declared_complete:
        audit.check(output is not None and summary.get('output_path') == str(output_path) and summary.get('output_sha256') == (sha(output_path) if output_path.exists() else None), 'summary_output_path_hash', directory)
        audit.check(summary.get('papers') == 43 and summary.get('records') == 335, 'summary_43_papers_335_records', directory)
        audit.check(summary.get('api_calls') == calls['logical_requests'] == calls['logical_accepted'], 'summary_all_logical_calls_accepted', directory)
        audit.check(all(r['post_calls'] == 1 and r['automatic_retries'] == 0 for r in calls['rows']), 'complete_stage_attempt_states', directory)
    else:
        audit.wait('stage_not_complete', directory)
    events = inspect_events(directory, old, stage, raw, config['paper_order'], output, stage1_output, calls, audit, declared_complete)
    if declared_complete:
        audit.check(summary.get('events') == events['observed_event_count'], 'summary_event_count', directory)
    # PAUSED summary may predate a successful manual resume. Latest checkpoint wins for activity only.
    observed = summary.get('status', 'NOT_STARTED')
    sp, cp = directory / 'summary.json', directory / 'checkpoint.json'
    if cp.exists() and (not sp.exists() or cp.stat().st_mtime_ns > sp.stat().st_mtime_ns) and not declared_complete:
        observed = checkpoint.get('status', observed)
    status = 'FAILED' if len(audit.errors) > start else ('COMPLETE' if declared_complete else 'INCOMPLETE')
    return {'status': status, 'observed_runtime_status': observed, 'summary_status': summary.get('status'),
            'checkpoint_status': checkpoint.get('status'), 'logical_requests': calls['logical_requests'],
            'logical_accepted': calls['logical_accepted'], 'physical_attempt_records': len(calls['rows']),
            'output': str(output_path), 'output_sha256': sha(output_path) if output_path.exists() else None}, calls, events, output


def scalar(row, key):
    if '/' in key:
        metric, statistic = key.split('/')
        return row['tuple'][metric][statistic]
    return row['leaderboard'][key]


def load_comparison(path, root, baseline, stage_checks):
    if not path.exists():
        return 'PENDING', None, ['comparison.json 尚未生成']
    issues = []
    try:
        data = read(path)
        for key in ('local_rows', 'paired_differences', 'cold_three_order_summaries', 'stage2_paper_changes'):
            if not isinstance(data[key], list):
                raise ValueError(key + ' must be a list')
        if data.get('status') in ('ERROR', 'FAILED'):
            return 'FAILED', None, ['comparison 状态：' + str(data.get('status'))]
        if data.get('status') != 'COMPLETE':
            return 'PENDING', None, ['comparison 状态：' + str(data.get('status'))]
        scope = data['scope']
        if [scope.get(k) for k in ('papers', 'predictions', 'gold_annotations', 'gold_boards')] != [43, 335, 295, 27]:
            raise ValueError('comparison scope must be Sol 43/335/295/27')
        index = {(r['model'], r['case']): r for r in data['local_rows']}
        expected = {(m, b + '_' + s) for m in MODELS for b in BRANCHES for s in STAGES}
        if set(index) != expected or len(data['local_rows']) != 16:
            raise ValueError('all 16 baseline/variant rows required')
        for (model, case), row in index.items():
            branch, stage = case.rsplit('_', 1)
            expected_path = (baseline if model == 'baseline' else root) / branch / stage / OUTPUTS[stage]
            if row['status'] != 'COMPLETE' or Path(row['normalized']).resolve() != expected_path.resolve() or row['input_sha256'] != sha(expected_path):
                raise ValueError('comparison normalized provenance:' + model + '/' + case)
            coverage = row['coverage']
            if coverage['status'] != 'COMPLETE' or any(coverage[k] != v for k, v in [('evaluated_papers', 43), ('tuple_macro_denominator', 43), ('predictions', 335), ('evaluated_gold_tdmrs', 295), ('gold_leaderboards', 27)]):
                raise ValueError('comparison coverage:' + case)
            if row['role'] != ('primary' if stage == 'stage2' else 'diagnostic'):
                raise ValueError('stage2 must be primary:' + case)
            for key in SCALARS:
                value = scalar(row, key)
                if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError('invalid metric:' + case + '/' + key)
        paired = {r['case']: r for r in data['paired_differences']}
        if set(paired) != {b + '_' + s for b in BRANCHES for s in STAGES} or len(paired) != len(data['paired_differences']):
            raise ValueError('eight paired differences required')
        for case, row in paired.items():
            for key in SCALARS:
                value = scalar(index['prompt_improvement_variant', case], key) - scalar(index['baseline', case], key)
                if not math.isclose(row['metrics'][key], value, abs_tol=1e-12):
                    raise ValueError('paired delta mismatch:' + case + '/' + key)
            for key in PRF:
                if index['baseline', case]['tuple']['Result IIM'][key] != index['prompt_improvement_variant', case]['tuple']['Result IIM'][key]:
                    raise ValueError('Result IIM changed despite frozen Results:' + case)
        cold = {(r['model'], r['stage']): r for r in data['cold_three_order_summaries']}
        if set(cold) != {(m, s) for m in (*MODELS, 'paired_delta') for s in STAGES} or len(data['cold_three_order_summaries']) != 6:
            raise ValueError('six cold summaries required')
        for (model, stage), row in cold.items():
            if row['status'] != 'COMPLETE' or set(row['orders_present']) != set(BRANCHES[1:]):
                raise ValueError('all three cold orders required')
            for key in SCALARS:
                values = [paired[b + '_' + stage]['metrics'][key] if model == 'paired_delta' else scalar(index[model, b + '_' + stage], key) for b in BRANCHES[1:]]
                stats = row['metrics'][key]
                if stats['n'] != 3 or not math.isclose(stats['mean'], statistics.mean(values), abs_tol=1e-12) or not math.isclose(stats['sample_sd'], statistics.stdev(values), abs_tol=1e-12):
                    raise ValueError('cold statistics mismatch:' + model + '/' + stage + '/' + key)
        changes = {(r['case'], r['metric']): r for r in data['stage2_paper_changes']}
        if set(changes) != {(b + '_stage2', m) for b in BRANCHES for m in METRICS[-2:]} or len(data['stage2_paper_changes']) != 8:
            raise ValueError('eight stage2 paper change summaries required')
        for (case, metric), row in changes.items():
            before, after = index['baseline', case]['per_paper'], index['prompt_improvement_variant', case]['per_paper']
            if set(before) != set(after) or len(before) != 43:
                raise ValueError('paper pairing:' + case)
            deltas = {p: after[p][metric]['F1'] - before[p][metric]['F1'] for p in before}
            tolerance = row.get('equality_tolerance', 1e-12)
            counts = [sum(v > tolerance for v in deltas.values()), sum(v < -tolerance for v in deltas.values()), sum(abs(v) <= tolerance for v in deltas.values())]
            if counts != [row['improved'], row['regressed'], row['unchanged']]:
                raise ValueError('paper change counts:' + case)
            for key in ('top_improvements', 'top_regressions'):
                for example in row[key]:
                    p = example['paper_id']
                    if example['baseline_F1'] != before[p][metric]['F1'] or example['variant_F1'] != after[p][metric]['F1'] or not math.isclose(example['delta_F1'], deltas[p], abs_tol=1e-12):
                        raise ValueError('paper example provenance:' + case)
        if data.get('source_integrity', {}).get('changed'):
            raise ValueError('comparison source_integrity changed')
    except (KeyError, TypeError, ValueError, OSError, IndexError) as exc:
        issues.append(type(exc).__name__ + ': ' + str(exc))
        return 'FAILED', None, issues
    return 'COMPLETE', data, issues


def final_status(audit_status, comparison_status):
    if audit_status == 'FAILED' or comparison_status == 'FAILED':
        return 'FAILED'
    if audit_status != 'PASS':
        return 'INCOMPLETE'
    return 'COMPLETE' if comparison_status == 'COMPLETE' else 'PENDING'


def resolve_output(value):
    path = Path(value).resolve()
    if path == ROOT.resolve():
        path = path / 'reporting'
    if path != HERE:
        raise ValueError('--out must be this experiment root or its reporting directory')
    return path


def save(path, value):
    path = Path(path)
    if not path.resolve().is_relative_to(HERE):
        raise ValueError('write outside reporting: ' + str(path))
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(text, encoding='utf8')
    temp.replace(path)


def main(argv=None):
    from offline_guard import activate
    guard = activate()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT, help='experiment root or its reporting directory')
    parser.add_argument('--comparison', type=Path, default=ROOT / 'analysis/comparison_final/comparison.json', help='existing offline comparison; never invokes evaluation')
    args = parser.parse_args(argv)
    out = resolve_output(args.out)
    audit = Audit()
    protected = audit.get(ROOT / 'protected_hashes.json', required=True) or {}
    audit.check(len(protected) == 83, 'protected_manifest_has_83_selected_files', ROOT / 'protected_hashes.json')
    before = {p: sha(p) if Path(p).is_file() else None for p in protected}
    changed = [p for p in protected if before[p] != protected[p]]
    audit.check(not changed, 'protected_hashes_match', ROOT / 'protected_hashes.json')
    raw = audit.get(ROOT / 'inputs/output.json', required=True)
    gold = audit.get(ROOT / 'inputs/gold.json', required=True)
    boards = audit.get(ROOT / 'inputs/leaderboards.json', required=True)
    prompts = audit.get(ROOT / 'prompts_semantic_v1.json', required=True)
    original = audit.get(ROOT / 'prompts_original.json', required=True)
    additions = audit.get(ROOT / 'prompt_additions.json', required=True)
    audit.check(sha(ROOT / 'inputs/output.json') == sha(BASE / 'inputs/output.json'), 'raw_extraction_byte_identity', ROOT)
    audit.check(len(raw) == 43 and sum(len(json.loads(v['output'])) for v in raw.values()) == 335 and len(gold) == 43 and sum(len(v['TDMs']) for v in gold.values()) == 295 and len(boards) == 27, 'scope_43_335_295_27', ROOT)
    audit.check(sha(ROOT / 'prompts_semantic_v1.json') == sha(DEEPSEEK / 'prompts_semantic_v1.json'), 'prompt_byte_identity_with_deepseek', ROOT)
    audit.check(set(additions) == {'masked-normalization-system-prompt', 'leaderboard-normalization-system-prompt'} and set(prompts) == set(original) and {k for k in prompts if prompts[k] != original[k]} == set(additions) and all(prompts[k] == original[k] + v for k, v in additions.items()), 'only_two_appended_prompts', ROOT)
    audit.check(generation_matches(audit.get(ROOT / 'generation_config.json', required=True)), 'generation_config', ROOT)
    stage_checks, events, all_calls, rows = {}, {}, [], []
    for branch in BRANCHES:
        print(json.dumps({'audit_branch': branch, 'mode': 'OFFLINE_READ_ONLY'}), flush=True)
        config = audit.get(ROOT / branch / 'config.json', required=True)
        oldconfig = audit.get(BASE / branch / 'config.json', required=True)
        for key in ('paper_order', 'cold_start', 'cold_start_seed', 'cold_start_seed_type', 'masking_seed', 'python_hash_seed', 'input_sha256'):
            audit.check(config.get(key) == oldconfig.get(key), 'baseline_config:' + key, ROOT / branch)
        audit.check(generation_matches(config['generation']) and config['model'] == GENERATION['model'], 'branch_generation', ROOT / branch)
        audit.check(config['paper_order'] == audit.get(ROOT / branch / 'paper_order.json', required=True), 'saved_paper_order', ROOT / branch)
        stage1_output = None
        for stage in STAGES:
            key = branch + '_' + stage
            check, calls, event, output = audit_stage(ROOT, BASE, branch, stage, raw, config, prompts, audit, stage1_output)
            stage_checks[key], events[key] = check, event
            all_calls.append(calls)
            rows.extend(calls['rows'])
            if stage == 'stage1':
                stage1_output = output
    after = {p: sha(p) if Path(p).is_file() else None for p in protected}
    changed_during = [p for p in protected if after[p] != before[p]]
    audit.check(not changed_during, 'protected_files_stable_during_audit', ROOT)
    # A live request/checkpoint can change while read. Such snapshots cannot be final.
    unstable = [p for p, h in audit.sources.items() if not Path(p).is_file() or sha(p) != h]
    for p in unstable:
        audit.wait('source_changed_during_snapshot_rerun_after_completion', p)
    status = 'FAILED' if audit.errors else ('PASS' if all(s['status'] == 'COMPLETE' for s in stage_checks.values()) and not unstable else 'INCOMPLETE')
    comparison_status, comparison, comparison_issues = load_comparison(args.comparison, ROOT, BASE, stage_checks)
    verification = {'status': status, 'report_status': final_status(status, comparison_status), **timestamps(),
                    'stage_checks': stage_checks, 'issues': audit.errors, 'pending': audit.pending,
                    'protected_file_count': len(protected), 'protected_changes': changed, 'protected_changes_during_audit': changed_during,
                    'protected_hashes_before': before, 'protected_hashes_after': after,
                    'comparison_status': comparison_status, 'comparison_issues': comparison_issues,
                    'comparison_path': str(args.comparison), 'comparison_sha256': sha(args.comparison) if args.comparison.exists() else None,
                    'generation_expected': GENERATION, 'prompt_sha256': sha(ROOT / 'prompts_semantic_v1.json'),
                    'papers': 43, 'prediction_records': 335, 'gold_records': 295, 'gold_boards': 27,
                    'audit_generated_api_requests': 0, 'source_snapshot_unstable': unstable,
                    'source_files_checked': len(audit.sources)}
    usage = usage_summary(rows, all_calls)
    usage['branches'] = {b: usage_summary([r for r in rows if r['branch'] == b], [all_calls[i] for i in range(len(all_calls)) if i // 2 == BRANCHES.index(b)]) for b in BRANCHES}
    usage.update(timestamps())
    save(out / 'verification.json', verification)
    save(out / 'api_usage_summary.json', usage)
    save(out / 'alignment_event_summary.json', {'status': status, **timestamps(), 'stages': events})
    save(out / 'output_index.json', stage_checks)
    with (out / 'request_audit.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        fields = list(rows[0]) if rows else ['branch', 'stage', 'call', 'attempt', 'status', 'usage_known', *TOKENS]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    # Local reporting-only module, deliberately independent of analysis/runtime code.
    from report_render import render
    report, examples = render(verification, usage, comparison if verification['report_status'] == 'COMPLETE' else None, events, gold, ROOT, BASE)
    save(out / 'report.md', report)
    save(out / 'alignment_examples.json', {'status': verification['report_status'], 'examples': examples})
    files = ['report.md', 'api_usage_summary.json', 'verification.json', 'request_audit.csv', 'alignment_event_summary.json', 'alignment_examples.json', 'output_index.json']
    save(out / 'index.json', {'status': verification['report_status'], **timestamps(), 'artifacts': [{'path': name, 'sha256': sha(out / name)} for name in files], 'comparison': str(args.comparison)})
    save(out / 'index.md', '# Sol 离线审计与报告\n\n状态：' + verification['report_status'] + '\n\n' + '\n'.join('- [' + name + '](' + name + ')' for name in files + ['offline_safety_proof.json', 'test_results.json', 'README.md']) + '\n\n生成时间：' + verification['checked_utc'] + ' / ' + verification['checked_shanghai'] + '\n')
    save(out / 'offline_safety_proof.json', {'status': 'PASS' if not guard.blocked and not changed_during else 'FAILED', **timestamps(),
         'enforcement': 'Python audit hook blocks socket/process/model imports/credential-file reads and all writes outside reporting',
         'blocked_events_during_audit': guard.blocked, 'observed_write_paths': sorted(guard.write_paths),
         'write_boundary': str(HERE), 'protected_files_checked_before_and_after': len(protected),
         'protected_changes_during_audit': changed_during, 'source_roots_read_only': [str(ROOT), str(BASE), str(DEEPSEEK)],
         'proof_write_itself': str(out / 'offline_safety_proof.json'), 'runtime_or_evaluator_imported': False,
         'network_or_model_calls': 0, 'reporting_source_hashes': {p.name: sha(p) for p in HERE.glob('*.py')}})
    print(json.dumps({'status': verification['report_status'], 'audit': status, 'comparison': comparison_status, 'attempt_records': len(rows), 'logical_accepted': usage['logical_accepted'], 'unknown_usage_attempts': usage['unknown_usage_attempts'], 'errors': len(audit.errors), 'report': str(out / 'report.md')}, ensure_ascii=False))
    return 0 if verification['report_status'] == 'COMPLETE' else (1 if verification['report_status'] == 'FAILED' else 2)


if __name__ == '__main__':
    sys.exit(main())
