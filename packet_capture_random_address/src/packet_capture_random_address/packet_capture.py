"""Packet capture implementation based on raw sockets.

This module is Linux-oriented and requires root privileges (CAP_NET_RAW).
"""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Optional


@dataclass
class PacketEvent:
    """A lightweight packet metadata record."""

    src_mac: str
    dst_mac: str
    eth_proto: int
    payload_size: int


class PacketSniffer:
    """Capture Ethernet frames and parse basic metadata."""

    def __init__(self, iface: str = "any", timeout: float = 1.0) -> None:
        self.iface = iface
        self.timeout = timeout
        self._sock: Optional[socket.socket] = None

    def __enter__(self) -> "PacketSniffer":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.close()

    def open(self) -> None:
        if self._sock is not None:
            return
        # ETH_P_ALL == 0x0003, receive all Ethernet protocols.
        self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        if self.iface != "any":
            self._sock.bind((self.iface, 0))
        self._sock.settimeout(self.timeout)

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    @staticmethod
    def _mac_from(raw: bytes) -> str:
        return ":".join(f"{byte:02x}" for byte in raw)

    def capture_once(self) -> Optional[PacketEvent]:
        if self._sock is None:
            raise RuntimeError("PacketSniffer is not open")
        try:
            frame, _addr = self._sock.recvfrom(65535)
        except socket.timeout:
            return None

        if len(frame) < 14:
            return None

        dst_mac = self._mac_from(frame[0:6])
        src_mac = self._mac_from(frame[6:12])
        eth_proto = int.from_bytes(frame[12:14], "big")
        payload_size = len(frame) - 14

        return PacketEvent(
            src_mac=src_mac,
            dst_mac=dst_mac,
            eth_proto=eth_proto,
            payload_size=payload_size,
        )
