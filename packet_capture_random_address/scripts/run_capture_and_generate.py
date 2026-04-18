#!/usr/bin/env python3
"""Run packet capture and high-frequency random generation together."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start packet sniffer and random generator runner together."
    )
    parser.add_argument("--interface", default="any", help="Sniffer network interface.")
    parser.add_argument(
        "--capture-output",
        default="outputs/packets.jsonl",
        help="JSONL output file for packet capture.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Capture duration in seconds.",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=100000,
        help="Generator calls per second.",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=5,
        help="How long to run the generator.",
    )
    parser.add_argument(
        "--type",
        choices=["mixed", "ipv4", "ipv6", "mac", "url"],
        default="mixed",
        help="Address generation type.",
    )
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    project_root = Path(__file__).resolve().parents[1]

    sniffer_cmd = [
        "sudo",
        "python3",
        str(project_root / "src" / "packet_sniffer.py"),
        "--interface",
        args.interface,
        "--duration",
        str(args.duration),
        "--output",
        str(project_root / args.capture_output),
    ]
    generator_cmd = [
        "python3",
        str(project_root / "scripts" / "run_100k_per_second.py"),
        "--rate",
        str(args.rate),
        "--seconds",
        str(args.seconds),
        "--type",
        args.type,
    ]

    sniffer = subprocess.Popen(sniffer_cmd, cwd=str(project_root))
    try:
        result = subprocess.run(generator_cmd, cwd=str(project_root), check=True)
        if result.returncode != 0:
            raise RuntimeError("Generator command failed.")
    finally:
        sniffer.wait(timeout=max(int(args.duration) + 5, 10))

    print("Capture and generation completed.")


if __name__ == "__main__":
    sys.exit(main())
