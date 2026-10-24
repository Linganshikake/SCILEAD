"""Validate mirrored public packages against official PyPI SHA256 before installation."""
import concurrent.futures,json,requests,time
from pathlib import Path
from packaging.utils import parse_wheel_filename,parse_sdist_filename
BASE=Path(__file__).resolve().parent
ROWS=json.loads((BASE/'wheelhouse_unverified_manifest.json').read_text())
SPECIAL={x['file']:x for x in json.loads((BASE/'cpu_wheel_artifacts.json').read_text())}
SPECIAL['en_core_web_sm-2.2.5.tar.gz']={'sha256':'60b69065c97fd2e4972c33300205e1dead3501d2e0bfd6a182c3a033e337caee','bytes':12013172,'source_url':'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.5/en_core_web_sm-2.2.5.tar.gz'}
SPECIAL['en_core_sci_sm-0.2.4.tar.gz']={'sha256':'d4d5c5048b69ca79ce083b254f95c0c951d108d427fad0b32cc8847fe4ed25a0','bytes':17042664,'source_url':'https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz'}
def audit(row):
 name=row['file'];out=dict(row)
 if name in SPECIAL:
  expected=SPECIAL[name]
  assert row['sha256']==expected['sha256'] and row['bytes']==expected['bytes']
  out.update(status='VERIFIED_PRIOR_OFFICIAL_ARTIFACT',source_url=expected['source_url']);return out
 if name.startswith('axcell-'):
  out.update(status='EXCLUDED_GENERATED_LOCAL_SOURCE_ARCHIVE',reason='Install original hash-checked local source directory instead');return out
 if name.endswith('.whl'):package,version,_,_=parse_wheel_filename(name)
 else:package,version=parse_sdist_filename(name)
 url='https://pypi.org/pypi/'+str(package)+'/'+str(version)+'/json'
 session=requests.Session();session.trust_env=False
 for attempt in range(3):
  try:
   response=session.get(url,timeout=(15,45));response.raise_for_status();data=response.json();break
  except requests.RequestException:
   if attempt==2:raise
   time.sleep(2*(attempt+1))
 matches=[x for x in data['urls'] if x['filename']==name]
 assert len(matches)==1,'Official filename missing: '+name
 official=matches[0]
 assert official['digests']['sha256']==row['sha256'] and official['size']==row['bytes'],'Official SHA256/size mismatch: '+name
 out.update(status='VERIFIED_OFFICIAL_PYPI_SHA256',metadata_url=url,source_url=official['url'],package=str(package),version=str(version));return out
def main():
 result=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for out in pool.map(audit,ROWS):result.append(out)
 report={'all_installable_files_verified':True,'files':result,'verified_count':sum(x['status'].startswith('VERIFIED') for x in result),'excluded_count':sum(x['status'].startswith('EXCLUDED') for x in result),'transport_mirror':'https://mirrors.aliyun.com/pypi/simple','verification_authority':'Official PyPI JSON SHA256; prior original PyTorch/spaCy files compared to recorded hashes'}
 (BASE/'wheelhouse_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='files'}))
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'status':'BLOCKED_HASH_AUDIT','error_type':type(e).__name__,'detail':str(e)[:200]}));raise SystemExit(1)
