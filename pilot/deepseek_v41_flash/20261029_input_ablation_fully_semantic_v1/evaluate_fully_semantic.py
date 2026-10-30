"""Offline Fully prompt comparison. Exit 0 complete, 2 incomplete, 1 failed.

Use existing scilead Python with -E -s -B -X utf8. No runtime imports or APIs.
Only evaluation/ and analysis/ are writable. --fixture-prior-completed explicitly
reuses previous completed inputs and writes separate evaluation/fixtures/ output.
"""
import argparse
import ast
import contextlib
import copy
import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
EVALUATION = ROOT / 'evaluation'
PREVIOUS = ROOT.parent / '20261029_input_ablation'
SCILEAD = ROOT.parents[2]
REPO = SCILEAD / 'emnlp2024-leaderboard-generation'
GOLD = SCILEAD / 'pilot/autodl_setup/20261021/stage/data/gold/tdm_annotations.json'
BOARDS = GOLD.with_name('leaderboards.json')
OLD_ANALYSIS = ROOT.parent / '20261028/analysis'
TUPLE_HELPER = OLD_ANALYSIS / 'evaluate_offline.py'
BOARD_HELPER = OLD_ANALYSIS / 'evaluations/partially_stage2/leaderboard/evaluate_paper_metrics.py'
CANDIDATES = ROOT.parent / '20261028/candidate_sets.json'
SELECTED = ('D19-1367.pdf', '1901.10430.pdf', '1808.08745.pdf',
            '2020.emnlp-main.523.pdf', '1911.09483.pdf')
ARMS = {'baseline_rag': 'baseline_rag/merged', 'parsed_full': 'parsed_full/fully/merged',
        'page_images': 'page_images/fully/merged'}
FIELDS = ('Task', 'Dataset', 'Metric', 'Result')
METRICS = ('Task IIM', 'Dataset IIM', 'Metric IIM', 'Result IIM',
           'TDM Exact Match', 'TDMR Exact Match', 'Strict Result numeric equality')
PINS = {
    PREVIOUS/'evaluate_ablation.py': 'f7d0aef0d93b94831aeb7e02d8d997182e8211c9cd88a261fe91da363de5c252',
    PREVIOUS/'evaluation/report.json': '93190c71b9ec3094bd108925ee9846a36c2add5ca8420ba787eee1e684487b22',
    PREVIOUS/'evaluation/latest.json': 'ce2225bece0a4671c06607fe82172fdc0660bb9c45e654d25478f74d31b924fa',
    PREVIOUS/'selection_frozen.json': '66347cbc5e457e1570a3b81fc1ae78f4cc8728e0476a0c6850ac105e064701f0',
    CANDIDATES: '39b0834d70a48db407d6bd14b041915f6d274ebb2eb1a4e32fcf079eabdc47da',
}
BLOCKED_EVENTS = []
_INSTALLED = False


class Incomplete(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def decode_json(text):
    def invalid(value):
        raise ValueError('Nonfinite JSON number: ' + value)
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid)


def check_read(path):
    text = os.fsdecode(path)
    if text.startswith(('\\\\', '//')):
        raise PermissionError('Network filesystem paths prohibited')
    p = Path(text)
    name = p.name.lower()
    if (name == '.env' or name.startswith('.env.') or name.endswith('.env')
            or name in ('id_rsa', 'id_ed25519', 'credentials', 'credentials.json', '.netrc')
            or name.endswith(('.pem', '.p12', '.key'))
            or any(x.lower() in ('.aws', '.ssh', '.azure') for x in p.parts)):
        raise PermissionError('Credential files prohibited')


