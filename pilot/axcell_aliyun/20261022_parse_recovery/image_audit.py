"""Inspect fixed image files in a short-lived read-only diagnostic container."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/root/scilead/axcell/runs/20261022_parse_recovery')
IMAGE='arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6'
EXPECTED='sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e'
assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==EXPECTED
assert not ROOT.exists();ROOT.mkdir(parents=True)
code=r'''
import glob,hashlib,json,os
from pathlib import Path
base=Path('/usr/local/share/perl/5.28.1/LaTeXML')
paths=[base/'Post.pm',base/'Post/MakeBibliography.pm',base/'Post/Scan.pm',base/'Post/CrossRef.pm',base/'Common/BibTeX.pm',Path('/usr/share/texlive/texmf-dist/tex/latex/tikzmark/tikzlibrarytikzmark.code.tex'),Path('/usr/share/texlive/texmf-dist/tex/latex/l3kernel/expl3-code.tex')]
for pattern in ['/app/engrafo*.js','/app/src/*.js','/app/lib/*.js','/usr/share/texlive/texmf-dist/tex/latex/*/capt-of.sty','/usr/share/texlive/texmf-dist/tex/latex/*/scalerel.sty','/usr/share/texlive/texmf-dist/tex/latex/*/adjustbox.sty']:
 paths.extend(Path(p) for p in glob.glob(pattern))
out={'files':{},'binding_matches':[str(p) for p in base.rglob('*') if any(x in p.name.lower() for x in ['expl3','tikzmark','bibtex'])],'app_listing':os.listdir('/app')}
for p in paths:
 if p.is_file():
  b=p.read_bytes();out['files'][str(p)]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode('utf-8',errors='replace')}
 else:out['files'][str(p)]={'exists':False}
print(json.dumps(out))
'''
args=['docker','run','--rm','--read-only','--network','none','--memory','512m','--memory-swap','512m','--cpus','1','--name','axcell-recovery-image-audit','--label','scilead.task=axcell-parse-recovery-20261022','-i','--entrypoint','python3',IMAGE,'-']
p=subprocess.run(args,input=code,capture_output=True,text=True,timeout=60)
(ROOT/'image_audit.json').write_text(p.stdout)
(ROOT/'image_audit.stderr').write_text(p.stderr)
print(p.stdout)
if p.returncode:raise SystemExit(p.returncode)
