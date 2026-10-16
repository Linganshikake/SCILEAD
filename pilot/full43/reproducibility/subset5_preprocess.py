"""One paper at a time, original SCILEAD preprocessing, durable checkpoints."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]; REPO=ROOT/'emnlp2024-leaderboard-generation'; SUB=Path(os.environ.get('SCILEAD_RUN_ROOT',str(ROOT/'pilot/subset5'))).resolve()
assert SUB.is_relative_to((ROOT/'pilot').resolve()),'Run root must remain inside SCILEAD/pilot'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,default=str),encoding='utf-8');t.replace(p)
def worker(paper):
    row=next(p for p in read(SUB/'manifest.json')['papers'] if p['id']==paper)
    if row['reused']:raise RuntimeError('Existing paper must never be reprocessed')
    out=Path(row['preprocess_dir']);out.mkdir(parents=True,exist_ok=True)
    if (out/'summary.json').exists() and read(out/'summary.json')['status']=='COMPLETE':print('SKIP_COMPLETE',paper);return
    if (out/'started.json').exists():raise RuntimeError('Prior unfinished preprocessing attempt; review before repeating PDF inference')
    work=SUB/'work';work.mkdir(exist_ok=True);os.chdir(work)
    os.environ.update({'HF_HOME':str(ROOT/'assets/huggingface'),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1','HF_HUB_DISABLE_IMPLICIT_TOKEN':'1','NLTK_DATA':str(ROOT/'assets/nltk_data'),'TESSDATA_PREFIX':str(ROOT/'tools/tesseract/tessdata'),'ANONYMIZED_TELEMETRY':'False','DO_NOT_TRACK':'1','LANGCHAIN_TRACING':'false','LANGCHAIN_TRACING_V2':'false','LANGSMITH_TRACING':'false','MPLCONFIGDIR':str(ROOT/'assets/matplotlib-cache')})
    os.environ['PATH']=os.pathsep.join([str(ROOT/'tools/tesseract'),str(ROOT/'tools/pdf-system/Library/bin'),os.environ.get('PATH','')])
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Offline PDF stage')
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(os.fsdecode(args[0]));s=str(p).replace('\\','/').lower()
            if p.name.startswith('.env') or '/.codex/' in s or '/.claude/' in s:raise RuntimeError('Sensitive configuration forbidden')
    sys.addaudithook(guard);sys.path.insert(0,str(REPO))
    import torch
    torch.set_num_threads(4)
    import pdf_loader,doc_preprocess,doc_preprocess_config
    config=doc_preprocess_config.get_config(argparse.Namespace(process_id=paper[:-4],papers_path=str(Path(row['pdf_path']).parent),prompt_file=str(REPO/'prompts.json'),output_path=out.parent.as_posix()+'/'))
    config.output_path=out.as_posix()+'/' # Filesystem-only path adaptation; scientific parameters unchanged.
    assert list(Path(config.papers_path).iterdir())==[Path(row['pdf_path'])]
    summary={'paper':paper,'status':'RUNNING','pdf_pages':row['pdf_pages'],'strategy':'hi_res','infer_table_structure':True,'chunk_size':2000,'chunk_overlap':200,'embedding':'multi-qa-mpnet-base-dot-v1','retrieval':'similarity default k=4 plus all tables'}
    partition=pdf_loader.partition_pdf
    def observed(*a,**kw):
        elements=partition(*a,**kw)
        save(out/'partition-elements.json',[e.to_dict() for e in elements]);tables=[e.to_dict() for e in elements if e.category=='Table'];save(out/'raw-tables.json',tables)
        summary.update(elements=len(elements),table_count=len(tables),table_pages=[e['metadata'].get('page_number') for e in tables],categories=dict(Counter(e.category for e in elements)))
        assert tables,'No tables detected; do not switch parsing strategy'
        return elements
    pdf_loader.partition_pdf=observed
    def doc(d):return {'content':d.page_content,'metadata':d.metadata}
    class Observed(pdf_loader.Documents):
        def init_retriever(self,*a,**kw):
            result=super().init_retriever(*a,**kw)
            save(out/'text-chunks.json',[doc(d) for d in self.split_docs]);save(out/'table-documents.json',[doc(d) for d in self.tables]);summary['text_chunks']=len(self.split_docs)
            return result
    doc_preprocess.Documents=Observed;start=time.monotonic();save(out/'started.json',{'paper':paper,'time':time.time()})
    try:
        doc_preprocess.main(config)
        with (out/'processed_docs.pkl').open('rb') as f:docs=pickle.load(f)
        assert list(docs)==[paper]
        save(out/'retrieval-evidence.json',{paper:[doc(d) for d in docs[paper]]});summary.update(status='COMPLETE',evidence_count=len(docs[paper]),evidence_types=dict(Counter(d.metadata['type'] for d in docs[paper])))
    except Exception as exc:
        summary.update(status='FAILED',error_type=type(exc).__name__,error=str(exc));raise
    finally:
        summary['seconds']=round(time.monotonic()-start,3);save(out/'summary.json',summary);print(json.dumps(summary),flush=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--paper');a=parser.parse_args()
    if a.paper:worker(a.paper);return
    for row in read(SUB/'manifest.json')['papers']:
        if row['reused']:continue
        if not Path(row['pdf_path']).is_file():print('SKIP_MISSING_PDF',row['id'],flush=True);continue
        out=Path(row['preprocess_dir']);out.mkdir(parents=True,exist_ok=True)
        if (out/'summary.json').exists() and read(out/'summary.json')['status']=='COMPLETE':continue
        print('PREPROCESS',row['id'],flush=True)
        with (out/'run.log').open('a',encoding='utf-8') as log:
            p=subprocess.run([sys.executable,'-X','utf8',__file__,'--paper',row['id']],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        m=read(SUB/'manifest.json');entry=next(e for e in m['papers'] if e['id']==row['id']);entry['status']='PREPROCESS_COMPLETE' if p.returncode==0 else 'PREPROCESS_FAILED';save(SUB/'manifest.json',m)
        print(entry['status'],row['id'],flush=True)
if __name__=='__main__':main()
