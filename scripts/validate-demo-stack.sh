#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"
cd "${PROJECT_ROOT}"

failures=0
check() {
  if ! print_check "$1" "$2"; then failures=$((failures + 1)); fi
}

printf '%s\n' '=== Infrastructure ==='
check Prometheus http://localhost:9090/-/ready
check Grafana http://localhost:3001/api/health
check Tempo http://localhost:3200/ready
check Loki http://localhost:3100/ready
check Collector http://localhost:13133/

printf '%s\n' '=== Backend/BFF health ==='
for item in 'full|8050' 'business|8061' 'operations|8062' 'simulation|8063' 'observability|8064' 'agentic|8065'; do
  IFS='|' read -r code port <<<"${item}"
  if backend_health_is_eos "http://localhost:${port}" "${code}"; then
    printf 'PASS %-32s %s/health\n' "${code}" "http://localhost:${port}"
  else
    printf 'FAIL %-32s %s/health\n' "${code}" "http://localhost:${port}"
    failures=$((failures + 1))
  fi
done

printf '%s\n' '=== Platform metadata ==='
for port in 8050 8061 8062 8063 8064 8065; do
  check "platform current (${port})" "http://localhost:${port}/api/v1/platform/current-experience"
  check "platform topology (${port})" "http://localhost:${port}/api/v1/platform/topology"
done

printf '%s\n' '=== Facades ==='
check business-facade http://localhost:8061/api/v1/business/summary
check operations-facade http://localhost:8062/api/v1/operations-console/summary
check simulation-facade http://localhost:8063/api/v1/simulation-lab/summary
check observability-facade http://localhost:8064/api/v1/observability-control/summary
check agentic-facade http://localhost:8065/api/v1/agentic-console/summary

printf '%s\n' '=== Frontends ==='
for port in 4001 4011 4012 4013 4014 4015; do
  check "frontend ${port}" "http://localhost:${port}"
done

if (( failures > 0 )); then
  printf 'Demo stack validation failed: %s check(s) failed.\n' "${failures}" >&2
  exit 1
fi
printf '%s\n' 'Demo stack validation passed.'
