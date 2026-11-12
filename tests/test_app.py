"""Small unit suite run as part of the CI build."""
import os
import unittest
from unittest.mock import patch
from app import app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_ui(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lab #10", response.data)

    def test_health_api(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_secret_not_disclosed(self):
        with patch.dict(os.environ, {"LAB10_API_KEY": "test-value-only"}):
            response = self.client.get("/api/config-status")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), {"api_key_configured": True})
            self.assertNotIn(b"test-value-only", response.data)


if __name__ == "__main__":
    unittest.main()
