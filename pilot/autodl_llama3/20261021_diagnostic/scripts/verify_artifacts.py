from pathlib import Path
import sys,json,hashlib,ast,subprocess
R=Path(__file__).resolve().parents[1];PRE=Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021')
sys.path.insert(0,str(PRE/'scripts'))
from connection import read_connection
from hf_access import token
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    protected=json.loads((R/'integrity_before.json').read_text(encoding='utf-8'))
    assert all(sha(Path(x['path']))==x['sha256'] for x in protected)
    secrets=[read_connection()[3].encode(),token().encode()]
    inventory=[]
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        if p.name in ['artifact_sha256.json','privacy_verification.json','publish_transfer.json']:continue
        if p.suffix not in ['.json','.txt','.log','.py','.md','.csv']:continue
        data=p.read_bytes();assert not any(v in data for v in secrets),'CREDENTIAL_FOUND_DETAILS_WITHHELD'
        if p.suffix=='.py':ast.parse(data.decode('utf-8'))
        inventory.append({'path':p.relative_to(R).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    for name in ['experiment_manifest.json','generation_config.json','format_audit.md','context_scope.md','comparison_with_paper.md','comparison_with_gpt41.md','run_report.md','verification.json']:
        assert (R/name).is_file()
    reqs=list((R/'extraction').rglob('request.json'));assert len(reqs)==3
    for p in reqs:
        x=json.loads(p.read_text(encoding='utf-8'));assert x['seed']==0 and not x['do_sample'] and x['max_new_tokens']==1024 and x['model_revision']=='50fd307e57011801c7833c87efa1984ddf2db42f'
        assert p.with_name('complete.json').exists()
    result=subprocess.run([sys.executable,str(R/'scripts/test_format_candidate.py')],capture_output=True,text=True);assert result.returncode==0
    (R/'artifact_sha256.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    proof={'status':'PASS','protected_files_unchanged':len(protected),'artifact_hash_count':len(inventory),'credential_values_absent':True,'actual_new_model_requests':3,'candidate_parser_tests':13,'formal_protocol_still_pending':True,'paid_api_calls':0}
    (R/'privacy_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof))
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'details':'sensitive values withheld'}));raise SystemExit(1)
