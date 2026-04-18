#!/usr/bin/env python3
"""Run packet capture and random-address generation together."""

from __future__ import annotations

import argparse
import threading
from pathlib import Path

from packet_capture import PacketSniffer
from random_address_generator import GenerationStats, RandomAddressGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run packet capture and random address generation in one command"
    )
    parser.add_argument("--rate", type=int, default=100000, help="Addresses generated per second.")
    parser.add_argument("--duration", type=int, default=5, help="Generation duration in seconds.")
    parser.add_argument(
        "--address-type",
        choices=["ipv4", "ipv6", "mac"],
        default="ipv4",
        help="Type of random address generated each iteration.",
    )
    parser.add_argument(
        "--sample-output",
        action="store_true",
        help="Print a small address sample for each second.",
    )
    parser.add_argument(
        "--capture-interface",
        default=None,
        help="Network interface for packet capture (example: eth0).",
    )
    parser.add_argument(
        "--capture-packet-limit",
        type=int,
        default=200,
        help="Maximum packets to capture.",
    )
    parser.add_argument(
        "--capture-timeout",
        type=int,
        default=10,
        help="Packet capture timeout in seconds.",
    )
    parser.add_argument(
        "--capture-output",
        default="outputs/captured_packets.log",
        help="Capture log output path.",
    )
    parser.add_argument(
        "--skip-capture",
        action="store_true",
        help="Skip packet capture and run generator only.",
    )
    args = parser.parse_args()

    generator = RandomAddressGenerator()
    generation_result: list[GenerationStats] = []
    generation_exception: list[BaseException] = []

    def run_generator() -> None:
        try:
            stats = generator.run_at_rate(
                target_per_second=args.rate,
                duration_seconds=args.duration,
                address_type=args.address_type,
                sample_output=args.sample_output,
            )
            generation_result.append(stats)
        except BaseException as exc:  # pragma: no cover - defensive capture
            generation_exception.append(exc)

    capture_messages: list[str] = []
    capture_exception: list[BaseException] = []

    def run_capture() -> None:
        output_path = Path(args.capture_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sniffer = PacketSniffer(interface=args.capture_interface)
        try:
            with output_path.open("a", encoding="utf-8") as output:
                captured = sniffer.capture(
                    packet_limit=args.capture_packet_limit,
                    timeout_seconds=args.capture_timeout,
                    output=output,
                    print_stdout=False,
                )
            capture_messages.append(
                f"Capture finished, packets captured: {captured}, log: {output_path}"
            )
        except PermissionError:
            capture_messages.append(
                "Packet capture skipped: raw sockets require root privileges (CAP_NET_RAW)."
            )
        except BaseException as exc:  # pragma: no cover - defensive capture
            capture_exception.append(exc)

    generator_thread = threading.Thread(target=run_generator, name="generator-thread")
    generator_thread.start()

    capture_thread = None
    if not args.skip_capture:
        capture_thread = threading.Thread(target=run_capture, name="capture-thread")
        capture_thread.start()

    generator_thread.join()
    if capture_thread:
        capture_thread.join()

    if generation_exception:
        raise generation_exception[0]
    if capture_exception:
        raise capture_exception[0]

    stats = generation_result[0]
    print(
        f"Generator finished: total={stats.total_generated}, "
        f"elapsed={stats.elapsed_seconds:.2f}s, rate={stats.rate:.2f}/s"
    )
    for message in capture_messages:
        print(message)


if __name__ == "__main__":
    main()
