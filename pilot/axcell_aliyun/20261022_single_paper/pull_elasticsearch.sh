set -euo pipefail
docker pull docker.elastic.co/elasticsearch/elasticsearch-oss@sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b
docker image inspect docker.elastic.co/elasticsearch/elasticsearch-oss@sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b --format '{{json .RepoDigests}}'
docker tag docker.elastic.co/elasticsearch/elasticsearch-oss@sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1
