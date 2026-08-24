#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export VITE_EOS_EXPERIENCE=agentic
export VITE_API_BASE_URL=http://localhost:8065
export FRONTEND_PORT="${FRONTEND_PORT:-4015}"
exec ./start_frontend.sh
