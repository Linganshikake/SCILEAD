"""Low-cost model probe. A successful proxy response is not proof of the underlying model identity."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from api_utils import read_env_file, get_api_config, chat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', default='.env', help='local .env; never commit it')
    parser.add_argument('--models', nargs='+', default=[
        'gpt-4.1-2025-04-14', 'gpt-4.1', 'gpt-4-turbo-2024-04-09',
    ])
    parser.add_argument('--save', default='probe_results.json')
    args = parser.parse_args()
    read_env_file(args.env)
    base, key = get_api_config()
    print('Target host:', base.split('/')[2])
    print('Number of requests (maximum):', len(args.models))
    out = []
    for name in args.models:
        record = {'requested_model': name, 'checked_at_utc': datetime.now(timezone.utc).isoformat()}
        try:
            resp = chat(base, key, name, [{'role':'user','content':'Reply with OK only.'}], 8, timeout=(15, 120))
            record.update({
                'status': 'success',
                'returned_model': resp.get('model'),
                'reply': (resp.get('choices') or [{}])[0].get('message', {}).get('content'),
                'usage': resp.get('usage', {}),
            })
            print('[SUCCESS]', name, '->', record['returned_model'], 'usage:', record['usage'])
        except Exception as exc:
            record.update({'status': 'failed', 'error': str(exc)})
            print('[FAILED] ', name, str(exc))
        out.append(record)
    with open(args.save, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Results written:', args.save)
    print('Note: a proxy may alias model IDs; success alone does not establish backend model identity.')

if __name__ == '__main__':
    main()
