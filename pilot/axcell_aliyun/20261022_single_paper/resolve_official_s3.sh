python3 - <<'PY'
import socket,json
host='s3.us-west-2.amazonaws.com'
ips=sorted({x[4][0] for x in socket.getaddrinfo(host,443,socket.AF_INET,socket.SOCK_STREAM)})
print(json.dumps({'host':host,'ipv4':ips}))
PY
