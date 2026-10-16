"""Read-only frozen-input and dependency audit. No model imports or calls."""
from common import *
import ast
import random


def entry(path):
    path = Path(path)
    return {'path': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}


def validate_normalized(raw, normalized):
    assert set(raw) == set(normalized) and len(raw) == 43
    per_paper = {}
    for paper, prediction in raw.items():
        rows = json.loads(prediction['output'])
        mapped = normalized[paper]['normalized_output']
        assert len(rows) == len(mapped), paper
        assert [x['Result'] for x in rows] == [x['Result'] for x in mapped], paper
        assert all(isinstance(x['Result'], str) for x in mapped), paper
        assert all(set(x) == {'Task', 'Dataset', 'Metric', 'Result'} for x in mapped), paper
        assert prediction['source_documents'] == normalized[paper]['source_documents'], paper
        per_paper[paper] = {'records': len(rows), 'result_strings_order_sources_unchanged': True}
    assert sum(x['records'] for x in per_paper.values()) == 284
    return {'papers': 43, 'records': 284, 'per_paper': per_paper}


def main():
    setup()
    audit = read(ROOT/'data_audit.json')
    assert audit['status'] == 'BLOCKED'  # This preparation never enables model execution.
    am = read(PILOT/'full43_uncapped/manifest.json')
    bm = read(PILOT/'full43_cs/manifest.json')
    invocation = read(PILOT/'leaderboard_eval_full43_uncapped/official/invocation.json')
    raw_path = Path(bm['extraction_source'])
    a_path = Path(invocation['normalized_output_file'])
    b_path = Path(bm['normalization_output'])
    raw, a, b = read(raw_path), read(a_path), read(b_path)
    assert set(raw) == set(read(am['gold_path']))
    assert am['gold_path'] == bm['gold_path'] == audit['frozen']['gold_path']
    assert sha(am['gold_path']) == am['gold_sha256']
    a_index, b_index = [], []
    assert len(am['papers']) == len(bm['papers']) == 43
    assert {x['id'] for x in am['papers']} == {x['id'] for x in bm['papers']} == set(raw)
    for row in am['papers']:
        paper = row['id']
        ep = Path(row['extraction_dir'])/'output.json'
        np = Path(row['normalization_dir'])/'normalized_output.json'
        assert read(ep)[paper] == raw[paper], paper
        assert read(np)[paper] == a[paper], paper
        a_index.append({'paper': paper, 'extraction': entry(ep), 'normalization': entry(np)})
    for row in bm['papers']:
        np = Path(row['checkpoint'])/'output.json'
        assert read(np)[row['id']] == b[row['id']]
        b_index.append({'paper': row['id'], 'normalization': entry(np)})
    fully = {'raw': entry(raw_path), 'same_zero_shot_extraction': True,
             'llm': {'input': entry(a_path), 'validation': validate_normalized(raw, a), 'index': a_index},
             'cs': {'input': entry(b_path), 'validation': validate_normalized(raw, b), 'index': b_index}}
    refs = {}
    for label, path, prediction in (
        ('fully_llm', PILOT/'leaderboard_eval_full43_uncapped/paper_metrics/leaderboard_metrics.json', a_path),
        ('fully_cs', PILOT/'full43_cs/leaderboard_evaluation/paper_metrics/leaderboard_metrics.json', b_path)):
        value = read(path)
        assert value['sources']['prediction_sha256'] == sha(prediction)
        assert value['sources']['gold_sha256'] == audit['frozen']['boards_sha256']
        refs[label] = {'frozen_reference': entry(path), 'aggregate': value['aggregate'],
                       'conventions': value['conventions'], 'copied_reference_only_not_recomputed': True}
    save(ROOT/'threshold3_frozen_reference.json', refs)

    src = REPO/'tdm_llm_masked_normalization.py'
    source = src.read_text(encoding='utf-8')
    tree = ast.parse(source)
    fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'sample_tdms')
    branch = next(x for x in fn.body if isinstance(x, ast.If))
    assert ast.unparse(branch.test) == 'not cold_start'
    # Cold branch writes a sidecar but never mutates candidate labels or uses Gold rows.
    cold_names = {x.id for s in branch.orelse for x in ast.walk(s) if isinstance(x, ast.Name)}
    assert not {'labels_dict', 'gold_data'} & cold_names
    main_fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'main')
    later_board_refs = [x.lineno for x in ast.walk(main_fn)
                        if isinstance(x, ast.Name) and x.id == 'gold_leaderboards']
    assert sorted(later_board_refs) == [66, 81]
    source_evidence = {'masked_normalization': entry(src),
        'leaderboard_normalization': entry(REPO/'leaderboard_llm_normalization.py'),
        'prompts': entry(REPO/'prompts.json'),
        'sample_tdms_lines': [fn.lineno, fn.end_lineno],
        'cold_branch_candidate_set_mutations': False,
        'main_gold_leaderboards_reference_lines': sorted(later_board_refs),
        'cold_stage1_independent_of_target_boards': True,
        'cold_stage1_reason': 'Initial Task/Dataset/Metric sets are empty; boards are only written to a masking sidecar. Subsequent model inputs depend on raw predictions, candidate-state, prompt and order, not target boards.',
        'partially_requires_new_stage1': True,
        'stage2_target_dependency': 'leaderboard_llm_normalization.py:17-23 builds candidates from ALL supplied target boards; both Partially and Cold stage2 must run against the new verified artifact.'}

    cold_index = read(PILOT/'full43_cold_start/output_index.json')
    cold = {}
    for order, index in cold_index.items():
        cfg = read(index['config'])
        order_info = read(index['paper_order'])
        initial = read(Path(index['stage1']).parent/'initial_labels.json')
        prior = read(index['verification'])
        assert prior['status'] == 'PASS'
        assert cfg['cold_start'] is True
        assert cfg['input_sha256'] == sha(raw_path) == sha(cfg['input_path'])
        assert cfg['seed'] == 0 and type(cfg['seed']) is int
        assert cfg['model'] == 'gpt-4.1-2025-04-14'
        assert cfg['python_hash_seed'] == 0 and cfg['output_limit_parameters'] == 'OMITTED'
        seed = cfg['cold_start_seed']
        assert type(seed).__name__ == cfg['cold_start_seed_type']
        assert seed == {'order_default': None, 'order_0': '0', 'order_42': '42'}[order]
        expected = list(raw) if seed is None else random.Random(seed).sample(list(raw), len(raw))
        assert order_info['papers'] == expected
        stage1 = read(index['stage1'])
        assert list(stage1) == expected
        assert all(initial[k]['ordered_values'] == [] and initial[k]['serialized'] == 'set()'
                   for k in ('Task', 'Dataset', 'Metric'))
        assert prior['stages']['stage1']['output_sha256'] == sha(index['stage1'])
        cold[order] = {'stage1': entry(index['stage1']), 'paper_order': entry(index['paper_order']),
                       'config': entry(index['config']), 'historical_verification': entry(index['verification']),
                       'cold_start_seed': seed, 'seed_type': type(seed).__name__,
                       'model_seed': 0, 'initial_sets_empty': True, 'order_recomputed_equal': True,
                       'validation': validate_normalized(raw, stage1),
                       'reuse_stage1': True, 'reuse_old_stage2': False,
                       'next_stage_enabled': False, 'requires_new_target_board_stage2': True}

    partial_config = read(PILOT/'full43_partially/config.json')
    assert sha(partial_config['input_path']) == sha(raw_path) == partial_config['input_sha256']
    partial = {'config': entry(PILOT/'full43_partially/config.json'),
               'same_zero_shot_extraction': True, 'reuse_stage1': False, 'reuse_stage2': False,
               'masking_seed': 0, 'seed_type': 'int', 'python_hash_seed': '0',
               'threshold2_masking_preview_executed': False,
               'old_mask_is_reference_only': entry(PILOT/'full43_partially/masking/partially_masked_leaderboards.json')}
    result = {'status': 'INPUT_REUSE_CHECKS_PASSED_TARGET_DATA_BLOCKED',
              'fully': fully, 'partially': partial, 'cold_start': cold,
              'source_dependencies': source_evidence, 'new_llm_api_inference_calls': 0}
    save(ROOT/'reuse_manifest.json', result)
    future_common = {'enabled': False, 'state': 'BLOCKED_MISSING_OFFICIAL_THRESHOLD2_ARTIFACT',
        'execution_authorized_this_round': False, 'model': 'gpt-4.1-2025-04-14',
        'base_url': 'https://9527.codes/v1', 'temperature': 0, 'seed': 0, 'stream': False,
        'output_limit_parameters': 'OMITTED', 'max_retries': 0, 'python_hash_seed': '0',
        'raw_input': entry(raw_path), 'gold_annotations': entry(am['gold_path']),
        'verified_threshold2_path': None, 'verified_threshold2_sha256': None,
        'shared_masked_subset_path': None, 'shared_masked_subset_sha256': None,
        'prompt_file': entry(REPO/'prompts.json'),
        'no_new_pdf_embedding_retrieval_extraction': True}
    save(ROOT/'next_stage_configs.json', {'common': future_common,
        'fully_llm': {'normalization_input': entry(a_path), 'action_after_data_ready': 'offline_evaluation_only'},
        'fully_cs': {'normalization_input': entry(b_path), 'action_after_data_ready': 'offline_evaluation_only'},
        'partially': {'cold_start': False, 'masking_seed': 0, 'preserve_author_artifact_order': True,
            'masking_function': 'tdm_llm_masked_normalization.sample_tdms',
            'stage1': 'RUN_NEW_DYNAMIC_NORMALIZATION_AFTER_NEXT_STAGE_AUTHORIZATION',
            'stage2': 'RUN_NEW_ALIGNMENT_AGAINST_ALL_VERIFIED_TARGET_BOARDS',
            'evaluation': 'ALL_TARGET_BOARDS_AND_SHARED_NEW_PARTIALLY_MASKED_SUBSET'},
        'cold_start': {order: {'cold_start_seed': info['cold_start_seed'], 'seed_type': info['seed_type'],
            'reuse_stage1': info['stage1'], 'preserve_paper_order': info['paper_order'],
            'stage2': 'RUN_NEW_ALIGNMENT_AGAINST_ALL_VERIFIED_TARGET_BOARDS_AFTER_NEXT_STAGE_AUTHORIZATION',
            'evaluation': 'ALL_TARGET_BOARDS_AND_SAME_NEW_PARTIALLY_MASKED_SUBSET'} for order, info in cold.items()}})
    print('REUSE PASS: Fully LLM/CS 43 papers, 284 predictions; Cold stage1 three orders validated; no inference.')


if __name__ == '__main__':
    main()
