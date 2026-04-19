"""Packet capture helper using Linux AF_PACKET raw sockets."""

from __future__ import annotations

import select
import socket
import time
from dataclasses import dataclass
from typing import List


@dataclass
class PacketSample:
    """A light packet sample for logging."""

    timestamp: float
    size: int
    source: str


class PacketSniffer:
    """Simple packet sniffer that captures packet metadata."""

    def __init__(self, interface: str = "any") -> None:
        self.interface = interface

    def _create_socket(self) -> socket.socket:
        raw_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        if self.interface != "any":
            raw_sock.bind((self.interface, 0))
        raw_sock.setblocking(False)
        return raw_sock

    def capture_samples(self, duration: float, sample_size: int = 5) -> List[PacketSample]:
        """Capture packet metadata for the given duration."""
        deadline = time.time() + duration
        samples: List[PacketSample] = []

        with self._create_socket() as raw_sock:
            while time.time() < deadline and len(samples) < sample_size:
                timeout = max(0.0, deadline - time.time())
                readable, _, _ = select.select([raw_sock], [], [], timeout)
                if not readable:
                    continue
                data, addr = raw_sock.recvfrom(65535)
                source = str(addr[0]) if addr else "unknown"
                samples.append(PacketSample(timestamp=time.time(), size=len(data), source=source))

        return samples
