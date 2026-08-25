#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/demo-stack-lib.sh"
backend_url="${EOS_BACKEND_URL:-http://localhost:8050}"
curl -fsS "${backend_url}/api/v1/ui-acceptance/summary" | if command -v jq >/dev/null 2>&1; then jq .; else cat; fi
