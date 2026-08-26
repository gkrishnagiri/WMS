#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${EOS_BACKEND_URL:-http://localhost:8050}"
echo "Stage 3 status"
curl -sS "${BASE_URL}/api/v1/stage3-autonomy/status"
echo
echo "Stage 3 profiles"
curl -sS "${BASE_URL}/api/v1/stage3-autonomy/profiles"
echo
echo "Stage 3 summary"
curl -sS "${BASE_URL}/api/v1/stage3-autonomy/summary"
echo
