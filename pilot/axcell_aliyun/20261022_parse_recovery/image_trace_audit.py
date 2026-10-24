import json,subprocess
from pathlib import Path
ROOT=Path('/root/scilead/axcell/runs/20261022_parse_recovery')
IMAGE='arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6'
code=r'''
import json,hashlib
from pathlib import Path
paths=[Path('/usr/local/share/perl/5.28.1/LaTeXML.pm'),Path('/usr/local/share/perl/5.28.1/LaTeXML/Post/Collector.pm'),Path('/usr/local/share/perl/5.28.1/LaTeXML/Post/Split.pm'),Path('/usr/local/share/perl/5.28.1/LaTeXML/Util/Pack.pm'),Path('/app/package.json')]
paths += [p for folder in ['/app/src','/app/bin','/app/latexml'] for p in Path(folder).rglob('*') if p.is_file() and p.suffix in ['.js','.py','.ltxml','.json'] and p.stat().st_size < 100000]
d={}
for p in paths:
 if p.is_file():
  b=p.read_bytes();d[str(p)]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode('utf-8',errors='replace')}
print(json.dumps(d))
'''
p=subprocess.run(['docker','run','--rm','--read-only','--network','none','--memory','512m','--memory-swap','512m','--cpus','1','--name','axcell-recovery-code-audit','--label','scilead.task=axcell-parse-recovery-20261022','-i','--entrypoint','python3',IMAGE,'-'],input=code,capture_output=True,text=True,timeout=60)
(ROOT/'image_trace_audit.json').write_text(p.stdout);(ROOT/'image_trace_audit.stderr').write_text(p.stderr)
print(p.stdout)
if p.returncode:raise SystemExit(p.returncode)
