"""Simple Linux packet sniffer using raw sockets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import errno
import socket
import time


ETH_P_ALL = 0x0003


@dataclass
class CapturedPacket:
    """Metadata extracted from a captured Ethernet frame."""

    timestamp: float
    length: int
    source_mac: str
    destination_mac: str
    ether_type: int


def _format_mac(raw: bytes) -> str:
    return ":".join(f"{part:02x}" for part in raw)


class PacketSniffer:
    """Packet sniffer wrapper over Linux AF_PACKET raw sockets."""

    def __init__(self, interface: str | None = None, buffer_size: int = 65535) -> None:
        self.interface = interface
        self.buffer_size = buffer_size
        self._socket: socket.socket | None = None

    def open(self) -> None:
        """Open and configure the raw socket once for repeated polling."""
        if self._socket is not None:
            return
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
        if self.interface:
            sock.bind((self.interface, 0))
        sock.setblocking(False)
        self._socket = sock

    def close(self) -> None:
        """Close the internal raw socket."""
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def __enter__(self) -> "PacketSniffer":
        self.open()
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self.close()

    def poll_one(self) -> CapturedPacket | None:
        """Try to fetch one packet without blocking. Return None if unavailable."""
        if self._socket is None:
            self.open()
        assert self._socket is not None

        try:
            raw_frame, _ = self._socket.recvfrom(self.buffer_size)
        except OSError as error:
            if error.errno in {errno.EAGAIN, errno.EWOULDBLOCK}:
                return None
            raise

        if len(raw_frame) < 14:
            return None

        destination_mac = _format_mac(raw_frame[0:6])
        source_mac = _format_mac(raw_frame[6:12])
        ether_type = int.from_bytes(raw_frame[12:14], "big")
        return CapturedPacket(
            timestamp=time.time(),
            length=len(raw_frame),
            source_mac=source_mac,
            destination_mac=destination_mac,
            ether_type=ether_type,
        )

    def capture(self, packet_limit: int = 100, timeout_seconds: float = 3.0) -> list[CapturedPacket]:
        """Capture packets and return parsed metadata."""
        packets: list[CapturedPacket] = []
        deadline = time.perf_counter() + timeout_seconds
        with self:
            while len(packets) < packet_limit and time.perf_counter() < deadline:
                packet = self.poll_one()
                if packet is None:
                    time.sleep(0.001)
                    continue
                packets.append(packet)
        return packets


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture network packets from a Linux interface.")
    parser.add_argument("--interface", default=None, help="Network interface to bind (e.g., eth0).")
    parser.add_argument("--count", type=int, default=10, help="Number of packets to capture.")
    parser.add_argument("--timeout", type=float, default=3.0, help="Capture timeout in seconds.")
    args = parser.parse_args()

    sniffer = PacketSniffer(interface=args.interface)
    captured = sniffer.capture(packet_limit=args.count, timeout_seconds=args.timeout)
    print(f"Captured {len(captured)} packets")
    for index, packet in enumerate(captured, start=1):
        print(
            f"[{index}] len={packet.length} src={packet.source_mac} "
            f"dst={packet.destination_mac} type=0x{packet.ether_type:04x}"
        )


if __name__ == "__main__":
    main()
