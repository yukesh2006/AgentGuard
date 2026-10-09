# ==============================================================================
# AgentGuard Backend - Dockerfile for Google Cloud Run
# ==============================================================================
# Note: When building, use the project root as build context so that root-level
# modules (ml/, policy/, database/) are accessible:
#   docker build -t agentguard-backend -f backend/Dockerfile .
# ==============================================================================

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" \
    PORT=8080 \
    HOST=0.0.0.0 \
    HF_HOME="/app/.cache/huggingface" \
    TRANSFORMERS_CACHE="/app/.cache/huggingface"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Create cache directory and pre-cache Sentence-Transformer embedding weights
RUN mkdir -p /app/.cache/huggingface && chmod -R 777 /app/.cache && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY backend/ ./backend/
COPY ml/ ./ml/
COPY policy/ ./policy/
COPY database/ ./database/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT}/health || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
