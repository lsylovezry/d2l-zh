#!/usr/bin/env python3
"""CLI entrypoint for packet sniffer + random address generator."""

from __future__ import annotations

import argparse
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.high_rate_runner import HighRateRunner  # noqa: E402
from src.packet_sniffer import PacketSniffer  # noqa: E402
from src.random_address_generator import RandomAddressGenerator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run packet sniffer and random-address generator at high frequency."
    )
    parser.add_argument(
        "--mode",
        choices=("generate-only", "sniff-and-generate"),
        default="generate-only",
        help="Run generation only, or generation with packet sniffing.",
    )
    parser.add_argument(
        "--interface",
        type=str,
        default="lo",
        help="Network interface to sniff (default: lo).",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=3,
        help="How long to run, in seconds.",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=100000,
        help="Target generation count per second.",
    )
    parser.add_argument(
        "--sample-packets",
        type=int,
        default=5,
        help="How many packets to sample in sniff mode.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generator = RandomAddressGenerator()
    runner = HighRateRunner(generator=generator, target_per_second=args.rate)

    if args.mode == "generate-only":
        result = runner.run_for_duration(seconds=args.duration)
        report = {
            "mode": args.mode,
            "target_per_second": args.rate,
            "duration_seconds": args.duration,
            "generated_total": result.generated_total,
            "actual_per_second": result.actual_per_second,
            "sample_output": result.sample_output,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    packets = []
    with PacketSniffer(interface=args.interface) as sniffer:
        result = runner.run_for_duration(seconds=args.duration)
        packets = sniffer.read_packets(max_packets=args.sample_packets)

    report = {
        "mode": args.mode,
        "interface": args.interface,
        "target_per_second": args.rate,
        "duration_seconds": args.duration,
        "generated_total": result.generated_total,
        "actual_per_second": result.actual_per_second,
        "sample_output": result.sample_output,
        "captured_packets": [packet.__dict__ for packet in packets],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
