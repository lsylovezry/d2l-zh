"""Simple packet sniffer based on Linux raw sockets."""

from __future__ import annotations

import select
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PacketSummary:
    """Lightweight representation of one captured packet."""

    timestamp: float
    source: Optional[str]
    destination: Optional[str]
    protocol: Optional[int]
    length: int

    def to_line(self) -> str:
        return (
            f"{self.timestamp:.6f} "
            f"src={self.source or '-'} "
            f"dst={self.destination or '-'} "
            f"proto={self.protocol if self.protocol is not None else '-'} "
            f"len={self.length}"
        )


class PacketSniffer:
    """Capture packets in a non-blocking poll loop."""

    def __init__(
        self,
        output_file: Path,
        interface: str | None = None,
        timeout: float = 0.01,
    ) -> None:
        self.output_file = output_file
        self.interface = interface
        self.timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._log_handle = None
        self.captured_packets = 0
        self.enabled = False

    def start(self) -> None:
        """Initialize raw socket sniffer."""
        try:
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            if self.interface:
                sock.bind((self.interface, 0))
            sock.setblocking(False)
            self._socket = sock
            self._log_handle = self.output_file.open("a", encoding="utf-8")
            self.enabled = True
            print(f"[sniffer] started iface={self.interface or 'default'}")
        except PermissionError:
            self.enabled = False
            print("[sniffer] no permission for raw socket, running without capture")

    def stop(self) -> None:
        """Stop capture and release resources."""
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        if self._log_handle is not None:
            self._log_handle.close()
            self._log_handle = None

    def poll_once(self) -> None:
        """Capture at most one packet in a non-blocking way."""
        if not self.enabled or self._socket is None:
            return

        ready, _, _ = select.select([self._socket], [], [], self.timeout)
        if not ready:
            return

        packet, _ = self._socket.recvfrom(65535)
        summary = self._summarize_packet(packet)
        self.captured_packets += 1
        if self._log_handle is not None:
            self._log_handle.write(summary.to_line() + "\n")

    @staticmethod
    def _summarize_packet(packet: bytes) -> PacketSummary:
        source = None
        destination = None
        protocol = None
        if len(packet) >= 34:
            ip_header = packet[14:34]
            protocol = ip_header[9]
            source = ".".join(str(b) for b in ip_header[12:16])
            destination = ".".join(str(b) for b in ip_header[16:20])

        return PacketSummary(
            timestamp=time.time(),
            source=source,
            destination=destination,
            protocol=protocol,
            length=len(packet),
        )
