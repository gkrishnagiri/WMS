#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"
mkdir_runtime

start_backend() {
  local code="$1" port="$2" script="$3"
  local url="http://localhost:${port}" pid_file="${RUNTIME_DIR}/backend-${code}.pid" log_file="${LOG_DIR}/${code}-backend.log"
  if backend_health_is_eos "${url}" "${code}"; then
    printf '%s backend already healthy on %s (unmanaged or previously started)\n' "${code}" "${port}"
    return 0
  fi
  if [[ -f "${pid_file}" ]] && record_is_current "${pid_file}"; then
    printf '%s backend PID is active but not healthy; see %s\n' "${code}" "${log_file}" >&2
    return 1
  fi
  rm -f -- "${pid_file}"
  if http_is_up "${url}/health"; then
    printf '%s backend port %s is occupied by a non-EOS service; skipped\n' "${code}" "${port}" >&2
    return 1
  fi
  printf 'Starting %s backend on %s\n' "${code}" "${port}"
  launch_owned_process "${PROJECT_ROOT}/backend" "./${script}" "${log_file}" "${pid_file}"
  if wait_for_backend "${url}" "${code}"; then
    printf '%s backend ready: %s\n' "${code}" "${url}"
    return 0
  fi
  printf '%s backend failed readiness; see %s\n' "${code}" "${log_file}" >&2
  return 1
}

failures=0
start_backend full 8050 start_full_backend.sh || failures=$((failures + 1))
start_backend business 8061 start_business_bff.sh || failures=$((failures + 1))
start_backend operations 8062 start_operations_bff.sh || failures=$((failures + 1))
start_backend simulation 8063 start_simulation_bff.sh || failures=$((failures + 1))
start_backend observability 8064 start_observability_bff.sh || failures=$((failures + 1))
start_backend agentic 8065 start_agentic_bff.sh || failures=$((failures + 1))

(( failures == 0 ))
