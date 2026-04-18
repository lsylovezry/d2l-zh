"""UDP packet capture helpers."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class CaptureStats:
    """Runtime statistics for captured UDP packets."""

    packets: int = 0
    bytes_received: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0
    first_packet_at: Optional[float] = None
    last_packet_at: Optional[float] = None

    @property
    def elapsed(self) -> float:
        if self.finished_at <= self.started_at:
            return 0.0
        return self.finished_at - self.started_at

    @property
    def packets_per_second(self) -> float:
        if self.elapsed == 0.0:
            return 0.0
        return self.packets / self.elapsed

    @property
    def active_elapsed(self) -> float:
        if self.first_packet_at is None or self.last_packet_at is None:
            return 0.0
        if self.last_packet_at < self.first_packet_at:
            return 0.0
        return self.last_packet_at - self.first_packet_at

    @property
    def active_packets_per_second(self) -> float:
        if self.active_elapsed == 0.0:
            return float(self.packets) if self.packets else 0.0
        return self.packets / self.active_elapsed


class UdpPacketCapture:
    """Capture UDP packets for a given host/port."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9999,
        *,
        buffer_size: int = 65535,
        timeout: float = 0.2,
    ) -> None:
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.timeout = timeout
        self._sock: Optional[socket.socket] = None

    def start(self) -> None:
        if self._sock is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.settimeout(self.timeout)
        self._sock = sock

    def stop(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def run(
        self,
        *,
        duration_seconds: Optional[int] = None,
        report_interval: float = 1.0,
        quiet: bool = False,
    ) -> CaptureStats:
        """Run capture loop and return capture statistics."""

        self.start()
        assert self._sock is not None

        stats = CaptureStats(started_at=time.perf_counter())
        next_report = stats.started_at + report_interval
        stop_at: Optional[float] = None
        if duration_seconds is not None and duration_seconds > 0:
            stop_at = stats.started_at + duration_seconds

        try:
            while True:
                now = time.perf_counter()
                if stop_at is not None and now >= stop_at:
                    break
                try:
                    payload, _ = self._sock.recvfrom(self.buffer_size)
                except TimeoutError:
                    payload = None

                if payload is not None:
                    packet_time = time.perf_counter()
                    if stats.first_packet_at is None:
                        stats.first_packet_at = packet_time
                    stats.last_packet_at = packet_time
                    stats.packets += 1
                    stats.bytes_received += len(payload)

                if now >= next_report:
                    if not quiet:
                        elapsed = now - stats.started_at
                        rate = 0.0 if elapsed <= 0 else stats.packets / elapsed
                        print(
                            f"[capture] elapsed={elapsed:.2f}s packets={stats.packets} "
                            f"bytes={stats.bytes_received} avg_rate={rate:.2f}/s"
                        )
                    next_report = now + report_interval
        finally:
            stats.finished_at = time.perf_counter()
            self.stop()

        return stats
