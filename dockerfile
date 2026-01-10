FROM python:3.12-slim-bookworm

# --- Env ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Merida

# --- Virtualenv ---
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# --- System deps ---
RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    libssl-dev \
    gcc \
    python3-dev \
    && update-ca-certificates --fresh \
    && rm -rf /var/lib/apt/lists/*

# --- Workdir ---
WORKDIR /app

# --- Install deps ---
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Copy source ---
COPY server/ server/
COPY app.py .

# --- Expose ---
EXPOSE 8000

# --- Run ASGI ---
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
