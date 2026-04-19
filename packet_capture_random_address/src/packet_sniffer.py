#!/usr/bin/env python3
"""Simple Linux packet sniffer based on raw sockets."""

from __future__ import annotations

import argparse
import json
import socket
import struct
import time
from dataclasses import asdict, dataclass


ETH_P_ALL = 0x0003


@dataclass(frozen=True)
class PacketSample:
    timestamp: float
    packet_length: int
    source_mac: str
    destination_mac: str
    ethernet_type: int


def _mac_to_str(raw_mac: bytes) -> str:
    return ":".join(f"{byte:02x}" for byte in raw_mac)


class PacketSniffer:
    """Capture ethernet frames via Linux AF_PACKET raw socket."""

    def __init__(self, interface: str | None = None, snap_length: int = 96, timeout: float = 0.0) -> None:
        self._socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
        if interface:
            self._socket.bind((interface, 0))
        self._socket.settimeout(timeout)
        self._snap_length = snap_length

    def close(self) -> None:
        self._socket.close()

    def capture_once(self) -> PacketSample | None:
        try:
            frame, _ = self._socket.recvfrom(self._snap_length)
        except socket.timeout:
            return None
        except BlockingIOError:
            return None

        if len(frame) < 14:
            return None

        destination_mac, source_mac, ethernet_type = struct.unpack("!6s6sH", frame[:14])
        return PacketSample(
            timestamp=time.time(),
            packet_length=len(frame),
            source_mac=_mac_to_str(source_mac),
            destination_mac=_mac_to_str(destination_mac),
            ethernet_type=ethernet_type,
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture packets from a network interface.")
    parser.add_argument("--interface", type=str, default=None, help="Interface name, e.g. eth0.")
    parser.add_argument("--count", type=int, default=20, help="How many packets to capture.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.05,
        help="Socket timeout in seconds for non-blocking behavior.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    captured = 0

    try:
        sniffer = PacketSniffer(interface=args.interface, timeout=args.timeout)
    except PermissionError as exc:
        raise SystemExit("Raw socket capture requires root privileges.") from exc

    try:
        while captured < args.count:
            packet = sniffer.capture_once()
            if packet is None:
                continue
            captured += 1
            print(json.dumps(asdict(packet), ensure_ascii=True))
    finally:
        sniffer.close()


if __name__ == "__main__":
    main()
