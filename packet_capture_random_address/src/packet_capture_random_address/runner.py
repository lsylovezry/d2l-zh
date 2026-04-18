"""Rate-controlled runner for packet capture + random address generation."""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass

from .packet_capture import PacketSniffer
from .random_address import RandomAddressGenerator


@dataclass
class RunStats:
    iterations: int
    elapsed_sec: float

    @property
    def throughput(self) -> float:
        return 0.0 if self.elapsed_sec <= 0 else self.iterations / self.elapsed_sec


class RateController:
    """Simple token-bucket style pacer."""

    def __init__(self, rate_per_sec: int) -> None:
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be positive")
        self.rate = rate_per_sec
        self.interval = 1.0 / rate_per_sec

    def next_tick(self, start_t: float, n: int) -> float:
        target = start_t + n * self.interval
        now = time.perf_counter()
        if target > now:
            time.sleep(target - now)
            return target
        return now


def run_loop(
    rate_per_sec: int = 100_000,
    duration_sec: float = 3.0,
    iface: str = "any",
    dry_run: bool = False,
) -> RunStats:
    """Run workload at requested rate for a fixed duration.

    Each iteration performs:
    1) generate a random address payload
    2) capture one packet metadata event (optional in dry_run)
    """

    generator = RandomAddressGenerator(secure=False)
    pacer = RateController(rate_per_sec)

    start = time.perf_counter()
    deadline = start + duration_sec
    iterations = 0

    if dry_run:
        while time.perf_counter() < deadline:
            _ = generator.generate()
            iterations += 1
            pacer.next_tick(start, iterations)
    else:
        with PacketSniffer(iface=iface, timeout=0.001) as sniffer:
            while time.perf_counter() < deadline:
                _ = generator.generate()
                _ = sniffer.capture_once()
                iterations += 1
                pacer.next_tick(start, iterations)

    elapsed = time.perf_counter() - start
    return RunStats(iterations=iterations, elapsed_sec=elapsed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Packet capture + random address runner")
    parser.add_argument("--rate", type=int, default=100_000, help="Target iterations per second")
    parser.add_argument("--duration", type=float, default=3.0, help="Run duration in seconds")
    parser.add_argument("--iface", type=str, default="any", help="Network interface (Linux)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip packet capture for benchmarking generator+rate control only",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    stats = run_loop(
        rate_per_sec=args.rate,
        duration_sec=args.duration,
        iface=args.iface,
        dry_run=args.dry_run,
    )
    print(
        f"iterations={stats.iterations} elapsed={stats.elapsed_sec:.4f}s "
        f"throughput={stats.throughput:.1f}/s"
    )


if __name__ == "__main__":
    main()
