#!/usr/bin/env bash

set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/.pids"

mkdir -p "$LOG_DIR" "$PID_DIR"

is_port_open() {
  local port="$1"
  lsof -tiTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

wait_for_url() {
  local name="$1"
  local url="$2"
  local attempts="${3:-60}"
  local count=0

  while [ "$count" -lt "$attempts" ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      printf '[OK] %s\n' "$name"
      return 0
    fi
    sleep 1
    count=$((count + 1))
  done

  printf '[ERROR] %s did not become ready. Check logs.\n' "$name"
  return 1
}

start_background() {
  local name="$1"
  local pid_file="$2"
  local log_file="$3"
  shift 3

  nohup "$@" >"$log_file" 2>&1 &
  local pid=$!
  printf '%s\n' "$pid" >"$pid_file"
  printf '[STARTED] %s (PID %s)\n' "$name" "$pid"
}

stop_pid_file() {
  local name="$1"
  local pid_file="$2"

  if [ ! -f "$pid_file" ]; then
    printf '[SKIP] %s has no PID file.\n' "$name"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"

  if kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    local count=0
    while kill -0 "$pid" >/dev/null 2>&1 && [ "$count" -lt 10 ]; do
      sleep 1
      count=$((count + 1))
    done
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    printf '[STOPPED] %s\n' "$name"
  else
    printf '[SKIP] %s is not running.\n' "$name"
  fi

  rm -f "$pid_file"
}
