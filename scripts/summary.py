"""Concise CI job summary, excluding any secret values."""
import json
import os
import sys
from pathlib import Path


def main():
    name = sys.argv[1]
    file = Path("reports") / ("semgrep.json" if name == "semgrep" else "trivy.json")
    lines = [f"### {name} findings", ""]
    if file.exists():
        obj = json.loads(file.read_text())
        if name == "semgrep":
            lines.append(f"- Semgrep findings: **{len(obj.get('results', []))}**")
            lines.append(f"- Files scanned: **{len(obj.get('paths', {}).get('scanned', []))}**")
        else:
            lines.append(f"- Dependency vulnerabilities: **{sum(len(x.get('Vulnerabilities') or []) for x in obj.get('Results', []))}**")
            lines.append(f"- Potential exposed secrets: **{sum(len(x.get('Secrets') or []) for x in obj.get('Results', []))}**")
        lines.append("- Finding count does not control pass/fail; scanner errors do.")
    else:
        lines.append("- Scanner report missing: investigate job logs.")
    message = "\n".join(lines) + "\n"
    dest = os.getenv("GITHUB_STEP_SUMMARY")
    if dest:
        with open(dest, "a", encoding="utf8") as f:
            f.write(message)
    print(message)

if __name__ == "__main__":
    main()
