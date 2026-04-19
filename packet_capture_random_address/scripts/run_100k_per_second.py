#!/usr/bin/env python3
"""Run random address generation at a target per-second rate and capture packets."""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections import deque

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from packet_sniffer import PacketSniffer
from random_address_generator import RandomAddressGenerator


def run_generator_for_n_seconds(rate: int, seconds: int, public_only: bool) -> tuple[int, list[str]]:
    """Run generator with a per-second target rate."""
    generator = RandomAddressGenerator(public_only=public_only)
    total_generated = 0
    recent = deque(maxlen=5)

    for _ in range(seconds):
        second_start = time.perf_counter()
        for _ in range(rate):
            recent.append(generator.generate_ipv4())
        total_generated += rate
        elapsed = time.perf_counter() - second_start
        sleep_left = 1.0 - elapsed
        if sleep_left > 0:
            time.sleep(sleep_left)

    return total_generated, list(recent)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture packets and generate random addresses at high frequency.")
    parser.add_argument("--rate", type=int, default=100000, help="Target generation count per second.")
    parser.add_argument("--seconds", type=int, default=3, help="How long to run.")
    parser.add_argument("--interface", type=str, default="any", help="Network interface for packet capture.")
    parser.add_argument("--public-only", action="store_true", help="Only generate public IPv4 addresses.")
    parser.add_argument("--sample-size", type=int, default=5, help="Number of packet samples to print.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate <= 0 or args.seconds <= 0:
        print("rate and seconds must be > 0", file=sys.stderr)
        return 2

    print(f"[INFO] Running random address generation at {args.rate}/s for {args.seconds}s")
    started_at = time.time()
    total_generated, recent_addresses = run_generator_for_n_seconds(args.rate, args.seconds, args.public_only)
    total_elapsed = time.time() - started_at
    actual_rate = total_generated / total_elapsed if total_elapsed > 0 else 0.0

    print(f"[RESULT] Generated {total_generated} addresses in {total_elapsed:.3f}s ({actual_rate:.0f}/s)")
    print(f"[RESULT] Recent addresses: {recent_addresses}")

    print(f"[INFO] Capturing packet samples on interface={args.interface}")
    try:
        sniffer = PacketSniffer(interface=args.interface)
        samples = sniffer.capture_samples(duration=1.0, sample_size=args.sample_size)
    except PermissionError:
        print("[WARN] Packet capture needs root or CAP_NET_RAW, skipped.")
        return 0
    except OSError as exc:
        print(f"[WARN] Packet capture failed: {exc}")
        return 0

    if not samples:
        print("[RESULT] No packets captured in sample window.")
        return 0

    print("[RESULT] Packet samples:")
    for sample in samples:
        print(f"  - ts={sample.timestamp:.3f} size={sample.size} src={sample.source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
