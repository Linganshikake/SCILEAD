"""Read-only pinned SSH pre/post checks; never launch the runtime probe."""
from pathlib import Path
import json, sys, time
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent.parent/'20261022_single_paper'))
import remote

def main():
    name = sys.argv[1]
    assert name in ('before', 'after')
    dest = OUT/('remote_'+name+'.json')
    assert not dest.exists(), 'Do not replace an earlier audit'
    t = remote.connect()
    try:
        c=t.open_session(timeout=20); c.exec_command('PYTHONDONTWRITEBYTECODE=1 python3 -')
        c.sendall((OUT.parent/'remote_stage0_probe.py').read_bytes()); c.shutdown_write()
        data=bytearray(); err=bytearray(); start=time.monotonic()
        while True:
            if c.recv_ready(): data.extend(c.recv(65536))
            if c.recv_stderr_ready(): err.extend(c.recv_stderr(65536))
            if c.exit_status_ready() and not c.recv_ready() and not c.recv_stderr_ready(): break
            if time.monotonic()-start>180: raise TimeoutError('Read-only audit timeout')
            time.sleep(.05)
        code=c.recv_exit_status()
        if code:
            (OUT/('audit_'+name+'_stderr.txt')).write_bytes(err)
            raise RuntimeError('Read-only audit failed')
        d=json.loads(data); dest.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
        assert d['original_assets_match'] and d['single_paper_run_unchanged'] and d['single_paper_script_and_parsed_match']
        assert not d['package_diff_from_single_paper'] and d['pip_check']['exit_code']==0
        print(json.dumps({'audit':name,'min_available_gib':min(s['memory']['MemAvailable'] for s in d['memory_samples'])/2**30,'free_disk_gib':d['disk_free_bytes']/2**30,'running_containers':d['running_containers']['stdout'],'old_assets_unchanged':True,'dependency_changes':0}))
    finally: t.close()

if __name__=='__main__': main()
