#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"
cd "${PROJECT_ROOT}"

printf '%s\n' '=== Docker infrastructure ==='
docker compose ps
printf '%s\n' '=== Backends/BFFs ==='
"${SCRIPT_DIR}/status-backends.sh"
printf '%s\n' '=== Frontends ==='
"${SCRIPT_DIR}/status-frontends.sh"
printf '%s\n' '=== Observability endpoints ==='
for check in \
  'Prometheus|http://localhost:9090/-/ready' \
  'Grafana|http://localhost:3001/api/health' \
  'Tempo|http://localhost:3200/ready' \
  'Loki|http://localhost:3100/ready' \
  'Collector|http://localhost:13133/'; do
  IFS='|' read -r label url <<<"${check}"
  print_check "${label}" "${url}" || true
done
