#!/usr/bin/env python3
"""Simple packet sniffer for Linux."""

from __future__ import annotations

import argparse
import ipaddress
import socket
import struct
import time
from dataclasses import dataclass
from typing import Optional


ETH_P_ALL = 0x0003
ETH_HEADER_LEN = 14
ETH_P_IP = 0x0800


@dataclass
class PacketSummary:
    timestamp: float
    length: int
    src_mac: str
    dst_mac: str
    ether_type: int
    src_ip: Optional[str]
    dst_ip: Optional[str]


def format_mac(mac_bytes: bytes) -> str:
    return ":".join(f"{item:02x}" for item in mac_bytes)


def parse_packet(packet: bytes) -> Optional[PacketSummary]:
    if len(packet) < ETH_HEADER_LEN:
        return None

    dst_mac, src_mac, proto = struct.unpack("!6s6sH", packet[:ETH_HEADER_LEN])
    src_ip = None
    dst_ip = None

    if proto == ETH_P_IP and len(packet) >= ETH_HEADER_LEN + 20:
        ip_header = packet[ETH_HEADER_LEN : ETH_HEADER_LEN + 20]
        src_ip = str(ipaddress.IPv4Address(ip_header[12:16]))
        dst_ip = str(ipaddress.IPv4Address(ip_header[16:20]))

    return PacketSummary(
        timestamp=time.time(),
        length=len(packet),
        src_mac=format_mac(src_mac),
        dst_mac=format_mac(dst_mac),
        ether_type=proto,
        src_ip=src_ip,
        dst_ip=dst_ip,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture packets from a network interface.")
    parser.add_argument(
        "--interface",
        default="any",
        help="Interface name, e.g. eth0. Use 'any' to listen on all interfaces.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Capture duration in seconds.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Max packets to capture.",
    )
    return parser.parse_args()


def open_socket(interface: str) -> socket.socket:
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
    if interface != "any":
        sock.bind((interface, 0))
    sock.settimeout(1.0)
    return sock


def main() -> None:
    args = parse_args()
    try:
        sock = open_socket(args.interface)
    except PermissionError:
        print("Permission denied: run with sudo/root privileges.")
        return

    deadline = time.time() + args.duration
    captured = 0
    print(
        f"Start capture interface={args.interface} duration={args.duration}s max_count={args.count}"
    )
    try:
        while captured < args.count and time.time() < deadline:
            try:
                packet, _ = sock.recvfrom(65535)
            except socket.timeout:
                continue

            info = parse_packet(packet)
            if info is None:
                continue

            captured += 1
            print(
                f"[{captured:04d}] ts={info.timestamp:.6f} len={info.length} "
                f"mac={info.src_mac}->{info.dst_mac} eth=0x{info.ether_type:04x} "
                f"ip={info.src_ip or '-'}->{info.dst_ip or '-'}"
            )
    finally:
        sock.close()
        print(f"Capture finished, total packets={captured}")


if __name__ == "__main__":
    main()
