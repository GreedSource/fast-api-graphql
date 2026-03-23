# =========================
# STAGE 1 — LINT
# =========================
FROM python:3.12-slim-bookworm AS lint

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir ruff

COPY server/ server/
COPY app.py .
COPY requirements.txt .

RUN ruff check .

# =========================
# STAGE 2 — BUILDER
# =========================
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Solo dependencias necesarias para compilar
RUN apt-get update && apt-get install --no-install-recommends -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Instalar deps (compiladas aquí)
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# =========================
# STAGE 3 — RUNTIME (final)
# =========================
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Merida

WORKDIR /app

# Solo lo mínimo para runtime
RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    && update-ca-certificates --fresh \
    && rm -rf /var/lib/apt/lists/*

# Copiar virtualenv ya construido
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar código
COPY server/ server/
COPY app.py .

# Usuario no-root (seguridad)
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]