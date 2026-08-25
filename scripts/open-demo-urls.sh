#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/demo-stack-lib.sh"
backend_url="${EOS_BACKEND_URL:-http://localhost:8050}"
if command -v jq >/dev/null 2>&1; then
  curl -fsS "${backend_url}/api/v1/demo-readiness/urls" | jq -r '.urls | sort_by(.recommended_order)[] | "\(.recommended_order). \(.label) [\(.experience)]\n   \(.url)\n   \(.description)"'
else
  echo "Presenter URLs: ${backend_url}/api/v1/demo-readiness/urls"
  curl -fsS "${backend_url}/api/v1/demo-readiness/urls"
fi
