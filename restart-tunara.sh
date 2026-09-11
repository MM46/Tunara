#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

"$PROJECT_ROOT/stop-tunara.sh"
sleep 2
"$PROJECT_ROOT/start-tunara.sh"
