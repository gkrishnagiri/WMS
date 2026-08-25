#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <RUN_ID>" >&2
  exit 2
fi
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/demo-stack-lib.sh"
backend_url="${EOS_BACKEND_URL:-http://localhost:8050}"
curl -fsS "${backend_url}/api/v1/ui-acceptance/runs/$1/report.md"
