#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$PROJECT_ROOT/scripts/tunara-common.sh"

ACE_ROOT="${ACE_STEP_HOME:-$HOME/Tunara-local-models/ACE-Step-1.5}"
CHECKPOINTS="${ACE_STEP_MODELS_DIR:-$HOME/Tunara-local-models/checkpoints}"
ACE_PORT="${ACE_STEP_PORT:-8010}"
ACE_URL="http://127.0.0.1:$ACE_PORT"
ACE_PID_FILE="$PID_DIR/ace-step.pid"
ACE_LOG_FILE="$LOG_DIR/ace-step-api.log"
UV_BIN="/opt/homebrew/bin/uv"

if curl -fsS "$ACE_URL/health" >/dev/null 2>&1; then
  printf '[OK] ACE-Step is already listening on port %s.\n' "$ACE_PORT"
else
  if [ ! -d "$ACE_ROOT" ]; then
    printf '[ERROR] ACE-Step was not found at %s\n' "$ACE_ROOT"
    exit 1
  fi
  if [ ! -x "$UV_BIN" ]; then
    UV_BIN="$(command -v uv || true)"
  fi
  if [ -z "$UV_BIN" ]; then
    printf '[ERROR] uv was not found.\n'
    exit 1
  fi

  nohup env -u VIRTUAL_ENV \
    PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin" \
    ACESTEP_CHECKPOINTS_DIR="$CHECKPOINTS" \
    "$UV_BIN" --directory "$ACE_ROOT" run acestep-api \
      --host 0.0.0.0 \
      --port "$ACE_PORT" \
      </dev/null \
      >"$ACE_LOG_FILE" 2>&1 &
  echo $! >"$ACE_PID_FILE"
  printf '[STARTED] ACE-Step API (PID %s)\n' "$(cat "$ACE_PID_FILE")"
fi

wait_for_url "ACE-Step" "$ACE_URL/health" 60

HEALTH="$(curl -fsS "$ACE_URL/health")"
INITIALIZED="$(printf '%s' "$HEALTH" | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["data"]["models_initialized"]).lower())')"
LLM_INITIALIZED="$(printf '%s' "$HEALTH" | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["data"]["llm_initialized"]).lower())')"

if [ "$INITIALIZED" != "true" ] || [ "$LLM_INITIALIZED" != "true" ]; then
  printf '[INIT] Loading ACE-Step Turbo and 5Hz LM 1.7B...\n'
  curl -fsS --max-time 900 \
    -X POST "$ACE_URL/v1/init" \
    -H 'Content-Type: application/json' \
    -d '{"model":"acestep-v15-turbo","slot":1,"init_llm":true,"lm_model_path":"acestep-5Hz-lm-1.7B"}' \
    >/tmp/tunara-ace-step-init.json
  python3 -c 'import json; d=json.load(open("/tmp/tunara-ace-step-init.json")); assert d.get("code")==200, d; print("[OK] ACE-Step models initialized")'
fi

curl -fsS "$ACE_URL/health" | python3 -c 'import json,sys; d=json.load(sys.stdin)["data"]; assert d["models_initialized"] and d["llm_initialized"]; print("[OK] ACE-Step ready on port 8010")'
