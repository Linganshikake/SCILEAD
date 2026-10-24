"""Task-local SSH/SFTP; reuse designated credentials and verify pinned host identity."""
import argparse,base64,hashlib,json,socket,sys,time
from pathlib import Path
import paramiko
sys.path.insert(0,r'D:\C++\SCILEAD\pilot\aliyun_remote_ssh\20261022')
from ecs_credentials import load
HOST='123.56.138.148'
PIN='SHA256:KGalzbokV4SulHzbq1wOCab/tALh6UzpY/curGepe4Q'

def connect():
    t=paramiko.Transport(socket.create_connection((HOST,22),timeout=20))
    t.get_security_options().key_types=['ssh-ed25519'];t.start_client(timeout=20)
    key=t.get_remote_server_key()
    fp='SHA256:'+base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('=')
    if fp!=PIN or not paramiko.HostKeys(str(Path.home()/'.ssh'/'known_hosts')).check(HOST,key):
        t.close();raise RuntimeError('Host identity mismatch')
    d=load();t.auth_password(d['username'],d['password'],fallback=False);d.clear()
    t.set_keepalive(30)
    return t

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['exec','put','get']);p.add_argument('local');p.add_argument('remote',nargs='?');p.add_argument('--timeout',type=int,default=90);a=p.parse_args()
    t=connect()
    try:
        if a.mode=='exec':
            script=Path(a.local).read_text(encoding='utf-8-sig').replace('\r\n','\n')
            c=t.open_session(timeout=20);c.exec_command('bash -s');c.sendall(script.encode());c.shutdown_write();start=time.monotonic()
            while True:
                if c.recv_ready():sys.stdout.buffer.write(c.recv(65536));sys.stdout.buffer.flush()
                if c.recv_stderr_ready():sys.stderr.buffer.write(c.recv_stderr(65536));sys.stderr.buffer.flush()
                if c.exit_status_ready() and not c.recv_ready() and not c.recv_stderr_ready():break
                if time.monotonic()-start>a.timeout:raise TimeoutError('Command timeout; remote state must be checked before retry')
                time.sleep(.05)
            return c.recv_exit_status()
        sftp=paramiko.SFTPClient.from_transport(t)
        if a.mode=='put':sftp.put(a.local,a.remote)
        else:sftp.get(a.remote,a.local)
        print(json.dumps({'operation':a.mode,'local':a.local,'remote':a.remote,'bytes':Path(a.local).stat().st_size}))
        sftp.close();return 0
    finally:t.close()
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as e:print(json.dumps({'error_type':type(e).__name__,'message':'Task operation failed; no credential values logged'}));raise SystemExit(1)
