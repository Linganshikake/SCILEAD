"""Offline ablation preparation. Reuse exact official text/table conversion method."""
import ast,base64,copy,csv,hashlib,json,random,shutil,subprocess,sys,os
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime,timezone
from PIL import Image
import tiktoken

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261028'
REPO=Path(r'D:\C++\SCILEAD\emnlp2024-leaderboard-generation')
GOLD=Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\tdm_annotations.json')

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        if read(p)==x:return
        raise ValueError('Refusing to overwrite differing preparation file: '+str(p))
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def framing(original,docs):
    assert len(original)==2 and original[0]['role']=='system' and original[1]['role']=='user'
    context='\n\n'.join(d['content'] for d in docs)
    text=original[1]['content']
    if not context or text.count(context)!=1:raise ValueError('Historical message context mismatch')
    return text.split(context,1)
def replace_context(original,old,new):
    prefix,suffix=framing(original,old)
    return [copy.deepcopy(original[0]),{'role':'user','content':prefix+'\n\n'.join(d['content'] for d in new)+suffix}]
def image_messages(original,old,data_urls):
    prefix,suffix=framing(original,old)
    return [copy.deepcopy(original[0]),{'role':'user','content':[
        {'type':'text','text':prefix},
        *[{'type':'image_url','image_url':{'url':url,'detail':'original'}} for url in data_urls],
        {'type':'text','text':suffix}]}]

class Doc:
    def __init__(self,page_content,metadata):self.page_content=page_content;self.metadata=metadata
    def serial(self):return {'content':self.page_content,'metadata':self.metadata}

def reconstruct(elements):
    tree=ast.parse((REPO/'pdf_loader.py').read_text('utf8'))
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Documents')
    method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='extract_text_and_tables')
    cache=[SimpleNamespace(category=e['type'],text=e['text'],metadata=SimpleNamespace(**e['metadata'])) for e in elements]
    ns={'Document':Doc,'partition_pdf':lambda **kw:cache}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),str(REPO/'pdf_loader.py'),'exec'),ns)
    tables,text=ns['extract_text_and_tables'](SimpleNamespace(pdf_directory='OFFLINE_CACHED_ELEMENTS_ONLY'))
    return [x.serial() for x in text],[x.serial() for x in tables]

