"""Small training web app for Lab #10. It never prints or returns secrets."""
from flask import Flask, jsonify
from config import get_api_key

app = Flask(__name__)


@app.get("/")
def home():
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
    <title>Lab #10 Demo</title></head><body>
    <h1>Lab #10 – CI Pipeline &amp; Secret Management</h1>
    <p>Training application with a UI and JSON API.</p>
    <p>Try <a href="/api/health">/api/health</a> or
    <a href="/api/config-status">/api/config-status</a>.</p>
    </body></html>"""


@app.get("/api/health")
def health():
    return jsonify(status="ok", service="lab10-demo")


@app.get("/api/config-status")
def config_status():
    # Only return whether configuration exists; never disclose the secret.
    return jsonify(api_key_configured=bool(get_api_key()))


if __name__ == "__main__":
    # Bind locally only. Flask's production serving is outside the lab scope.
    app.run(host="127.0.0.1", port=5000, debug=False)
