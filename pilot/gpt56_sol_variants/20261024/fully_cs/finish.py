"""Verify artifacts and frozen sources, then write this branch's report."""
import inspect
import subprocess
from cs_common import *

def main():
    setup();frozen=verify()
    cfg=read(RUN/'config.json');raw=read(RUN/'merged/output.json');norm=read(RUN/'normalization/embedding_normalized_output.json')
    labels=read(RUN/'candidate_labels.json');old_labels=read(ROOT/'pilot/full43_cs/candidate_labels.json')
    assert labels==old_labels
    assert list(raw)==list(norm) and len(norm)==43
    assert sha(RUN/'merged/output.json')==sha(RUN/'work/output.json')==cfg['input_sha256']==sha(cfg['input_path'])
    audits=[json.loads(line) for line in (RUN/'normalization/mapping_audit.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(audits)==1005
    audit_map={(a['paper_id'],a['record'],a['field']):a for a in audits}
    assert len(audit_map)==1005
    for paper,value in raw.items():
        rows=json.loads(value['output']);n=norm[paper]
        assert value['source_documents']==n['source_documents'] and len(rows)==len(n['normalized_output'])
        for i,(a,b) in enumerate(zip(rows,n['normalized_output']),1):
            assert list(a)==list(b) and a['Result']==b['Result']
            for k in labels['labels']:
                d=audit_map[(paper,i,k)]
                assert b[k] in labels['labels'][k] and d['selected']==b[k] and d['original']==a[k]
                assert d['exact_match']==(a[k] in labels['labels'][k])
                if d['exact_match']:assert a[k]==b[k]
                else:assert labels['labels'][k][d['corpus_id']]==b[k] and d['corpus_id'] in d['top1_tied_corpus_ids']
    summary=read(RUN/'normalization/summary.json');assert summary['records']==335
    assert summary['exact_fields']==cfg['expected_exact_fields'] and summary['cs_fields']==cfg['expected_cs_fields']
    mm=read(RUN/'model_manifest.json')
    for name,h in mm['model_files_sha256'].items():assert sha(SNAPSHOT/name)==h,name
    runtime=read(RUN/'model_load_validation.json')
    for key,name in [('config_class_module','config.py'),('model_class_module','modeling.py')]:
        actual=RUN/'runtime/huggingface/modules'/Path(*runtime[key].split('.')).with_suffix('.py')
        assert sha(actual)==mm['code_files_sha256'][name]
    mm['actual_runtime']=runtime;mm['actual_imported_code_matches_pinned_repository']=True
    save(RUN/'model_manifest.json',mm)
    tuple_metrics=read(RUN/'evaluation/metrics_with_f1.json')
    lb=read(RUN/'leaderboard_evaluation/paper_metrics/leaderboard_metrics.json')['aggregate']
    lb_values=read(RUN/'leaderboard_evaluation/official/eval_values.json')['gold_results']
    assert all(len(v)==27 for v in lb_values.values()) and lb['gold_leaderboards']==27
    assert read(RUN/'leaderboard_evaluation/official/execution_status.json')['original_main_executed']
    # Each official file must match the historical full43_cs frozen SHA256 as well.
    historical=read(ROOT/'pilot/full43_cs/freeze_before.json')['sources_gold']
    for name in ('tdm_embedding_normalization.py','tdm_eval.py','leaderboard_eval.py'):
        path=REPO/name;assert sha(path)==historical[str(path)]
    status=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'status','--porcelain'],cwd=REPO,text=True,capture_output=True)
    save(RUN/'reproducibility/git_after.json',{'stdout':status.stdout,'stderr':status.stderr,'returncode':status.returncode})
    assert status.returncode==0 and status.stdout==frozen['git_status_before']
    verification={'status':'PASS','scope':'offline Fully+CS only','papers':43,'gold_tdmrs':295,'predicted_tdmrs':335,'mapping_audit_fields':1005,'frozen_source_files':len(frozen['sources_gold'])+sum(len(x) for x in frozen['directories'].values()),'source_gold_input_hashes_unchanged':True,'old_full43_cs_file_list_and_hashes_unchanged':True,'model_weight_and_code_hashes_unchanged':True,'dependency_versions_unchanged':True,'raw_copy_byte_identical':True,'paper_record_key_order_results_sources_preserved':True,'exact_fields':summary['exact_fields'],'cosine_top1_fields':summary['cs_fields'],'candidate_order_matches_frozen_full43_cs':True,'official_threshold':None,'official_normalization_main_executed':True,'official_tuple_main_executed':True,'official_leaderboard_main_executed':True,'gold_leaderboards':27,'gold_leaderboard_records':140,'actual_imported_code_matches_pinned_revision':True,'result_iim_unchanged':True,'top1_ties':summary['top1_tie_cases'],'embedding_cache_reused':False,'new_remote_inference_requests':0,'new_model_downloads':0,'api_calls':0,'git_status_unchanged':True,'git_status_before':frozen['git_status_before'],'git_clean':not bool(status.stdout),'runtime_write_scope_guard':str(RUN),'runtime_network_and_credential_file_guards':True,'official_rc_above_one':[k for k,v in lb_values['Result Coverage'].items() if v>1]}
    save(RUN/'verification.json',verification)
    if (RUN/'blocked_resources.json').exists():
        save(RUN/'blocked_resources.json',{'status':'RESOLVED_AFTER_USER_RELEASED_MEMORY','initial_block_archived_under':'reproducibility/attempts','successful_preload_memory':read(RUN/'memory_before_model_load.json'),'resource_policy':read(RUN/'resource_policy.json')})
    save(RUN/'metrics.json',{'tuple':tuple_metrics['aggregate'],'leaderboard':lb})
    save(RUN/'api_usage_summary.json',{'new_llm_requests':0,'new_remote_inference_requests':0,'model_downloads':0,'embedding_cache_reused':False,'local_name_embedding_model':MODEL})
    lines=['# GPT-5.6 Sol Fully+CS offline run','', 'Status: COMPLETE; verification PASS. 43 papers, 335 predictions, 295 Gold tuples; fixed 27 Gold leaderboards / 140 entries.','', '## Tuple metrics','', '| Metric | Precision | Recall | F1 |','|---|---:|---:|---:|']
    for k,m in tuple_metrics['aggregate'].items():lines.append(f"| {k} | {m['Precision']:.9f} | {m['Recall']:.9f} | {m['F1']:.9f} |")
    lines+=['','Official per-paper macro P/R; reported F1 is the harmonic mean of aggregate P/R. Official Result IIM and TDMR use substring Result matching, not strict numeric equality. No result rewriting or deduplication was introduced.','', '## Fixed 27-board evaluation','', '| Metric | Value |','|---|---:|']
    for k,v in lb.items():lines.append(f'| {k} | {v:.9f} |' if isinstance(v,float) else f'| {k} | {v} |')
    lines+=['','PC, RC and RBO are from unchanged official leaderboard_eval.main. RBO ranks deduplicated numeric values with the installed rbo default p=1. Official numeric conversion, less-than-one scaling, metric directions and last-valid-record overwrite order are preserved. LR coverage and paper-ID AO are supplementary and retain all 27 boards in the denominator. AO sorts score then paper ID for ties.','', '## Method and reproducibility','',f'- Official commit: `{frozen["commit"]}`.',f'- Frozen extraction input: `{cfg["input_path"]}`.',f'- Input SHA256: `{cfg["input_sha256"]}`.',f'- Model: `{MODEL}`, weights `{REV}`; code `{CODE}` at `{CODE_REV}`.', '- CPU FP32, four torch threads, seed 0, PYTHONHASHSEED=0. Existing local weights and code were used; no downloads or model API calls.', '- Unmodified official normalization main; local model factory, diagnostic search wrapper and per-paper checkpoints reused from full43_cs. Exact labels bypass encoding; all other labels use cosine semantic_search(top_k=1). The official method has no similarity threshold.', '- Candidate counts: 23 Task / 71 Dataset / 26 Metric; actual candidate lists and order match frozen full43_cs. No candidate filtering, sorting, thresholding, embedding cache reuse, batching change or preprocessing change.',f'- {summary["exact_fields"]} exact fields; {summary["cs_fields"]} cosine mappings; {summary["top1_tie_cases"]} top-score tie cases.',f'- Normalization wall time including model loading/probe: {summary["seconds"]:.3f} seconds.',f'- Immediately before model load: {json.dumps(read(RUN/"memory_before_model_load.json"))}.',f'- Final normalization memory / process peaks: {json.dumps(summary["memory"])}.', '- Source, Gold, extraction, previous full43_cs artifacts, model weights/code and package versions passed before/after hash checks. All runtime writes were restricted to this owned branch; network and credential-file access were guarded.',f'- Official repository initial and final status: `{status.stdout.strip() or "clean"}`. The pre-existing untracked __pycache__ was not created or removed by this run.', '', '## Files','', '- normalization/embedding_normalized_output.json: official compatible normalized output.', '- normalization/mapping_audit.jsonl and papers/: actual selections, cosine scores, candidate IDs and checkpoints.', '- evaluation/: unmodified official tuple outputs, aggregate F1, per-paper metrics and invocation.', '- leaderboard_evaluation/official/: official 27-board outputs and invocation.', '- leaderboard_evaluation/paper_metrics/ and leaderboards/: supplementary coverage/AO and numeric conversion traces.', '- config.json, model_manifest.json, freeze_before.json, reproducibility/: settings, versions, hashes and adapter audit.', '- verification.json, metrics.json, artifact_sha256.json: final checks and machine-readable results.', '', 'Only the Fully+CS branch was executed; Partially, ColdStart and provider configuration were outside this run.']
    (RUN/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (RUN/'README.md').write_text('Run with D:\\miniconda3\\envs\\scilead\\python.exe -B -X utf8 run_pipeline.py. Preparation is already frozen and should not be repeated. The runner uses fixed local cached weights, offline guards and per-paper checkpoints. See report.md, metrics.json and verification.json.\n',encoding='utf-8')
    verify()
    save(RUN/'artifact_sha256.json',{str(p.relative_to(RUN)):sha(p) for p in sorted(RUN.rglob('*')) if p.is_file() and 'runtime' not in p.relative_to(RUN).parts and p.name not in ('artifact_sha256.json','finish.log')})
    print(json.dumps({'verification':'PASS','tuple':tuple_metrics['aggregate'],'leaderboard':lb}),flush=True)

if __name__=='__main__':main()
