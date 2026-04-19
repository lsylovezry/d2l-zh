#!/usr/bin/env python3
"""Standalone packet capture script."""

from __future__ import annotations

import argparse
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from packet_sniffer import PacketSniffer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture packet samples from a network interface.")
    parser.add_argument("--interface", type=str, default="any", help="Network interface (example: eth0).")
    parser.add_argument("--duration", type=float, default=1.0, help="Capture time in seconds.")
    parser.add_argument("--sample-size", type=int, default=20, help="Max samples to print.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.duration <= 0 or args.sample_size <= 0:
        print("duration and sample-size must be > 0", file=sys.stderr)
        return 2

    print(f"[INFO] Capturing on interface={args.interface} for {args.duration:.2f}s")
    try:
        sniffer = PacketSniffer(interface=args.interface)
        samples = sniffer.capture_samples(duration=args.duration, sample_size=args.sample_size)
    except PermissionError:
        print("[ERROR] Packet capture requires root or CAP_NET_RAW.")
        return 1
    except OSError as exc:
        print(f"[ERROR] Packet capture failed: {exc}")
        return 1

    if not samples:
        print("[RESULT] No packets captured.")
        return 0

    print(f"[RESULT] Captured {len(samples)} packet samples:")
    for sample in samples:
        print(f"  - ts={sample.timestamp:.3f} size={sample.size} src={sample.source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
