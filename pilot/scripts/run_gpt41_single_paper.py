"""SCILEAD original zero-shot/stuff prompt, one explicitly authorized API attempt."""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import logging
import os
from pathlib import Path
import pickle
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT / 'emnlp2024-leaderboard-generation'
OUT = ROOT / 'pilot/outputs/gpt41_single_paper'
INPUT = ROOT / 'pilot/outputs/scilead-pilot-13.10.2026-16-58-13/processed_docs.pkl'
ENV_FILE = ROOT / 'SCILEAD_small_test/.env'
PAPER = '2020.findings-emnlp.378.pdf'
MODEL = 'gpt-4.1-2025-04-14'
BASE = 'https://9527.codes/v1'
EXPECTED_INPUT_HASH = '8268049bc057a1e9c22a90cc8210c16c534142fa6712aa16020dc57f39f8c9e2'
FIELDS = ('Task', 'Dataset', 'Metric', 'Result')
KEY = ''
NETWORK_ALLOWED = False
MODEL_RETURNED = False

def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def scrub(value):
    if isinstance(value, str):
        return value.replace(KEY, '[REDACTED]') if KEY else value
    if isinstance(value, dict):
        return {k: '[REDACTED]' if k.lower() in ('authorization', 'api_key', 'api-key', 'x-api-key') else scrub(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value

def save(name, data):
    (OUT / name).write_text(json.dumps(scrub(data), ensure_ascii=False, indent=2), encoding='utf-8')

def log(message):
    # Only predetermined status text is logged, never clients/headers/credentials.
    line = now() + ' ' + message
    print(line, flush=True)
    with (OUT / 'run.log').open('a', encoding='utf-8') as f:
        f.write(line + '\n')

def audit(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo') and not NETWORK_ALLOWED:
        raise RuntimeError('Network disabled outside single authorized request')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        p = Path(os.fsdecode(args[0]))
        norm = str(p).replace('\\', '/').lower()
        if '/.codex/' in norm or '/.aws/' in norm or '/.claude/' in norm:
            raise RuntimeError('Unrelated sensitive configuration prohibited')
        if p.name.startswith('.env') and p.resolve() != ENV_FILE.resolve():
            raise RuntimeError('Only user-designated dotenv is authorized')
        if not MODEL_RETURNED and ('/pilot/gold/' in norm or p.name in ('tdm_annotations.json', 'leaderboards.json', 'data-provenance.json')):
            raise RuntimeError('Gold unavailable until model has returned')

def credential():
    from dotenv import dotenv_values
    for name in ('OPENAI_API_KEY', 'API_KEY'):
        if os.environ.get(name, '').strip():
            return os.environ[name].strip(), 'environment:' + name
    values = dotenv_values(ENV_FILE, interpolate=False, encoding='utf-8-sig') if ENV_FILE.is_file() else {}
    for name in ('OPENAI_API_KEY', 'API_KEY'):
        if values.get(name, '').strip():
            return values[name].strip(), 'user-designated dotenv:' + name
    return '', 'missing'

def validate_output(raw):
    report = {'json_parseable': False, 'is_array': False, 'fields_complete': False, 'results_are_strings': False, 'duplicates': [], 'record_count': None}
    try:
        records = json.loads(raw)  # No stripping fences, repair or coercion.
    except json.JSONDecodeError as exc:
        report['json_error'] = {'message': exc.msg, 'line': exc.lineno, 'column': exc.colno}
        return report, None
    report['json_parseable'] = True
    report['is_array'] = isinstance(records, list)
    if not isinstance(records, list):
        return report, None
    report['record_count'] = len(records)
    report['fields_complete'] = all(isinstance(r, dict) and all(k in r for k in FIELDS) for r in records)
    report['results_are_strings'] = all(isinstance(r, dict) and isinstance(r.get('Result'), str) for r in records)
    seen = {}
    for i, row in enumerate(records):
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key in seen:
            report['duplicates'].append({'index': i, 'same_as': seen[key]})
        else:
            seen[key] = i
    return report, records

def main(execute=False):
    global KEY, NETWORK_ALLOWED, MODEL_RETURNED
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'request-attempt.json').exists():
        raise RuntimeError('Persistent request marker exists: repeat model calls prohibited')
    work = ROOT / 'pilot/work'
    os.chdir(work)
    os.environ.update({'TIKTOKEN_CACHE_DIR': str(ROOT / 'assets/tiktoken'), 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'HF_HUB_DISABLE_TELEMETRY': '1', 'ANONYMIZED_TELEMETRY': 'False', 'DO_NOT_TRACK': '1', 'LANGCHAIN_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false', 'LANGSMITH_TRACING': 'false'})
    logging.disable(logging.CRITICAL)
    sys.addaudithook(audit)
    KEY, key_source = credential()
    sys.path.insert(0, str(REPO))
    from prompting import TDMPrompt
    from pdf_loader import PreProcessedDocuments
    from langchain.chains import RetrievalQA
    from langchain_core.language_models.fake_chat_models import FakeListChatModel
    from langchain_core.callbacks import BaseCallbackHandler
    import tiktoken

    assert INPUT.is_file(), 'Missing preprocessed input'
    input_hash = sha(INPUT.read_bytes())
    assert input_hash == EXPECTED_INPUT_HASH, 'Preprocessed evidence hash changed'
    with INPUT.open('rb') as f:
        papers = pickle.load(f)  # Known, locally generated artifact with pinned SHA256.
    assert list(papers) == [PAPER], 'Unexpected paper list'
    docs = papers[PAPER]
    assert len(docs) == 16, 'Expected sixteen evidence documents'
    expected_scores = ['90.32', '55.14', '50.68', '81.18', '96.62', '69.78']
    table5 = [d for d in docs if d.metadata.get('page_number') == 7 and 'Table 5:' in d.page_content]
    assert len(table5) == 1 and all(s in table5[0].page_content for s in expected_scores)
    prompts = json.loads((REPO / 'prompts.json').read_text(encoding='utf-8'))
    template = TDMPrompt(prompts['tdm-extraction-system-prompt'], 'gpt4-turbo-128k').prompt_template
    retriever = PreProcessedDocuments(docs=docs).init_retriever()
    captured = []
    class Capture(BaseCallbackHandler):
        def on_chat_model_start(self, serialized, messages, **kwargs):
            captured.extend(messages)
    fake = FakeListChatModel(responses=['[]'], cache=False)
    chain = RetrievalQA.from_chain_type(llm=fake, chain_type='stuff', retriever=retriever, return_source_documents=True, chain_type_kwargs={'prompt': template})
    trial = chain.invoke(prompts['query'], config={'callbacks': [Capture()]})
    assert trial['source_documents'] == docs
    assert len(captured) == 1
    messages = [{'role': {'system': 'system', 'human': 'user'}[m.type], 'content': m.content} for m in captured[0]]
    expected = template.format_messages(question=prompts['query'], context='\n\n'.join(d.page_content for d in docs))
    assert [m.content for m in expected] == [m['content'] for m in messages]
    assert [m['role'] for m in messages] == ['system', 'user']
    assert '[Start of the Example]' not in json.dumps(messages)
    enc = tiktoken.encoding_for_model(MODEL)
    content_tokens = sum(len(enc.encode(m['content'])) for m in messages)
    estimated_tokens = 3 + sum(3 + len(enc.encode(m['role'])) + len(enc.encode(m['content'])) for m in messages)
    checks = {'paper_id_exact': True, 'paper_count': 1, 'evidence_count': len(docs), 'evidence_sha256_matches_stage3': True, 'table5_all_six_scores_present': True, 'official_zero_shot_template': True, 'roles': ['system', 'user'], 'stuff_context_exact': True, 'gold_not_read_or_appended': True, 'key_present': bool(KEY), 'windows_output_path_valid': all(c not in OUT.name for c in '<>:"/\\|?*'), 'input_under_30000': estimated_tokens <= 30000, 'within_official_model_context': estimated_tokens + 1024 <= 1047576}
    ready = bool(KEY) and checks['input_under_30000'] and checks['within_official_model_context'] and checks['windows_output_path_valid']
    source_hashes = {n: sha((REPO / n).read_bytes()) for n in ['prompts.json', 'prompting.py', 'pdf_loader.py', 'tdm_extraction.py', 'tdm_extraction_config.py', 'model_init.py', 'utils.py', 'requirements.txt']}
    config = {'model': MODEL, 'base_url': BASE, 'temperature': 0, 'seed': 0, 'max_tokens': 1024, 'n': 1, 'stream': False, 'zero_shot': True, 'chain_type': 'stuff', 'official_prompt_branch': 'gpt4-turbo-128k', 'official_commit': '8bf74b0a830feb7035c6166dce3394dc344ae532', 'timeout_seconds': {'connect': 20, 'read': 180, 'write': 30, 'pool': 20}, 'max_retries': 0, 'follow_redirects': False, 'paper': PAPER, 'processed_docs_path': str(INPUT), 'processed_docs_sha256': input_hash, 'source_hashes': source_hashes, 'system_prompt_source': "prompts.json['tdm-extraction-system-prompt']", 'query': prompts['query'], 'evidence_count': 16, 'provider_context_limit': 'UNVERIFIED', 'provider_unverified_authorization': 'User explicitly allows one unchanged request if complete input <= 30000 tokens and other checks pass.', 'official_context_limit': 1047576, 'official_max_output': 32768, 'output_dir': str(OUT), 'input_messages_sha256': sha(json.dumps(messages, ensure_ascii=False, separators=(',', ':')).encode()), 'seed_support': 'UNVERIFIED before request; success demonstrates parameter acceptance, not deterministic behavior', 'credential_source': key_source}
    dry = {'time': now(), 'ready_for_authorized_single_request': ready, 'checks': checks, 'content_tokens': content_tokens, 'estimated_prompt_tokens': estimated_tokens, 'tokenizer': 'o200k_base', 'estimation_method': 'Chat message content/role tokens + 3 tokens per message + 3 reply primer; actual server usage may differ.', 'max_output_tokens': 1024, 'provider_context_limit': 'UNVERIFIED', 'provider_limit_exception_authorized_by_user': True, 'actual_model_calls': 0, 'offline_chain_test': 'PASS using FakeListChatModel; no API request', 'gold_separation': 'Messages assembled exclusively from official zero-shot prompt/query and immutable pickle; audit guard rejects Gold access before response.'}
    save('config.json', config)
    save('dry_run_report.json', dry)
    save('input_messages.json', messages)
    usage = {'requested_model': MODEL, 'returned_model': None, 'prompt_tokens': None, 'completion_tokens': None, 'total_tokens': None, 'estimated_prompt_tokens': estimated_tokens, 'actual_model_request_attempts': 0, 'http_success': False, 'seed': 0, 'seed_parameter_accepted': None, 'seed_determinism_verified': False, 'snapshot_requested': True, 'snapshot_response_matches': None, 'provider_context_limit': 'UNVERIFIED', 'billing_cost': None, 'billing_note': 'Third-party billing unavailable; no LangChain USD estimate used.', 'sdk_max_retries': 0, 'http_transport_retries': 0}
    save('api_usage.json', usage)
    log(f'DRY_RUN ready={ready} estimated_prompt_tokens={estimated_tokens} documents=16 model_calls=0')
    if not ready:
        return 2
    if not execute:
        return 0

    import httpx
    import openai
    from langchain_openai import ChatOpenAI
    def request_hook(request):
        payload = json.loads(request.content)
        assert str(request.url) == BASE + '/chat/completions' and request.method == 'POST'
        assert payload['messages'] == messages, 'Actual messages differ from dry run'
        assert payload['model'] == MODEL and payload['temperature'] == 0 and payload['seed'] == 0 and payload['max_tokens'] == 1024
        assert not payload.get('stream', False) and payload.get('n', 1) == 1
        assert usage['actual_model_request_attempts'] == 0
        # Atomic, persistent marker before handing the request to the transport.
        with (OUT / 'request-attempt.json').open('x', encoding='utf-8') as f:
            json.dump({'time': now(), 'model': MODEL, 'attempts': 1, 'message_hash': config['input_messages_sha256']}, f)
        usage['actual_model_request_attempts'] = 1
        save('api_usage.json', usage)
        save('request_payload.json', payload)  # Body only: no headers or key.
    def response_hook(response):
        usage['http_status'] = response.status_code
        usage['server_request_id'] = response.headers.get('x-request-id') or response.headers.get('request-id')
        usage['http_success'] = 200 <= response.status_code < 300
        save('api_usage.json', usage)
        response.read()
        try:
            data = response.json()
        except ValueError:
            data = {'body_text': response.text}
        save('raw_api_response.json' if usage['http_success'] else 'api_error.json', data)
    timeout = httpx.Timeout(connect=20, read=180, write=30, pool=20)
    client = httpx.Client(timeout=timeout, follow_redirects=False, event_hooks={'request': [request_hook], 'response': [response_hook]})
    sdk = openai.OpenAI(api_key=KEY, base_url=BASE, organization='', project='', max_retries=0, timeout=timeout, http_client=client)
    llm = ChatOpenAI(model=MODEL, api_key=KEY, base_url=BASE, temperature=0, max_tokens=1024, model_kwargs={'seed': 0}, max_retries=0, timeout=timeout, client=sdk.chat.completions, async_client=object(), cache=False)
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever, return_source_documents=True, chain_type_kwargs={'prompt': template})
    start = time.monotonic()
    log('REQUEST_START one request maximum; SDK retries disabled')
    try:
        NETWORK_ALLOWED = True
        result = chain.invoke(prompts['query'])
        NETWORK_ALLOWED = False
        MODEL_RETURNED = True
        assert result['source_documents'] == docs
        output = {PAPER: {'output': result['result'], 'source_documents': [{'content': d.page_content, 'metadata': d.metadata} for d in result['source_documents']]}}
        save('output.json', output)
        raw_api = json.loads((OUT / 'raw_api_response.json').read_text(encoding='utf-8'))
        token_usage = raw_api.get('usage') or {}
        usage.update(returned_model=raw_api.get('model'), prompt_tokens=token_usage.get('prompt_tokens'), completion_tokens=token_usage.get('completion_tokens'), total_tokens=token_usage.get('total_tokens'), response_id=raw_api.get('id'), system_fingerprint=raw_api.get('system_fingerprint'), finish_reason=(raw_api.get('choices') or [{}])[0].get('finish_reason'), seed_parameter_accepted=True, seed_support='Request containing seed=0 accepted; server may ignore it, determinism unverified', snapshot_response_matches=raw_api.get('model') == MODEL, raw_token_usage=token_usage)
        validation, rows = validate_output(result['result'])
        validation['finish_reason'] = usage['finish_reason']
        validation['output_truncated'] = usage['finish_reason'] == 'length'
        save('validation.json', validation)
        # Gold is opened only here, after the model response and raw output are saved.
        gold = json.loads((ROOT / 'pilot/gold/tdm_annotations.json').read_text(encoding='utf-8'))[PAPER]['TDMs']
        comparison = [{'gold': g, 'output_indices_with_same_result': [i for i, r in enumerate(rows or []) if isinstance(r, dict) and str(r.get('Result')) == str(g['Result'])]} for g in gold]
        save('gold_comparison.json', {'phase': 'post-response offline only', 'numeric_matches': sum(bool(c['output_indices_with_same_result']) for c in comparison), 'gold_count': len(gold), 'comparison': comparison, 'binding_and_baseline_status': 'Pending human review; numeric equality alone is insufficient'})
        log(f'REQUEST_COMPLETED records={validation["record_count"]} json_valid={validation["json_parseable"]}')
    except Exception as exc:
        NETWORK_ALLOWED = False
        usage['error_type'] = type(exc).__name__
        usage['error_http_status'] = getattr(exc, 'status_code', None)
        save('execution_error.json', {'error_type': type(exc).__name__, 'http_status': getattr(exc, 'status_code', None), 'message': scrub(str(exc)), 'retry': False})
        log('REQUEST_STOPPED error_type=' + type(exc).__name__ + '; no retry')
        return 3
    finally:
        NETWORK_ALLOWED = False
        usage['elapsed_seconds'] = round(time.monotonic() - start, 3)
        usage['source_files_unchanged'] = all(sha((REPO / n).read_bytes()) == h for n, h in source_hashes.items())
        usage['processed_docs_unchanged'] = sha(INPUT.read_bytes()) == input_hash
        save('api_usage.json', usage)
        client.close()
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', help='One model request, only after successful checks; persistent marker prevents repeat.')
    args = parser.parse_args()
    try:
        sys.exit(main(args.execute))
    except Exception as exc:
        # Deliberately avoid traceback/local-variable or client repr disclosure.
        if OUT.is_dir():
            save('preflight_error.json', {'error_type': type(exc).__name__, 'message': scrub(str(exc)), 'model_request_not_retried': True})
        print('STOP:', type(exc).__name__, '(see sanitized preflight_error.json)', flush=True)
        sys.exit(2)
