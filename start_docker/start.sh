#!/bin/bash

echo "Waiting..."
sleep 5

alembic upgrade 1988f72f5bba

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000