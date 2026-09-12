#!/usr/bin/env bash
set -u
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$PROJECT_ROOT/scripts/tunara-common.sh"
printf 'Stopping TUNARA services...\n\n'
stop_pid_file "Tunara UI" "$PID_DIR/ui.pid"
stop_pid_file "Tunara API" "$PID_DIR/api.pid"
docker rm -f tunara-ai-service >/dev/null 2>&1 && printf '[STOPPED] Tunara AI\n' || printf '[SKIP] Tunara AI is not running.\n'
rm -f "$PID_DIR/ai-container.id"
stop_pid_file "ACE-Step" "$PID_DIR/ace-step.pid"
ACE_PIDS="$(lsof -tiTCP:8010 -sTCP:LISTEN 2>/dev/null || true)"
if [ -n "$ACE_PIDS" ]; then kill $ACE_PIDS 2>/dev/null || true; printf '[STOPPED] ACE-Step listener on 8010\n'; fi
stop_pid_file "Tunara Audio" "$PID_DIR/audio.pid"
stop_pid_file "Ollama" "$PID_DIR/ollama.pid"
if [ "${1:-}" = "--with-database" ]; then (cd "$PROJECT_ROOT/tunara-api" && docker compose down); printf '[STOPPED] PostgreSQL\n'; else printf '[KEEP] PostgreSQL remains running. Use --with-database to stop it.\n'; fi
printf '\nTUNARA stopped.\n'
