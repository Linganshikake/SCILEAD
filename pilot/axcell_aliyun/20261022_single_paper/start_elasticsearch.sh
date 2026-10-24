set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import socket
s=socket.socket();s.bind(('127.0.0.1',9200));s.close()
PY
test -z "$(docker ps -a --filter name=^/axcell-single-es$ --format '{{.ID}}')"
mkdir -p "$ROOT/data/elasticsearch-single"
chown 1000:0 "$ROOT/data/elasticsearch-single"
docker run -d --name axcell-single-es --label scilead.task=axcell-single-20261022 \
  --memory 3g --memory-swap 3g --cpus 2 \
  --publish 127.0.0.1:9200:9200 \
  --mount type=bind,source="$ROOT/data/elasticsearch-single",target=/usr/share/elasticsearch/data \
  --env ES_JAVA_OPTS=-Xms1g\ -Xmx1g \
  --log-opt max-size=20m --log-opt max-file=3 \
  --user elasticsearch --entrypoint elasticsearch \
  docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1 \
  -Ehttp.port=9200 -Etransport.host=localhost -Ehttp.host=0.0.0.0 \
  -Ebootstrap.system_call_filter=false -Ehttp.cors.enabled=true \
  '-Ehttp.cors.allow-origin=*' '-Ehttp.cors.allow-headers=*' -Ehttp.cors.allow-credentials=true \
  > "$RUN/elasticsearch_container_id.txt"
python3 - <<'PY'
import json,time,urllib.request
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper');start=time.monotonic()
while time.monotonic()-start<90:
 try:
  with urllib.request.urlopen('http://127.0.0.1:9200',timeout=4) as response:d=json.load(response)
  assert d['version']['number']=='6.7.1'
  (r/'elasticsearch_version.json').write_text(json.dumps(d,indent=2));print('Elasticsearch OSS 6.7.1 ready on loopback only.');break
 except (OSError,ValueError):time.sleep(2)
else:raise RuntimeError('Elasticsearch startup did not complete within 90 seconds')
PY
