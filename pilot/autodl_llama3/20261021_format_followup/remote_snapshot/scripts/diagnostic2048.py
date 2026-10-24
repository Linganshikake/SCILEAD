from pathlib import Path
import sys,os,json,hashlib,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead');OLD=ROOT/'runs/llama3/20261021_formal42';OUT=R/'token2048_diagnostic';PID='2105.03654.pdf'
sys.path.insert(0,str(ROOT/'adapters'));sys.path.insert(0,str(R/'parser_v2'))
from parser import parse
def main():
    import run_llama as old
    if (OUT/'done.json').exists():print('DIAGNOSTIC_ALREADY_DONE');return
    config=old.read(OLD/'extraction/config.json');source=(ROOT/'adapters/run_llama.py').read_text()
    # Observational task-local copy: change ROOT resolution; add actual token-ID capture only.
    source=source.replace('ROOT=Path(__file__).resolve().parents[1]',"ROOT=Path('/root/autodl-tmp/scilead')",1)
    needle='                    eos=kw.get(\'eos_token_id\',pipe.model.generation_config.eos_token_id)'
    assert source.count(needle)==1
    source=source.replace(needle,"                    save(path/'token_ids.json',{'input_ids':ids[0].tolist(),'generated_ids':seq[0,length:].tolist()})\n"+needle)
    code=R/'scripts/diagnostic_adapter.py';code.write_text(source)
    spec=importlib.util.spec_from_file_location('diagnostic_adapter',code);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    from transformers import AutoTokenizer,AutoConfig
    tok=AutoTokenizer.from_pretrained(config['model_path'],use_fast=False,legacy=False,padding_side='left',local_files_only=True)
    oldcall=OLD/'extraction/2105.03654/extraction/calls/000000';req=m.read(oldcall/'request.json');oldtext=(oldcall/'response.txt').read_text();oldgen=m.read(oldcall/'complete.json')['actual_generation']
    assert not parse(oldtext)['ok'] and oldgen['output_tokens']==1024 and oldgen['finish_reason']=='length_or_other'
    ids=tok(req['prompt'],add_special_tokens=False,truncation=False)['input_ids'];limit=AutoConfig.from_pretrained(config['model_path'],local_files_only=True).max_position_embeddings
    assert len(ids)==oldgen['input_tokens']==2639 and len(ids)+2048<=limit
    m.save(OUT/'config.json',{'original':config,'only_generation_change':{'max_new_tokens':[1024,2048]},'input_tokens':len(ids),'native_context':limit,'source_request_sha256':hashlib.sha256((oldcall/'request.json').read_bytes()).hexdigest(),'maximum_new_extraction_calls':1})
    factory=m.factory
    def changed(c,budget,logs):
        assert budget==1024
        return factory(c,2048,logs)
    m.factory=changed;m.extract(config,PID,OUT/'extraction')
    newcall=OUT/'extraction/calls/000000';q=m.read(newcall/'request.json');assert q==dict(req,max_new_tokens=2048)
    result=m.read(OUT/'extraction/output.json');p=parse(result[PID]['output']);m.save(OUT/'parse.json',p)
    newids=m.read(newcall/'token_ids.json')['generated_ids'];oldids=tok(oldtext,add_special_tokens=False)['input_ids'];prefix=0
    for x,y in zip(oldids,newids):
        if x!=y:break
        prefix+=1
    m.save(OUT/'token_comparison.json',{'old_token_ids_provenance':'reconstructed by pinned tokenizer from original raw text; historical run did not save full generated IDs','old_reconstructed_ids':oldids,'old_length_matches_logged':len(oldids)==oldgen['output_tokens'],'old_last_id_matches_logged':oldids[-1]==oldgen['last_token_id'],'old_decode_roundtrip':tok.decode(oldids,skip_special_tokens=True,clean_up_tokenization_spaces=True)==oldtext,'longest_common_reconstructed_token_prefix':prefix,'first1024_equal_to_reconstructed_old':newids[:1024]==oldids,'new_text_starts_with_exact_old_text':result[PID]['output'].startswith(oldtext),'new_generated_ids_captured_directly':True})
    done={'status':'COMPLETE' if p['ok'] else 'FORMAT_FAILED','parse_valid':p['ok'],'records':p.get('records'),'actual_generation':m.read(newcall/'complete.json')['actual_generation'],'new_extraction_calls':1}
    if p['ok'] and done['actual_generation']['finish_reason']=='eos':m.save(OUT/'extraction/prepared_output.json',{PID:{**result[PID],'output':p['text']}})
    else:done['downstream_blocked']=True
    m.save(OUT/'done.json',done);print(json.dumps(done))
if __name__=='__main__':main()
