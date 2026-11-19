"""Check real HTTPS behavior and Docker settings (run after docker compose up)."""
import json
import ssl
import subprocess
import sys
import urllib.request


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print('PASS:', message)


def get_container(service):
    cid = run('docker', 'compose', 'ps', '-q', service)
    check(bool(cid), service + ' container exists')
    return json.loads(run('docker', 'inspect', cid))[0]


def main():
    # Bypass CA check ONLY for our intentionally self-signed localhost cert.
    ctx = ssl._create_unverified_context()
    for path in ('/', '/api/health', '/api/config-status'):
        with urllib.request.urlopen('https://127.0.0.1:8443' + path, context=ctx, timeout=10) as response:
            body = response.read()
            check(response.status == 200, path + ' returns HTTP 200')
            check(response.headers.get('X-Content-Type-Options') == 'nosniff', 'nosniff header present')
            check(response.headers.get('X-Frame-Options') == 'DENY', 'frame protection present')
            check('default-src' in response.headers.get('Content-Security-Policy', ''), 'CSP header present')
            check(response.headers.get('Cache-Control') == 'no-store', 'no-store header present')
            if path == '/api/health':
                check(json.loads(body)['status'] == 'ok', 'health status is ok')
            if path == '/api/config-status':
                check('LAB10_API_KEY' not in body.decode(), 'API key is not in the response')
    for name in ('app', 'proxy'):
        data = get_container(name)
        host = data['HostConfig']
        check(host['ReadonlyRootfs'] is True, name + ': read-only root filesystem')
        check('ALL' in [x.upper() for x in host.get('CapDrop') or []], name + ': all Linux capabilities dropped')
        check(any('no-new-privileges' in x for x in host.get('SecurityOpt') or []), name + ': no-new-privileges is enabled')
        check(data['Config'].get('User') not in ('', '0', 'root'), name + ': runs as non-root user')
        check(not host.get('Privileged'), name + ': not privileged')
    app = get_container('app')
    check(not app['HostConfig'].get('PortBindings'), 'app container has no host-published ports')
    print('PASS: Lab 11 integration and security checks completed.')
    print('NOTE: TLS certificate is intentionally self-signed; this is NOT a public production deployment.')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        sys.exit(1)
