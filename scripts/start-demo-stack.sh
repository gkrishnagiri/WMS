#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/start-infra.sh"
"${SCRIPT_DIR}/start-backends.sh"
"${SCRIPT_DIR}/start-frontends.sh"

cat <<'EOF'

EOS demo stack URLs
-------------------
Full UI:               http://localhost:4001
Business UI:           http://localhost:4011
Operations UI:         http://localhost:4012
Simulation Lab UI:     http://localhost:4013
Observability UI:      http://localhost:4014
Agentic UI:            http://localhost:4015
Demo Control Panel:    http://localhost:4001/demo-control

Grafana:               http://localhost:3001
Prometheus:            http://localhost:9090
Tempo ready endpoint:  http://localhost:3200/ready
Loki ready endpoint:   http://localhost:3100/ready

Next validation command:
  ./scripts/status-demo-stack.sh
  ./scripts/validate-demo-stack.sh
EOF
