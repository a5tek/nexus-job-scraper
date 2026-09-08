FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright, PyMuPDF, and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api/app /app/app
COPY apps/api/migrations /app/migrations
COPY apps/api/pyproject.toml /app/pyproject.toml

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
