#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8766}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared is required. Install it with: brew install cloudflared" >&2
  exit 1
fi

"$PROJECT_ROOT/scripts/run_public_dashboard.sh" --port "$PORT" &
dashboard_pid=$!

cleanup() {
  kill "$dashboard_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cloudflared tunnel --url "http://127.0.0.1:$PORT" --no-autoupdate
