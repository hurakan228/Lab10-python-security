"""Run an ephemeral, local-only Vault dev server and prove least-privilege token access.

The dev root token is generated for this CI run, only used for bootstrap,
and never printed. The application uses a separate 10-minute read-only token.
Never use Vault dev mode for production secrets.
"""
import json
import os
import secrets
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = 'http://127.0.0.1:8200'
NAME = 'lab10-vault-demo'

def api(method, path, token=None, value=None):
    data = json.dumps(value).encode('utf-8') if value is not None else None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['X-Vault-Token'] = token
    req = Request(URL + '/v1/' + path, data=data, headers=headers, method=method)
    with urlopen(req, timeout=7) as response:
        body = response.read()
        return json.loads(body) if body else {}

def ready():
    for attempt in range(60):
        # If Docker exited, do not keep waiting for an unreachable port.
        state = subprocess.run(
            ['docker', 'inspect', '-f', '{{.State.Running}}', NAME],
            capture_output=True, text=True, check=False)
        if state.returncode == 0 and state.stdout.strip() == 'false':
            status = subprocess.run(
                ['docker', 'inspect', '-f', '{{.State.Status}} (exit={{.State.ExitCode}})', NAME],
                capture_output=True, text=True, check=False)
            raise RuntimeError('Vault Docker container stopped: ' + status.stdout.strip())
        try:
            api('GET', 'sys/health')
            return
        except (HTTPError, URLError, OSError, TimeoutError, ValueError):
            # ConnectionResetError is an OSError and can occur during startup.
            if attempt in (0, 10, 20, 40):
                print(f'Vault readiness check: waiting for dev server ({attempt + 1}/60)')
            time.sleep(1)
    raise RuntimeError('Vault dev server did not become ready within 60 seconds')

def main():
    root_token = secrets.token_urlsafe(32)
    # Remove any leftover demo container from a previous interrupted run.
    subprocess.run(['docker', 'rm', '-f', NAME], check=False, capture_output=True)
    cmd = ['docker','run','-d','--name',NAME,
           '--cap-add=IPC_LOCK','-p','127.0.0.1:8200:8200',
           '-e','VAULT_DEV_ROOT_TOKEN_ID='+root_token,
           '-e','VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200',
           'hashicorp/vault:1.20.4','server','-dev']
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    try:
        ready()
        api('POST','sys/mounts/lab10',root_token,
            {'type':'kv','options':{'version':'2'}})
        api('POST','lab10/data/app',root_token,
            {'data':{'LAB10_API_KEY':'lab10-demo-'+secrets.token_urlsafe(24)}})
        policy = 'path "lab10/data/app" { capabilities = ["read"] }'
        api('PUT','sys/policies/acl/lab10-readonly',root_token,{'policy':policy})
        response = api('POST','auth/token/create',root_token,{
            'policies':['lab10-readonly'], 'ttl':'10m',
            'renewable': False, 'no_default_policy': True})
        scoped_token = response['auth']['client_token']
        issued_policies = response['auth']['policies']
        if issued_policies != ['lab10-readonly']:
            raise RuntimeError('Unexpected policies on restricted token')
        # App config reads from Vault, not from local .env or GitHub Secrets.
        env = os.environ.copy()
        env.pop('LAB10_API_KEY', None)
        env.update({'LAB10_SECRET_BACKEND':'vault',
                    'VAULT_ADDR':URL, 'VAULT_TOKEN':scoped_token})
        subprocess.run([sys.executable,'-m','scripts.check_secret'],
                       check=True, env=env)
        # Prove least privilege: write must be refused with HTTP 403.
        try:
            api('POST','lab10/data/app',scoped_token,
                {'data':{'LAB10_API_KEY':'forbidden-update'}})
        except HTTPError as exc:
            if exc.code != 403:
                raise RuntimeError('Expected 403 for write request') from exc
        else:
            raise RuntimeError('Restricted token unexpectedly allowed write')
        print('PASS: Vault stored a random demo secret; scoped token READ allowed, WRITE 403.')
        print('PASS: app read Vault KV v2 via token; no secret values were logged.')
    finally:
        subprocess.run(['docker','rm','-f',NAME], check=False, capture_output=True)

if __name__ == '__main__':
    main()
