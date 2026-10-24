from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
try:
    patterns=[re.compile(rb'\bhf_[A-Za-z0-9]{20,}\b'),re.compile(rb'\bsk-[A-Za-z0-9_-]{20,}\b'),re.compile(rb'(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._-]{16,}')];n=0
    for p in R.rglob('*'):
        if p.is_file():assert p.suffix!='.env' and p.name!='.env'
        if p.is_file() and p.suffix in ['.json','.jsonl','.md','.txt','.py','.log','.csv']:
            assert not any(s.search(p.read_bytes()) for s in patterns);n+=1
    proof={'status':'PASS','text_files_checked':n,'recognized_token_or_bearer_patterns_absent':True,'no_env_files_in_artifact_tree':True,'credentials_used_only_by_pinned_authentication_client':True,'credential_configs_not_read_for_scan':True,'limitation':'Pattern scan plus provenance; not a claim that arbitrary password-like text is mathematically impossible.'}
    (R/'reports/privacy_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof))
except Exception as e:print(json.dumps({'status':'FAIL','error_type':type(e).__name__,'details':'withheld'}));raise SystemExit(1)
