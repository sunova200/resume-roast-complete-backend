#!/usr/bin/env bash
set -a
[ -f /workspace/.env ] && . /workspace/.env
set +a

uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
