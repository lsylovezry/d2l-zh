#!/usr/bin/env python3
"""Run packet capture and random address generation at high frequency."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict

from packet_sniffer import PacketSniffer
from random_address_generator import RandomAddressGenerator


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="High-frequency task runner.")
    parser.add_argument(
        "--iterations-per-second",
        type=int,
        default=100000,
        help="Target loop count per second.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=3,
        help="How many seconds to run.",
    )
    parser.add_argument(
        "--mode",
        choices=("generator", "sniffer", "both"),
        default="both",
        help="Task mode for each iteration.",
    )
    parser.add_argument(
        "--interface",
        type=str,
        default=None,
        help="Network interface for packet capture mode, e.g. eth0.",
    )
    parser.add_argument(
        "--report-every-second",
        action="store_true",
        help="Print one summary line per second.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional deterministic seed for random generator.",
    )
    return parser


def _run_generator(generator: RandomAddressGenerator) -> None:
    generator.generate()


def _run_sniffer(sniffer: PacketSniffer) -> bool:
    return sniffer.capture_once() is not None


def run_high_frequency(
    iterations_per_second: int,
    duration_seconds: int,
    mode: str,
    interface: str | None,
    report_every_second: bool,
    seed: int | None,
) -> dict[str, float | int]:
    generator = RandomAddressGenerator(seed=seed)
    sniffer = None
    captured_packets = 0

    if mode in {"sniffer", "both"}:
        sniffer = PacketSniffer(interface=interface, timeout=0.0)

    started_at = time.perf_counter()
    seconds_completed = 0
    total_iterations = 0

    try:
        for second_index in range(duration_seconds):
            window_start = time.perf_counter()
            second_captured = 0

            for _ in range(iterations_per_second):
                if mode in {"generator", "both"}:
                    _run_generator(generator)
                if mode in {"sniffer", "both"} and sniffer is not None:
                    if _run_sniffer(sniffer):
                        captured_packets += 1
                        second_captured += 1
                total_iterations += 1

            elapsed = time.perf_counter() - window_start
            sleep_budget = 1.0 - elapsed
            if sleep_budget > 0:
                time.sleep(sleep_budget)

            seconds_completed = second_index + 1
            if report_every_second:
                print(
                    json.dumps(
                        {
                            "second": seconds_completed,
                            "target_iterations": iterations_per_second,
                            "elapsed_compute_seconds": round(elapsed, 6),
                            "captured_packets": second_captured,
                        },
                        ensure_ascii=True,
                    )
                )
    finally:
        if sniffer is not None:
            sniffer.close()

    total_elapsed = time.perf_counter() - started_at
    return {
        "iterations_per_second": iterations_per_second,
        "duration_seconds": duration_seconds,
        "seconds_completed": seconds_completed,
        "total_iterations": total_iterations,
        "captured_packets": captured_packets,
        "total_elapsed_seconds": total_elapsed,
        "achieved_iterations_per_second": total_iterations / total_elapsed if total_elapsed > 0 else 0.0,
    }


def main() -> None:
    args = _build_parser().parse_args()
    try:
        summary = run_high_frequency(
            iterations_per_second=args.iterations_per_second,
            duration_seconds=args.duration_seconds,
            mode=args.mode,
            interface=args.interface,
            report_every_second=args.report_every_second,
            seed=args.seed,
        )
    except PermissionError as exc:
        raise SystemExit("Sniffer mode requires root privileges on Linux.") from exc

    print(json.dumps(summary, ensure_ascii=True))


if __name__ == "__main__":
    main()
