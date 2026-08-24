#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"

failures=0
stop_owned_record "${RUNTIME_DIR}/frontend-full.pid" full '--port 4001' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/frontend-business.pid" business '--port 4011' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/frontend-operations.pid" operations '--port 4012' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/frontend-simulation.pid" simulation '--port 4013' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/frontend-observability.pid" observability '--port 4014' || failures=$((failures + 1))
stop_owned_record "${RUNTIME_DIR}/frontend-agentic.pid" agentic '--port 4015' || failures=$((failures + 1))
(( failures == 0 ))
