#!/usr/bin/env python3
"""Capture packets and save as JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from packet_capture_random_address.capture import PacketSniffer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple Linux packet sniffer")
    parser.add_argument("--interface", default="lo", help="network interface, e.g. lo/eth0")
    parser.add_argument("--count", type=int, default=200, help="packet count to capture")
    parser.add_argument("--timeout", type=float, default=10.0, help="capture timeout seconds")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/packets.jsonl"),
        help="jsonl output path",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sniffer = PacketSniffer(interface=args.interface)
    stats = sniffer.capture(
        output_path=args.output,
        packet_count=args.count,
        timeout_seconds=args.timeout,
    )
    print(json.dumps(stats, ensure_ascii=True, indent=2))
    print(f"Saved packet records to: {args.output}")


if __name__ == "__main__":
    main()

