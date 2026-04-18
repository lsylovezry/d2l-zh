#!/usr/bin/env python3
"""Generate random addresses at a configured rate."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from packet_capture_random_address.addresses import RandomAddressGenerator
from packet_capture_random_address.rate import run_at_rate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Random address high-rate generator")
    parser.add_argument("--rate", type=int, default=100000, help="target operations per second")
    parser.add_argument("--duration", type=float, default=1.0, help="run duration in seconds")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/generated_addresses.jsonl"),
        help="jsonl output file path",
    )
    parser.add_argument(
        "--loopback-only",
        action="store_true",
        help="restrict generated addresses to loopback range 127.x.x.x",
    )
    parser.add_argument("--seed", type=int, default=None, help="optional random seed")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    generator = RandomAddressGenerator(seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as fp:
        def operation() -> None:
            endpoint = generator.random_endpoint(loopback_only=args.loopback_only)
            fp.write(
                json.dumps(
                    {"ip": endpoint.ip, "port": endpoint.port, "uri": endpoint.as_udp_uri()},
                    ensure_ascii=True,
                )
                + "\n"
            )

        stats = run_at_rate(
            operation=operation,
            target_per_second=args.rate,
            duration_seconds=args.duration,
        )

    print(json.dumps(asdict(stats), ensure_ascii=True, indent=2))
    print(f"Saved generated endpoints to: {args.output}")


if __name__ == "__main__":
    main()

