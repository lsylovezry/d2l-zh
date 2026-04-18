#!/usr/bin/env python3
"""CLI random address generator."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from packet_stress_tools.random_address import iter_random_ipv4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate random IPv4 addresses."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of addresses to generate (default: 10).",
    )
    parser.add_argument(
        "--loopback-only",
        action="store_true",
        help="Generate only 127.x.x.x addresses.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for addr in iter_random_ipv4(max(0, args.count), loopback_only=args.loopback_only):
        print(addr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
