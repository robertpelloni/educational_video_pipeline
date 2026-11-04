#!/bin/bash
# ==============================================================================
# Educational Video Pipeline - Service Startup Script
# Boots FastAPI backend (uvicorn), Redis broker, and Celery background workers.
# ==============================================================================

set -e

# Base environment variables
export API_USERNAME=${API_USERNAME:-admin}
export API_PASSWORD=${API_PASSWORD:-local_dev_password}
export CELERY_BROKER_URL=${CELERY_BROKER_URL:-redis://localhost:6379/0}

echo "[INFO] Starting Redis message broker..."
if ! pgrep -x "redis-server" > /dev/null; then
    redis-server --daemonize yes 2>/dev/null || redis-server > redis.log 2>&1 &
fi

echo "[INFO] Starting FastAPI Uvicorn API server on port 8000..."
kill $(lsof -t -i :8000) 2>/dev/null || true
uvicorn src.api_router:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

echo "[INFO] Starting Celery asynchronous video processing worker..."
celery -A src.worker.celery_app worker --loglevel=info > celery.log 2>&1 &

sleep 3
echo "[INFO] Verifying service health..."
curl -s http://127.0.0.1:8000/status || echo "[WARN] API still warming up..."
echo ""
echo "[SUCCESS] Services initialized successfully."
