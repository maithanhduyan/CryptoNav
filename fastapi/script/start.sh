#!/bin/bash
# app/script/start.sh
set -e

if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in development mode (reload enabled)"
    exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting in production mode (multiple workers)"
    # Chạy Uvicorn với 4 worker (số lượng worker tùy chỉnh theo tài nguyên)
    exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
