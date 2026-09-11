#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$PROJECT_ROOT/scripts/tunara-common.sh"

printf 'Starting TUNARA services...\n\n'

if ! docker info >/dev/null 2>&1; then
  printf '[ERROR] Docker or OrbStack is not running.\n'
  exit 1
fi

printf '[1/6] PostgreSQL\n'
(
  cd "$PROJECT_ROOT/tunara-api"
  docker compose up -d
)

printf '\n[2/6] Ollama\n'
if is_port_open 11434; then
  printf '[OK] Ollama is already listening on port 11434.\n'
else
  OLLAMA_BIN="$(command -v ollama || true)"
  if [ -z "$OLLAMA_BIN" ] && [ -x /usr/local/bin/ollama ]; then
    OLLAMA_BIN=/usr/local/bin/ollama
  fi
  if [ -z "$OLLAMA_BIN" ] && [ -x /opt/homebrew/bin/ollama ]; then
    OLLAMA_BIN=/opt/homebrew/bin/ollama
  fi
  if [ -z "$OLLAMA_BIN" ]; then
    printf '[ERROR] Ollama was not found.\n'
    exit 1
  fi
  start_background \
    "Ollama" \
    "$PID_DIR/ollama.pid" \
    "$LOG_DIR/ollama.log" \
    "$OLLAMA_BIN" serve
fi
wait_for_url "Ollama" "http://localhost:11434/api/tags" 30

printf '\n[3/6] Tunara Audio\n'
if is_port_open 8001; then
  printf '[OK] Tunara Audio is already listening on port 8001.\n'
else
  AUDIO_PYTHON="$PROJECT_ROOT/tunara-ai/.venv-audio/bin/python"
  if [ ! -x "$AUDIO_PYTHON" ]; then
    printf '[ERROR] Audio environment not found at %s\n' "$AUDIO_PYTHON"
    exit 1
  fi
  start_background \
    "Tunara Audio" \
    "$PID_DIR/audio.pid" \
    "$LOG_DIR/audio.log" \
    "$AUDIO_PYTHON" -m uvicorn app.main:app \
      --app-dir "$PROJECT_ROOT/tunara-audio" \
      --host 0.0.0.0 \
      --port 8001
fi
wait_for_url "Tunara Audio" "http://localhost:8001/health" 30

printf '\n[4/6] Tunara AI\n'
if is_port_open 8000; then
  printf '[OK] Tunara AI is already listening on port 8000.\n'
else
  docker rm -f tunara-ai-service >/dev/null 2>&1 || true
  docker run -d \
    --name tunara-ai-service \
    -p 8000:8000 \
    tunara-ai >"$PID_DIR/ai-container.id"
  printf '[STARTED] Tunara AI container\n'
fi
wait_for_url "Tunara AI" "http://localhost:8000/health" 30

printf '\n[5/6] Tunara API\n'
if is_port_open 8080; then
  printf '[OK] Tunara API is already listening on port 8080.\n'
else
  start_background \
    "Tunara API" \
    "$PID_DIR/api.pid" \
    "$LOG_DIR/api.log" \
    "$PROJECT_ROOT/tunara-api/mvnw" \
      -f "$PROJECT_ROOT/tunara-api/pom.xml" \
      spring-boot:run
fi
wait_for_url "Tunara API" "http://localhost:8080/actuator/health" 90

printf '\n[6/6] Tunara UI\n'
if is_port_open 3000; then
  printf '[OK] Tunara UI is already listening on port 3000.\n'
else
  NPM_BIN="$(command -v npm || true)"
  if [ -z "$NPM_BIN" ]; then
    printf '[ERROR] npm was not found.\n'
    exit 1
  fi
  start_background \
    "Tunara UI" \
    "$PID_DIR/ui.pid" \
    "$LOG_DIR/ui.log" \
    "$NPM_BIN" --prefix "$PROJECT_ROOT/tunara-ui" run dev
fi
wait_for_url "Tunara UI" "http://localhost:3000/dashboard" 60

printf '\nTUNARA is ready:\n'
printf '  UI:    http://localhost:3000/dashboard\n'
printf '  API:   http://localhost:8080/actuator/health\n'
printf '  AI:    http://localhost:8000/health\n'
printf '  Audio: http://localhost:8001/health\n'
printf '\nLogs: %s\n' "$LOG_DIR"
