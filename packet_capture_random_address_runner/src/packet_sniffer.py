"""Minimal Linux packet sniffer based on raw sockets."""

from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class CapturedPacket:
    timestamp: float
    interface: str
    src_mac: str
    dst_mac: str
    eth_type: int
    payload_size: int


def _mac_to_str(raw: bytes) -> str:
    return ":".join(f"{item:02x}" for item in raw)


class PacketSniffer:
    """Capture packets on a Linux interface using AF_PACKET."""

    def __init__(self, interface: str = "eth0", timeout_s: float = 0.001):
        self.interface = interface
        self.timeout_s = timeout_s
        self.socket: Optional[socket.socket] = None
        self.total_captured = 0

    def __enter__(self) -> "PacketSniffer":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()

    def start(self) -> None:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        sock.bind((self.interface, 0))
        sock.settimeout(self.timeout_s)
        self.socket = sock

    def stop(self) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def capture_once(self) -> Optional[CapturedPacket]:
        if self.socket is None:
            raise RuntimeError("Sniffer not started. Call start() first.")
        try:
            packet, addr = self.socket.recvfrom(65535)
        except socket.timeout:
            return None
        except BlockingIOError:
            return None

        if len(packet) < 14:
            return None

        dst_mac, src_mac, eth_type = struct.unpack("!6s6sH", packet[:14])
        self.total_captured += 1
        return CapturedPacket(
            timestamp=time.time(),
            interface=addr[0],
            src_mac=_mac_to_str(src_mac),
            dst_mac=_mac_to_str(dst_mac),
            eth_type=eth_type,
            payload_size=max(0, len(packet) - 14),
        )

    def get_packet(self, timeout: Optional[float] = None) -> Optional[dict[str, object]]:
        """Capture one packet and return JSON-serializable data."""
        if self.socket is None:
            raise RuntimeError("Sniffer not started. Call start() first.")

        old_timeout = self.socket.gettimeout()
        if timeout is not None:
            self.socket.settimeout(timeout)
        try:
            pkt = self.capture_once()
        finally:
            if timeout is not None:
                self.socket.settimeout(old_timeout)

        if pkt is None:
            return None

        return {
            "timestamp": pkt.timestamp,
            "interface": pkt.interface,
            "src_mac": pkt.src_mac,
            "dst_mac": pkt.dst_mac,
            "eth_type": pkt.eth_type,
            "payload_size": pkt.payload_size,
        }
