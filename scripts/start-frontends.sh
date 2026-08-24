#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/demo-stack-lib.sh"
mkdir_runtime

start_frontend() {
  local code="$1" port="$2" script="$3"
  local url="http://localhost:${port}" pid_file="${RUNTIME_DIR}/frontend-${code}.pid" log_file="${LOG_DIR}/${code}-frontend.log"
  if http_is_success "${url}"; then
    printf '%s frontend already responding on %s (unmanaged or previously started)\n' "${code}" "${port}"
    return 0
  fi
  if [[ -f "${pid_file}" ]] && record_is_current "${pid_file}"; then
    printf '%s frontend PID is active but URL is not ready; see %s\n' "${code}" "${log_file}" >&2
    return 1
  fi
  rm -f -- "${pid_file}"
  if http_is_up "${url}"; then
    printf '%s frontend port %s is occupied by a non-EOS service; skipped\n' "${code}" "${port}" >&2
    return 1
  fi
  printf 'Starting %s frontend on %s\n' "${code}" "${port}"
  launch_owned_process "${PROJECT_ROOT}/frontend" "./${script}" "${log_file}" "${pid_file}"
  if wait_for_url "${url}"; then
    printf '%s frontend ready: %s\n' "${code}" "${url}"
    return 0
  fi
  printf '%s frontend failed readiness; see %s\n' "${code}" "${log_file}" >&2
  return 1
}

failures=0
start_frontend full 4001 start_full_frontend.sh || failures=$((failures + 1))
start_frontend business 4011 start_business_frontend.sh || failures=$((failures + 1))
start_frontend operations 4012 start_operations_frontend.sh || failures=$((failures + 1))
start_frontend simulation 4013 start_simulation_frontend.sh || failures=$((failures + 1))
start_frontend observability 4014 start_observability_frontend.sh || failures=$((failures + 1))
start_frontend agentic 4015 start_agentic_frontend.sh || failures=$((failures + 1))

(( failures == 0 ))
