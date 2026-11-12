# Lab #10 — Defense report checklist

Student: Zhunussov Mukhammed
Topic: CI Pipeline and Secret Management
Language: Python (Flask)

1. **Purpose:** Build Python UI + API, scan with 2 SAST and 1 SCA tools, export artifacts, demonstrate external, decentralized and centralized secret provisioning.
2. **Repository:** URL to the new public GitHub repo (insert after creation).
3. **Build:** Python 3.12; unittest results; distributable ZIP.
4. **SAST:** Semgrep p/python + local lab rule; CodeQL Python security-extended. Record actual counts and evidence from produced JSON and SARIF (do not fabricate).
5. **SCA:** Trivy filesystem vuln + secret scans. List counts from JSON report, noting that findings do not automatically fail CI.
6. **External secrets:** Application reads from local ignored `.env`; never show values.
7. **Decentralized:** SOPS + age encrypts a dotenv file. Public recipient is in `.sops.yaml`; ciphertext is committed; private identity is outside Git and provided to CI using a GitHub Actions secret.
8. **Centralized:** HashiCorp Vault KV v2 in ephemeral dev server; app obtains value with restricted 10-min read-only token; write is rejected (403). Note dev-mode limitations.
9. **Conclusions:** Describe real status of 5 jobs and reports, scope, limitations and recommendations.

Before submitting, attach a screenshot of each job and artifacts; record actual run URL and date. No production keys should be used.
