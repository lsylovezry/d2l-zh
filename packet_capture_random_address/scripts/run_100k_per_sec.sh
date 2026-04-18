#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"

python3 -m packet_capture_random_address.runner \
  --rate 100000 \
  --duration "${1:-3}" \
  "${@:2}"
