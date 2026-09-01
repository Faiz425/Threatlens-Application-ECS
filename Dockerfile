FROM python:3.12-slim AS builder

WORKDIR /build

COPY app/requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

COPY app/app.py .
COPY app/scanner.py .


ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD /opt/venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:80/health')" || exit 1

CMD ["/opt/venv/bin/gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]