
import os
import requests

def load_env(path=".env"):
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

base_url = os.environ["BASE_URL"].rstrip("/")
api_key = os.environ["API_KEY"]

if base_url.endswith("/v1"):
    url = base_url + "/models"
else:
    url = base_url + "/v1/models"

response = requests.get(
    url,
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=30
)

print("HTTP Status:", response.status_code)
response.raise_for_status()

data = response.json()
models = sorted(
    item["id"]
    for item in data.get("data", [])
    if "id" in item
)

print(f"Available model entries: {len(models)}")
for model in models:
    print(model)
