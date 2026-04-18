"""Minimal packet sniffer for authorized network diagnostics.

Usage requires root/admin privileges on most systems.
"""

from __future__ import annotations

import argparse
import socket
import struct
import textwrap
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass
class PacketSummary:
    timestamp: str
    src_mac: str
    dst_mac: str
    eth_proto: int
    src_ip: str | None = None
    dst_ip: str | None = None
    l4_proto: int | None = None


def _format_mac(raw: bytes) -> str:
    return ":".join(f"{octet:02x}" for octet in raw)


def _parse_ethernet_frame(frame: bytes) -> tuple[str, str, int, bytes]:
    dst_mac, src_mac, proto = struct.unpack("!6s6sH", frame[:14])
    return _format_mac(src_mac), _format_mac(dst_mac), socket.ntohs(proto), frame[14:]


def _parse_ipv4_packet(payload: bytes) -> tuple[str, str, int] | None:
    if len(payload) < 20:
        return None
    version_ihl = payload[0]
    version = version_ihl >> 4
    if version != 4:
        return None
    ihl = (version_ihl & 0x0F) * 4
    if len(payload) < ihl:
        return None
    proto = payload[9]
    src = socket.inet_ntoa(payload[12:16])
    dst = socket.inet_ntoa(payload[16:20])
    return src, dst, proto


def capture_packets(interface: str | None, limit: int) -> Iterable[PacketSummary]:
    """Capture packets from local machine network interface.

    Linux AF_PACKET sockets are used here for low-level frame capture.
    """
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    if interface:
        sock.bind((interface, 0))

    captured = 0
    while captured < limit:
        frame, _ = sock.recvfrom(65535)
        src_mac, dst_mac, eth_proto, payload = _parse_ethernet_frame(frame)
        summary = PacketSummary(
            timestamp=datetime.now().isoformat(timespec="milliseconds"),
            src_mac=src_mac,
            dst_mac=dst_mac,
            eth_proto=eth_proto,
        )

        if eth_proto == 8:  # IPv4
            parsed_ipv4 = _parse_ipv4_packet(payload)
            if parsed_ipv4 is not None:
                summary.src_ip, summary.dst_ip, summary.l4_proto = parsed_ipv4

        yield summary
        captured += 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture and print packet summaries (authorized use only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              sudo python packet_sniffer.py --limit 20
              sudo python packet_sniffer.py --interface eth0 --limit 100
            """
        ),
    )
    parser.add_argument("--interface", default=None, help="Network interface, e.g. eth0")
    parser.add_argument("--limit", type=int, default=20, help="Number of packets to capture")
    args = parser.parse_args()

    for packet in capture_packets(interface=args.interface, limit=args.limit):
        print(
            f"[{packet.timestamp}] "
            f"MAC {packet.src_mac} -> {packet.dst_mac}, ETH={packet.eth_proto}, "
            f"IP {packet.src_ip or '-'} -> {packet.dst_ip or '-'}, L4={packet.l4_proto or '-'}"
        )


if __name__ == "__main__":
    main()
