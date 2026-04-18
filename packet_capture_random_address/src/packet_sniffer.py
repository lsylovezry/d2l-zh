#!/usr/bin/env python3
"""Simple Linux packet sniffer based on raw sockets."""

from __future__ import annotations

import argparse
import json
import signal
import socket
import struct
import threading
import time
from pathlib import Path
from typing import Any

ETH_P_ALL = 0x0003
ETH_TYPE_IPV4 = 0x0800
ETH_TYPE_IPV6 = 0x86DD


def _format_mac(raw: bytes) -> str:
    return ":".join(f"{byte:02x}" for byte in raw)


def _parse_ipv4(packet: bytes) -> dict[str, Any]:
    if len(packet) < 34:
        return {}

    ip_header = packet[14:34]
    version_ihl = ip_header[0]
    ihl = (version_ihl & 0x0F) * 4
    if len(packet) < 14 + ihl:
        return {}

    protocol = ip_header[9]
    src_ip = socket.inet_ntoa(ip_header[12:16])
    dst_ip = socket.inet_ntoa(ip_header[16:20])
    return {
        "network": "ipv4",
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": protocol,
        "ip_header_len": ihl,
    }


def _parse_ipv6(packet: bytes) -> dict[str, Any]:
    if len(packet) < 54:
        return {}

    ip_header = packet[14:54]
    next_header = ip_header[6]
    src_ip = socket.inet_ntop(socket.AF_INET6, ip_header[8:24])
    dst_ip = socket.inet_ntop(socket.AF_INET6, ip_header[24:40])
    return {
        "network": "ipv6",
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "next_header": next_header,
    }


def parse_packet(packet: bytes) -> dict[str, Any]:
    """Parse an ethernet frame into a JSON-serializable summary."""
    if len(packet) < 14:
        return {"frame_len": len(packet), "error": "truncated_ethernet_header"}

    dst_mac, src_mac, eth_type = struct.unpack("!6s6sH", packet[:14])
    summary: dict[str, Any] = {
        "timestamp": time.time(),
        "frame_len": len(packet),
        "src_mac": _format_mac(src_mac),
        "dst_mac": _format_mac(dst_mac),
        "eth_type": f"0x{eth_type:04x}",
    }

    if eth_type == ETH_TYPE_IPV4:
        summary.update(_parse_ipv4(packet))
    elif eth_type == ETH_TYPE_IPV6:
        summary.update(_parse_ipv6(packet))

    return summary


class PacketSniffer:
    """Packet sniffer that writes parsed packet summaries to JSONL."""

    def __init__(self, interface: str, output_file: str, socket_timeout: float = 1.0) -> None:
        self.interface = interface
        self.output_file = Path(output_file)
        self.socket_timeout = socket_timeout
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def start(self, max_packets: int = 0, duration: float = 0.0) -> int:
        """Start packet capture. Returns the number of captured packets."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        start_time = time.time()
        packet_count = 0
        should_limit_packets = max_packets > 0
        should_limit_duration = duration > 0

        raw_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
        if self.interface and self.interface != "any":
            raw_sock.bind((self.interface, 0))
        raw_sock.settimeout(self.socket_timeout)

        try:
            with self.output_file.open("a", encoding="utf-8") as output:
                while not self._stop_event.is_set():
                    if should_limit_packets and packet_count >= max_packets:
                        break
                    if should_limit_duration and (time.time() - start_time) >= duration:
                        break

                    try:
                        packet, _ = raw_sock.recvfrom(65535)
                    except socket.timeout:
                        continue

                    summary = parse_packet(packet)
                    output.write(json.dumps(summary, ensure_ascii=True) + "\n")
                    packet_count += 1
        finally:
            raw_sock.close()

        return packet_count


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture packets and save summaries to JSONL.")
    parser.add_argument(
        "--interface",
        default="any",
        help='Network interface name (e.g. "eth0"), use "any" for all interfaces.',
    )
    parser.add_argument(
        "--output",
        default="outputs/packets.jsonl",
        help="Output JSONL file path.",
    )
    parser.add_argument(
        "--max-packets",
        type=int,
        default=0,
        help="Maximum number of packets to capture, 0 means unlimited.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="Capture duration in seconds, 0 means unlimited.",
    )
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    sniffer = PacketSniffer(interface=args.interface, output_file=args.output)

    def _handle_signal(_signum: int, _frame: Any) -> None:
        sniffer.stop()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        captured = sniffer.start(max_packets=args.max_packets, duration=args.duration)
    except PermissionError as exc:
        parser.error(
            f"Permission denied: {exc}. Raw socket capture needs root privileges."
        )
        return

    print(f"Captured {captured} packets into {args.output}")


if __name__ == "__main__":
    main()
