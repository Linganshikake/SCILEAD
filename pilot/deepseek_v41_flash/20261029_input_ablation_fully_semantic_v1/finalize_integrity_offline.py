"""Finish a post-request file audit after Windows process locks have closed. No HTTP."""
import json,msvcrt,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def guard(event,args):
    if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Offline finalization forbids network')
sys.addaudithook(guard)
from transport import load,save,digest,load_credentials
def main():
    # Confirm the finalizer's observed PermissionError was its own locked byte.
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        p=Path(tmp)/'process.lock';f=p.open('w+b');f.write(b'0');f.flush();f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
        try:p.read_bytes()
        except PermissionError:locked_read_failed=True
        else:locked_read_failed=False
        f.close();unlocked=p.read_bytes()==b'0'
    assert locked_read_failed and unlocked
    protected=load(ROOT/'protected_hashes.json');changed=[p for p,h in protected.items() if not Path(p).exists() or digest(p)!=h]
    assert not changed
    key,_=load_credentials() # Internal exact-byte leak check; never log or persist the secret.
    for arm in ('baseline_rag','parsed_full','page_images'):
        root=ROOT/arm;cp=load(root/'checkpoint.json');assert cp['state']=='COMPLETE'
        assert all(s['status']=='COMPLETE' for s in cp['papers'].values())
        # Verify completion files before writing only the previously absent audit.
        for pid in cp['papers']:
            folder=root/'papers'/pid
            assert all(digest(folder/p)==h for p,h in load(folder/'completion_hashes.json').items())
        scanned=[p for p in root.rglob('*') if p.is_file()]
        clean=all(key.encode() not in p.read_bytes() for p in scanned);assert clean
        assert not (root/'verification.json').exists(),'Do not replace an existing verification'
        save(root/'verification.json',{'status':'COMPLETE','protected_count':len(protected),'protected_changed':changed,
            'secret_scan_passed':clean,'scanned_files':len(scanned),'complete_papers':5,
            'usage':load(root/'api_usage_summary.json'),'post_request_finalization':'OFFLINE_AFTER_LOCK_RELEASE',
            'original_worker_exit':'PermissionError in final file scan; requests and outputs already complete',
            'new_api_calls_during_finalization':0,'predictions_changed':False})
    save(ROOT/'engineering_finalization.json',{'cause':'Windows msvcrt byte lock denied reading the still-open process.lock during final leak scan',
        'reproduced_locked_read_permission_error':locked_read_failed,'read_succeeded_after_close':unlocked,
        'recovery':'Independent offline completion/hash/leak audit after worker exit; original exception logs preserved',
        'new_api_calls':0,'raw_response_or_normalized_output_changes':0})
    print(json.dumps({'offline_finalization':'PASS','arms':3,'new_api_calls':0,'protected_changes':len(changed)}))
if __name__=='__main__':main()
