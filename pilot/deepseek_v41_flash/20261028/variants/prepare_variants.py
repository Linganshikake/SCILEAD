"""Wait for complete Fully outputs, then freeze independent variant inputs. No API/model."""
import argparse
import importlib.metadata
import json
import random
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from runtime_policy import OWNED, offline_guard, owned
import variant_runtime as v

REFERENCE = v.PILOT / 'gpt56_sol_variants/20261024'
BRANCHES = (('partially', None), ('cold_default', None), ('cold_0', '0'), ('cold_42', '42'))
FIELDS = ('Task', 'Dataset', 'Metric')


def paper_order(order, seed):
    return list(order) if seed is None else random.Random(seed).sample(list(order), len(order))


def completed_inputs(source, normalized_source, order):
    """None means incomplete publication. Incompatible completed data raises, never repairs."""
    try:
        raw = v.read(source)
        normalized = v.read(normalized_source)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict) or not isinstance(normalized, dict):
        raise ValueError('Fully files must be paper-keyed objects')
    if set(raw) != set(order) or set(normalized) != set(order):
        return None
    for paper in order:
        if not all(k in raw[paper] for k in ('output', 'source_documents')):
            return None
        if not all(k in normalized[paper] for k in ('normalized_output', 'source_documents')):
            return None
        rows = json.loads(raw[paper]['output'])
        nr = normalized[paper]['normalized_output']
        if not isinstance(rows, list) or not isinstance(nr, list):
            raise ValueError('Fully prediction rows must be arrays')
        if len(rows) != len(nr) or raw[paper]['source_documents'] != normalized[paper]['source_documents']:
            return None
        for row, nrow in zip(rows, nr):
            if not isinstance(row, dict) or set(row) != {*FIELDS, 'Result'}:
                raise ValueError('Fully extraction must have exactly Task/Dataset/Metric/Result')
            if not all(isinstance(x, str) for x in row.values()):
                raise ValueError('Fully extraction values must be strings; use main\'s compatible output')
            if not isinstance(nrow, dict) or set(nrow) != {*FIELDS, 'Result'}:
                raise ValueError('Fully normalization must have exactly Task/Dataset/Metric/Result')
            if any(nrow[k] is not None and not isinstance(nrow[k], str) for k in FIELDS):
                raise ValueError('Normalized labels must be strings or null')
            if row['Result'] != nrow['Result']:
                raise ValueError('Fully normalization changed Result')
    return ({p: raw[p] for p in order}, {p: normalized[p] for p in order})


