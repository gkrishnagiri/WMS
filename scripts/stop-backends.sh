#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"

failures=0
stop_owned_record "${RUNTIME_DIR}/backend-full.pid" full 'app.main:app' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/backend-business.pid" business 'app.bff.business_main:app' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/backend-operations.pid" operations 'app.bff.operations_main:app' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/backend-simulation.pid" simulation 'app.bff.simulation_main:app' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/backend-observability.pid" observability 'app.bff.observability_main:app' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/backend-agentic.pid" agentic 'app.bff.agentic_main:app' || failures=$((failures + 1))
(( failures == 0 ))
