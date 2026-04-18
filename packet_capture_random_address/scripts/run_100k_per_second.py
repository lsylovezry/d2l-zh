#!/usr/bin/env python3
"""Run random address generation at a target rate."""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.random_address_generator import generate_random_address


def run(rate: int, seconds: int, address_type: str) -> tuple[int, float]:
    """Run generator at approximately `rate` calls per second."""
    total_count = 0
    start = time.perf_counter()

    for _ in range(seconds):
        second_start = time.perf_counter()
        for _ in range(rate):
            generate_random_address(address_type)
        total_count += rate

        elapsed = time.perf_counter() - second_start
        sleep_time = 1.0 - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    total_elapsed = time.perf_counter() - start
    return total_count, total_elapsed


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run random address generation at fixed QPS.")
    parser.add_argument(
        "--rate",
        type=int,
        default=100000,
        help="Number of generations per second.",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=1,
        help="How many seconds to run.",
    )
    parser.add_argument(
        "--type",
        choices=["mixed", "ipv4", "ipv6", "mac", "url"],
        default="mixed",
        help="Address generation type.",
    )
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    if args.rate <= 0:
        raise ValueError("--rate must be > 0")
    if args.seconds <= 0:
        raise ValueError("--seconds must be > 0")

    total, elapsed = run(rate=args.rate, seconds=args.seconds, address_type=args.type)
    achieved = total / elapsed if elapsed else math.inf
    print(f"Generated: {total}")
    print(f"Elapsed: {elapsed:.4f}s")
    print(f"Achieved rate: {achieved:.2f}/s")


if __name__ == "__main__":
    main()