def read(path):
    check_read(path)
    return decode_json(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    check_read(path)
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def writable(path):
    check_read(path)
    p = Path(path).resolve()
    if not any(p.is_relative_to(base.resolve()) for base in (EVALUATION, ROOT/'analysis')):
        raise PermissionError('Writes restricted to new evaluation/ and analysis/')
    return p


def save(path, value, frozen=False):
    path = writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if frozen and path.exists():
        if read(path) != value:
            raise ValueError('Frozen scope changed: ' + str(path))
        return
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    with temp.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    temp.replace(path)


def install_boundary():
    global _INSTALLED
    if _INSTALLED:
        return
    # Dependencies may consult environment options, but receive no inherited values.
    # No getenv/environ contents are read or logged, and no real env is modified.
    os.environ = {}
    if hasattr(os, 'environb'):
        os.environb = {}
    blocked_imports = {'torch', 'transformers', 'tensorflow', 'openai', 'anthropic',
                       'langchain', 'langchain_openai', 'sentence_transformers',
                       'requests', 'httpx', 'dotenv', 'transport', 'normalize_fully', 'frozen_runner'}

    def guard(event, args):
        prohibited = (event.startswith('socket.') or event.startswith('subprocess.')
                      or event in ('os.system', 'os.posix_spawn', 'os.spawn', 'os.exec',
                                   'os.putenv', 'os.unsetenv'))
        if event == 'import' and args[0].split('.')[0] in blocked_imports:
            prohibited = True
        if prohibited:
            BLOCKED_EVENTS.append(event)
            raise PermissionError('Offline evaluator prohibits ' + event)
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            check_read(args[0])
            mode, flags = args[1] or '', args[2] or 0
            if any(c in mode for c in 'wax+') or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                writable(args[0])
        if event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime', 'os.truncate'):
            writable(args[0])
        if event in ('os.rename', 'os.replace', 'os.link', 'os.symlink'):
            writable(args[0]); writable(args[1])
    sys.addaudithook(guard)
    _INSTALLED = True


def check_hashes(hashes):
    for path, expected in hashes.items():
        if sha(path) != expected:
            raise ValueError('Frozen SHA256 mismatch: ' + str(path))


def load_core():
    """Compile only existing function definitions; never run old module top level."""
    check_hashes(PINS)
    previous = read(PREVIOUS/'evaluation/report.json')
    check_hashes(previous['protected_sha256'])
    namespace = dict(globals())
    names = {'load_pure_helpers', 'derive_boards', 'raw_view', 'scope_inputs',
             'official_modules', 'evaluate_stage'}
    path = PREVIOUS/'evaluate_ablation.py'
    tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in functions} != names:
        raise ValueError('Previous evaluator function contract changed')
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), namespace)
    namespace['HELPERS'] = namespace['load_pure_helpers']()
    for name in ('metric', 'number', 'strict_metric'):
        namespace[name] = namespace['HELPERS'][name]
    return SimpleNamespace(**namespace)


def verify_reference(core):
    previous = read(PREVIOUS/'evaluation/report.json')
    latest = read(PREVIOUS/'evaluation/latest.json')
    protected = {str(p): h for p,h in PINS.items()}
    protected.update(previous['protected_sha256'])
    protected[latest['report']] = PINS[PREVIOUS/'evaluation/report.json']
    if (previous['status'] != 'COMPLETE' or latest['status'] != 'COMPLETE'
            or not previous['all_three_arms_complete'] or not previous['protected_files_unchanged']):
        raise ValueError('Previous verified evaluation is not complete')
    selected = tuple(x['paper_id'] for x in read(PREVIOUS/'selection_frozen.json')['selected'])
    if selected != SELECTED or previous['scope']['selected_ids'] != list(SELECTED):
        raise ValueError('Frozen five-paper selection mismatch')
    gold, boards = read(GOLD), read(BOARDS)
    derived, scope = core.derive_boards(boards, SELECTED)
    counts = (len(gold), sum(len(v['TDMs']) for v in gold.values()), len(boards),
              sum(len(gold[p]['TDMs']) for p in SELECTED), len(derived),
              sum(len(b['Leaderboard']) for b in derived), scope['singleton_boards'])
    if counts != (43, 295, 27, 28, 10, 14, 6):
        raise ValueError('Frozen scope must be 43/295/27; selected 5/28/10/14/6')
    serialized = read(CANDIDATES)
    candidates = {k: ast.literal_eval(v) for k,v in serialized.items()}
    if {k:len(v) for k,v in candidates.items()} != {'Task':23, 'Dataset':71, 'Metric':26}:
        raise ValueError('Frozen candidate count mismatch')
    for key in FIELDS[:3]:
        if candidates[key] != {r[key] for p in gold.values() for r in p['TDMs']}:
            raise ValueError('Frozen candidates differ from full Gold: ' + key)
    for name, folder in ARMS.items():
        old = previous['arms'][name]
        if old['status'] != 'COMPLETE' or old['stages']['fullyllm']['evaluated_ids'] != list(SELECTED):
            raise ValueError('Previous arm is not complete: ' + name)
        protected.update(old['input_sha256'])
        check_hashes(old['input_sha256'])
        if validate_inputs(read(PREVIOUS/folder/'output.json'), read(PREVIOUS/folder/'normalized_output.json'), core, candidates)['status'] != 'COMPLETE':
            raise ValueError('Previous arm inputs are incomplete: ' + name)
    check_hashes(protected)
    return previous, protected, candidates


