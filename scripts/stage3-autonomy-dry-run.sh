#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <STAGE3_RUN_ID>" >&2
  echo "The run must already exist; this script only requests a local dry-run plan." >&2
  exit 2
fi

BASE_URL="${EOS_BACKEND_URL:-http://localhost:8050}"
curl -sS -X POST "${BASE_URL}/api/v1/stage3-autonomy/runs/$1/dry-run" \
  -H "Content-Type: application/json" \
  -d '{"requested_by_role":"DEMO_PRESENTER"}'
echo
