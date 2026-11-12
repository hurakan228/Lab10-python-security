"""Fast, offline check of the Vault-reading application code."""
import io
import os
import unittest
from unittest.mock import patch

import config

class FakeResponse:
    def __enter__(self):
        return io.BytesIO(b'{"data":{"data":{"LAB10_API_KEY":"vault-demo-test"}}}')
    def __exit__(self, *args):
        return False

class ConfigTests(unittest.TestCase):
    @patch('config.urlopen', return_value=FakeResponse())
    def test_vault_reads_with_scoped_token(self, fake_urlopen):
        with patch.dict(os.environ, {'LAB10_SECRET_BACKEND':'vault',
                                  'VAULT_ADDR':'http://127.0.0.1:8200',
                                  'VAULT_TOKEN':'not-a-real-token'}):
            self.assertEqual(config.get_api_key(), 'vault-demo-test')
            request = fake_urlopen.call_args.args[0]
            self.assertEqual(request.get_header('X-vault-token'), 'not-a-real-token')
            self.assertEqual(request.full_url,
                'http://127.0.0.1:8200/v1/lab10/data/app')

if __name__ == '__main__':
    unittest.main()
