#!/usr/bin/env python3
"""Simple packet sniffer for Linux using raw sockets."""

from __future__ import annotations

import argparse
import json
import os
import socket
import struct
import sys
import time
from pathlib import Path
from typing import Any


ETH_P_ALL = 0x0003


def parse_ethernet_header(frame: bytes) -> tuple[str, str, int] | None:
    if len(frame) < 14:
        return None
    dst_mac, src_mac, ethertype = struct.unpack("!6s6sH", frame[:14])
    return format_mac(src_mac), format_mac(dst_mac), ethertype


def format_mac(mac: bytes) -> str:
    return ":".join(f"{b:02x}" for b in mac)


def parse_ipv4_header(packet: bytes) -> dict[str, Any] | None:
    if len(packet) < 20:
        return None
    version_ihl = packet[0]
    version = version_ihl >> 4
    ihl = (version_ihl & 0x0F) * 4
    if version != 4 or ihl < 20 or len(packet) < ihl:
        return None

    total_length = struct.unpack("!H", packet[2:4])[0]
    protocol = packet[9]
    src_ip = socket.inet_ntoa(packet[12:16])
    dst_ip = socket.inet_ntoa(packet[16:20])
    return {
        "version": version,
        "ihl": ihl,
        "total_length": total_length,
        "protocol": protocol,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
    }


def parse_transport(packet: bytes, protocol: int) -> dict[str, Any]:
    if protocol == 6 and len(packet) >= 4:
        src_port, dst_port = struct.unpack("!HH", packet[:4])
        return {"protocol_name": "TCP", "src_port": src_port, "dst_port": dst_port}
    if protocol == 17 and len(packet) >= 4:
        src_port, dst_port = struct.unpack("!HH", packet[:4])
        return {"protocol_name": "UDP", "src_port": src_port, "dst_port": dst_port}
    if protocol == 1:
        return {"protocol_name": "ICMP"}
    return {"protocol_name": f"OTHER({protocol})"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture packets from a network interface."
    )
    parser.add_argument(
        "--interface",
        default="any",
        help="Network interface to sniff (e.g. eth0).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of packets to capture before exiting.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Capture timeout in seconds.",
    )
    parser.add_argument(
        "--protocol",
        choices=("all", "tcp", "udp", "icmp"),
        default="all",
        help="Filter protocol for IPv4 packets.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Write captured packet metadata to JSON Lines file.",
    )
    return parser.parse_args()


def protocol_match(protocol: int, protocol_filter: str) -> bool:
    if protocol_filter == "all":
        return True
    mapping = {"tcp": 6, "udp": 17, "icmp": 1}
    return protocol == mapping[protocol_filter]


def create_socket(interface: str) -> socket.socket:
    sniffer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    if interface != "any":
        sniffer.bind((interface, 0))
    return sniffer


def run() -> int:
    args = parse_args()

    if args.count <= 0:
        raise ValueError("--count must be > 0")
    if args.timeout <= 0:
        raise ValueError("--timeout must be > 0")

    output_handle = None
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_handle = output_path.open("w", encoding="utf-8")

    try:
        sniffer = create_socket(args.interface)
    except PermissionError:
        print(
            "Permission denied: raw socket requires root privileges. "
            "Run with sudo.",
            file=sys.stderr,
        )
        return 1
    except OSError as exc:
        print(f"Failed to open raw socket: {exc}", file=sys.stderr)
        return 1

    sniffer.settimeout(0.5)
    deadline = time.time() + args.timeout
    captured = 0
    skipped = 0
    start_time = time.time()

    try:
        while captured < args.count and time.time() < deadline:
            try:
                frame, _ = sniffer.recvfrom(65535)
            except socket.timeout:
                continue
            except OSError as exc:
                print(f"Socket read error: {exc}", file=sys.stderr)
                return 1

            eth = parse_ethernet_header(frame)
            if eth is None:
                skipped += 1
                continue
            src_mac, dst_mac, ethertype = eth

            if ethertype != 0x0800:
                skipped += 1
                continue

            ip_packet = frame[14:]
            ip = parse_ipv4_header(ip_packet)
            if ip is None:
                skipped += 1
                continue

            if not protocol_match(ip["protocol"], args.protocol):
                skipped += 1
                continue

            payload = ip_packet[ip["ihl"] :]
            transport = parse_transport(payload, ip["protocol"])
            captured += 1

            event = {
                "timestamp": time.time(),
                "index": captured,
                "src_mac": src_mac,
                "dst_mac": dst_mac,
                "src_ip": ip["src_ip"],
                "dst_ip": ip["dst_ip"],
                "protocol": transport["protocol_name"],
                "src_port": transport.get("src_port"),
                "dst_port": transport.get("dst_port"),
                "length": len(frame),
            }
            print(json.dumps(event, ensure_ascii=True))
            if output_handle is not None:
                output_handle.write(json.dumps(event, ensure_ascii=True))
                output_handle.write("\n")
    finally:
        sniffer.close()
        if output_handle is not None:
            output_handle.close()

    elapsed = time.time() - start_time
    print(
        f"captured={captured} skipped={skipped} elapsed={elapsed:.2f}s",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    if os.name != "posix":
        print("This sniffer currently supports Linux only.", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(run())
