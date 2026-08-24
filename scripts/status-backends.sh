#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"

printf '%-16s %-6s %-11s %-10s %-30s %s\n' experience port pid health current-experience log
for item in \
  'full|8050|backend-full.pid|full-backend.log' \
  'business|8061|backend-business.pid|business-backend.log' \
  'operations|8062|backend-operations.pid|operations-backend.log' \
  'simulation|8063|backend-simulation.pid|simulation-backend.log' \
  'observability|8064|backend-observability.pid|observability-backend.log' \
  'agentic|8065|backend-agentic.pid|agentic-backend.log'; do
  IFS='|' read -r code port pid_name log_name <<<"${item}"
  pid_file="${RUNTIME_DIR}/${pid_name}"
  pid_state=stopped
  if [[ -f "${pid_file}" ]]; then
    if record_is_current "${pid_file}"; then pid_state=owned-running; else pid_state=stale; fi
  fi
  status="$(http_status "http://localhost:${port}/health")"
  health="HTTP-${status}"
  current=unavailable
  if backend_health_is_eos "http://localhost:${port}" "${code}"; then
    health=healthy
    current="$(http_body "http://localhost:${port}/api/v1/platform/current-experience" | tr -d '\n' | cut -c1-90)"
  fi
  printf '%-16s %-6s %-11s %-10s %-30s %s\n' "${code}" "${port}" "${pid_state}" "${health}" "${current}" "${LOG_DIR}/${log_name}"
done
