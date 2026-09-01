# ==============================================================================
# SEPTERIA (SIH26186) - Production Backend Dockerfile
# Multi-arch compatible Python 3.11 image for Railway / Cloud Container Hosting
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Ensure Python output is unbuffered and PYTHONPATH includes the root app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Install minimal OS dependencies for psycopg2 and audio feature extraction
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy only the necessary runtime application code and trained models
COPY backend /app/backend
COPY shared /app/shared
COPY database /app/database
COPY ml/models /app/ml/models

# Default port for Railway/Render ($PORT) with fallback to 8000
EXPOSE 8000

# Run uvicorn binding to 0.0.0.0 and dynamic $PORT
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
