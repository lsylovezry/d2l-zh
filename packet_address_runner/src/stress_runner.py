#!/usr/bin/env python3
"""Run generator task at a target operations-per-second rate."""

from __future__ import annotations

import argparse
import time
from collections import Counter

from random_address_generator import GENERATORS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run random address generation at high frequency.")
    parser.add_argument(
        "--rate",
        type=int,
        default=100_000,
        help="Target operations per second.",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=5,
        help="How many one-second rounds to run.",
    )
    parser.add_argument(
        "--type",
        choices=sorted(GENERATORS.keys()),
        default="ipv4",
        help="Address type to generate.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generator = GENERATORS[args.type]
    total_done = 0
    global_counts = Counter()

    for second in range(1, args.seconds + 1):
        round_start = time.perf_counter()
        round_counts = Counter()

        for _ in range(args.rate):
            value = generator()
            # Keep side effects minimal while ensuring generation is not optimized away.
            round_counts[value[-1]] += 1

        elapsed = time.perf_counter() - round_start
        achieved = args.rate / elapsed if elapsed > 0 else 0.0
        total_done += args.rate
        global_counts.update(round_counts)
        print(
            f"round={second} type={args.type} target_ops={args.rate} elapsed={elapsed:.6f}s "
            f"achieved_ops_per_sec={achieved:.2f}"
        )

        if elapsed < 1.0 and second < args.seconds:
            time.sleep(1.0 - elapsed)

    print(f"total_generated={total_done}")
    print(f"checksum_buckets={dict(global_counts)}")


if __name__ == "__main__":
    main()
