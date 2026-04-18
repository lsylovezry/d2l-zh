#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

python3 "${PROJECT_ROOT}/src/high_frequency_runner.py" \
  --ops-per-second 100000 \
  --duration-seconds 1 \
  "$@"
