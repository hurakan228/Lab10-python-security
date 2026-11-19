# Lab #11: secure application artifact; do not include source-tree secrets.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /opt/app
COPY requirements.txt ./requirements.txt
COPY deploy/requirements-prod.txt ./deploy/requirements-prod.txt
RUN python -m pip install --no-cache-dir -r deploy/requirements-prod.txt \
    && groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin appuser

COPY app.py config.py ./
USER 10001:10001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--worker-tmp-dir", "/tmp", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
