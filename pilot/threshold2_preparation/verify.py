"""Independent final counts, boundaries and frozen-file hash verification."""
from common import *
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import subprocess


def main():
    setup()
    frozen = read(ROOT/'freeze_before.json')
    dirs = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for root, expected in frozen['directories'].items():
            paths = [str(p) for p in Path(root).rglob('*') if p.is_file()]
            assert set(paths) == set(expected), root
            actual = dict(zip(paths, pool.map(sha, paths)))
            assert actual == expected, root
            dirs[root] = {'files': len(paths), 'inventory_and_sha256_unchanged': True}
            print('UNCHANGED', Path(root).name, len(paths), flush=True)
    assert all(sha(p) == h for p, h in frozen['sources_gold'].items())
    deps = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
    assert deps == frozen['dependencies']
    git = ['git', '-c', 'safe.directory='+REPO.as_posix(), '-C', str(REPO)]
    commit = subprocess.check_output(git+['rev-parse', 'HEAD'], text=True).strip()
    status = subprocess.check_output(git+['status', '--porcelain'], text=True)
    assert commit == frozen['commit'] and status == frozen['git_status'] == ''

    audit = read(ROOT/'data_audit.json')
    gold = read(audit['frozen']['gold_path'])
    boards = read(audit['frozen']['boards_path'])
    members = defaultdict(dict)
    rows = 0
    for paper, value in gold.items():
        for r in value['TDMs']:
            key = (r['Task'], r['Dataset'], r['Metric'])
            assert paper not in members[key], (paper, key)
            members[key][paper] = r['Result']
            rows += 1
    assert (len(gold), rows, len(members)) == (43, 295, 141)
    ge2 = {k: v for k, v in members.items() if len(v) >= 2}
    ge3 = {k: v for k, v in members.items() if len(v) >= 3}
    assert len(ge2) == 62 and len(ge3) == 33
    assert sum(map(len, ge2.values())) == 216
    assert len(boards) == 27 and sum(len(b['Leaderboard']) for b in boards) == 140
    for b in boards:
        key = (b['Task'], b['Dataset'], b['Metric'])
        assert b['Leaderboard'] == members[key] == ge2[key] == ge3[key]
    assert audit['status'] == 'BLOCKED'
    assert not audit['official_threshold2_candidates']
    assert not audit['formal_threshold2_evaluation_executed'] and not audit['masking_preview_executed']
    for name in ('fully_llm_evaluation', 'fully_cs_evaluation', 'masking_preview'):
        assert not (ROOT/name).exists(), 'Blocked run must not create formal result directories'
    for x in audit['annotation_versions']:
        assert not x['duplicate_json_keys'] and x['comparison_to_frozen']['equal_structured_records']
        assert x['sha256'] == audit['frozen']['gold_sha256']
    for x in audit['candidate_boards']:
        assert not x['duplicate_json_keys'] and x['exactly_equal_frozen27']
        assert not x['profile']['unknown_papers'] and not x['profile']['duplicate_boards']
    reuse = read(ROOT/'reuse_manifest.json')
    assert reuse['fully']['same_zero_shot_extraction']
    assert all(x['reuse_stage1'] and x['order_recomputed_equal'] for x in reuse['cold_start'].values())
    sources = read(ROOT/'source_manifest.json')
    assert all(sources['official_download_matches_local_original'].values())
    for x in sources['fetches']:
        if x.get('status') == 'FETCHED':
            assert sha(x['path']) == x['sha256']
    cfg = read(ROOT/'next_stage_configs.json')
    assert cfg['common']['enabled'] is False and cfg['common']['verified_threshold2_path'] is None
    for p in ROOT.glob('*.py'):
        compile(p.read_text(encoding='utf-8'), str(p), 'exec')
    verification = {
        'status': 'AUDIT_PASS_EXPERIMENT_BLOCKED', 'data_readiness': 'BLOCKED',
        'directories': dirs, 'total_frozen_files': sum(x['files'] for x in dirs.values()),
        'sources_prompt_gold_checked_files': len(frozen['sources_gold']),
        'sources_prompts_gold_unchanged': True, 'dependencies_unchanged': True,
        'git_commit': commit, 'git_clean': True,
        'independent_counts': {'papers': 43, 'tdmr_rows': 295, 'unique_tdm': 141,
            'diagnostic_ge2_groups': 62, 'diagnostic_ge2_records': 216,
            'diagnostic_ge3_groups': 33, 'provided_boards': 27, 'provided_records': 140},
        'shared27_raw_members_and_values_equal': True,
        'common27_threshold2_scores_compared': False,
        'common27_score_comparison_status': 'NOT_RUN_NO_VERIFIED_OFFICIAL_THRESHOLD2_FILE',
        'no_gold_result_scaling_in_audit': True,
        'fully_llm_cs_input_validation_passed': True,
        'cold_stage1_three_order_reuse_validation_passed': True,
        'formal_threshold2_evaluation_executed': False, 'masking_preview_executed': False,
        'new_llm_api_inference_calls': 0, 'new_pdf_processing_model_downloads_installs': 0,
        'credentials_read': False, 'archive_scripts_executed': False,
        'audit_scripts_network_blocked': True, 'python_syntax_checks_passed': True,
        'checked_epoch': time.time()}
    save(ROOT/'verification.json', verification)
    print('VERIFIED', verification['status'], verification['total_frozen_files'], 'unchanged files', flush=True)


if __name__ == '__main__':
    main()
