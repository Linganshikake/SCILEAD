"""Small shared functions for authorized low-cost API testing.
Secrets are read from environment or from a local .env file and never printed.
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

import requests


def read_env_file(path: str | None) -> None:
    if not path:
        return
    env = Path(path)
    if not env.is_file():
        raise FileNotFoundError(f"Cannot find env file: {env}")
    for raw_line in env.read_text(encoding='utf-8-sig').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k in ('BASE_URL', 'API_KEY') and not os.environ.get(k):
            os.environ[k] = v


def get_api_config() -> tuple[str, str]:
    base = os.getenv('BASE_URL', '').rstrip('/')
    key = os.getenv('API_KEY', '')
    if not base or not key:
        raise ValueError('Missing BASE_URL or API_KEY in environment/.env')
    parts = urlsplit(base)
    if parts.scheme != 'https' or not parts.netloc or parts.username or parts.password:
        raise ValueError('BASE_URL must be an HTTPS URL without embedded credentials')
    if not base.endswith('/v1'):
        base += '/v1'
    return base, key


def redact(s: str, key: str) -> str:
    s = s.replace(key, '[REDACTED]')
    s = re.sub(r'sk-[A-Za-z0-9_-]{10,}', '[REDACTED]', s)
    return s[:380]


def chat(base: str, key: str, model: str, messages: list[dict], max_tokens: int, timeout: int = 75):
    payload = {'model': model, 'messages': messages, 'max_tokens': max_tokens, 'stream': False}
    # For GPT-4/GPT-4.1, temperature=0 is acceptable. For other new models, omit it if unsupported.
    if model.startswith(('gpt-4', 'gpt4')):
        payload['temperature'] = 0
    try:
        response = requests.post(
            base + '/chat/completions',
            headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
            json=payload, timeout=timeout,
        )
    except requests.RequestException as exc:
        raise RuntimeError(redact(f'Network error: {type(exc).__name__}: {exc}', key)) from None
    if response.status_code >= 400:
        raise RuntimeError(redact(f'HTTP {response.status_code}: {response.text}', key))
    try:
        return response.json()
    except ValueError:
        raise RuntimeError('Server returned non-JSON response') from None
