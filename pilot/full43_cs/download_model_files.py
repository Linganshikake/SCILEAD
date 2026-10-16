"""Bounded, resumable public artifact downloads; never performs model inference."""
import concurrent.futures,hashlib,json,time,urllib.request
from pathlib import Path
RUN=Path(__file__).resolve().parent;CACHE=RUN.parents[1]/'assets/hf_cache'
def fetch(name):
    info=json.loads((RUN/'reproducibility/bilingual-embedding-large-repository.json').read_text());revision=info['sha'];meta=next(x for x in info['siblings'] if x['rfilename']==name)
    path=CACHE/'models--Lajavaness--bilingual-embedding-large'/'snapshots'/revision/name;path.parent.mkdir(parents=True,exist_ok=True);part=path.with_suffix(path.suffix+'.partial');expected=meta.get('lfs',{}).get('sha256');size=meta['size']
    if path.exists() and path.stat().st_size==size:
        print('EXISTS',name,flush=True);return
    for attempt in range(1,4):
        offset=part.stat().st_size if part.exists() else 0
        try:
            url=f'https://huggingface.co/Lajavaness/bilingual-embedding-large/resolve/{revision}/{name}?download=true&nocache={int(time.time())}'
            req=urllib.request.Request(url,headers={'Range':f'bytes={offset}-'} if offset else {})
            with urllib.request.urlopen(req,timeout=60) as response:
                append=offset>0 and response.status==206
                if offset and not append:offset=0
                if append:assert response.headers['Content-Range'].startswith(f'bytes {offset}-')
                last=time.monotonic()
                with part.open('ab' if append else 'wb') as f:
                    while True:
                        block=response.read(1024*1024)
                        if not block:break
                        f.write(block);offset+=len(block)
                        if time.monotonic()-last>=20:print(name,offset,'/',size,flush=True);last=time.monotonic()
            assert part.stat().st_size==size,(part.stat().st_size,size)
            digest=hashlib.file_digest(part.open('rb'),'sha256').hexdigest()
            if expected:assert digest==expected,'LFS sha256 mismatch'
            part.replace(path);print('VERIFIED',name,size,digest,flush=True);return
        except Exception as e:
            print('DOWNLOAD_ERROR',name,attempt,type(e).__name__,getattr(e,'code',None),flush=True)
            if attempt==3:raise RuntimeError('Public model artifact download failed; partial retained') from None
    
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(fetch,['model.safetensors','tokenizer.json','sentencepiece.bpe.model']))
