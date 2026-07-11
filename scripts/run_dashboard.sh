#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT/dashboard"

if [[ ! -d node_modules ]]; then
  npm ci
fi

exec python3 server.py "$@"
