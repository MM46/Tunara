#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$PROJECT_ROOT/scripts/tunara-common.sh"
printf 'Starting TUNARA services...\n\n'
if ! docker info >/dev/null 2>&1; then printf '[ERROR] Docker or OrbStack is not running.\n'; exit 1; fi
printf '[1/7] PostgreSQL\n'
(cd "$PROJECT_ROOT/tunara-api" && docker compose up -d)
printf '\n[2/7] Ollama\n'
if is_port_open 11434; then printf '[OK] Ollama is already listening on port 11434.\n'; else
  OLLAMA_BIN="$(command -v ollama || true)"
  [ -n "$OLLAMA_BIN" ] || OLLAMA_BIN=/opt/homebrew/bin/ollama
  [ -x "$OLLAMA_BIN" ] || { printf '[ERROR] Ollama was not found.\n'; exit 1; }
  start_background "Ollama" "$PID_DIR/ollama.pid" "$LOG_DIR/ollama.log" "$OLLAMA_BIN" serve
fi
wait_for_url "Ollama" "http://localhost:11434/api/tags" 30
printf '\n[3/7] Tunara Audio\n'
if is_port_open 8001; then printf '[OK] Tunara Audio is already listening on port 8001.\n'; else
  AUDIO_PYTHON="$PROJECT_ROOT/tunara-ai/.venv-audio/bin/python"
  [ -x "$AUDIO_PYTHON" ] || { printf '[ERROR] Audio environment not found.\n'; exit 1; }
  start_background "Tunara Audio" "$PID_DIR/audio.pid" "$LOG_DIR/audio.log" "$AUDIO_PYTHON" -m uvicorn app.main:app --app-dir "$PROJECT_ROOT/tunara-audio" --host 0.0.0.0 --port 8001
fi
wait_for_url "Tunara Audio" "http://localhost:8001/health" 30
printf '\n[4/7] ACE-Step\n'
"$PROJECT_ROOT/scripts/start-ace-step.sh"
printf '\n[5/7] Tunara AI\n'
if is_port_open 8000; then printf '[OK] Tunara AI is already listening on port 8000.\n'; else
  docker rm -f tunara-ai-service >/dev/null 2>&1 || true
  docker run -d --name tunara-ai-service -p 8000:8000 \
    -e ACESTEP_BASE_URL=http://host.docker.internal:8010 \
    -e ACESTEP_TIMEOUT_SECONDS=1800 \
    -e TUNARA_AUDIO_BASE_URL=http://host.docker.internal:8001 \
    -e ACESTEP_PUBLIC_BASE_URL=http://localhost:8010 \
    tunara-ai >"$PID_DIR/ai-container.id"
  printf '[STARTED] Tunara AI container\n'
fi
wait_for_url "Tunara AI" "http://localhost:8000/health" 30
printf '\n[6/7] Tunara API\n'
if is_port_open 8080; then printf '[OK] Tunara API is already listening on port 8080.\n'; else
  start_background "Tunara API" "$PID_DIR/api.pid" "$LOG_DIR/api.log" "$PROJECT_ROOT/tunara-api/mvnw" -f "$PROJECT_ROOT/tunara-api/pom.xml" spring-boot:run
fi
wait_for_url "Tunara API" "http://localhost:8080/actuator/health" 90
printf '\n[7/7] Tunara UI\n'
if is_port_open 3000; then printf '[OK] Tunara UI is already listening on port 3000.\n'; else
  NPM_BIN="$(command -v npm || true)"; [ -n "$NPM_BIN" ] || { printf '[ERROR] npm was not found.\n'; exit 1; }
  start_background "Tunara UI" "$PID_DIR/ui.pid" "$LOG_DIR/ui.log" "$NPM_BIN" --prefix "$PROJECT_ROOT/tunara-ui" run dev
fi
wait_for_url "Tunara UI" "http://localhost:3000/dashboard" 60
printf '\nTUNARA is ready:\n  UI:       http://localhost:3000/dashboard\n  API:      http://localhost:8080/actuator/health\n  AI:       http://localhost:8000/health\n  Audio:    http://localhost:8001/health\n  ACE-Step: http://localhost:8010/health\n\nLogs: %s\n' "$LOG_DIR"
