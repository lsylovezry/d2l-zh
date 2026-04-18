#!/usr/bin/env python3
"""Run packet capture and random-address generation together."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from packet_capture_random_address.addresses import RandomAddressGenerator
from packet_capture_random_address.capture import PacketSniffer
from packet_capture_random_address.rate import run_at_rate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture packets while generating random addresses at high rate"
    )
    parser.add_argument("--rate", type=int, default=100000, help="operations per second")
    parser.add_argument("--duration", type=float, default=1.0, help="generation duration in seconds")
    parser.add_argument("--interface", default="lo", help="capture interface, default loopback")
    parser.add_argument(
        "--addresses-output",
        type=Path,
        default=Path("outputs/generated_addresses.jsonl"),
        help="address output jsonl",
    )
    parser.add_argument(
        "--packets-output",
        type=Path,
        default=Path("outputs/packets.jsonl"),
        help="packet capture output jsonl",
    )
    parser.add_argument(
        "--capture-count",
        type=int,
        default=5000,
        help="max packets to capture during run",
    )
    parser.add_argument(
        "--capture-timeout",
        type=float,
        default=5.0,
        help="capture timeout seconds",
    )
    parser.add_argument(
        "--loopback-only",
        action="store_true",
        help="generate only loopback endpoints to keep traffic local",
    )
    parser.add_argument(
        "--send-udp",
        action="store_true",
        help="send a UDP byte to each generated endpoint",
    )
    parser.add_argument("--seed", type=int, default=None, help="optional random seed")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.addresses_output.parent.mkdir(parents=True, exist_ok=True)
    args.packets_output.parent.mkdir(parents=True, exist_ok=True)

    sniffer_stats: dict[str, float | int] = {}

    def capture_job() -> None:
        nonlocal sniffer_stats
        sniffer = PacketSniffer(interface=args.interface)
        sniffer_stats = sniffer.capture(
            output_path=args.packets_output,
            packet_count=args.capture_count,
            timeout_seconds=args.capture_timeout,
        )

    capture_thread = threading.Thread(target=capture_job, daemon=True)
    capture_thread.start()

    generator = RandomAddressGenerator(seed=args.seed)
    udp_sock: socket.socket | None = None
    if args.send_udp:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with args.addresses_output.open("w", encoding="utf-8") as fp:

        def operation() -> None:
            endpoint = generator.random_endpoint(loopback_only=args.loopback_only)
            fp.write(
                json.dumps(
                    {"ip": endpoint.ip, "port": endpoint.port, "uri": endpoint.as_udp_uri()},
                    ensure_ascii=True,
                )
                + "\n"
            )
            if udp_sock is not None:
                udp_sock.sendto(b"x", (endpoint.ip, endpoint.port))

        generator_stats = run_at_rate(
            operation=operation,
            target_per_second=args.rate,
            duration_seconds=args.duration,
        )
    if udp_sock is not None:
        udp_sock.close()

    capture_thread.join()

    print(
        json.dumps(
            {
                "generator": asdict(generator_stats),
                "sniffer": sniffer_stats,
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    print(f"Saved generated endpoints to: {args.addresses_output}")
    print(f"Saved packet records to: {args.packets_output}")


if __name__ == "__main__":
    main()
