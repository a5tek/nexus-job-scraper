# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python packages from builder
COPY --from=builder /install /usr/local

# Security: Create non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app appuser \
    && mkdir -p /app/storage/resumes \
    && chown -R appuser:appgroup /app

COPY --chown=appuser:appgroup apps/api/app /app/app
COPY --chown=appuser:appgroup apps/api/migrations /app/migrations
COPY --chown=appuser:appgroup apps/api/pyproject.toml /app/pyproject.toml

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
