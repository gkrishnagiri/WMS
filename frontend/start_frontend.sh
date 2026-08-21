#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -d node_modules ]]; then
  npm install
fi

FRONTEND_PORT="${FRONTEND_PORT:-4001}"
echo "EOS frontend: http://localhost:${FRONTEND_PORT}"
exec npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"
