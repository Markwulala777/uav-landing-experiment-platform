#!/usr/bin/env bash
set -euo pipefail

PORT="${MICROXRCE_PORT:-8888}"

if ! command -v MicroXRCEAgent >/dev/null 2>&1; then
  echo "MicroXRCEAgent was not found in PATH." >&2
  exit 1
fi

exec MicroXRCEAgent udp4 -p "$PORT"
