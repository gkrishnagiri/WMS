#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export VITE_EOS_EXPERIENCE=full
export VITE_API_BASE_URL=http://localhost:8050
export FRONTEND_PORT="${FRONTEND_PORT:-4001}"
exec ./start_frontend.sh
