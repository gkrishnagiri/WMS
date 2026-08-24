#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export APP_PORT=8062
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-eos-operations-bff}"
exec .venv/bin/uvicorn app.bff.operations_main:app --host 0.0.0.0 --port 8062 --reload
