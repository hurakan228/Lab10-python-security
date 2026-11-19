# Lab #11 — Protecting App (using the existing Lab #10 Flask project)

This overlay is added to the existing repository. Keep the old `app.py`, `config.py`, `requirements.txt`, `tests/test_app.py`, SAST/SCA workflows, and secret-management demos. The overlay includes only the NEW or intentionally updated files listed below.

## Project origin and scope

- **Task 1 — Take an app:** Existing Flask UI + `/api/health` + `/api/config-status` from `hurakan228/Lab10-python-security`.
- **Task 2 — Design infrastructure:** Browser on localhost:8443 → unprivileged Nginx (TLS) → private Docker backend network → non-root Gunicorn + Flask on port 8000. No public cloud/VPS is claimed.
- **Task 3 — Infrastructure hardening:** Docker network segmentation, no public app ports, read-only filesystems, `cap_drop: ALL`, `no-new-privileges`, CPU/memory/PID limits, no root processes, minimal image, security headers, request-size limits, and timeouts.
- **Task 4 — Build securely:** Dockerfile only copies source files and pinned runtime dependencies; `.dockerignore` excludes credentials and .git; original SAST/SCA and new image Trivy scan; tests in CI.
- **Task 5 — Deploy securely:** Local Docker Compose TLS demo on `https://localhost:8443`. End-to-end HTTP behavior and Docker restrictions checked automatically.

## Windows walkthrough (PowerShell; Docker Desktop must be running)

1. Open PowerShell inside the cloned `Lab10-python-security` root after extracting the overlay *into the root*, keeping the folders `.github`, `deploy`, `scripts`, `tests`. Do not upload the ZIP to GitHub as a single file.

2. Run these commands one by one:

```powershell
git switch -c lab11
py -m pip install -r requirements.txt
python -m unittest discover -s tests -v
docker compose config -q
.\scripts\lab11_create_tls.ps1
docker compose build --pull
docker compose up -d --wait
docker compose ps
python scripts/lab11_verify.py
```

3. Open **https://localhost:8443** in a browser. The browser warns about the LOCAL self-signed certificate; only proceed for this locally generated demo. This does not provide publicly trusted HTTPS. Also open `https://localhost:8443/api/health`.

4. Collect real evidence for your report:

```powershell
docker compose ps
docker compose exec app id
docker compose exec proxy nginx -t
docker inspect (docker compose ps -q app) --format '{{json .HostConfig.ReadonlyRootfs}}'
docker inspect (docker compose ps -q app) --format '{{json .HostConfig.CapDrop}}'
docker compose logs --tail=30
```

5. Push your Lab #11 branch (requires GitHub authentication):

```powershell
git add .
git commit -m "Lab11 container and infrastructure hardening"
git push -u origin lab11
```

6. Open GitHub **Actions → Lab 11 - Hardened Container and Local HTTPS Deployment** and open the run for branch `lab11`. Take screenshots of tests, secure container checks, image scan, and artifact download. Never report PASS unless you see it.

7. Stop the application with `docker compose down`. The named Docker TLS volume stays so you can restart later. To delete the demo certificate as well, *after stopping*: `docker volume rm lab11_tls`.

## What has NOT been done automatically

- No real public server, public DNS, production CA certificate, remote SSH firewall, or monitored Vault installation.
- GitHub Actions and Docker must be run by you; this overlay was statically checked but cannot prove your Docker Desktop and GitHub runner results before they run.
- The TLS private key is inside a Docker-managed volume and is only for the localhost demo. Do not use it for a real site.
- The old Lab #10 HashiCorp Vault `dev` server is NOT suitable for production secrets. For a real deployment use a managed/secure Vault setup, protected identity, secrets rotation, log retention, backups, monitoring, reliable CI gates, immutable image digest pinning, a fully trusted TLS cert, and host firewall/SSH hardening.
- The new Trivy image job uploads a vulnerability report but uses `exit-code: '0'`; findings must be reviewed and resolved before calling the deployment production-ready.

## Screenshots checklist

- Task 1: GitHub app code (`app.py`) and existing tests
- Task 2: architecture diagram / compose file / network layout
- Task 3: read-only, non-root, dropped caps and backend-only private network
- Task 4: Docker build, tests, CI job and Trivy image report
- Task 5: `docker compose ps`, localhost HTTPS page, `/api/health`, `PASS` messages from `lab11_verify.py`

## Short defense text (easy English A2)

**Task 1.** I used my Python Flask application from Lab 10. The application has a web page and two API routes.

**Task 2.** I designed two services. Nginx receives HTTPS requests. The Flask app runs behind Nginx on a private Docker network.

**Task 3.** I added security rules. Containers do not run as root. They use read-only filesystems. I removed Linux capabilities and set resource limits.

**Task 4.** I built the app with Docker and Gunicorn. I did not copy secret files into the image. I used tests and security scans in GitHub Actions.

**Task 5.** I deployed the app on my own computer. I checked HTTPS, security headers, and Docker settings. This is a local test, not a public production server.
