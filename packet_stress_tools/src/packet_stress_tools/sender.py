"""High-rate UDP sender helpers."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Optional

from .random_address import generate_random_ipv4, generate_random_loopback_ipv4


@dataclass
class SendStats:
    """Runtime statistics for sent UDP packets."""

    packets_sent: int = 0
    bytes_sent: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0

    @property
    def elapsed(self) -> float:
        if self.finished_at <= self.started_at:
            return 0.0
        return self.finished_at - self.started_at

    @property
    def packets_per_second(self) -> float:
        if self.elapsed == 0.0:
            return 0.0
        return self.packets_sent / self.elapsed


class UdpRateSender:
    """Send UDP packets at a target packets-per-second rate."""

    def __init__(
        self,
        *,
        target_host: str = "127.0.0.1",
        target_port: int = 9999,
        packet_size: int = 128,
        randomize_destination: bool = False,
        destination_loopback_only: bool = True,
    ) -> None:
        self.target_host = target_host
        self.target_port = target_port
        self.packet_size = max(1, packet_size)
        self.randomize_destination = randomize_destination
        self.destination_loopback_only = destination_loopback_only

    def _make_target(self) -> tuple[str, int]:
        if not self.randomize_destination:
            return self.target_host, self.target_port
        if self.destination_loopback_only:
            return generate_random_loopback_ipv4(), self.target_port
        return generate_random_ipv4(), self.target_port

    def run(
        self,
        *,
        pps: int = 100_000,
        duration_seconds: int = 1,
        report_interval: float = 1.0,
        quiet: bool = False,
    ) -> SendStats:
        """Run sender loop.

        Notes:
        - ``pps`` is a best-effort target because the Python runtime and OS scheduler
          introduce jitter at high rates.
        - If ``duration_seconds`` <= 0, the sender exits immediately.
        """

        stats = SendStats(started_at=time.perf_counter())
        if duration_seconds <= 0:
            stats.finished_at = time.perf_counter()
            return stats

        interval = 1.0 / max(1, pps)
        payload = b"x" * self.packet_size
        deadline = stats.started_at + duration_seconds
        next_report = stats.started_at + report_interval
        next_send = stats.started_at

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while True:
                now = time.perf_counter()
                if now >= deadline:
                    break

                if now < next_send:
                    sleep_for = next_send - now
                    if sleep_for > 0:
                        time.sleep(sleep_for)
                    continue

                target = self._make_target()
                try:
                    sent = sock.sendto(payload, target)
                except OSError:
                    # Ignore transient send failures to keep loop resilient.
                    sent = 0

                stats.packets_sent += 1
                stats.bytes_sent += sent
                next_send += interval

                if now >= next_report:
                    if not quiet:
                        elapsed = now - stats.started_at
                        rate = 0.0 if elapsed <= 0 else stats.packets_sent / elapsed
                        print(
                            f"[sender] elapsed={elapsed:.2f}s sent={stats.packets_sent} "
                            f"bytes={stats.bytes_sent} avg_rate={rate:.2f}/s"
                        )
                    next_report = now + report_interval

        stats.finished_at = time.perf_counter()
        return stats
