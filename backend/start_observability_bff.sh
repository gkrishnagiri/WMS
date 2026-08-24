#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export APP_PORT=8064
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-eos-observability-bff}"
exec .venv/bin/uvicorn app.bff.observability_main:app --host 0.0.0.0 --port 8064 --reload
