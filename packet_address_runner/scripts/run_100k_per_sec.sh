#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RATE="${RATE:-100000}"
SECONDS="${SECONDS:-5}"
ADDRESS_TYPE="${ADDRESS_TYPE:-ipv4}"

python3 "${PROJECT_ROOT}/src/stress_runner.py" \
  --rate "${RATE}" \
  --seconds "${SECONDS}" \
  --type "${ADDRESS_TYPE}"
