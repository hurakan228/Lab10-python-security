"""Read decrypted dotenv content from stdin; verify app receives it, do not log it."""
import io
import os
import sys
from dotenv import dotenv_values
from config import get_api_key


def main():
    text = sys.stdin.read()
    values = dotenv_values(stream=io.StringIO(text))
    key = values.get("LAB10_API_KEY")
    if not key:
        raise SystemExit("ERROR: SOPS decrypt did not return LAB10_API_KEY")
    os.environ["LAB10_API_KEY"] = key
    os.environ.pop("LAB10_SECRET_BACKEND", None)
    if get_api_key() != key:
        raise SystemExit("ERROR: application did not use the decrypted value")
    print("PASS: application loaded decrypted dotenv value without displaying it")


if __name__ == "__main__":
    main()
