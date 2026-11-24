FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY frontend /app/frontend
COPY src/assets /app/src/assets

RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8080/api/v1/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
