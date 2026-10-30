"""Inspect eventual DeepSeek files; optionally evaluate available jobs offline.

An output file is evidence of availability, not proof that generation finished.
--execute validates its actual contents and records full/partial/failed coverage.
"""
import argparse
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from offline_support import ANALYSIS, PILOT, boundary, fresh_directory, read, save
from evaluate_offline import evaluate

EXPERIMENT = ANALYSIS.parent
BRANCHES = ('partially', 'cold_default', 'cold_0', 'cold_42')
CASE_IDS = ('fully', 'fully_cs') + tuple(b+'_'+s for b in BRANCHES for s in ('stage1', 'stage2'))
MASK = PILOT/'full43_partially/masking/partially_masked_leaderboards.json'


def cases(cs_normalized=None):
    raw = EXPERIMENT/'fully/merged/output.json'
    cs_root = EXPERIMENT/'variants/fully_cs'
    candidates = sorted(cs_root.glob('**/*normalized_output.json')) if cs_root.exists() else []
    # Runtime/work checkpoints are never silently selected as final outputs.
    candidates = [p for p in candidates if not any(x in ('work', 'runtime', 'reproducibility', 'offline_test') for x in p.relative_to(cs_root).parts)]
    cs_path = Path(cs_normalized).resolve() if cs_normalized else (candidates[0] if len(candidates)==1 else None)
    items = [{'case': 'fully', 'raw': str(raw), 'normalized': str(EXPERIMENT/'fully/merged/normalized_output.json')},
             {'case': 'fully_cs', 'raw': str(raw), 'normalized': str(cs_path) if cs_path else None,
              'candidate_paths': [str(p) for p in candidates], 'selection': 'explicit override' if cs_normalized else 'unique candidate only'}]
    for branch in BRANCHES:
        for stage, name in [('stage1', 'normalized_output.json'), ('stage2', 'leaderboard_normalized_output.json')]:
            items.append({'case': branch+'_'+stage, 'raw': str(raw),
                          'normalized': str(EXPERIMENT/'variants'/branch/stage/name)})
    return items


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--execute', action='store_true', help='Evaluate existing inputs; never calls a model')
    p.add_argument('--masked10', action='store_true', help='Additionally evaluate stage2 on masked10; optional, separate scope')
    p.add_argument('--cs-normalized', type=Path, help='Explicit final CS path after inspection')
    args = p.parse_args()
    boundary()
    out = fresh_directory(args.out)
    jobs = cases(args.cs_normalized)
    commands = []
    for job in jobs:
        missing = [job['raw']] if not Path(job['raw']).is_file() else []
        if not job['normalized'] or not Path(job['normalized']).is_file(): missing.append(job['normalized'] or 'CS final output unselected')
        job.update(availability='MISSING' if missing else 'AVAILABLE_UNVERIFIED', missing=missing)
        job['evaluations'] = {}
        if job['normalized']:
            scopes = ['all27', 'masked10'] if args.masked10 and job['case'].endswith('_stage2') else ['all27']
            for scope in scopes:
                dest = out/job['case'] if scope=='all27' else out/job['case']/'masked10'
                command = f'& "{sys.executable}" -B -X utf8 "{ANALYSIS / "evaluate_offline.py"}" --raw "{job["raw"]}" --normalized "{job["normalized"]}" --out "{dest}"'
                if scope=='masked10': command += f' --boards "{MASK}"'
                commands.append(command)
                if args.execute and not missing:
                    kwargs = {'board_path': MASK} if scope=='masked10' else {}
                    result = evaluate(job['raw'], job['normalized'], dest, **kwargs)
                    job['evaluations'][scope] = {'status': result['status'], 'path': str(dest)}
    complete = args.execute and all(j['evaluations'] and all(v['status']=='COMPLETE' for v in j['evaluations'].values()) for j in jobs)
    report = {'status': 'COMPLETE' if complete else 'INCOMPLETE', 'mode': 'execute' if args.execute else 'inspection_only',
              'new_api_requests': 0, 'jobs': jobs, 'scope': 'Ten expected normalized files. File presence alone never proves completion.'}
    save(out/'inspection.json', report)
    (out/'commands.ps1').write_text('\n\n'.join(commands)+'\n', encoding='utf-8')
    print('\n'.join(f"{j['case']}: {j['availability']} {j['evaluations']}" for j in jobs))
    return 0 if complete else 2


if __name__ == '__main__':
    sys.exit(main())
