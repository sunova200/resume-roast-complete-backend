#!/usr/bin/env bash
set -a
[ -f /workspace/.env ] && . /workspace/.env
set +a

rq worker --with-scheduler --url redis://valkey:6379
