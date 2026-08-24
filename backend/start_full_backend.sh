#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export APP_PORT=8050
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-eos-full-backend}"
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8050 --reload
