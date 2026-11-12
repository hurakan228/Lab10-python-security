"""Get a demo secret from the environment/.env or a token-scoped Vault KV v2 path."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from dotenv import load_dotenv

# An ignored local .env may be used for offline practice; it is never packaged.
load_dotenv(dotenv_path=Path(__file__).resolve().parent / '.env', override=False)

def get_api_key():
    if os.getenv('LAB10_SECRET_BACKEND', 'env') != 'vault':
        return os.getenv('LAB10_API_KEY', '')
    url = os.environ['VAULT_ADDR'].rstrip('/') + '/v1/lab10/data/app'
    token = os.environ['VAULT_TOKEN']
    req = Request(url, headers={'X-Vault-Token': token})
    with urlopen(req, timeout=7) as res:
        payload = json.load(res)
    return payload['data']['data']['LAB10_API_KEY']
