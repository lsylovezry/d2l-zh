#!/usr/bin/env python3
"""Run random address generation at 100000 iterations per second.

Optional mode enables parallel packet capture sampling.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import threading
import time
from typing import List

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.packet_capture import CapturedPacket, capture_packets
from src.random_address_generator import generate_address_record


def _capture_worker(interface: str, max_packets: int, sink: List[CapturedPacket]) -> None:
    """Collect packet metadata in background."""
    for packet in capture_packets(interface=interface, max_packets=max_packets):
        sink.append(packet)


def run_loop(iterations_per_second: int, seconds: int) -> int:
    """Run generation loop at fixed rate and return total iterations."""
    interval = 1.0 / iterations_per_second
    total = iterations_per_second * seconds
    next_tick = time.perf_counter()

    for _ in range(total):
        _ = generate_address_record()
        next_tick += interval
        sleep_for = next_tick - time.perf_counter()
        if sleep_for > 0:
            time.sleep(sleep_for)

    return total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run random generator 100000 times/sec.")
    parser.add_argument("--iterations-per-second", type=int, default=100000)
    parser.add_argument("--seconds", type=int, default=1)
    parser.add_argument("--enable-capture", action="store_true")
    parser.add_argument("--interface", type=str, default="eth0")
    parser.add_argument("--capture-max-packets", type=int, default=100)
    parser.add_argument(
        "--output",
        type=str,
        default=str(ROOT / "outputs" / "run_summary.json"),
        help="Path for JSON summary output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    captured_packets: List[CapturedPacket] = []
    capture_thread = None

    if args.enable_capture:
        capture_thread = threading.Thread(
            target=_capture_worker,
            args=(args.interface, args.capture_max_packets, captured_packets),
            daemon=True,
        )
        capture_thread.start()

    start = time.perf_counter()
    total_iterations = run_loop(args.iterations_per_second, args.seconds)
    elapsed = time.perf_counter() - start

    if capture_thread is not None:
        capture_thread.join(timeout=2)

    summary = {
        "iterations_per_second_target": args.iterations_per_second,
        "seconds": args.seconds,
        "total_iterations": total_iterations,
        "elapsed_seconds": elapsed,
        "achieved_iterations_per_second": total_iterations / elapsed if elapsed else 0,
        "capture_enabled": args.enable_capture,
        "captured_packets": [
            {
                "timestamp": packet.timestamp,
                "packet_length": packet.packet_length,
                "interface": packet.interface,
                "eth_type": packet.eth_type,
            }
            for packet in captured_packets
        ],
    }

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
