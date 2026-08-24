#!/usr/bin/env bash

# Shared helpers for the PID-owned local EOS demo processes.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
RUNTIME_DIR="${EOS_DEMO_RUNTIME_DIR:-/tmp/eos-demo}"
LOG_DIR="${RUNTIME_DIR}/logs"

mkdir_runtime() {
  mkdir -p "${LOG_DIR}"
}

http_status() {
  local url="$1"
  local status
  status="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 2 "${url}" 2>/dev/null || true)"
  printf '%s\n' "${status:-000}"
}

http_body() {
  local url="$1"
  curl -sS --max-time 2 "${url}" 2>/dev/null || true
}

http_is_up() {
  local status
  status="$(http_status "$1")"
  [[ "${status}" != "000" ]]
}

http_is_success() {
  local status
  status="$(http_status "$1")"
  [[ "${status}" =~ ^2[0-9][0-9]$|^3[0-9][0-9]$ ]]
}

backend_health_is_eos() {
  local url="$1"
  local experience="${2:-full}"
  local body
  body="$(http_body "${url}/health")"
  grep -Eq '"application"[[:space:]]*:[[:space:]]*"Enterprise Operations Suite"' <<<"${body}" || return 1
  if [[ "${experience}" != "full" ]]; then
    grep -Eq '"experience"[[:space:]]*:[[:space:]]*"'"${experience}"'"' <<<"${body}" || return 1
  fi
}

wait_for_backend() {
  local url="$1"
  local experience="${2:-full}"
  local attempt
  for attempt in {1..30}; do
    if backend_health_is_eos "${url}" "${experience}"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

wait_for_url() {
  local url="$1"
  local attempt
  for attempt in {1..30}; do
    if http_is_success "${url}"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

process_start_ticks() {
  local pid="$1"
  [[ -r "/proc/${pid}/stat" ]] || return 1
  awk '{line=$0; sub(/^[0-9]+ \([^)]*\) /, "", line); split(line, fields, " "); print fields[20]}' "/proc/${pid}/stat"
}

write_pid_record() {
  local pid="$1"
  local file="$2"
  local ticks
  ticks="$(process_start_ticks "${pid}")"
  {
    printf '%s\n' "${pid}"
    printf '%s\n' "${ticks}"
  } >"${file}"
}

record_pid() {
  local file="$1"
  [[ -s "${file}" ]] || return 1
  sed -n '1p' "${file}"
}

record_is_current() {
  local file="$1"
  [[ -s "${file}" ]] || return 1
  local pid expected actual
  pid="$(sed -n '1p' "${file}")"
  expected="$(sed -n '2p' "${file}")"
  [[ "${pid}" =~ ^[0-9]+$ ]] || return 1
  kill -0 "${pid}" 2>/dev/null || return 1
  actual="$(process_start_ticks "${pid}" 2>/dev/null || true)"
  [[ -n "${actual}" && "${actual}" == "${expected}" ]]
}

process_args() {
  local pid="$1"
  ps -ww -p "${pid}" -o args= 2>/dev/null || true
}

process_group_alive() {
  local pid="$1"
  kill -0 -- "-${pid}" 2>/dev/null
}

record_matches() {
  local file="$1"
  local pattern="$2"
  record_is_current "${file}" || return 1
  grep -Fq -- "${pattern}" <<<"$(process_args "$(record_pid "${file}")")"
}

launch_owned_process() {
  local workdir="$1"
  local script="$2"
  local log_file="$3"
  local pid_file="$4"
  local pid
  # Start a new session so terminal/process-group cleanup cannot reap a
  # deliberately backgrounded demo process. The PID remains script-owned.
  nohup setsid bash -c 'cd "$1" && exec "$2"' _ "${workdir}" "${script}" >>"${log_file}" 2>&1 </dev/null &
  pid=$!
  write_pid_record "${pid}" "${pid_file}"
}

stop_owned_record() {
  local file="$1"
  local label="$2"
  local pattern="$3"
  [[ -f "${file}" ]] || { printf '%s: stopped (no PID file)\n' "${label}"; return 0; }
  if ! record_is_current "${file}"; then
    printf '%s: stale PID file removed\n' "${label}"
    rm -f -- "${file}"
    return 0
  fi
  if ! record_matches "${file}" "${pattern}"; then
    printf '%s: PID ownership mismatch; leaving process untouched\n' "${label}"
    rm -f -- "${file}"
    return 1
  fi
  local pid
  pid="$(record_pid "${file}")"
  kill -TERM "${pid}" 2>/dev/null || true
  # The launcher uses setsid, so the recorded PID is also the process-group
  # ID. This reaps children such as Vite/esbuild without touching other groups.
  kill -TERM -- "-${pid}" 2>/dev/null || true
  for _ in {1..10}; do
    if ! record_is_current "${file}" && ! process_group_alive "${pid}"; then
      rm -f -- "${file}"
      printf '%s: stopped\n' "${label}"
      return 0
    fi
    sleep 0.5
  done
  if record_matches "${file}" "${pattern}"; then
    kill -KILL "${pid}" 2>/dev/null || true
  fi
  if process_group_alive "${pid}"; then
    kill -KILL -- "-${pid}" 2>/dev/null || true
  fi
  rm -f -- "${file}"
  printf '%s: stopped\n' "${label}"
}

compose_service_health() {
  local service="$1"
  local container_id health
  container_id="$(docker compose ps -q "${service}")"
  [[ -n "${container_id}" ]] || return 1
  health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "${container_id}" 2>/dev/null || true)"
  [[ "${health}" == "healthy" || "${health}" == "no-healthcheck" ]]
}

wait_for_compose_health() {
  local service="$1"
  local attempt
  for attempt in {1..30}; do
    if compose_service_health "${service}"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

print_check() {
  local label="$1"
  local url="$2"
  local status
  status="$(http_status "${url}")"
  if [[ "${status}" =~ ^2[0-9][0-9]$|^3[0-9][0-9]$ ]]; then
    printf 'PASS %-32s HTTP %s %s\n' "${label}" "${status}" "${url}"
    return 0
  fi
  printf 'FAIL %-32s HTTP %s %s\n' "${label}" "${status}" "${url}"
  return 1
}
