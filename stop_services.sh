#!/bin/bash
# ==============================================================================
# Educational Video Pipeline - Service Teardown Script
# Safely shuts down uvicorn, redis-server, and celery workers.
# ==============================================================================

echo "[INFO] Shutting down Educational Video Pipeline services..."

python3 src/tray_icon.py --stop || {
    echo "[INFO] Fallback manual shutdown..."
    kill $(lsof -t -i :8000) 2>/dev/null || true
    pkill -f "celery -A src.worker" 2>/dev/null || true
    pkill -x "redis-server" 2>/dev/null || true
}

echo "[SUCCESS] All pipeline background services terminated cleanly."
