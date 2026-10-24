"""Compare only credentials already authorized for this task, never print values."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];PRE=Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021');sys.path.insert(0,str(PRE/'scripts'))
from connection import read_connection
from hf_access import token
def main():
    values=[read_connection()[3].encode(),token().encode()];count=0
    assert all(len(x)>5 for x in values)
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix not in ['.json','.jsonl','.txt','.log','.md','.py','.csv']:continue
        assert not any(v in p.read_bytes() for v in values),'CREDENTIAL_FOUND_DETAILS_WITHHELD';count+=1
    proof={'status':'PASS','credential_values_absent':True,'text_files_checked':count,'credential_values_never_written_to_report':True}
    (R/'privacy_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof))
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'details':'withheld'}));raise SystemExit(1)
