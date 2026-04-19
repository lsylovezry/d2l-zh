#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-generator}"
DURATION="${2:-3}"
INTERFACE="${3:-}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

CMD=(
  "$PYTHON_BIN"
  "$PROJECT_ROOT/src/high_frequency_runner.py"
  "--iterations-per-second" "100000"
  "--duration-seconds" "$DURATION"
  "--mode" "$MODE"
  "--report-every-second"
)

if [[ -n "$INTERFACE" ]]; then
  CMD+=("--interface" "$INTERFACE")
fi

if [[ "$MODE" == "sniffer" || "$MODE" == "both" ]]; then
  if [[ "${EUID}" -ne 0 ]]; then
    echo "Sniffer mode requires root. Re-run with sudo."
    exit 1
  fi
fi

"${CMD[@]}"
