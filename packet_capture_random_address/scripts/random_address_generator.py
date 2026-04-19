#!/usr/bin/env python3
"""CLI for random address generation."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.random_address_generator import generate_address_record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate random address records.")
    parser.add_argument("--count", type=int, default=10, help="Number of records to generate.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for _ in range(args.count):
        record = generate_address_record()
        print(json.dumps(record.to_dict(), ensure_ascii=True))


if __name__ == "__main__":
    main()
