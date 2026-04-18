"""Run random address generation at a target throughput.

This script drives address generation calls and reports achieved QPS.
"""

from __future__ import annotations

import argparse
import time

from network_traffic_tools.address_generator import RandomAddressGenerator


def run_benchmark(target_qps: int, seconds: int, mode: str) -> None:
    gen = RandomAddressGenerator()
    fn_map = {
        "private_ipv4": gen.random_private_ipv4,
        "public_ipv4": gen.random_public_ipv4,
        "mac": gen.random_mac,
    }
    generate = fn_map[mode]

    total_calls = target_qps * seconds
    started = time.perf_counter()

    for _ in range(total_calls):
        generate()

    elapsed = time.perf_counter() - started
    actual_qps = total_calls / elapsed if elapsed > 0 else 0.0

    print(f"target_qps={target_qps}")
    print(f"duration_s={seconds}")
    print(f"mode={mode}")
    print(f"total_calls={total_calls}")
    print(f"elapsed_s={elapsed:.4f}")
    print(f"actual_qps={actual_qps:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Address generation throughput benchmark")
    parser.add_argument("--target-qps", type=int, default=100000)
    parser.add_argument("--seconds", type=int, default=1)
    parser.add_argument(
        "--mode",
        choices=["private_ipv4", "public_ipv4", "mac"],
        default="private_ipv4",
    )
    args = parser.parse_args()

    run_benchmark(target_qps=args.target_qps, seconds=args.seconds, mode=args.mode)


if __name__ == "__main__":
    main()
