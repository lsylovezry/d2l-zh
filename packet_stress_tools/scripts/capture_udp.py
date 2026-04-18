#!/usr/bin/env python3
"""Run UDP packet capture."""

from __future__ import annotations

import argparse
import pathlib
import sys


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from packet_stress_tools import UdpPacketCapture  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UDP packet capture program.")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=9999, help="UDP port to bind (default: 9999).")
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=10,
        help="Capture duration in seconds; <=0 means run until interrupted.",
    )
    parser.add_argument(
        "--report-interval",
        type=float,
        default=1.0,
        help="Progress report interval in seconds.",
    )
    parser.add_argument("--quiet", action="store_true", help="Disable per-interval logs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    capture = UdpPacketCapture(host=args.host, port=args.port)

    duration = args.duration_seconds if args.duration_seconds > 0 else None
    print(
        f"[capture] start host={args.host} port={args.port} duration={args.duration_seconds}s"
    )
    stats = capture.run(
        duration_seconds=duration,
        report_interval=args.report_interval,
        quiet=args.quiet,
    )
    print(
        f"[capture] done packets={stats.packets} bytes={stats.bytes_received} "
        f"elapsed={stats.elapsed:.3f}s avg_rate={stats.packets_per_second:.2f}/s "
        f"active_rate={stats.active_packets_per_second:.2f}/s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
