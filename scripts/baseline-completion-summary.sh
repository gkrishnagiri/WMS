#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${EOS_BACKEND_URL:-http://localhost:8050}"
curl -sS "${BASE_URL}/api/v1/baseline-completion/summary"
printf '\n'
