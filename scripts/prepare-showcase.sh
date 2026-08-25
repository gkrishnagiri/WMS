#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/demo-stack-lib.sh"

backend_url="${EOS_BACKEND_URL:-http://localhost:8050}"
echo "Preparing local EOS showcase (no model call, approval, execution, or external integration)…" >&2
curl -fsS -X POST "${backend_url}/api/v1/demo-readiness/prepare-showcase" \
  -H "Content-Type: application/json" \
  -d '{"profile":"SHOWCASE_RESET","create_prepared_runs":true,"created_by_role":"DEMO_PRESENTER"}' \
  | if command -v jq >/dev/null 2>&1; then jq .; else cat; fi
