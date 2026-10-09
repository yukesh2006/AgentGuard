# ==============================================================================
# AgentGuard Backend - Dockerfile for Google Cloud Run
# ==============================================================================
# Multi-stage / optimized build using Python 3.11 slim.
# PyTorch CPU-only wheel is installed first to keep image lightweight and fast.
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" \
    PORT=8080 \
    HOST=0.0.0.0 \
    HF_HOME="/app/.cache/huggingface" \
    TRANSFORMERS_CACHE="/app/.cache/huggingface"

WORKDIR /app

# Install minimal OS dependencies for health checking
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt .

# Upgrade pip, install CPU-only PyTorch first (saves ~2GB vs default CUDA wheels),
# then install remaining backend dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Create cache directory and pre-cache Sentence-Transformer embedding weights
RUN mkdir -p /app/.cache/huggingface && chmod -R 777 /app/.cache && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application source code and modules
COPY backend/ ./backend/
COPY ml/ ./ml/
COPY policy/ ./policy/
COPY database/ ./database/

# Expose default Cloud Run container port
EXPOSE 8080

# Health check against existing /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT}/health || exit 1

# Launch FastAPI backend binding to 0.0.0.0 and Cloud Run's dynamic $PORT
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
