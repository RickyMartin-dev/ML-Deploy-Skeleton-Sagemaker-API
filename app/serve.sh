#!/usr/bin/env bash
set -euo pipefail

# SageMaker calls: docker run <image> serve [possibly other args]
# We just ignore the word 'serve' and boot gunicorn+uvicorn on :8080.

# If the first arg is 'serve', drop it.
if [[ "${1-}" == "serve" ]]; then
  shift
fi

# Boot the FastAPI app
exec gunicorn \
  -k uvicorn.workers.UvicornWorker \
  -w "${WORKERS:-2}" \
  -b 0.0.0.0:8080 \
  app.app:app