def validate_inputs(raw, normalized, core, candidates):
    for name, data in [('raw', raw), ('normalized', normalized)]:
        if not isinstance(data, dict):
            raise ValueError(name + ' must be a paper-ID object')
        if set(data)-set(SELECTED):
            raise ValueError('Unexpected ' + name + ' paper IDs')
        for paper, entry in data.items():
            if not isinstance(entry, dict) or not isinstance(entry.get('source_documents'), list):
                raise ValueError(paper + ': missing/invalid source_documents')
    scoped, coverage = core.scope_inputs(raw, normalized, SELECTED)
    for paper, entry in scoped.items():
        before = core.raw_view({paper:raw[paper]}, [paper])[paper]['normalized_output']
        for index, (source, row) in enumerate(zip(before, entry['normalized_output'])):
            if set(row) != set(FIELDS) or set(source) != set(FIELDS):
                raise ValueError(paper + ': expected exactly four tuple fields')
            for field in FIELDS[:3]:
                if row[field] is not None and row[field] not in candidates[field]:
                    raise ValueError(f'{paper} row {index} {field}: label outside frozen candidates')
                if source[field] in candidates[field] and row[field] != source[field]:
                    raise ValueError(f'{paper} row {index} {field}: already-valid label changed')
    coverage['tuple_scope'] = 'Exactly all five selected papers required; partial metrics withheld.'
    return coverage


def metrics_view(stage):
    return {'tuple': stage['aggregate'], 'leaderboard': stage['leaderboard']['aggregate'],
            'per_paper': stage['per_paper'],
            'mean_per_paper_f1_SEPARATE': stage['mean_per_paper_f1_SEPARATE']}


def difference(old, new):
    if isinstance(old, dict):
        if set(old) != set(new):
            raise ValueError('Metric schema mismatch')
        return {k:difference(old[k], new[k]) for k in old}
    return new-old


def compare(old, new):
    complete = all(s['status'] == 'COMPLETE' and set(s.get('evaluated_ids', [])) == set(SELECTED) for s in (old,new))
    return {'status': 'COMPLETE' if complete else 'UNAVAILABLE',
            'prompt_comparison_same_extraction': True,
            'interpretation': 'Old zero-shot Fully LLM versus enhanced Fully LLM prompt; same extraction, fixed candidates and original None fallback; no joint TDM stage.',
            'delta_direction': 'enhanced minus old; raw fractions, not percentage points',
            'delta': difference(metrics_view(old), metrics_view(new)) if complete else None}


def binding_changes(raw, old, new):
    counts = {f:0 for f in FIELDS[:3]}
    per_paper, rows = {}, []
    for paper in SELECTED:
        per_paper[paper] = {f:0 for f in FIELDS[:3]}
        source = json.loads(raw[paper]['output'])
        for index,(before,after) in enumerate(zip(old[paper]['normalized_output'],new[paper]['normalized_output'])):
            changes = {f:{'raw':source[index][f], 'old':before[f], 'new':after[f]}
                       for f in FIELDS[:3] if before[f] != after[f]}
            for f in changes:
                counts[f] += 1; per_paper[paper][f] += 1
            if changes:
                rows.append({'paper_id':paper, 'row_index_zero_based':index,
                             'Result':after['Result'], 'changes':changes,
                             'old_TDM':{f:before[f] for f in FIELDS[:3]},
                             'new_TDM':{f:after[f] for f in FIELDS[:3]}})
    return {'changed_fields':sum(counts.values()), 'changed_rows':len(rows),
            'counts_by_field':counts, 'per_paper':per_paper, 'rows':rows,
            'result_and_source_documents_unchanged':True}


