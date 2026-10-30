"""Freeze a Fully-only normalization Prompt comparison; no network or credentials."""
import ast,difflib,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'20261029_input_ablation'
SOURCE=ROOT.parent/'20261028_semantic_alignment_v1'
REPO=Path(r'D:\C++\SCILEAD\emnlp2024-leaderboard-generation')
ARMS={'baseline_rag':'baseline_rag/merged','parsed_full':'parsed_full/fully/merged','page_images':'page_images/fully/merged'}
def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def copy(a,b):
    b=Path(b);b.parent.mkdir(parents=True,exist_ok=True);assert not b.exists();shutil.copyfile(a,b)
def main():
    assert not (ROOT/'experiment_manifest.json').exists(),'Existing preparation must be inspected'
    protected={str(OLD/p):h for p,h in load(OLD/'delivery_hashes.json').items()}
    protected.update(load(OLD/'protected_hashes.json'))
    assert all(Path(p).is_file() and sha(p)==h for p,h in protected.items()),'Old frozen file changed'
    before=load(OLD/'parsed_full/frozen_prompts.json')
    additions=load(SOURCE/'prompt_additions.json')
    inherited=additions['masked-normalization-system-prompt'].split('\nIf one candidate is a clear semantic match,')[0]
    suffix=inherited+'\nIf one candidate is a clear semantic match, output that candidate exactly as written in the item list. If the list is empty, no candidate matches, or the match remains ambiguous, output None. Do not invent a new canonical name. Output only the selected item or None, without quotes, explanation or extra formatting.'
    after=dict(before);after['normalization-system-prompt']+=suffix
    save(ROOT/'prompts_original.json',before);save(ROOT/'prompts_fully_semantic_v1.json',after)
    copy(SOURCE/'prompt_additions.json',ROOT/'source_prompt_additions.json')
    save(ROOT/'prompt_migration.json',{'source':str(SOURCE/'prompt_additions.json'),'source_sha256':sha(SOURCE/'prompt_additions.json'),
        'changed_key':'normalization-system-prompt','fully_addition':suffix,'verbatim_inherited_requirements':inherited,
        'adaptation':'Unmatched/ambiguous names return None as in Fully; no dynamic candidate insertion; no joint TDM stage or extra context.',
        'not_migrated':['Return unchanged input and extend name sets','Second-stage joint TDM candidate list'],
        'official_fully_logic':'exact candidates accepted; other answers null; Result untouched; duplicate field positions called separately'})
    (ROOT/'prompt_diff.txt').write_text(''.join(difflib.unified_diff(before['normalization-system-prompt'].splitlines(True),after['normalization-system-prompt'].splitlines(True),fromfile='Fully original',tofile='Fully semantic v1')),encoding='utf8')
    (ROOT/'enhanced_prompt.txt').write_text(after['normalization-system-prompt'],encoding='utf8')
    for name in ['selection_frozen.json','input_manifest.json']:copy(OLD/name,ROOT/name)
    for name in ['transport.py','generation_config.json','candidate_sets.json','result_compat.py']:
        copy(OLD/'parsed_full'/name,ROOT/name)
    copy(OLD/'parsed_full/run_fully.py',ROOT/'frozen_runner.py')
    ids=[r['paper_id'] for r in load(OLD/'input_manifest.json')]
    strings=load(ROOT/'candidate_sets.json');sets={k:ast.literal_eval(v) for k,v in strings.items()}
    assert {k:len(v) for k,v in sets.items()}=={'Task':23,'Dataset':71,'Metric':26}
    assert sha(OLD/'page_images/candidate_sets.json')==sha(ROOT/'candidate_sets.json')
    arm_meta={};total=0
    for arm,path in ARMS.items():
        original=OLD/path/'output.json';raw=load(original);assert list(raw)==ids
        copy(original,ROOT/arm/'merged/output.json');copy(OLD/path/'normalized_output.json',ROOT/arm/'previous_normalized_output.json')
        planned=[];records=0
        for pid,entry in raw.items():
            rows=json.loads(entry['output']);records+=len(rows)
            for i,row in enumerate(rows):
                assert set(row)=={'Task','Dataset','Metric','Result'} and all(isinstance(v,str) for v in row.values())
                for field,value in row.items():
                    if field!='Result' and value not in sets[field]:
                        planned.append({'paper_id':pid,'record':i,'field':field,'input':value,'candidate_serialized':strings[field]})
        # Prior successful requests must have identical user content and wire parameters.
        old_calls=[]
        if arm=='baseline_rag':
            calls_root=ROOT.parent/'20261028/fully/papers'
        else:calls_root=OLD/arm/'fully/papers'
        for pid in ids:
            old_calls.extend(sorted((calls_root/pid/'normalization/requests').glob('*/request.json')))
        assert len(old_calls)==len(planned),(arm,len(old_calls),len(planned))
        for plan,old_call in zip(planned,old_calls):
            req=load(old_call)
            assert req['messages'][0]['content']==before['normalization-system-prompt']
            expected='\n\nItem list: '+plan['candidate_serialized']+'\n\nInput: '+plan['input']+'\n\nAnswer: '
            assert req['messages'][1]=={'role':'user','content':expected}
            assert {k:v for k,v in req.items() if k!='messages'}==load(ROOT/'generation_config.json')
            plan['previous_request_path']=str(old_call);plan['previous_request_sha256']=sha(old_call)
        save(ROOT/arm/'request_manifest.json',planned)
        arm_meta[arm]={'source':str(original),'source_sha256':sha(original),'records':records,'requests':len(planned),
                       'candidate_sets_sha256':sha(ROOT/'candidate_sets.json'),'previous_output':str(OLD/path/'normalized_output.json')}
        total+=len(planned)
    for name in ['tdm_llm_normalization.py','tdm_eval.py','leaderboard_eval.py','prompting.py','prompts.json']:
        protected[str(REPO/name)]=sha(REPO/name)
    for f in SOURCE.glob('prompt*'):
        if f.is_file():protected[str(f)]=sha(f)
    for f in ROOT.rglob('*'):
        if f.is_file() and 'analysis' not in f.parts and f.suffix in ('.py','.json','.txt'):
            protected[str(f)]=sha(f)
    save(ROOT/'protected_hashes.json',protected)
    save(ROOT/'experiment_manifest.json',{'status':'PREPARED','utc':datetime.now(timezone.utc).isoformat(),
        'experiment':'Fully LLM semantic Prompt comparison on frozen input ablation subset','papers':5,'gold_records':28,'paper_ids':ids,
        'model':'deepseek-flash','generation':load(ROOT/'generation_config.json'),'arms':arm_meta,'normalization_requests':total,
        'new_extraction_requests':0,'new_retrieval':False,'new_pdf_parsing':False,'semantic_cache':False,'automatic_retries':0,
        'changed_prompt_key':'normalization-system-prompt','prompt_sha256':sha(ROOT/'prompts_fully_semantic_v1.json'),
        'candidate_sizes':{k:len(v) for k,v in sets.items()},'evaluation':'Same five papers / 28 Gold and induced ten leaderboards / 14 members',
        'request_pairing':'Only system prompt changes; user message, candidate strings and generation payload verified against each old request'})
    print(json.dumps({'status':'PREPARED','arms':arm_meta,'normalization_requests':total,'protected_files':len(protected)},ensure_ascii=False))
if __name__=='__main__':main()
