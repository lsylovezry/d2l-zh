#!/usr/bin/env python3
"""CLI for packet capture."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import List

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.packet_capture import CapturedPacket, capture_packets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture packets using Linux raw sockets.")
    parser.add_argument("--interface", type=str, default="eth0")
    parser.add_argument("--max-packets", type=int, default=10)
    parser.add_argument(
        "--output",
        type=str,
        default=str(ROOT / "outputs" / "captured_packets.json"),
        help="Path for captured packet metadata.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records: List[dict] = []
    for packet in capture_packets(interface=args.interface, max_packets=args.max_packets):
        typed_packet: CapturedPacket = packet
        records.append(
            {
                "timestamp": typed_packet.timestamp,
                "packet_length": typed_packet.packet_length,
                "interface": typed_packet.interface,
                "eth_type": typed_packet.eth_type,
            }
        )

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
