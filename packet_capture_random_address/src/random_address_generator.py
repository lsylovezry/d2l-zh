#!/usr/bin/env python3
"""High-throughput random address generator."""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path
from typing import Callable


def random_ipv4(rng: random.Random) -> str:
    value = rng.getrandbits(32)
    return ".".join(
        str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0)
    )


def random_mac(rng: random.Random) -> str:
    return ":".join(f"{rng.getrandbits(8):02x}" for _ in range(6))


def generate_batch(batch_size: int, generator: Callable[[random.Random], str], rng: random.Random) -> list[str]:
    return [generator(rng) for _ in range(batch_size)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate random network addresses with target throughput."
    )
    parser.add_argument(
        "--kind",
        choices=("ipv4", "mac"),
        default="ipv4",
        help="Address type to generate.",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=100000,
        help="Target generation rate per second.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Run duration in seconds.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output file path. Leave empty for no address output.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Number of addresses generated per batch.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducibility.",
    )
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    if args.rate <= 0:
        raise ValueError("--rate must be > 0")
    if args.duration <= 0:
        raise ValueError("--duration must be > 0")
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be > 0")

    rng = random.Random(args.seed)
    generator = random_ipv4 if args.kind == "ipv4" else random_mac

    output_handle = None
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_handle = output_path.open("w", encoding="utf-8")

    total_generated = 0
    start = time.perf_counter()
    end_time = start + args.duration

    try:
        while True:
            second_start = time.perf_counter()
            if second_start >= end_time:
                break

            remaining_seconds = end_time - second_start
            second_budget = min(1.0, remaining_seconds)
            target_for_window = int(args.rate * second_budget)
            generated_this_window = 0

            while generated_this_window < target_for_window:
                batch_size = min(args.batch_size, target_for_window - generated_this_window)
                batch = generate_batch(batch_size, generator, rng)
                if output_handle is not None:
                    output_handle.write("\n".join(batch))
                    output_handle.write("\n")
                generated_this_window += batch_size

            total_generated += generated_this_window

            elapsed_in_window = time.perf_counter() - second_start
            sleep_time = second_budget - elapsed_in_window
            if sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        if output_handle is not None:
            output_handle.close()

    elapsed_total = time.perf_counter() - start
    achieved_rate = total_generated / elapsed_total if elapsed_total else 0.0
    print(
        f"kind={args.kind} generated={total_generated} "
        f"elapsed={elapsed_total:.3f}s achieved_rate={achieved_rate:.2f}/s",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
