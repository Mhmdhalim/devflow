#!/bin/sh
set -eu

cd /app
/app/.venv/bin/alembic upgrade head
exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}"
