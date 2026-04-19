#!/usr/bin/env python3
"""
Run random address generation at high frequency.

Default target rate: 100000 calls per second.
"""

from __future__ import annotations

import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from random_address_generator import generate_random_address


def _worker(
    rate_per_thread: int,
    end_time: float,
    address_type: str,
    counter: list[int],
    idx: int,
    lock: Lock,
) -> None:
    local_count = 0
    while time.perf_counter() < end_time:
        tick_start = time.perf_counter()
        for _ in range(rate_per_thread):
            generate_random_address(address_type)
            local_count += 1
        with lock:
            counter[idx] = local_count
        elapsed = time.perf_counter() - tick_start
        sleep_time = max(0.0, 1.0 - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)
    counter[idx] = local_count


def run_high_frequency(rate: int, duration: int, address_type: str, workers: int) -> int:
    if rate <= 0:
        raise ValueError("rate must be > 0")
    if duration <= 0:
        raise ValueError("duration must be > 0")
    if workers <= 0:
        raise ValueError("workers must be > 0")

    rate_per_thread = rate // workers
    remainder = rate % workers

    end_time = time.perf_counter() + duration
    counts = [0 for _ in range(workers)]
    counts_lock = Lock()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        for i in range(workers):
            this_rate = rate_per_thread + (1 if i < remainder else 0)
            executor.submit(_worker, this_rate, end_time, address_type, counts, i, counts_lock)

        last = 0
        start = time.perf_counter()
        while time.perf_counter() < end_time:
            time.sleep(1)
            with counts_lock:
                total = sum(counts)
            current = total - last
            last = total
            print(f"[stats] generated in last second: {current}")

        with counts_lock:
            total = sum(counts)
        elapsed = time.perf_counter() - start
        achieved_rate = int(total / elapsed) if elapsed > 0 else 0
        print(f"[done] total={total}, elapsed={elapsed:.2f}s, achieved_rate={achieved_rate}/s")
        return total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run address generation at high rate.")
    parser.add_argument(
        "--rate",
        type=int,
        default=100000,
        help="Target calls per second (default: 100000).",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="How long to run in seconds (default: 5).",
    )
    parser.add_argument(
        "--type",
        choices=["ipv4", "ipv6", "mac"],
        default="ipv4",
        help="Address type to generate.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker threads (default: 4).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_high_frequency(rate=args.rate, duration=args.duration, address_type=args.type, workers=args.workers)


if __name__ == "__main__":
    main()
