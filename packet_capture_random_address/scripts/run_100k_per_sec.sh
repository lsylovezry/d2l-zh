#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 "$PROJECT_ROOT/src/random_address_generator.py" \
  --kind ipv4 \
  --rate 100000 \
  --duration 10 \
  --batch-size 5000 \
  --output "$PROJECT_ROOT/outputs/random_ipv4_100k.txt"
