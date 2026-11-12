"""Intentional scanner test input. NEVER import or execute this example.

This file exists to produce a detectable static-analysis finding. It is
not included in the app distribution and is never used by the Flask app.
"""

def insecure_example(untrusted_text):
    return eval(untrusted_text)  # intentionally unsafe; scanner demo only
