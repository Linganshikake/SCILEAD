from pathlib import Path
import sys,json,argparse
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021\scripts')))
from remote_client import connect,execute
def main():
    p=argparse.ArgumentParser();p.add_argument('file',type=Path);a=p.parse_args();assert a.file.resolve().is_relative_to(R.resolve())
    c=connect()
    try:
        v=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',a.file.read_text(encoding='utf-8'),timeout=180)
        print(json.dumps(v,ensure_ascii=False));assert v['exit_code']==0
    finally:c.close()
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'error_type':type(e).__name__,'details':'withheld'}));raise SystemExit(1)
