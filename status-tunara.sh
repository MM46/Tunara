#!/usr/bin/env bash

set -u

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$PROJECT_ROOT/scripts/tunara-common.sh"

check_url() {
  local name="$1"
  local url="$2"
  local port="$3"

  if curl -fsS "$url" >/dev/null 2>&1; then
    printf '[UP]   %-15s port %s\n' "$name" "$port"
  else
    printf '[DOWN] %-15s port %s\n' "$name" "$port"
  fi
}

printf 'TUNARA status\n\n'
check_url "Ollama" "http://localhost:11434/api/tags" 11434
check_url "Tunara Audio" "http://localhost:8001/health" 8001
check_url "Tunara AI" "http://localhost:8000/health" 8000
check_url "Tunara API" "http://localhost:8080/actuator/health" 8080
check_url "Tunara UI" "http://localhost:3000/dashboard" 3000

printf '\nPostgreSQL\n'
(
  cd "$PROJECT_ROOT/tunara-api"
  docker compose ps
)
