"""CLI entrypoint for packet sniffing and random address generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .random_address import RandomAddressGenerator
from .rate_runner import run_with_target_rate
from .sniffer import PacketSniffer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run packet sniffer and random address generator at fixed rate."
    )
    parser.add_argument(
        "--per-second",
        type=int,
        default=100000,
        help="Operations per second for random address generation (default: 100000).",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Run duration in seconds for generator benchmark (default: 5).",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=10000,
        help="Print one sample address every N operations (default: 10000).",
    )
    parser.add_argument(
        "--iface",
        type=str,
        default=None,
        help="Network interface for packet capture. If omitted, OS default is used.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="outputs/packets.log",
        help="Packet log file path relative to project root (default: outputs/packets.log).",
    )
    parser.add_argument(
        "--disable-sniffer",
        action="store_true",
        help="Disable packet sniffing and run only random address generation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    log_file = (project_root / args.log_file).resolve()
    log_file.parent.mkdir(parents=True, exist_ok=True)

    generator = RandomAddressGenerator()
    counter = 0

    sniffer: PacketSniffer | None = None
    if not args.disable_sniffer:
        sniffer = PacketSniffer(
            output_file=log_file,
            interface=args.iface,
        )
        sniffer.start()

    def task() -> None:
        nonlocal counter
        address = generator.generate_ipv4()
        counter += 1
        if counter % args.log_every == 0:
            print(f"[generator] op={counter} sample={address}")
        if sniffer is not None:
            sniffer.poll_once()

    result = run_with_target_rate(
        task=task,
        target_rate=args.per_second,
        duration_seconds=args.duration,
    )
    print(result.summary())

    if sniffer:
        sniffer.stop()
        print(f"[sniffer] captured={sniffer.captured_packets} log={log_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
