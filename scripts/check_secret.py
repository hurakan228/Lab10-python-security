"""Verify external secret provisioning without printing any values."""
from config import get_api_key

if not get_api_key():
    raise SystemExit("FAIL: LAB10_API_KEY was not provided")
print("PASS: LAB10_API_KEY was loaded; value was not printed")
