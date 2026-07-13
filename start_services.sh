#!/bin/bash
API_USERNAME=admin API_PASSWORD=supersecretpipeline uvicorn src.api_router:app --port 8000 > uvicorn.log 2>&1 &
redis-server > /dev/null 2>&1 &
celery -A src.worker.celery_app worker --loglevel=info > /dev/null 2>&1 &
sleep 5
