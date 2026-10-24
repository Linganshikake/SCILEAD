set -eu
curl --silent --show-error --location --max-time 20 --connect-timeout 10 --output /dev/null --write-out 'HTTPS_MIRROR_HTTP=%{http_code} BYTES=%{size_download} SECONDS=%{time_total}\n' https://mirrors.aliyun.com/pypi/simple/awscli/
