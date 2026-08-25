#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/demo-stack-lib.sh"

profile="SOFT_RESET"
confirmation=""
reason="Presenter reset the local EOS demo."
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) profile="${2:?--profile requires a value}"; shift 2 ;;
    --confirmation) confirmation="${2:?--confirmation requires a value}"; shift 2 ;;
    --reason) reason="${2:?--reason requires a value}"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

backend_url="${EOS_BACKEND_URL:-http://localhost:8050}"
payload="$(jq -cn --arg profile "$profile" --arg reason "$reason" --arg confirmation "$confirmation" '{profile:$profile,reset_reason:$reason} + (if $confirmation == "" then {} else {confirmation:$confirmation} end)' 2>/dev/null || true)"
if [[ -z "$payload" ]]; then
  payload="{\"profile\":\"${profile}\",\"reset_reason\":\"${reason}\"}"
fi
curl -fsS -X POST "${backend_url}/api/v1/demo-readiness/reset" -H "Content-Type: application/json" -d "$payload" \
  | if command -v jq >/dev/null 2>&1; then jq .; else cat; fi