def render(row):
    out=ROOT/'rendered'/row['paper_id'];out.mkdir(parents=True,exist_ok=True)
    manifest=out/'manifest.json'
    if manifest.exists():
        data=read(manifest)
        assert data['pdf_sha256']==sha(row['paths']['original_pdf'])
        assert all(sha(p['path'])==p['sha256'] for p in data['pages'])
        return data['pages']
    if list(out.glob('page-*.png')):raise ValueError('Interrupted rendering requires explicit inspection')
    exe=r'D:\C++\SCILEAD\tools\pdf-system\Library\bin\pdftoppm.exe';assert Path(exe).is_file()
    command=[exe,'-r','150','-png',row['paths']['original_pdf'],str(out/'page')]
    p=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300)
    (out/'render.log').write_bytes(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError('Poppler rendering failed: '+row['paper_id'])
    files=sorted(out.glob('page-*.png'),key=lambda x:int(x.stem.split('-')[-1]))
    assert len(files)==row['input_statistics']['pdf_pages']
    pages=[]
    for i,f in enumerate(files,1):
        with Image.open(f) as im:
            im.load();w,h=im.size
            assert w>0 and h>0 and max(w,h)<=4096 and im.format=='PNG'
        assert f.stat().st_size<32*2**20
        pages.append({'page_number':i,'path':str(f),'sha256':sha(f),'width':w,'height':h,'bytes':f.stat().st_size})
    save(manifest,{'pdf_path':row['paths']['original_pdf'],'pdf_sha256':sha(row['paths']['original_pdf']),
                  'command':command,'dpi':150,'renderer_path':exe,'renderer_sha256':sha(exe),
                  'ocr':False,'crop':False,'pages':pages})
    return pages

def main():
    discovery=read(ROOT/'discovery.json');selection=discovery['selection'];selected=selection['selected']
    assert len(selected)==5 and len({x['paper_id'] for x in selected})==5
    rng=random.Random(selection['seed']);draws=[rng.choice(v) for v in selection['strata_in_draw_order'].values()]
    remaining=sorted({p for v in selection['strata_in_draw_order'].values() for p in v}-set(draws))
    draws.append(rng.choice(remaining));assert draws==[x['paper_id'] for x in selected]
    save(ROOT/'selection_frozen.json',selection)
    protected={}
    for row in selected:
        for k,p in row['paths'].items():
            assert sha(p)==row['sha256'][k],(row['paper_id'],k)
            protected[p]=row['sha256'][k]
    frozen=['run_fully.py','transport.py','result_compat.py','candidate_sets.json','frozen_prompts.json','generation_config.json']
    for n in frozen:protected[str(BASE/n)]=sha(BASE/n)
    for p in [GOLD,GOLD.with_name('leaderboards.json'),REPO/'pdf_loader.py',REPO/'tdm_eval.py',REPO/'leaderboard_eval.py',REPO/'prompts.json']:
        protected[str(p)]=sha(p)
    save(ROOT/'protected_hashes.json',protected)
    os.environ['TIKTOKEN_CACHE_DIR']=r'D:\C++\SCILEAD\assets\tiktoken'
    gold=read(GOLD);enc=tiktoken.get_encoding('o200k_base')
    arminputs={x:[] for x in ['parsed_full','page_images']};original={};normalized={};summary=[]
    for row in selected:
        pid=row['paper_id'];p=row['paths'];old=read(p['baseline_source_documents_json']);original_messages=read(p['baseline_extraction_messages_json'])
        text,tables=reconstruct(read(p['partition_elements_json']))
        assert tables==[x for x in old if x['metadata']['type']=='Table']
        assert len(text)==row['input_statistics']['reconstructed_page_text_documents']
        full=text+tables
        fullmessages=replace_context(original_messages,old,full)
        pages=render(row)
        data_urls=['data:image/png;base64,'+base64.b64encode(Path(x['path']).read_bytes()).decode('ascii') for x in pages]
        images=image_messages(original_messages,old,data_urls)
        image_docs=[{'content':'PDF page image; no local OCR or text extraction',
                     'metadata':{'filename':pid,'page_number':x['page_number'],'type':'PageImage','image_path':x['path'],'sha256':x['sha256']}} for x in pages]
        for arm,docs,messages in [('parsed_full',full,fullmessages),('page_images',image_docs,images)]:
            d=ROOT/arm/'inputs'/pid
            save(d/'source_documents.json',docs);save(d/'extraction_messages.json',messages)
            textparts=[m['content'] if isinstance(m['content'],str) else ''.join(x.get('text','') for x in m['content']) for m in messages]
            proxy=sum(len(enc.encode(x)) for x in textparts)+16
            config=read(BASE/'generation_config.json');payload={**config,'messages':messages}
            request_bytes=len(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf8'))
            assert request_bytes<48*2**20
            bound=sum(len(s.encode('utf8')) for s in textparts)+256+(len(pages)*1024 if arm=='page_images' else 0)
            assert bound+65536<1000000
            arminputs[arm].append({'paper_id':pid,'gold_count_audit_only':len(gold[pid]['TDMs']),
                'cached_evidence_path':str(d/'source_documents.json'),'evidence_file_sha256':sha(d/'source_documents.json'),
                'messages_path':str(d/'extraction_messages.json'),'messages_file_sha256':sha(d/'extraction_messages.json'),
                'input_mode':arm,'text_documents':len(text) if arm=='parsed_full' else 0,
                'table_documents':len(tables) if arm=='parsed_full' else None,'page_images':len(pages) if arm=='page_images' else 0,
                'evidence_count':len(docs),'o200k_text_proxy_tokens':proxy,'not_native_tokenizer':True,
                'image_token_documented_max':len(pages)*1024 if arm=='page_images' else 0,
                'conservative_input_bound':bound,'request_bytes':request_bytes,'exact_tokens':'API usage after execution'})
        original.update(read(p['deepseek_rag_output_json']));normalized.update(read(p['deepseek_fullyllm_output_json']))
        summary.append({'paper_id':pid,'gold':len(gold[pid]['TDMs']),'pages':len(pages),'parsed_text_documents':len(text),
                        'tables':len(tables),'baseline_evidence_documents':len(old),'table_parity':True,
                        'parsed_text_proxy_tokens':arminputs['parsed_full'][-1]['o200k_text_proxy_tokens'],
                        'images_request_bytes':arminputs['page_images'][-1]['request_bytes']})
        print(json.dumps(summary[-1]),flush=True)
    save(ROOT/'baseline_rag/merged/output.json',original)
    save(ROOT/'baseline_rag/merged/normalized_output.json',normalized)
    for arm,inputs in arminputs.items():
        dest=ROOT/arm;dest.mkdir(exist_ok=True)
        for n in frozen:
            target=dest/n
            if target.exists():assert sha(target)==sha(BASE/n)
            else:shutil.copyfile(BASE/n,target)
        save(dest/'input_manifest.json',inputs)
        armprotected=dict(protected)
        for n in frozen:armprotected[str(dest/n)]=sha(dest/n)
        for item in inputs:
            armprotected[item['cached_evidence_path']]=item['evidence_file_sha256'];armprotected[item['messages_path']]=item['messages_file_sha256']
        save(dest/'protected_hashes.json',armprotected)
        assert all(sha(dest/n)==sha(BASE/n) for n in frozen)
    save(ROOT/'input_manifest.json',summary)
    save(ROOT/'preparation_verification.json',{'status':'PASS','papers':5,'gold':sum(x['gold'] for x in summary),
        'pdf_pages':sum(x['pages'] for x in summary),'tables':sum(x['tables'] for x in summary),
        'original_fully_runtime_copied_byte_identically':True,'native_pdf_api_supported':False,
        'user_approved_page_images':True,'new_model_requests':0,'unchanged_protected_files':len(protected),
        'gold_used_for_input_content':False,'predictions_used_for_input_content':False})
    print('PREPARATION_PASS',flush=True)

if __name__=='__main__':main()
