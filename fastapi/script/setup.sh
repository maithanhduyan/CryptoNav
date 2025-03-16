#!/bin/bash
# app/script/start.sh

alembic upgrade head

if [ "$MODE" == "development" ]; then
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
fi