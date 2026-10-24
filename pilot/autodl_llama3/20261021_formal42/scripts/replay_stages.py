"""Offline official-main replay using recorded responses; absolutely no new inference."""
from pathlib import Path
import sys,json,hashlib,os,subprocess,importlib.metadata
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead');sys.path.insert(0,str(ROOT/'adapters'))
import run_llama as adapter
def main():
    assert os.environ.get('PYTHONHASHSEED')=='0';base=R/'reproducibility/replay';config=adapter.read(R/'extraction/config.json');checks=[]
    from langchain_core.language_models.llms import LLM
    from langchain_core.pydantic_v1 import PrivateAttr
    def replay_factory(stage):
        source={'fully':R/'normalization/fully_llm','partial':R/'normalization/partially/stage1','leaderboard':R/'normalization/partially/stage2'}[stage]
        records=sorted((source/'calls').glob('*/request.json'));visited=[]
        class Replay(LLM):
            _index=PrivateAttr(default=0)
            @property
            def _llm_type(self):return 'offline-recorded-response-only'
            def _call(self,prompt,stop=None,run_manager=None,**kwargs):
                i=self._index;self._index+=1;path=records[i];request=adapter.read(path)
                assert prompt==request['prompt'] and hashlib.sha256(prompt.encode()).hexdigest()==request['prompt_sha256']
                assert (path.parent/'complete.json').exists();answer=(path.parent/'response.txt').read_text();assert hashlib.sha256(answer.encode()).hexdigest()==adapter.read(path.parent/'complete.json')['response_sha256']
                visited.append(i);return answer
        instance=Replay();return instance,records,visited,source
    for stage in ['fully','partial','leaderboard']:
        llm,records,visited,source=replay_factory(stage);adapter.factory=lambda *a,**k:llm
        inp=R/'extraction/prepared_output.json' if stage!='leaderboard' else R/'normalization/partially/stage1/partially_masked_normalization/partially_masked_normalized_output.json'
        out=base/stage
        if (out/'stage_complete.json').exists():raise RuntimeError('Replay already exists; do not repeat')
        adapter.official_stage(stage,config,R/'extraction/config.json',inp,out)
        rel={'fully':'normalization/normalized_output.json','partial':'partially_masked_normalization/partially_masked_normalized_output.json','leaderboard':'leaderboard_normalized_output.json'}[stage]
        assert adapter.read(out/rel)==adapter.read(source/rel);assert len(visited)==len(records)
        checks.append({'stage':stage,'identical_official_output':True,'identical_prompts':len(records),'new_model_calls':0})
    hashes=adapter.read(R/'config/remote_expected_hashes.json');assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
    prior=adapter.read(R/'preflight.json');versions={k:importlib.metadata.version(k) for k in prior['versions']};assert versions==prior['versions']
    pip=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True);assert pip.returncode==0
    gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free','--format=csv,noheader'],capture_output=True,text=True)
    adapter.save(R/'reproducibility/verification_remote.json',{'status':'PASS','official_main_replays':checks,'frozen_source_adapter_gold_evidence_files':len(hashes),'versions_unchanged':versions,'pip_check':pip.stdout.strip(),'gpu_after':gpu.stdout.strip(),'new_generation_calls_in_replay':0})
    print(json.dumps({'status':'PASS','replays':checks}))
if __name__=='__main__':main()
