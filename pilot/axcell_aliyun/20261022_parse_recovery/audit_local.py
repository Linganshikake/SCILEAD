"""Read frozen inputs and save independent recovery evidence only."""
import hashlib, json, re, shutil, tarfile, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FORMAL=ROOT.parent/'20261022_formal'
SOURCE=Path(r'E:\SCILEAD\axcell\source\axcell')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 assert not (ROOT/'frozen_local_before.json').exists()
 snapshot={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(FORMAL.rglob('*')) if p.is_file()}
 save(ROOT/'frozen_local_before.json',snapshot)
 q=json.loads((FORMAL/'stage2/queue.json').read_text(encoding='utf-8'))
 selected=[]
 for pid in ['1905.03197.pdf','2203.16804.pdf']:
  row=next(x for x in q if x['paper_id']==pid);selected.append(row)
  out=ROOT/'diagnosis'/pid;out.mkdir(parents=True)
  shutil.copytree(FORMAL/'stage2/parse_logs'/pid,out/'original_failure_logs')
  archive=Path(row['local_source']);assert sha(archive)==row['sha256']
  (out/'original_input').mkdir();shutil.copy2(archive,out/'original_input'/archive.name)
  inventory=[];tex={}
  with tarfile.open(archive) as t:
   for m in t.getmembers():
    assert m.isfile() or m.isdir()
    if not m.isfile():continue
    f=t.extractfile(m);h=hashlib.sha256();content=b''
    for b in iter(lambda:f.read(1024*1024),b''):
     h.update(b)
     if m.name.endswith(('.tex','.sty','.bst')):content+=b
    inventory.append({'name':m.name,'bytes':m.size,'sha256':h.hexdigest()})
    if m.name.endswith('.tex'):tex[m.name]=content.decode('utf-8')
  save(out/'archive_inventory.json',inventory)
  main='unified.tex' if pid.startswith('1905') else 'acl.tex'
  text=tex[main];tables=[]
  for match in re.finditer(r'\\begin\{table\*?\}(.*?)\\end\{table\*?\}',text,re.S):
   body=match.group(0);tables.append({'source_line':text[:match.start()].count('\n')+1,'tex':body,'numeric_literals':re.findall(r'(?<![A-Za-z0-9])\d+(?:\.\d+)?',body)})
  save(out/'source_structure.json',{'paper_id':pid,'main':main,'all_documentclass_files':[k for k,v in tex.items() if re.search(r'\\documentclass(?:\[.*?\])?\{',v)],'main_bytes':len(text.encode()),'tables':tables,'table_float_count':len(tables),'tabular_begin_count':len(re.findall(r'\\begin\{tabular\*?\}',text)),'tex_files':tex})
  log=(out/'original_failure_logs/container_stderr.log').read_text(encoding='utf-8');lines=log.splitlines()
  first=next(i for i,l in enumerate(lines) if l.startswith('Error:'))
  save(out/'log_diagnosis.json',{'line_count':len(lines),'first_error_line':first+1,'first_error_context':lines[max(0,first-10):first+30],'last_lines':lines[-25:],'errors':[{'line':i+1,'text':l} for i,l in enumerate(lines) if l.startswith(('Error:','Fatal:'))]})
  samples=[json.loads(l) for l in (out/'original_failure_logs/conversion_linux_resources.jsonl').read_text(encoding='utf-8').splitlines()]
  save(out/'historical_resources.json',{'cpu_time_recorded':False,'samples':samples,'peak_container_bytes':max(c.get('memory.current',0) for s in samples for c in s['containers']),'partial_output_retention':'Original remove=True container and TemporaryDirectory cleaned on failure; remote checked separately.'})
 save(ROOT/'selected_inputs.json',selected)
 frozen={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((SOURCE/'axcell/scripts').rglob('*')) if p.is_file()}
 frozen.update({r['local_source']:{'bytes':Path(r['local_source']).stat().st_size,'sha256':sha(Path(r['local_source']))} for r in selected})
 save(ROOT/'protected_source_before.json',frozen)
 print(json.dumps({'frozen_formal_files':len(snapshot),'selected':[r['paper_id'] for r in selected],'protected_source_files':len(frozen)}))
if __name__=='__main__':main()
