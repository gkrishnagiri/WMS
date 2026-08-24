#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

case "${1:-}" in
  '') docker compose down ;;
  --volumes) docker compose down --volumes ;;
  *) printf 'Usage: %s [--volumes]\n' "$0" >&2; exit 2 ;;
esac
