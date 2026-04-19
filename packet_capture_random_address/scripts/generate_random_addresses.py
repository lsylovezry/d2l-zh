#!/usr/bin/env python3
"""Generate random IPv4 addresses at a target rate."""

from __future__ import annotations

import argparse
import os
import sys
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from random_address_generator import RandomAddressGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate random IPv4 addresses at high frequency.")
    parser.add_argument("--rate", type=int, default=100000, help="Target generation count per second.")
    parser.add_argument("--seconds", type=int, default=1, help="How long to run.")
    parser.add_argument("--public-only", action="store_true", help="Only generate public IPv4 addresses.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate <= 0 or args.seconds <= 0:
        print("rate and seconds must be > 0", file=sys.stderr)
        return 2

    generator = RandomAddressGenerator(public_only=args.public_only)
    total = 0
    recent = []
    started_at = time.perf_counter()

    for _ in range(args.seconds):
        second_started = time.perf_counter()
        for _ in range(args.rate):
            addr = generator.generate_ipv4()
            if len(recent) < 5:
                recent.append(addr)
            else:
                recent.pop(0)
                recent.append(addr)
        total += args.rate

        elapsed_this_second = time.perf_counter() - second_started
        sleep_left = 1.0 - elapsed_this_second
        if sleep_left > 0:
            time.sleep(sleep_left)

    elapsed_total = time.perf_counter() - started_at
    actual_rate = total / elapsed_total if elapsed_total > 0 else 0.0
    print(f"generated={total} elapsed={elapsed_total:.3f}s actual_rate={actual_rate:.0f}/s")
    print(f"recent={recent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
