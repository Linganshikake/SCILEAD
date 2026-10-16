"""Unmodified official normalization loop with an isolated ChatOpenAI adapter.

Default: offline preflight only. --execute is reserved for explicit user approval.
No result cache, response cleanup, retry, PDF parsing, or extraction calls.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT / 'emnlp2024-leaderboard-generation'
EXTRACTION = ROOT / 'pilot/outputs/gpt41_single_paper'
OUT = EXTRACTION / 'normalization'
GOLD = Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\tdm_annotations.json')
ENV_FILE = ROOT / 'SCILEAD_small_test/.env'
PAPER = '2020.findings-emnlp.378.pdf'
MODEL = 'gpt-4.1-2025-04-14'
BASE = 'https://9527.codes/v1'
KEY = ''
NETWORK_ALLOWED = False

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat()

def scrub(obj):
    if isinstance(obj, str):
        return obj.replace(KEY, '[REDACTED]') if KEY else obj
    if isinstance(obj, list):
        return [scrub(v) for v in obj]
    if isinstance(obj, dict):
        return {k: '[REDACTED]' if k.lower() in ('authorization', 'api_key', 'x-api-key') else scrub(v) for k, v in obj.items()}
    return obj

def save(name, data):
    (OUT / name).write_text(json.dumps(scrub(data), ensure_ascii=False, indent=2), encoding='utf-8')

def log(message):
    line = now() + ' ' + message
    print(line, flush=True)
    with (OUT / 'run.log').open('a', encoding='utf-8') as f:
        f.write(line + '\n')

def guard(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo') and not NETWORK_ALLOWED:
        raise RuntimeError('Network disabled during preflight and offline work')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        p = Path(os.fsdecode(args[0])); norm = str(p).replace('\\', '/').lower()
        if any(s in norm for s in ('/.codex/', '/.claude/', '/.aws/')):
            raise RuntimeError('Unrelated sensitive config access prohibited')
        if p.name.startswith('.env') and p.resolve() != ENV_FILE.resolve():
            raise RuntimeError('Only designated dotenv is authorized')

def credential():
    from dotenv import dotenv_values
    for name in ('OPENAI_API_KEY', 'API_KEY'):
        if os.environ.get(name, '').strip():
            return os.environ[name].strip(), 'environment:' + name
    values = dotenv_values(ENV_FILE, interpolate=False, encoding='utf-8-sig') if ENV_FILE.is_file() else {}
    for name in ('OPENAI_API_KEY', 'API_KEY'):
        if (values.get(name) or '').strip():
            return values[name].strip(), 'designated dotenv:' + name
    return '', 'missing'

def wire(messages):
    return [{'role': {'system': 'system', 'human': 'user'}[m.type], 'content': m.content} for m in messages]

def main(execute=False):
    global KEY, NETWORK_ALLOWED
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'execution-started.json').exists() or (OUT / 'normalized_output.json').exists():
        raise RuntimeError('Existing execution/output: automatic restart prohibited')
    os.chdir(ROOT / 'pilot/work')
    os.environ.update({'TIKTOKEN_CACHE_DIR': str(ROOT / 'assets/tiktoken'), 'HF_HOME': str(ROOT / 'assets/huggingface'), 'LANGCHAIN_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false', 'LANGSMITH_TRACING': 'false', 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'HF_HUB_DISABLE_TELEMETRY': '1', 'ANONYMIZED_TELEMETRY': 'False'})
    logging.disable(logging.CRITICAL)
    sys.addaudithook(guard)
    sys.path.insert(0, str(REPO))
    from prompting import NormalizationPrompt
    import tiktoken
    gold = json.loads(GOLD.read_text(encoding='utf-8'))
    extracted = json.loads((EXTRACTION / 'output.json').read_text(encoding='utf-8'))
    assert list(extracted) == [PAPER] and PAPER in gold
    assert GOLD.read_bytes() == (ROOT / 'pilot/gold/tdm_annotations.json').read_bytes()
    rows = json.loads(extracted[PAPER]['output'])
    assert len(rows) == 6 and all(set(r) == {'Task', 'Dataset', 'Metric', 'Result'} for r in rows)
    assert all(isinstance(r['Result'], str) for r in rows)
    labels = {'Task': set(), 'Dataset': set(), 'Metric': set()}
    for paper in gold:
        for item in gold[paper]['TDMs']:
            for field in labels:
                labels[field].add(item[field])
    prompts = json.loads((REPO / 'prompts.json').read_text(encoding='utf-8'))
    template = NormalizationPrompt(prompts['normalization-system-prompt'], 'gpt4-turbo-128k').prompt_template
    encoder = tiktoken.encoding_for_model(MODEL)
    plan, checks = [], []
    for index, row in enumerate(rows):
        for field, value in row.items():
            needs_call = field != 'Result' and value not in labels[field]
            checks.append({'record': index + 1, 'field': field, 'original_value': value, 'requires_llm': needs_call, 'action': 'LLM' if needs_call else 'preserve original string'})
            if needs_call:
                # Preserve official str(set), not sorted lists or JSON arrays.
                messages = wire(template.invoke({'items': str(labels[field]), 'input': value}).to_messages())
                estimate = 3 + sum(3 + len(encoder.encode(m['role'])) + len(encoder.encode(m['content'])) for m in messages)
                plan.append({'call': len(plan) + 1, 'record': index + 1, 'field': field, 'original_value': value, 'messages': messages, 'estimated_prompt_tokens': estimate})
    assert len(plan) == 12 and len(plan) <= 18
    KEY, key_source = credential()
    group_counts = Counter((p['field'], p['original_value']) for p in plan)
    report = {'time': now(), 'status': 'AWAITING_USER_APPROVAL', 'gold_path': str(GOLD), 'gold_sha256': digest(GOLD), 'gold_papers': len(gold), 'gold_tdmrs': sum(len(v['TDMs']) for v in gold.values()), 'target_paper': PAPER, 'target_gold_tdmrs': len(gold[PAPER]['TDMs']), 'extracted_tdmrs': len(rows), 'standard_label_counts': {k: len(v) for k, v in labels.items()}, 'expected_model_requests': len(plan), 'actual_model_requests': 0, 'calls_by_field': dict(Counter(p['field'] for p in plan)), 'field_checks': checks, 'repeated_inputs': [{'field': k[0], 'value': k[1], 'count': n} for k, n in group_counts.items() if n > 1], 'official_caching': False, 'hypothetical_calls_with_cache_NOT_USED': len(group_counts), 'estimated_total_prompt_tokens': sum(p['estimated_prompt_tokens'] for p in plan), 'estimated_each_prompt_tokens': [p['estimated_prompt_tokens'] for p in plan], 'max_completion_tokens_per_request': 15, 'max_total_completion_tokens': 15 * len(plan), 'key_present': bool(KEY), 'credential_source': key_source, 'seed': 0, 'temperature': 0, 'python_hash_seed': '0', 'set_serialization': 'Original str(set); PYTHONHASHSEED=0 fixes iteration order for reproducible dry-run/request correspondence.', 'out_of_set_response_handling': 'Official exact membership check; None when invalid. No strip, quote removal, manual correction or retries.', 'prompt_exposure': 'Only entire-dataset field-name set and current predicted field value. No paper ID, Result, Gold tuple relationships, source documents or other field types in request.', 'provider_context_limit': 'UNVERIFIED', 'provider_pricing': 'UNVERIFIED; third-party billing not available', 'ready_for_request_after_user_approval': bool(KEY)}
    save('preflight_report.json', report)
    save('request_plan.json', plan)
    save('standard_name_sets.json', {k: {'count': len(v), 'official_set_string': str(v)} for k, v in labels.items()})
    source_names = ['tdm_llm_normalization.py', 'tdm_eval.py', 'prompting.py', 'utils.py', 'model_init.py', 'prompts.json', 'requirements.txt']
    source_hashes = {n: digest(REPO / n) for n in source_names}
    config = {'model': MODEL, 'base_url': BASE, 'temperature': 0, 'seed': 0, 'max_tokens': 15, 'max_retries': 0, 'expected_calls': len(plan), 'max_allowed_calls': len(plan), 'zero_shot': True, 'official_prompt_branch': 'gpt4-turbo-128k', 'python_hash_seed': '0', 'gold_sha256': digest(GOLD), 'extraction_sha256': digest(EXTRACTION / 'output.json'), 'extraction_config_sha256': digest(EXTRACTION / 'config.json'), 'source_hashes': source_hashes, 'implementation': 'Call unmodified tdm_llm_normalization.main; replace only model initialization and in-memory config compatibility fields.', 'cost_warning': 'Official normalization_costs.txt may contain unsupported zero/estimated OpenAI costs. It is not third-party billing; use token logs.', 'timeout_seconds': {'connect': 20, 'read': 180, 'write': 30, 'pool': 20}}
    save('config.json', config)
    usage = {'phase': 'PREFLIGHT_ONLY', 'expected_requests': len(plan), 'actual_request_attempts': 0, 'completed_requests': 0, 'calls': [], 'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0, 'actual_billing_cost': None, 'retries': 0}
    save('normalization_api_usage.json', usage)
    log(f'PREFLIGHT calls={len(plan)} estimated_input_tokens={report["estimated_total_prompt_tokens"]} output_cap={15*len(plan)} paid_calls=0')
    if not execute:
        return 0
    assert KEY, 'API key missing'
    with (OUT / 'execution-started.json').open('x', encoding='utf-8') as f:
        json.dump({'time': now(), 'approved_entrypoint': '--execute', 'max_calls': len(plan)}, f)

    import httpx
    import openai
    from langchain_openai import ChatOpenAI
    import tdm_llm_normalization as official
    active = {}
    def request_hook(request):
        payload = json.loads(request.content)
        assert request.method == 'POST' and str(request.url) == BASE + '/chat/completions'
        assert payload['messages'] == active['plan']['messages']
        assert payload['model'] == MODEL and payload['max_tokens'] == 15 and payload['temperature'] == 0 and payload['seed'] == 0
        assert active['record']['attempts'] == 0 and usage['actual_request_attempts'] < len(plan)
        number = active['plan']['call']
        with (OUT / f'call-{number:02d}-attempt.json').open('x', encoding='utf-8') as f:
            json.dump({'time': now(), 'attempt': 1, 'model': MODEL}, f)
        active['record']['attempts'] = 1
        usage['actual_request_attempts'] += 1
        save(f'call-{number:02d}-request.json', payload)
        save('normalization_api_usage.json', usage)
    def response_hook(response):
        record = active['record']; number = active['plan']['call']
        record['http_status'] = response.status_code
        record['request_id'] = response.headers.get('x-request-id') or response.headers.get('request-id')
        response.read()
        try:
            body = response.json()
        except ValueError:
            body = {'body_text': response.text}
        save(f'call-{number:02d}-response.json', body)
        if 200 <= response.status_code < 300:
            u = body.get('usage') or {}
            record.update(returned_model=body.get('model'), response_id=body.get('id'), system_fingerprint=body.get('system_fingerprint'), usage=u, finish_reason=(body.get('choices') or [{}])[0].get('finish_reason'), seed_parameter_accepted=True, seed_determinism_verified=False)
            for name in ('prompt_tokens', 'completion_tokens', 'total_tokens'):
                if isinstance(u.get(name), int):
                    usage[name] += u[name]
        save('normalization_api_usage.json', usage)
    timeout = httpx.Timeout(connect=20, read=180, write=30, pool=20)
    client = httpx.Client(timeout=timeout, follow_redirects=False, event_hooks={'request': [request_hook], 'response': [response_hook]})
    sdk = openai.OpenAI(api_key=KEY, base_url=BASE, organization='', project='', max_retries=0, timeout=timeout, http_client=client)
    llm = ChatOpenAI(model=MODEL, api_key=KEY, base_url=BASE, temperature=0, max_tokens=15, model_kwargs={'seed': 0}, max_retries=0, timeout=timeout, client=sdk.chat.completions, async_client=object(), cache=False)
    class ObservedModel:
        def invoke(self, prompt):
            global NETWORK_ALLOWED
            index = usage['completed_requests']
            assert index < len(plan)
            item = plan[index]
            assert wire(prompt.to_messages()) == item['messages'], 'Official call differs from preflight'
            record = {'call': index + 1, 'record': item['record'], 'field': item['field'], 'original_value': item['original_value'], 'attempts': 0}
            usage['calls'].append(record); active.update(plan=item, record=record)
            start = time.monotonic()
            try:
                NETWORK_ALLOWED = True
                answer = llm.invoke(prompt)
                NETWORK_ALLOWED = False
                record['raw_answer'] = answer.content
                record['exact_member_of_standard_set'] = answer.content in labels[item['field']]
                record['official_normalized_value'] = answer.content if record['exact_member_of_standard_set'] else None
                record['invalid_reason'] = None if record['exact_member_of_standard_set'] else ('output_truncated' if record.get('finish_reason') == 'length' else 'raw answer not exact standard label; official None')
                usage['completed_requests'] += 1
                log(f'CALL {index+1}/{len(plan)} field={item["field"]} completed')
                return answer
            except Exception as exc:
                record['error_type'] = type(exc).__name__
                save('error.json', {'call': index + 1, 'error_type': type(exc).__name__, 'message': scrub(str(exc)), 'retry': False})
                raise
            finally:
                NETWORK_ALLOWED = False
                record['elapsed_seconds'] = round(time.monotonic() - start, 3)
                save('normalization_api_usage.json', usage)
    reader = official.utils.read_json
    def compatible_reader(path):
        data = reader(path)
        if Path(path).resolve() == (EXTRACTION / 'config.json').resolve():
            data = dict(data)
            data.update(is_few_shot=False, model_type='gpt4-turbo-128k')
        return data
    official.utils.read_json = compatible_reader
    official.utils.llm_init_langchain = lambda config, max_new_tokens, seed: ObservedModel()
    args = argparse.Namespace(seed=0, max_new_tokens=15, gold_tdm_path=str(GOLD), tdm_output_path=EXTRACTION.as_posix() + '/', prompt_file=str(REPO / 'prompts.json'))
    usage['phase'] = 'RUNNING'
    try:
        official.main(args)
        assert usage['actual_request_attempts'] == usage['completed_requests'] == len(plan)
        normalized = json.loads((OUT / 'normalized_output.json').read_text(encoding='utf-8'))
        assert normalized[PAPER]['source_documents'] == extracted[PAPER]['source_documents']
        assert [v['Result'] for v in normalized[PAPER]['normalized_output']] == [v['Result'] for v in rows]
        usage['phase'] = 'COMPLETE'
    except Exception:
        usage['phase'] = 'STOPPED_NO_RETRY'
        raise
    finally:
        NETWORK_ALLOWED = False
        usage['source_unchanged'] = all(digest(REPO / n) == h for n, h in source_hashes.items())
        usage['extraction_unchanged'] = digest(EXTRACTION / 'output.json') == config['extraction_sha256']
        usage['extraction_config_unchanged'] = digest(EXTRACTION / 'config.json') == config['extraction_config_sha256']
        save('normalization_api_usage.json', usage)
        client.close()
    return 0

if __name__ == '__main__':
    # Preserve official set formatting with reproducible Python set order.
    if os.environ.get('PYTHONHASHSEED') != '0':
        import subprocess
        env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')
        sys.exit(subprocess.call([sys.executable, '-X', 'utf8', __file__, *sys.argv[1:]], env=env))
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', help='ONLY after user confirms paid normalization calls.')
    args = parser.parse_args()
    try:
        sys.exit(main(args.execute))
    except Exception as exc:
        if OUT.is_dir():
            save('adapter_error.json', {'error_type': type(exc).__name__, 'message': scrub(str(exc)), 'automatic_retry': False})
        print('STOP', type(exc).__name__, '(sanitized error saved)')
        sys.exit(2)
