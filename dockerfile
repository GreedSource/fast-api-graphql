# =========================
# STAGE 1 — LINT
# =========================
FROM python:3.12-slim-bookworm AS lint

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

# Dependencias SOLO para build
RUN apt-get update && apt-get install --no-install-recommends -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# =========================
# STAGE 3 — RUNTIME
# =========================
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Merida

# 🔐 Crear usuario no root
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Solo dependencias mínimas runtime
RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar venv desde builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar código
COPY server/ server/
COPY app.py .
COPY manage.py .

# Cambiar permisos
RUN chown -R app:app /app

USER app

EXPOSE 8000

# ⚠️ seed opcional
CMD ["sh", "-c", "python manage.py migrate && if [ \"$RUN_SEEDERS\" = \"true\" ]; then python manage.py seed-all; fi && uvicorn app:app --host 0.0.0.0 --port 8000 --ws websockets --proxy-headers"]