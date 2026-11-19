# Lab #11 — Protecting App
**Student:** Zhunussov Mukhammed  
**Topic:** Protecting app  
**Target:** Applying as much practical protection as possible to a demo application

## Task 1 — Take an app
I used my Flask application from Lab 10. It has a simple web page and two API endpoints. My source code is on GitHub.

**Screenshot 1:** [Insert screenshot of repository and app.py]

## Task 2 — Design infrastructure
My design has a user, Nginx, and a Flask app. Nginx uses HTTPS. Gunicorn starts Flask. The app is on a private Docker network. Only the local HTTPS port is published.

**Diagram:** User → https://localhost:8443 → Nginx → private Docker backend → Gunicorn / Flask.

**Screenshot 2:** [Insert screenshot of docker-compose.yml]

## Task 3 — Harden infrastructure
I set a non-root user, a read-only filesystem, `no-new-privileges`, dropped Linux capabilities, and CPU/memory/PID limits. I limited request size and timeouts in Nginx and added HTTP security headers.

**Screenshot 3:** [Insert actual `docker inspect` and `id` output]

## Task 4 — Build securely
I created a Dockerfile. It copies only the needed Python files. It does not include secret files. I used tests and static security checks. I also scan the final Docker image with Trivy.

**Screenshot 4:** [Insert real Docker build + GitHub Actions / Trivy results]

## Task 5 — Deploy securely
I run two Docker containers. Nginx uses a local self-signed HTTPS certificate for this lab. The Flask app is not published directly. I test the website, health API, headers, and Docker settings.

**Screenshot 5:** [Insert real localhost HTTPS page]
**Screenshot 6:** [Insert real `python scripts/lab11_verify.py` PASS output]

## Conclusion
I added application and infrastructure security. The main protections are HTTPS, network isolation, non-root containers, read-only filesystems, security headers, and automated tests. This is a local demonstration and not a finished public production environment.

## Real test results (fill after running)
- Unit tests: [PASS/FAIL + date]
- Docker Compose config: [PASS/FAIL + date]
- Image build: [PASS/FAIL + date]
- HTTPS and hardening script: [PASS/FAIL + date]
- Trivy findings: [count + severity + what was fixed]
- GitHub Actions run: [URL + outcome]
