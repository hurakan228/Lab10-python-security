"""Validate that scanners really ran, without treating security findings as CI errors."""
import json
import sys
from pathlib import Path


def main():
    tool, filename = sys.argv[1:3]
    path = Path(filename)
    if not path.is_file() or not path.stat().st_size:
        raise SystemExit(f"FAIL: {tool} output file missing or empty")
    data = json.loads(path.read_text(encoding="utf-8"))
    if tool == "semgrep":
        if not isinstance(data.get("results"), list):
            raise SystemExit("FAIL: Semgrep results list missing")
        if data.get("errors"):
            raise SystemExit("FAIL: Semgrep reported errors")
        if not data.get("paths", {}).get("scanned"):
            raise SystemExit("FAIL: Semgrep scanned no files")
        rules = [result.get("check_id", "") for result in data["results"]]
        if not any("lab10-python-eval" in rid for rid in rules):
            raise SystemExit("FAIL: Semgrep did not detect the intentional eval example")
        print(f"Semgrep PASS: scanned files; {len(data['results'])} findings reported")
    elif tool == "trivy":
        if not isinstance(data.get("Results"), list):
            raise SystemExit("FAIL: Trivy Results list missing; scanner possibly failed")
        vulnerabilities = sum(len(x.get("Vulnerabilities") or []) for x in data["Results"])
        secrets = sum(len(x.get("Secrets") or []) for x in data["Results"])
        print(f"Trivy PASS: {vulnerabilities} vulnerability findings; {secrets} secret findings")
    else:
        raise SystemExit("Unknown scanner")


if __name__ == "__main__":
    main()
