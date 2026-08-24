#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"
cd "${PROJECT_ROOT}"

docker compose config >/dev/null
docker compose up -d
docker compose ps

for service in postgres redis otel-collector; do
  if wait_for_compose_health "${service}"; then
    printf 'Infrastructure service ready: %s\n' "${service}"
  else
    printf 'Infrastructure service not ready: %s\n' "${service}" >&2
    exit 1
  fi
done

for check in \
  'Prometheus|http://localhost:9090/-/ready' \
  'Grafana|http://localhost:3001/api/health' \
  'Tempo|http://localhost:3200/ready' \
  'Loki|http://localhost:3100/ready' \
  'Collector|http://localhost:13133/'; do
  IFS='|' read -r label url <<<"${check}"
  print_check "${label}" "${url}"
done
