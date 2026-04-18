#!/usr/bin/env python3
"""Simple Linux packet sniffer based on raw sockets."""

from __future__ import annotations

import argparse
import socket
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


ETH_P_ALL = 0x0003


@dataclass
class PacketSummary:
    timestamp: float
    src_mac: str
    dst_mac: str
    ether_type: int
    frame_length: int

    def to_line(self) -> str:
        return (
            f"{self.timestamp:.6f} "
            f"src={self.src_mac} dst={self.dst_mac} "
            f"eth_type=0x{self.ether_type:04x} len={self.frame_length}"
        )


def format_mac(raw: bytes) -> str:
    return ":".join(f"{b:02x}" for b in raw)


def parse_ethernet_frame(frame: bytes) -> PacketSummary | None:
    if len(frame) < 14:
        return None
    dst, src, ether_type = struct.unpack("!6s6sH", frame[:14])
    return PacketSummary(
        timestamp=time.time(),
        src_mac=format_mac(src),
        dst_mac=format_mac(dst),
        ether_type=ether_type,
        frame_length=len(frame),
    )


class PacketSniffer:
    """Capture packets using AF_PACKET raw sockets on Linux."""

    def __init__(self, interface: str | None = None) -> None:
        self.interface = interface

    def _open_socket(self) -> socket.socket:
        sniffer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
        if self.interface:
            sniffer.bind((self.interface, 0))
        return sniffer

    def capture(
        self,
        packet_limit: int,
        timeout_seconds: int,
        output: TextIO,
        print_stdout: bool = True,
    ) -> int:
        if packet_limit <= 0:
            raise ValueError("packet_limit must be > 0")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")

        with self._open_socket() as sniffer:
            sniffer.settimeout(0.2)
            start = time.time()
            captured = 0

            while captured < packet_limit and (time.time() - start) < timeout_seconds:
                try:
                    frame, _ = sniffer.recvfrom(65535)
                except TimeoutError:
                    continue

                summary = parse_ethernet_frame(frame)
                if not summary:
                    continue

                line = summary.to_line()
                output.write(line + "\n")
                captured += 1

                if print_stdout and captured <= 10:
                    print(line)

        return captured


def main() -> None:
    parser = argparse.ArgumentParser(description="Raw-socket packet capture utility")
    parser.add_argument(
        "--interface",
        default=None,
        help="Network interface to bind (example: eth0).",
    )
    parser.add_argument(
        "--packet-limit",
        type=int,
        default=200,
        help="Maximum packets to capture before stopping.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Maximum capture duration in seconds.",
    )
    parser.add_argument(
        "--output",
        default="outputs/captured_packets.log",
        help="Path to save packet summaries.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable packet preview on stdout.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sniffer = PacketSniffer(interface=args.interface)
    try:
        with output_path.open("a", encoding="utf-8") as f:
            captured = sniffer.capture(
                packet_limit=args.packet_limit,
                timeout_seconds=args.timeout,
                output=f,
                print_stdout=not args.quiet,
            )
    except PermissionError:
        print("Permission denied: raw socket capture requires root privileges.")
        print("Run with sudo/root or grant CAP_NET_RAW capability.")
        return

    print(f"Capture finished, packets captured: {captured}, log: {output_path}")


if __name__ == "__main__":
    main()