def snapshot(path, observed, expected=None):
    path = Path(path)
    check_read(path)
    if not path.exists():
        observed[str(path)] = None
        raise Incomplete('Missing artifact: ' + str(path))
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    observed[str(path)] = digest
    if expected is not None and digest != expected:
        raise ValueError('Frozen byte-copy mismatch: ' + str(path))
    try:
        return decode_json(content.decode('utf-8-sig'))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise Incomplete('Artifact JSON not ready: ' + str(path)) from error


def changed_inputs(observed):
    return [p for p,h in observed.items() if (sha(p) if Path(p).exists() else None) != h]


def empty_stage(status, reason):
    return {'status':status, 'reason':reason, 'evaluated_ids':[],
            'tuple_macro_denominator':0, 'aggregate':{}, 'per_paper':{}, 'leaderboard':None}


def evaluate_arm(name, run, core, previous, candidates, board_path, fixture, observed, setup_error):
    old = copy.deepcopy(previous['arms'][name]['stages']['fullyllm'])
    previous_dir = PREVIOUS/ARMS[name]
    source = previous_dir if fixture else ROOT/name/'merged'
    paths = {'raw':source/'output.json', 'normalized':source/'normalized_output.json',
             'previous_normalized':previous_dir/'normalized_output.json' if fixture else ROOT/name/'previous_normalized_output.json'}
    out = run/name
    out.mkdir(parents=True)
    result = {'arm':name, 'status':'INCOMPLETE', 'old_fully':old,
              'enhanced_fully':empty_stage('INCOMPLETE','Inputs not ready'),
              'input_paths':{k:str(p) for k,p in paths.items()}, 'field_binding_changes':None}
    try:
        if setup_error is not None:
            raise setup_error
        raw = snapshot(paths['raw'], observed, previous['arms'][name]['input_sha256'][str(previous_dir/'output.json')])
        previous_norm = snapshot(paths['previous_normalized'], observed, previous['arms'][name]['input_sha256'][str(previous_dir/'normalized_output.json')])
        norm = snapshot(paths['normalized'], observed)
        coverage = validate_inputs(raw, norm, core, candidates)
        result['coverage'] = coverage
        if coverage['status'] != 'COMPLETE':
            raise Incomplete('Not all five selected papers have normalized outputs; metrics withheld')
        if changed_inputs(observed):
            raise Incomplete('Inputs changed during snapshot; rerun after producer finishes')
        with core.official_modules() as official:
            result['enhanced_fully'] = core.evaluate_stage(out/'enhanced_fully', norm, read(GOLD), board_path, SELECTED, official)
        result['field_binding_changes'] = binding_changes(raw, previous_norm, norm)
        if fixture:
            for key in ('aggregate','per_paper','leaderboard','mean_per_paper_f1_SEPARATE'):
                if old[key] != result['enhanced_fully'][key]:
                    raise ValueError('Fixture parity mismatch: ' + name + '/' + key)
        result['status'] = 'COMPLETE'
    except Incomplete as error:
        result['enhanced_fully'] = empty_stage('INCOMPLETE', str(error))
    except Exception as error:
        result['status'] = 'FAILED'
        result['enhanced_fully'] = empty_stage('FAILED', type(error).__name__ + ': ' + str(error))
    result['comparison'] = compare(old, result['enhanced_fully'])
    save(out/'report.json', result)
    return result


