"""Reuse the verified official CS runner; compute recovered/new papers only."""
from pathlib import Path
import sys,os,importlib.util,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_formal42')
def main():
    mode=sys.argv[1];assert mode in ['v2','diagnostic'];base=R/('format_v2' if mode=='v2' else 'token2048_diagnostic')
    spec=importlib.util.spec_from_file_location('verified_cs',OLD/'scripts/run_cs.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.R=base;m.OUT=base/'normalization/fully_cs';m.OUT.mkdir(parents=True,exist_ok=True)
    if (m.OUT/'complete.json').exists():print('CS_ALREADY_DONE');return
    for name in ['cs_reference.json','cs_model_transfer.json']:m.save(base/'config'/name,m.read(OLD/'config'/name))
    # Existing verified dynamic-model source cache is copied locally on the server, not downloaded.
    os.environ.update(HF_HOME=str(R/'cache'),HF_HUB_CACHE=str(R/'cache/hub'),HF_MODULES_CACHE=str(R/'cache/modules'))
    raw=m.read(base/'extraction/prepared_output.json');prior=m.read(OLD/'extraction/prepared_output.json');reused=[]
    if mode=='v2':
        for p,v in prior.items():
            assert raw[p]==v
            source=OLD/'normalization/fully_cs/papers'/p.removesuffix('.pdf');target=m.OUT/'papers'/p.removesuffix('.pdf')
            for name in ['normalized_output.json','mapping.json','complete.json']:
                dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);data=(source/name).read_bytes()
                if dest.exists():assert dest.read_bytes()==data
                else:dest.write_bytes(data)
            reused.append(p)
    m.save(m.OUT/'reuse.json',{'unchanged_papers_reused':reused,'new_papers':[p for p in raw if p not in reused]});m.main()
if __name__=='__main__':main()
