#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

case "${1:-}" in
  ''|--with-infra) ;;
  *) printf 'Usage: %s [--with-infra]\n' "$0" >&2; exit 2 ;;
esac

"${SCRIPT_DIR}/stop-frontends.sh"
"${SCRIPT_DIR}/stop-backends.sh"

if [[ "${1:-}" == "--with-infra" ]]; then
  "${SCRIPT_DIR}/stop-infra.sh"
else
  printf 'Application processes stopped; Docker infrastructure left running.\n'
fi
