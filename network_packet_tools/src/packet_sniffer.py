#!/usr/bin/env python3
"""Minimal Linux packet sniffer.

This script captures packets through a raw AF_PACKET socket and prints a
human-readable summary for each packet.
"""

from __future__ import annotations

import argparse
import socket
import struct
import time
from dataclasses import dataclass
from typing import Optional


ETH_P_ALL = 0x0003
ETH_HEADER_LEN = 14


def _format_mac(raw_mac: bytes) -> str:
    return ":".join(f"{part:02x}" for part in raw_mac)


def _format_ipv4(raw_ip: bytes) -> str:
    return ".".join(str(part) for part in raw_ip)


def _format_ipv6(raw_ip: bytes) -> str:
    return socket.inet_ntop(socket.AF_INET6, raw_ip)


@dataclass
class PacketSummary:
    timestamp: float
    length: int
    src: str
    dst: str
    protocol: str

    def to_line(self) -> str:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
        millis = int((self.timestamp - int(self.timestamp)) * 1000)
        return f"{ts}.{millis:03d} len={self.length:<5} {self.src} -> {self.dst} proto={self.protocol}"


def _parse_packet(packet: bytes, ts: float) -> PacketSummary:
    if len(packet) < ETH_HEADER_LEN:
        return PacketSummary(ts, len(packet), "unknown", "unknown", "truncated")

    eth_dst, eth_src, eth_type = struct.unpack("!6s6sH", packet[:ETH_HEADER_LEN])
    payload = packet[ETH_HEADER_LEN:]
    src_mac = _format_mac(eth_src)
    dst_mac = _format_mac(eth_dst)

    if eth_type == 0x0800 and len(payload) >= 20:  # IPv4
        version_ihl = payload[0]
        ihl = (version_ihl & 0x0F) * 4
        if len(payload) < ihl or ihl < 20:
            return PacketSummary(ts, len(packet), src_mac, dst_mac, "ipv4-bad-header")
        proto = payload[9]
        src_ip = _format_ipv4(payload[12:16])
        dst_ip = _format_ipv4(payload[16:20])
        return PacketSummary(ts, len(packet), src_ip, dst_ip, f"ipv4/{proto}")

    if eth_type == 0x86DD and len(payload) >= 40:  # IPv6
        next_header = payload[6]
        src_ip = _format_ipv6(payload[8:24])
        dst_ip = _format_ipv6(payload[24:40])
        return PacketSummary(ts, len(packet), src_ip, dst_ip, f"ipv6/{next_header}")

    return PacketSummary(ts, len(packet), src_mac, dst_mac, f"eth/0x{eth_type:04x}")


def sniff(interface: str, count: int, timeout: float, output_file: Optional[str]) -> int:
    try:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    except PermissionError as exc:
        raise PermissionError(
            "Raw socket requires root/admin privileges. "
            "Try: sudo python3 src/packet_sniffer.py --interface <iface>"
        ) from exc

    with sock:
        sock.bind((interface, 0))
        sock.settimeout(1.0)

        start = time.time()
        captured = 0
        out = open(output_file, "w", encoding="utf-8") if output_file else None

        try:
            while captured < count and (time.time() - start) < timeout:
                try:
                    packet, _ = sock.recvfrom(65535)
                except socket.timeout:
                    continue

                summary = _parse_packet(packet, time.time())
                line = summary.to_line()
                print(line)
                if out:
                    out.write(line + "\n")
                captured += 1
        finally:
            if out:
                out.close()

    return captured


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple packet sniffer (Linux AF_PACKET).")
    parser.add_argument(
        "--interface",
        default="eth0",
        help="Network interface to capture on (example: eth0, ens5, lo).",
    )
    parser.add_argument("--count", type=int, default=100, help="Max packets to capture.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Capture timeout in seconds.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional file path to save packet summaries.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    captured = sniff(
        interface=args.interface,
        count=args.count,
        timeout=args.timeout,
        output_file=args.output,
    )
    print(f"Capture finished: {captured} packets.")


if __name__ == "__main__":
    main()
