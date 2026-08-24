#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export APP_PORT=8063
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-eos-simulation-bff}"
exec .venv/bin/uvicorn app.bff.simulation_main:app --host 0.0.0.0 --port 8063 --reload
