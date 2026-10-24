"""Original PaperExtractor with the previously validated execution guards only."""
import argparse, datetime, json, os, resource, time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from policy import sha

ROOT=Path('/root/scilead/axcell/runs/20261022_formal/stage2')
IMAGE='arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6'
DIGEST='sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e'

def save(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));tmp.replace(path)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('paper_id');a=ap.parse_args()
    queue=json.loads((ROOT/'queue.json').read_text()); row=next(r for r in queue if r['paper_id']==a.paper_id)
    log=ROOT/'parse_logs'/row['paper_id'];source=Path(row['remote_source']);data=ROOT/'parsed'
    assert sha(source)==row['sha256'] and source.stat().st_size==row['bytes']
    assert not (data/'papers'/row['tex_version']).exists(), 'Never replace existing parser output'
    assert not (log/'parser_result.json').exists(), 'Never repeat an attempt'
    import docker
    from axcell.helpers.paper_extractor import PaperExtractor
    from axcell.data.paper_collection import PaperCollection
    original_from_env=docker.from_env
    def negotiated(**kwargs):
        kwargs.setdefault('version','auto');return original_from_env(**kwargs)
    with patch('docker.from_env',negotiated):extract=PaperExtractor(data)
    containers=extract.latex.client.containers;original_run=containers.run
    image=extract.latex.client.images.get(IMAGE)
    assert image.id==DIGEST
    def guarded_run(image,command,**kwargs):
        assert image==IMAGE and kwargs.get('remove') is True
        kwargs.update(name='axcell-formal-convert',labels={'scilead.task':'axcell-formal-parse-20261022'},
                      mem_limit='20g',memswap_limit='20g',nano_cpus=6000000000,network_disabled=True)
        save(log/'container_config.json',{'image':image,'digest':DIGEST,'command':command,
             'memory_bytes':20*2**30,'cpus':6,'network_disabled':True,'remove':True,
             'mounts':[{'host':str(k),'target':v} for k,v in kwargs['volumes'].items()]})
        try:
            output=original_run(image,command,**kwargs)
            (log/'container_stdout.log').write_bytes(output or b'')
            save(log/'container_exit.json',{'exit_code':0});return output
        except docker.errors.ContainerError as e:
            (log/'container_stderr.log').write_bytes(e.stderr or b'')
            save(log/'container_exit.json',{'exit_code':e.exit_status,'error_type':'ContainerError'});raise
    containers.run=guarded_run
    extract.latex.client=SimpleNamespace(containers=containers,images=extract.latex.client.images)
    start=time.monotonic();status=extract(source)
    result={'paper_id':row['paper_id'],'tex_version':row['tex_version'],'input_sha256':row['sha256'],
            'configuration_sha256':json.loads((ROOT/'configuration.json').read_text())['configuration_sha256'],
            'official_status':status,'seconds':time.monotonic()-start,'new_model_generations':0,'api_calls':0,
            'original_entrypoint':'PaperExtractor(data_root)(source)','artifacts':[]}
    if status=='success':
        pc=PaperCollection.from_files(data/'papers'/row['tex_version'],jobs=1)
        assert len(pc)==1
        paper=pc.get_by_id(row['tex_version'],ignore_version=False);assert paper is not None
        tables=[{'name':t.name,'caption':t.caption,'rows':len(t.df),'columns':len(t.df.columns)} for t in paper.tables]
        result.update(fragment_count=len(paper.text.fragments),table_count=len(tables),tables=tables,
                      parsed_paper_path=str(data/'papers'/row['tex_version']),html_path=str(data/'htmls'/row['tex_version']/'index.html'))
        for directory in [data/'papers'/row['tex_version'],data/'htmls'/row['tex_version']]:
            for p in sorted(directory.rglob('*')):
                if p.is_file():result['artifacts'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
        result['warnings']=[]
        if not tables:result['warnings'].append('ZERO_TABLE_REGIONS_NOT_REPAIRED')
        if not paper.text.fragments:result['warnings'].append('ZERO_TEXT_FRAGMENTS_NOT_REPAIRED')
    result['child_max_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    save(log/'parser_result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','tables')}),flush=True)
    return 0 if status=='success' else 2
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as e:
        # Traceback goes to the per-paper log; no credentials are accessed in this process.
        print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'error':str(e)}),flush=True);raise
