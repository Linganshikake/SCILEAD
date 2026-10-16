"""Run official preprocessing once; observe outputs without changing its algorithms."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import pickle
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'emnlp2024-leaderboard-generation'
PILOT = ROOT / 'pilot'
os.chdir(PILOT / 'work')
os.environ.update({
    'HF_HOME': str(ROOT / 'assets/huggingface'),
    'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
    'HF_HUB_DISABLE_TELEMETRY': '1', 'HF_HUB_DISABLE_IMPLICIT_TOKEN': '1',
    'NLTK_DATA': str(ROOT / 'assets/nltk_data'),
    'TESSDATA_PREFIX': str(ROOT / 'tools/tesseract/tessdata'),
    'ANONYMIZED_TELEMETRY': 'False', 'DO_NOT_TRACK': '1',
    'LANGCHAIN_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false',
    'LANGSMITH_TRACING': 'false',
    'MPLCONFIGDIR': str(ROOT / 'assets/matplotlib-cache'),
})
os.environ['PATH'] = os.pathsep.join([str(ROOT / 'tools/tesseract'), str(ROOT / 'tools/pdf-system/Library/bin'), os.environ.get('PATH', '')])

def guard(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise RuntimeError('Pilot preprocessing prohibits network access')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        p = os.fsdecode(args[0]).replace('\\', '/').lower()
        if Path(p).name.startswith('.env') or '/.codex/' in p or '/.aws/' in p:
            raise RuntimeError('Sensitive configuration access prohibited')

sys.addaudithook(guard)
sys.path.insert(0, str(REPO))
import torch
torch.set_num_threads(4)
import doc_preprocess
import doc_preprocess_config
import pdf_loader

papers = list((PILOT / 'papers').iterdir())
assert len(papers) == 1 and papers[0].suffix.lower() == '.pdf'
args = argparse.Namespace(process_id='scilead-pilot', papers_path=str(PILOT / 'papers'), prompt_file=str(REPO / 'prompts.json'), output_path=(PILOT / 'outputs').as_posix() + '/')
config = doc_preprocess_config.get_config(args)
# Windows prohibits ':' inside directory names. Preserve all scientific settings.
raw_output = config.output_path
config.output_path = str(Path(raw_output).parent / Path(raw_output).name.replace(':', '-')) + '/'
OUT = Path(config.output_path)
OUT.mkdir(parents=True, exist_ok=False)
print('OUTPUT', OUT, flush=True)
summary = {'status': 'RUNNING', 'paper': papers[0].name, 'output_path': str(OUT), 'original_output_path': raw_output, 'adaptation': 'Only output directory timestamp colons replaced by hyphens; original main and original parameters retained.', 'network': 'prohibited by audit hook', 'cuda': torch.cuda.is_available()}

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def serialize(doc):
    return {'text': doc.page_content, 'metadata': doc.metadata}

original_partition = pdf_loader.partition_pdf
def observe_partition(*a, **kw):
    print('PARTITION_START', kw, flush=True)
    elements = original_partition(*a, **kw)
    save('partition-elements.json', [e.to_dict() for e in elements])
    tables = [e.to_dict() for e in elements if e.category == 'Table']
    save('raw-tables.json', tables)
    summary.update(elements=len(elements), element_categories=dict(Counter(e.category for e in elements)), table_count=len(tables), table_pages=[e['metadata'].get('page_number') for e in tables])
    print('PARTITION_DONE', summary, flush=True)
    assert tables, 'No table recognized. Stop without changing parsing strategy.'
    return elements
pdf_loader.partition_pdf = observe_partition

class ObservedDocuments(pdf_loader.Documents):
    def init_retriever(self, *a, **kw):
        result = super().init_retriever(*a, **kw)
        save('text-chunks.json', [serialize(d) for d in self.split_docs])
        save('official-table-documents.json', [serialize(d) for d in self.tables])
        summary.update(text_chunks=len(self.split_docs), official_table_documents=len(self.tables))
        print('INDEX_READY', len(self.split_docs), 'chunks', flush=True)
        return result
doc_preprocess.Documents = ObservedDocuments
start = time.monotonic()
try:
    doc_preprocess.main(config)
    with (OUT / 'processed_docs.pkl').open('rb') as f:
        docs = pickle.load(f)  # Only our just-created official output.
    evidence = {k: [serialize(d) for d in v] for k, v in docs.items()}
    save('retrieval-evidence.json', evidence)
    summary.update(status='PASS', evidence_count=sum(len(v) for v in evidence.values()), evidence_types=dict(Counter(d['metadata'].get('type') for v in evidence.values() for d in v)))
except Exception as exc:
    summary.update(status='FAIL', error_type=type(exc).__name__, error=str(exc))
    raise
finally:
    summary['seconds'] = round(time.monotonic() - start, 2)
    save('pilot-summary.json', summary)
    (PILOT / 'latest-run.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('FINAL', json.dumps(summary), flush=True)
