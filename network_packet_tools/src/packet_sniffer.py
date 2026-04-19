#!/usr/bin/env python3
"""
Simple packet sniffer for Linux using raw sockets.

Usage example (requires root):
    sudo python3 src/packet_sniffer.py --interface eth0 --count 10
"""

from __future__ import annotations

import argparse
import json
import socket
import struct
import time
from typing import Dict, Optional


ETH_P_ALL = 0x0003


def mac_str(raw: bytes) -> str:
    return ":".join(f"{b:02x}" for b in raw)


def parse_ipv4_header(packet: bytes, offset: int) -> Optional[Dict[str, object]]:
    if len(packet) < offset + 20:
        return None
    iph = struct.unpack("!BBHHHBBH4s4s", packet[offset : offset + 20])
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = (version_ihl & 0xF) * 4
    if version != 4 or len(packet) < offset + ihl:
        return None
    proto = iph[6]
    src_ip = socket.inet_ntoa(iph[8])
    dst_ip = socket.inet_ntoa(iph[9])
    return {
        "ip_version": version,
        "ip_header_length": ihl,
        "protocol": proto,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
    }


def sniff(interface: str, count: int, timeout: float, output: Optional[str]) -> None:
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    sock.bind((interface, 0))
    sock.settimeout(timeout)

    output_file = open(output, "w", encoding="utf-8") if output else None
    captured = 0
    dropped_timeout = 0

    try:
        while captured < count:
            try:
                raw_data, _addr = sock.recvfrom(65535)
            except socket.timeout:
                dropped_timeout += 1
                continue

            if len(raw_data) < 14:
                continue

            dest_mac, src_mac, eth_proto = struct.unpack("!6s6sH", raw_data[:14])
            record: Dict[str, object] = {
                "timestamp": time.time(),
                "src_mac": mac_str(src_mac),
                "dst_mac": mac_str(dest_mac),
                "eth_proto": eth_proto,
                "length": len(raw_data),
            }

            ip_info = parse_ipv4_header(raw_data, 14)
            if ip_info:
                record.update(ip_info)

            print(json.dumps(record, ensure_ascii=True))
            if output_file:
                output_file.write(json.dumps(record, ensure_ascii=True) + "\n")

            captured += 1

        print(
            json.dumps(
                {
                    "status": "done",
                    "captured": captured,
                    "timeouts": dropped_timeout,
                    "interface": interface,
                },
                ensure_ascii=True,
            )
        )
    finally:
        if output_file:
            output_file.close()
        sock.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Raw socket packet sniffer (Linux)")
    parser.add_argument("--interface", required=True, help="Interface name, e.g., eth0")
    parser.add_argument("--count", type=int, default=20, help="Number of packets to capture")
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Socket timeout seconds for each receive call",
    )
    parser.add_argument("--output", default=None, help="Optional output JSONL file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count <= 0:
        raise ValueError("--count must be positive")
    if args.timeout <= 0:
        raise ValueError("--timeout must be positive")
    sniff(args.interface, args.count, args.timeout, args.output)


if __name__ == "__main__":
    main()
