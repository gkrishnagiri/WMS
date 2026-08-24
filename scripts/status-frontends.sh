#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"

printf '%-16s %-6s %-11s %-8s %-28s %-26s %s\n' experience port pid http backend log
for item in \
  'full|4001|8050|frontend-full.pid|full-frontend.log' \
  'business|4011|8061|frontend-business.pid|business-frontend.log' \
  'operations|4012|8062|frontend-operations.pid|operations-frontend.log' \
  'simulation|4013|8063|frontend-simulation.pid|simulation-frontend.log' \
  'observability|4014|8064|frontend-observability.pid|observability-frontend.log' \
  'agentic|4015|8065|frontend-agentic.pid|agentic-frontend.log'; do
  IFS='|' read -r code port backend_port pid_name log_name <<<"${item}"
  pid_file="${RUNTIME_DIR}/${pid_name}"
  pid_state=stopped
  if [[ -f "${pid_file}" ]]; then
    if record_is_current "${pid_file}"; then pid_state=owned-running; else pid_state=stale; fi
  fi
  status="$(http_status "http://localhost:${port}")"
  printf '%-16s %-6s %-11s %-8s %-28s %s\n' "${code}" "${port}" "${pid_state}" "${status}" "http://localhost:${backend_port}" "${LOG_DIR}/${log_name}"
done
