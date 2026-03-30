#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_INSTALL_ROOT="$HOME/uav-usv-experiment-platform-runtime"

if [[ -d "$SCRIPT_ROOT/catkin_ws" || -d "$SCRIPT_ROOT/PX4_Firmware" ]]; then
  DEFAULT_INSTALL_ROOT="$SCRIPT_ROOT"
fi

INSTALL_ROOT="${1:-${INSTALL_ROOT:-$DEFAULT_INSTALL_ROOT}}"

exec "$SCRIPT_DIR/run_sim.sh" "$INSTALL_ROOT"
