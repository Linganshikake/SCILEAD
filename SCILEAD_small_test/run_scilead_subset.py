"""One- or two-paper SCILEAD original-retriever API smoke test.

This runs the official SciLead Documents.init_retriever() / .invoke(query), reproduces
its GPT-4 chat prompt text, and substitutes only the LLM transport with a compatible
OpenAI-style API. It is NOT a complete-paper benchmark or metric reproduction.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

from api_utils import read_env_file, get_api_config, chat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--env', default='.env')
    ap.add_argument('--repo', required=True, help='path to the cloned official SciLead repository')
    ap.add_argument('--pdf-dir', required=True, help='directory with 1-3 real SciLead PDF files')
    ap.add_argument('--model', default='gpt-4.1-2025-04-14')
    ap.add_argument('--max-papers', type=int, default=1)
    ap.add_argument('--max-output-tokens', type=int, default=1024)
    ap.add_argument('--max-prompt-chars', type=int, default=110000,
                    help='If prompt exceeds this, skip instead of silently truncating')
    ap.add_argument('--output', default='scilead_subset_output.json')
    args = ap.parse_args()
    if not 1 <= args.max_papers <= 3:
        ap.error('--max-papers must be between 1 and 3 to prevent accidental full-data runs')
    if args.max_output_tokens < 1 or args.max_output_tokens > 2048:
        ap.error('--max-output-tokens must be 1..2048')
    out_path = Path(args.output)
    if out_path.exists():
        ap.error(f'{out_path} already exists. Choose another output name to avoid repeated paid requests.')
    repo = Path(args.repo).resolve()
    pdf_dir = Path(args.pdf_dir).resolve()
    prompts_file = repo / 'prompts.json'
    if not prompts_file.exists():
        ap.error('Official SciLead prompts.json not found in --repo directory')
    papers = sorted(p for p in pdf_dir.iterdir() if p.is_file() and p.suffix.lower() == '.pdf')[:args.max_papers]
    if not papers:
        ap.error('No PDF papers in --pdf-dir. Please use original SciLead papers for valid experiments.')

    read_env_file(args.env)
    base, key = get_api_config()
    sys.path.insert(0, str(repo))
    from pdf_loader import Documents  # official code: Unstructured hi_res + Chroma/MPNet + all tables

    prompts = json.loads(prompts_file.read_text(encoding='utf-8'))
    results = {}
    try:
        for index, paper in enumerate(papers, start=1):
            print(f'[{index}/{len(papers)}] PDF processing:', paper.name)
            obj = Documents(pdf_directory=str(paper))
            try:
                retriever = obj.init_retriever()
                docs = retriever.invoke(prompts['query'])
                # default LangChain StuffDocumentsChain document_separator == '\n\n'
                context = '\n\n'.join(doc.page_content for doc in docs)
                # Same GPT chat prompt construction as SciLead prompting.py
                user = (prompts['query'] + '\n\nRetrieved document contents:\n\n'
                        + context + '.\n\n Output json:\n\n')
                messages = [
                    {'role':'system','content':prompts['tdm-extraction-system-prompt']},
                    {'role':'user','content':user},
                ]
                total_chars = sum(len(msg['content']) for msg in messages)
                print('  evidence docs:', len(docs), 'prompt chars:', total_chars)
                if total_chars > args.max_prompt_chars:
                    print('  SKIPPED: prompt exceeds length cap; no API call made')
                    results[paper.name] = {'status':'skipped_prompt_too_long', 'prompt_chars':total_chars}
                    continue
                resp = chat(base,key,args.model,messages,args.max_output_tokens,timeout=180)
                choices = resp.get('choices') or []
                text = (choices[0].get('message', {}).get('content') if choices else None)
                # mimic official output shape and retain source_documents for followup diagnostics
                results[paper.name] = {
                    'status':'success', 'output':text, 'source_documents':[
                        {'content':d.page_content,'metadata':d.metadata} for d in docs
                    ],
                    'request_metadata':{
                        'requested_model':args.model,
                        'returned_model':resp.get('model'),
                        'usage':resp.get('usage', {}),
                        'finish_reason':choices[0].get('finish_reason') if choices else None,
                        'prompt_chars':total_chars,
                        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
                    },
                }
                try:
                    parsed = json.loads(text)
                    print('  SUCCESS; JSON records:', len(parsed) if isinstance(parsed,list) else 'non-list JSON')
                except (TypeError, ValueError):
                    print('  API responded, but extraction JSON was not valid (inspect output).')
            except Exception as exc:
                # no secrets in normal parser errors; still do not print arbitrary full exception body
                print('  ERROR:', type(exc).__name__, str(exc)[:180].replace(key,'[REDACTED]'))
                results[paper.name] = {'status':'failed','error_type':type(exc).__name__}
            finally:
                if getattr(obj,'db',None) is not None:
                    try: obj.db.delete_collection()
                    except Exception: pass
            # save after each paper to preserve progress, but don't rerun on same path
            out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2),encoding='utf-8')
    finally:
        if not out_path.exists():
            out_path.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Completed. Output:', out_path)
    print('This is a smoke test, not an official SciLead F1 until normalization/evaluation are run.')

if __name__ == '__main__':
    main()
