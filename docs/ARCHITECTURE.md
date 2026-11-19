# Lab 11 Architecture

```mermaid
flowchart TB
    U["Browser: local machine"] -->|"HTTPS 127.0.0.1:8443"| N["Nginx proxy: TLS + headers"]
    subgraph DockerHost ["Docker Desktop / Linux host"]
        subgraph EdgeNetwork ["edge bridge network"]
            N
        end
        subgraph BackendNetwork ["backend internal network"]
            N -->|"HTTP 8000, internal only"| A["Gunicorn + Flask app"]
        end
    end
    G["GitHub Actions"] --> S["Semgrep + CodeQL + Tests"]
    G --> T["Docker Build + Trivy"]
    T --> A
```

**Trust boundaries:** The host only publishes port 8443 on `127.0.0.1`, not on public interfaces. The Flask backend has no published host port. Both application and proxy containers are non-root with read-only root filesystems and dropped capabilities. TLS uses a **temporary self-signed certificate** kept in a local Docker volume, not in Git.

**Production changes required:** Trusted public certificate and managed key storage, real DNS and host firewall, secured server/SSH, continuous monitoring, robust secret provision/rotation, digest pinning, image scanning gates, and appropriate backups. This is a lab deployment, not public production.
