"""Minimal Linux packet capture utility using raw sockets."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class CapturedPacket:
    """Represents one captured packet metadata record."""

    timestamp: float
    packet_length: int
    interface: str
    eth_type: str


def _parse_eth_type(packet: bytes) -> str:
    """Extract Ethernet type field from frame."""
    if len(packet) < 14:
        return "unknown"
    eth_type = int.from_bytes(packet[12:14], "big")
    return f"0x{eth_type:04x}"


def capture_packets(interface: str, max_packets: Optional[int] = None) -> Iterator[CapturedPacket]:
    """Yield captured packets from a network interface.

    Note:
        Requires Linux and root privileges.
    """
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    sock.bind((interface, 0))
    count = 0

    try:
        while True:
            packet, _ = sock.recvfrom(65535)
            count += 1
            yield CapturedPacket(
                timestamp=time.time(),
                packet_length=len(packet),
                interface=interface,
                eth_type=_parse_eth_type(packet),
            )
            if max_packets is not None and count >= max_packets:
                return
    finally:
        sock.close()
