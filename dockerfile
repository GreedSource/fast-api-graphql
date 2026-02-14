# =========================
# STAGE 1 — LINT
# =========================
FROM python:3.12-slim-bookworm AS lint

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar ruff solamente
RUN pip install --no-cache-dir ruff

# Copiar código
COPY server/ server/
COPY app.py .
COPY requirements.txt .

# Ejecutar lint (si falla, se detiene el build)
RUN ruff check .

# =========================
# STAGE 2 — RUNTIME
# =========================
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Merida

# Crear virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias del sistema (solo lo necesario)
RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    libssl-dev \
    gcc \
    python3-dev \
    && update-ca-certificates --fresh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY server/ server/
COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
