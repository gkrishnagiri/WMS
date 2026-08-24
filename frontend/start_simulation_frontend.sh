#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export VITE_EOS_EXPERIENCE=simulation
export VITE_API_BASE_URL=http://localhost:8063
export FRONTEND_PORT="${FRONTEND_PORT:-4013}"
exec ./start_frontend.sh
