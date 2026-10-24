"""Independent post-run hash/index check, no model imports or writes outside stage2."""
import json, subprocess, datetime
from pathlib import Path
from policy import sha
ROOT=Path('/root/scilead/axcell/runs/20261022_formal/stage2')
manifest=json.loads((ROOT/'parse_manifest.json').read_text());queue=json.loads((ROOT/'queue.json').read_text())
result=json.loads((ROOT/'batch_result.json').read_text());config=json.loads((ROOT/'configuration.json').read_text())
assert len(manifest['papers'])==39 and len({r['paper_id'] for r in manifest['papers']})==39
assert [r['paper_id'] for r in manifest['papers']]==[r['paper_id'] for r in queue]
checks=[]
for state,inp in zip(manifest['papers'],queue):
    assert sha(inp['remote_source'])==inp['sha256']
    if state['status']!='PARSE_COMPLETE':continue
    d=json.loads((ROOT/'parse_logs'/state['paper_id']/'parser_result.json').read_text())
    assert d['input_sha256']==inp['sha256'] and d['configuration_sha256']==config['configuration_sha256']
    assert state['fragment_count']==d['fragment_count'] and state['table_count']==d['table_count']==len(d['tables'])
    assert Path(d['parsed_paper_path'],'text.json').is_file() and Path(d['html_path']).is_file()
    for e in d['artifacts']:
        p=Path(e['path']);assert p.is_file() and p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
        checks.append(e)
    if not state['reused']:
        resource=json.loads((ROOT/'parse_logs'/state['paper_id']/'conversion_linux_status.json').read_text())
        assert resource['exit_code']==0 and resource['stop_reason'] is None
        assert not resource['cleanup']['containers']['remaining_running_task_containers']
        assert not resource['cleanup']['process_group']['remaining_live_members']
running=subprocess.check_output(['docker','ps','--format','{{.ID}} {{.Names}}'],text=True).splitlines()
assert not running
assert result['new_model_generations']==result['api_calls']==0
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASSED','papers_checked':39,
     'input_hashes_match':True,'parsed_artifact_files_checked':len(checks),'all_artifact_hashes_match':True,
     'running_containers':running,'counts':result['counts'],'new_model_generations':0,'api_calls':0}
out['task_storage']={}
for name in ['parsed/sources','parsed/unpacked_sources','parsed/htmls','parsed/papers','parse_logs']:
    p=ROOT/name
    if p.exists():out['task_storage'][name]={'apparent_bytes':int(subprocess.check_output(['du','-sb',str(p)],text=True).split()[0]),'allocated_bytes':int(subprocess.check_output(['du','-sB1',str(p)],text=True).split()[0])}
p=ROOT/'remote_output_verification.json';assert not p.exists();p.write_text(json.dumps(out,indent=2));print(json.dumps(out))