def copy_frozen(source, target):
    source, target = Path(source), owned(target)
    if target.exists():
        assert v.sha(target) == v.sha(source), 'FROZEN_COPY_CHANGED: ' + str(target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def prepare(source, normalized_source, output_dir=OWNED, reference=REFERENCE, scope=None, verification=None):
    out, reference = owned(output_dir), Path(reference).resolve()
    source, normalized_source = Path(source).resolve(), Path(normalized_source).resolve()
    order_path = reference / 'partially/paper_order.json'
    order = v.read(order_path)['papers']
    verification = Path(verification) if verification is not None else source.parent.parent / 'verification.json'
    try:
        marker = v.read(verification)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if (marker.get('complete_papers') != len(order) or marker.get('state') not in ('QUEUE_FINISHED', 'COMPLETE', 'CHECKPOINT')
            or marker.get('protected_files_changed') != [] or marker.get('secret_scan_passed') is not True
            or marker.get('stop') is not None):
        return None
    # Hash/read/hash prevents freezing files replaced while being read.
    if not source.is_file() or not normalized_source.is_file():
        return None
    source_hashes = {str(p): v.sha(p) for p in (source, normalized_source)}
    complete = completed_inputs(source, normalized_source, order)
    if complete is None:
        return None
    assert source_hashes == {str(p): v.sha(p) for p in (source, normalized_source)}, 'FULLY_CHANGED_DURING_READ'
    raw, normalized = complete
    if marker.get('records') != sum(len(json.loads(x['output'])) for x in raw.values()):
        return None
    if (out / 'experiment_manifest.json').exists():
        manifest = v.read(out / 'experiment_manifest.json')
        assert manifest['source_hashes'] == source_hashes, 'PREPARED_INPUT_CHANGED'
        for p, h in v.read(out / 'protected_hashes.json').items():
            assert v.sha(p) == h, 'FROZEN_SOURCE_CHANGED: ' + p
        return manifest

    legacy = v.read(reference / 'partially/config.json')
    gold_source, boards_source = Path(legacy['gold_path']), Path(legacy['leaderboards_path'])
    protected = [source, normalized_source, verification, order_path, reference / 'partially/config.json']
    if scope is not None:
        scope = Path(scope).resolve()
        scoped = v.read(scope)
        current_gold, current_boards = Path(scoped['gold_path']), Path(scoped['leaderboard_path'])
        assert v.sha(current_gold) == scoped['gold_sha256']
        assert v.sha(current_boards) == scoped['leaderboard_sha256']
        assert v.read(current_gold) == v.read(gold_source) and list(v.read(current_gold)) == list(v.read(gold_source)), 'GOLD_SCOPE_CHANGED'
        assert v.read(current_boards) == v.read(boards_source), 'LEADERBOARD_SCOPE_CHANGED'
        protected += [scope, gold_source, boards_source]
        gold_source, boards_source = current_gold, current_boards
    gold, boards = v.read(gold_source), v.read(boards_source)
    assert set(gold) == set(order), 'FROZEN_PAPER_SCOPE_CHANGED'
    generation = {k: x for k, x in v.frozen.payload([]).items() if k != 'messages'}
    assert generation == {'model': v.MODEL, 'thinking': {'type': 'enabled'}, 'reasoning_effort': 'high', 'stream': False}, 'TRANSPORT_CONFIG_DRIFT'
    out.mkdir(parents=True, exist_ok=True)
    v.immutable(out / 'inputs/output.json', raw)
    v.immutable(out / 'merged/output.json', raw)
    v.immutable(out / 'inputs/normalized_output.json', normalized)
    v.immutable(out / 'merged/normalized_output.json', normalized)
    gold_path, boards_path = out / 'inputs/gold.json', out / 'inputs/leaderboards.json'
    copy_frozen(gold_source, gold_path)
    copy_frozen(boards_source, boards_path)
    for name in ('masking/initial_labels.json', 'masking/partially_masked_leaderboards.json',
                 'references/cold_initial_labels.json'):
        copy_frozen(reference / name, out / name)
        protected += [reference / name, out / name]
    for name, seed in BRANCHES:
        cold = name.startswith('cold_')
        ordered = paper_order(order, seed)
        legacy_order = reference / name / 'paper_order.json'
        assert ordered == v.read(legacy_order)['papers'], 'FROZEN_ORDER_CHANGED: ' + name
        conf = dict(run_id=name, model=v.MODEL, generation=generation, api_base=v.URL,
                    cold_start=cold, cold_start_seed=seed, cold_start_seed_type=type(seed).__name__,
                    masking_seed=0, python_hash_seed=0, gold_path=str(gold_path),
                    leaderboards_path=str(boards_path), input_path=str(out / 'inputs/output.json'),
                    input_sha256=v.sha(out / 'inputs/output.json'), paper_order=ordered,
                    original_default_output_budgets={'stage1': 15, 'stage2': 100},
                    override='Parent DeepSeek transport settings; omit all client output caps',
                    automatic_retries=0, semantic_cache=False)
        v.immutable(out / name / 'config.json', conf)
        v.immutable(out / name / 'official_config.json', {'model_type': 'gpt4-turbo-128k', 'actual_request_model': v.MODEL})
        v.immutable(out / name / 'paper_order.json', {'papers': ordered, 'legacy_order_source': str(legacy_order), 'cold_start_seed': seed})
        protected += [legacy_order, out / name / 'config.json', out / name / 'official_config.json']
    rows = [r for x in raw.values() for r in json.loads(x['output'])]
    labels = {k: set() for k in FIELDS}
    for value in gold.values():
        for tdm in value['TDMs']:
            for k in FIELDS:
                labels[k].add(tdm[k])
    labels = {k: list(values) for k, values in labels.items()}
    assert labels == v.read(reference / 'fully_cs/candidate_labels.json')['labels'], 'CS_CANDIDATE_ORDER_CHANGED'
    cs = out / 'fully_cs'
    for name in ('candidate_labels.json',):
        copy_frozen(reference / 'fully_cs' / name, cs / name)
        protected += [reference / 'fully_cs' / name, cs / name]
    resource_policy = v.read(reference / 'fully_cs/resource_policy.json')
    resource_policy.update(minimum_physical_GiB=4.0,
                           basis='User-requested 4 GiB available RAM minimum; retain existing 7.5 GiB commit gate. Run CS alone before API branches.')
    v.immutable(cs / 'resource_policy.json', resource_policy)
    protected += [reference / 'fully_cs/resource_policy.json', cs / 'resource_policy.json']
    mm = v.read(reference / 'fully_cs/model_manifest.json')
    mm.pop('actual_runtime', None)
    mm.update(current_run_model_hashes_verified=False, validation='Deferred to explicit CS execution',
              embedding_cache_reused=False, model_downloads=0)
    v.immutable(cs / 'model_manifest.json', mm)
    # Existing implementation cache only; no weights, embeddings, downloads or model load.
    for p in (reference / 'fully_cs/runtime/huggingface').rglob('*'):
        if p.is_file() and p.suffix in ('.py', '.json', '.txt') and '__pycache__' not in p.parts:
            dest = cs / 'runtime/huggingface' / p.relative_to(reference / 'fully_cs/runtime/huggingface')
            copy_frozen(p, dest)
            protected += [p, dest]
    for name in ('work/output.json', 'merged/output.json'):
        v.immutable(cs / name, raw)
    cs_config = v.read(reference / 'fully_cs/config.json')
    for name in ('started_epoch', 'memory_before', 'disk_free'):
        cs_config.pop(name, None)
    exact = sum(r[k] in labels[k] for r in rows for k in FIELDS)
    cs_config.update(gold_path=str(gold_path), gold_leaderboards_path=str(boards_path),
                     input_path=str(out / 'inputs/output.json'), input_sha256=v.sha(out / 'inputs/output.json'),
                     papers=len(raw), gold_tdmrs=sum(len(x['TDMs']) for x in gold.values()), raw_records=len(rows),
                     expected_cs_fields=len(FIELDS) * len(rows) - exact, expected_exact_fields=exact,
                     candidate_counts={k: len(x) for k, x in labels.items()},
                     gold_leaderboards=len(boards), gold_leaderboard_records=sum(len(b['Leaderboard']) for b in boards),
                     generation_model=v.MODEL)
    v.immutable(cs / 'config.json', cs_config)
    dependencies = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
    v.immutable(out / 'reproducibility/dependency_versions.json', dependencies)
    v.immutable(out / 'input_manifest.json', [dict(paper_id=p, records=len(json.loads(raw[p]['output'])),
                gold_records=len(gold[p]['TDMs']), per_paper_content_sha256=v.digest(raw[p]),
                source_documents_sha256=v.digest(raw[p]['source_documents'])) for p in order])
    v.immutable(out / 'generation_config.json', generation)
    protected += [gold_source, boards_source, gold_path, boards_path, v.TRANSPORT_PATH,
                  reference / 'variant_runtime.py', reference / 'prepare_variants.py',
                  reference / 'fully_cs/cs_common.py', reference / 'fully_cs/run_cs.py',
                  reference / 'fully_cs/model_manifest.json', reference / 'fully_cs/config.json',
                  cs / 'model_manifest.json', cs / 'config.json', cs / 'work/output.json',
                  out / 'inputs/output.json', out / 'inputs/normalized_output.json',
                  v.PILOT / 'full43_partially/engine.py', v.PILOT / 'full43_cold_start/engine.py']
    protected += [p for p in v.REPO.iterdir() if p.is_file() and p.suffix in ('.py', '.json', '.md', '.txt')]
    hashes = {str(p): v.sha(p) for p in protected}
    v.immutable(out / 'protected_hashes.json', hashes)
    v.immutable(out / 'critical_paths.json', list(hashes))
    manifest = dict(status='PREPARED', created_utc=v.frozen.now(), model=v.MODEL,
                    source=str(source), normalized_source=str(normalized_source), source_hashes=source_hashes,
                    papers=len(raw), gold_records=cs_config['gold_tdmrs'], predictions=len(rows),
                    gold_boards=len(boards), masked_boards=len(v.read(out / 'masking/partially_masked_leaderboards.json')),
                    paper_order_reference=str(order_path), input_paper_reorder_only=list(v.read(source)) != order,
                    per_paper_content_unchanged=True, scenarios=['fully_cs'] + [name for name, _ in BRANCHES],
                    generation=generation, maximum_method_positions=len(BRANCHES) * len(rows) * (len(FIELDS) + 1),
                    new_extraction_requests=0, model_loaded=False, semantic_cache=False,
                    protected_file_count=len(hashes), reference=str(reference))
    v.immutable(out / 'experiment_manifest.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fully-output', type=Path, default=OWNED.parent / 'fully/merged/output.json')
    parser.add_argument('--fully-normalized', type=Path, default=OWNED.parent / 'fully/merged/normalized_output.json')
    parser.add_argument('--fully-verification', type=Path, default=OWNED.parent / 'fully/verification.json')
    parser.add_argument('--output-dir', type=Path, default=OWNED)
    parser.add_argument('--reference', type=Path, default=REFERENCE)
    parser.add_argument('--scope', type=Path, default=OWNED.parent / 'evaluation_scope.json')
    parser.add_argument('--poll-seconds', type=float, default=15)
    parser.add_argument('--timeout-seconds', type=float, default=0, help='0 waits indefinitely')
    parser.add_argument('--no-wait', action='store_true', help='Exit 2 while inputs are incomplete')
    args = parser.parse_args()
    if not 0 < args.poll_seconds <= 60 or args.timeout_seconds < 0:
        parser.error('poll-seconds must be in (0, 60]; timeout-seconds must be nonnegative')
    assert __import__('os').environ.get('PYTHONHASHSEED') == '0', 'PYTHONHASHSEED must be 0 before interpreter starts'
    offline_guard()
    started = time.monotonic()
    while True:
        result = prepare(args.fully_output, args.fully_normalized, args.output_dir, args.reference, args.scope, args.fully_verification)
        if result is not None:
            print(json.dumps({k: result[k] for k in ('status', 'papers', 'predictions', 'gold_records', 'model_loaded')}), flush=True)
            return 0
        print(json.dumps({'status': 'WAITING_FOR_COMPLETE_FULLY', 'output': str(args.fully_output), 'normalized': str(args.fully_normalized)}), flush=True)
        if args.no_wait or (args.timeout_seconds and time.monotonic() - started >= args.timeout_seconds):
            return 2
        time.sleep(args.poll_seconds)


if __name__ == '__main__':
    sys.exit(main())
