#!/usr/bin/env python3
"""Run UDP sender at 100000 packets per second."""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from packet_stress_tools.sender import UdpRateSender


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run UDP sender at target 100000 packets per second."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Target host.")
    parser.add_argument("--port", type=int, default=9999, help="Target UDP port.")
    parser.add_argument(
        "--duration",
        type=int,
        default=1,
        help="How many seconds to run (default: 1).",
    )
    parser.add_argument(
        "--packet-size",
        type=int,
        default=128,
        help="Payload size in bytes (default: 128).",
    )
    parser.add_argument(
        "--pps",
        type=int,
        default=100_000,
        help="Target packets per second (default: 100000).",
    )
    parser.add_argument(
        "--random-destination",
        action="store_true",
        help="Randomize destination address on each send.",
    )
    parser.add_argument(
        "--allow-public-ip",
        action="store_true",
        help="When random destination is enabled, allow non-loopback random IPv4.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable periodic logs and print final summary only.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sender = UdpRateSender(
        target_host=args.host,
        target_port=args.port,
        packet_size=args.packet_size,
        randomize_destination=args.random_destination,
        destination_loopback_only=not args.allow_public_ip,
    )
    stats = sender.run(pps=args.pps, duration_seconds=args.duration, quiet=args.quiet)
    print(
        "[summary] sent_packets={sent} sent_bytes={bytes_} elapsed={elapsed:.4f}s "
        "avg_rate={rate:.2f}/s target={target}/s".format(
            sent=stats.packets_sent,
            bytes_=stats.bytes_sent,
            elapsed=stats.elapsed,
            rate=stats.packets_per_second,
            target=args.pps,
        )
    )


if __name__ == "__main__":
    main()