def run_evaluation(arm_names, fixture=False):
    install_boundary()
    destination = EVALUATION/'fixtures' if fixture else EVALUATION
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')+'_'+uuid.uuid4().hex[:6]
    run = destination/'runs'/stamp
    run.mkdir(parents=True)
    report = {'schema_version':1, 'status':'FAILED', 'fixture':fixture, 'run_directory':str(run),
              'new_api_requests':0, 'all_three_arms_complete':False, 'fixture_parity_verified':False,
              'arm_results':{}, 'completion_scope':'Requested arms with exactly five stable paper artifacts; not producer job status.',
              'normalization_strategy':'Fully LLM; zero-shot original versus enhanced prompt; fixed candidates; None fallback.',
              'network_attempts':[], 'protected_files_unchanged':False}
    observed = {}
    try:
        core = load_core()
        previous, protected, candidates = verify_reference(core)
        protected[str(Path(__file__).resolve())] = sha(__file__)
        setup_error = None
        try:
            selection_path = PREVIOUS/'selection_frozen.json' if fixture else ROOT/'selection_frozen.json'
            snapshot(selection_path, observed, PINS[PREVIOUS/'selection_frozen.json'])
            if not fixture:
                snapshot(ROOT/'candidate_sets.json', observed, PINS[CANDIDATES])
        except (Incomplete, ValueError) as error:
            setup_error = error
        boards, board_scope = core.derive_boards(read(BOARDS), SELECTED)
        board_path = run/'scope/leaderboards_selected.json'
        save(board_path, boards)
        scope = dict(previous['scope'], selected_ids=list(SELECTED), board_memberships=14,
                     derived_boards_path=str(board_path), derived_boards_sha256=sha(board_path),
                     candidate_sizes={k:len(v) for k,v in candidates.items()},
                     candidate_sets_sha256=PINS[CANDIDATES], stage2_added=False, **board_scope)
        save(run/'scope/manifest.json', scope)
        protected[str(board_path)] = sha(board_path)
        results = {name:evaluate_arm(name,run,core,previous,candidates,board_path,fixture,observed,setup_error) for name in arm_names}
        changed = changed_inputs(observed)
        try:
            check_hashes(protected)
            protected_ok = True
        except (OSError, ValueError):
            protected_ok = False
        if changed or not protected_ok:
            for name,value in results.items():
                value['status'] = 'FAILED'
                value['enhanced_fully'] = empty_stage('FAILED','Input or protected source changed during evaluation; discard this run')
                value['comparison'] = compare(value['old_fully'],value['enhanced_fully'])
                value['field_binding_changes'] = None
                save(run/name/'report.json',value)
                if (run/name/'enhanced_fully').exists():
                    save(run/name/'enhanced_fully/report.json',value['enhanced_fully'])
        status = 'FAILED' if any(x['status']=='FAILED' for x in results.values()) else ('COMPLETE' if all(x['status']=='COMPLETE' for x in results.values()) else 'INCOMPLETE')
        report.update(status=('FIXTURE_COMPLETE' if fixture and status=='COMPLETE' else status),
                      scope=scope, arm_results=results, protected_sha256=protected,
                      input_sha256=observed, changed_inputs=changed,
                      protected_files_unchanged=protected_ok, fixture_parity_verified=fixture and status=='COMPLETE',
                      all_three_arms_complete=not fixture and len(results)==3 and status=='COMPLETE')
    except Exception as error:
        report.update(error_type=type(error).__name__, error=str(error))
    report['network_attempts'] = [x for x in BLOCKED_EVENTS if x.startswith('socket.')]
    report['offline_audit'] = {'new_api_requests':0, 'inherited_environment_available':False,
                               'credential_files_prohibited':True, 'subprocesses_prohibited':True,
                               'blocked_events':list(BLOCKED_EVENTS), 'python':sys.executable}
    # Both names intentionally expose the same schema to the main report writer.
    save(run/'report.json', report)
    save(run/'comparison.json', report)
    save(destination/'report.json', report)
    save(destination/'comparison.json', report)
    save(destination/'latest.json', {'report':str(run/'report.json'), 'comparison':str(run/'comparison.json'),
                                   'status':report['status'], 'fixture':fixture, 'new_api_requests':0})
    print(json.dumps({'status':report['status'], 'report':str(run/'report.json'),
                      'comparison':str(destination/'comparison.json'),
                      'arms':{k:v['status'] for k,v in report['arm_results'].items()}, 'new_api_requests':0}))
    return 0 if report['status'] in ('COMPLETE','FIXTURE_COMPLETE') else 2 if report['status']=='INCOMPLETE' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arms', nargs='+', choices=list(ARMS), default=list(ARMS))
    parser.add_argument('--fixture-prior-completed', action='store_true', help='Explicit old-input parity fixture; separate output pointers')
    args = parser.parse_args()
    raise SystemExit(run_evaluation(list(dict.fromkeys(args.arms)), args.fixture_prior_completed))
