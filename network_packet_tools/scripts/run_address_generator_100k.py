#!/usr/bin/env python3
"""Run random address generation at a fixed operations-per-second target."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from random_address_generator import RandomAddressGenerator  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run random address generation at target rate per second."
    )
    parser.add_argument(
        "--mode",
        default="ipv4",
        choices=["ipv4", "ipv6", "mac", "socket", "url"],
        help="Type of address to generate.",
    )
    parser.add_argument(
        "--target-per-sec",
        type=int,
        default=100000,
        help="Target generation count per second.",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=10,
        help="How many seconds to run. Use 0 for endless mode.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    return parser


def run(target_per_sec: int, seconds: int, mode: str, seed: int | None) -> None:
    if target_per_sec <= 0:
        raise ValueError("target-per-sec must be > 0")

    generator = RandomAddressGenerator(seed=seed)
    total = 0
    tick = 0
    started = time.perf_counter()

    while True:
        tick += 1
        tick_start = time.perf_counter()

        for _ in range(target_per_sec):
            generator.generate(mode)

        total += target_per_sec
        elapsed_tick = time.perf_counter() - tick_start
        if elapsed_tick < 1.0:
            time.sleep(1.0 - elapsed_tick)
            status = "on-target"
        else:
            status = "overloaded"

        print(
            f"sec={tick:<4} generated={target_per_sec:<8} "
            f"elapsed={elapsed_tick:.4f}s status={status}"
        )

        if seconds > 0 and tick >= seconds:
            break

    elapsed_all = time.perf_counter() - started
    actual_rate = total / elapsed_all if elapsed_all > 0 else 0
    print(
        f"finished total={total} elapsed={elapsed_all:.2f}s "
        f"avg_rate={actual_rate:.2f}/sec"
    )


def main() -> None:
    args = build_parser().parse_args()
    run(
        target_per_sec=args.target_per_sec,
        seconds=args.seconds,
        mode=args.mode,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
