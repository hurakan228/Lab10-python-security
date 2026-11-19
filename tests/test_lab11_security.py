"""Static guardrails for the added Lab 11 deployment files."""
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]


class Lab11SecurityTests(unittest.TestCase):
    def test_dockerfile_runs_unprivileged(self):
        content = (BASE / 'Dockerfile').read_text()
        self.assertIn('USER 10001:10001', content)
        self.assertIn('gunicorn', content)
        self.assertNotIn('COPY . .', content)

    def test_app_not_published(self):
        content = (BASE / 'docker-compose.yml').read_text()
        self.assertIn('internal: true', content)
        self.assertIn('127.0.0.1:8443:8443', content)
        self.assertIn('no-new-privileges:true', content)
        self.assertIn('read_only: true', content)
        self.assertIn('cap_drop: [ALL]', content)

    def test_nginx_has_security_headers(self):
        content = (BASE / 'deploy/nginx/default.conf').read_text()
        self.assertIn('ssl_protocols TLSv1.2 TLSv1.3', content)
        self.assertIn('X-Content-Type-Options', content)
        self.assertIn('Content-Security-Policy', content)


if __name__ == '__main__':
    unittest.main()
