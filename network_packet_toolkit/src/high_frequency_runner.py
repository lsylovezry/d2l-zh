"""High-frequency executor for packet sniffing and random address generation."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import os
import time

from packet_sniffer import PacketSniffer
from random_address_generator import RandomAddressGenerator


@dataclass
class RunnerStats:
    """Stores throughput and per-second accounting."""

    requested_ops_per_second: int
    elapsed_seconds: float
    total_operations: int
    packet_capture_operations: int
    address_generation_operations: int

    @property
    def achieved_ops_per_second(self) -> float:
        if self.elapsed_seconds == 0:
            return 0.0
        return self.total_operations / self.elapsed_seconds


def _run_single_operation(sniffer: PacketSniffer, generator: RandomAddressGenerator) -> tuple[str, str]:
    packet = sniffer.poll_one()
    endpoint = generator.random_endpoint(public_ip=False)
    packet_info = packet.source_mac if packet else "no-packet"
    endpoint_info = f"{endpoint.ip}:{endpoint.port}"
    return packet_info, endpoint_info


def run_high_frequency_loop(
    target_ops_per_second: int = 100_000,
    duration_seconds: int = 1,
    interface: str | None = None,
) -> RunnerStats:
    """Run combined operations at approximately target_ops_per_second."""
    if target_ops_per_second <= 0:
        raise ValueError("target_ops_per_second must be positive.")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive.")

    generator = RandomAddressGenerator()
    sniffer = PacketSniffer(interface=interface)
    total_ops = target_ops_per_second * duration_seconds

    started = time.perf_counter()
    packet_ops = 0
    address_ops = 0
    with sniffer:
        for _ in range(total_ops):
            _run_single_operation(sniffer=sniffer, generator=generator)
            packet_ops += 1
            address_ops += 1
    elapsed = time.perf_counter() - started

    return RunnerStats(
        requested_ops_per_second=target_ops_per_second,
        elapsed_seconds=elapsed,
        total_operations=total_ops,
        packet_capture_operations=packet_ops,
        address_generation_operations=address_ops,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run packet capture + random address generation at high frequency."
    )
    parser.add_argument("--ops-per-second", type=int, default=100_000)
    parser.add_argument("--duration-seconds", type=int, default=1)
    parser.add_argument("--interface", default=None, help="Optional interface name, such as eth0.")
    args = parser.parse_args()

    if os.geteuid() != 0:
        raise SystemExit("Raw socket capture requires root privileges. Run with sudo.")

    stats = run_high_frequency_loop(
        target_ops_per_second=args.ops_per_second,
        duration_seconds=args.duration_seconds,
        interface=args.interface,
    )

    print("High-frequency run complete:")
    print(f"  requested ops/s: {stats.requested_ops_per_second}")
    print(f"  elapsed seconds : {stats.elapsed_seconds:.4f}")
    print(f"  total operations: {stats.total_operations}")
    print(f"  achieved ops/s  : {stats.achieved_ops_per_second:.2f}")
    print(f"  packet ops      : {stats.packet_capture_operations}")
    print(f"  address ops     : {stats.address_generation_operations}")


if __name__ == "__main__":
    main()
