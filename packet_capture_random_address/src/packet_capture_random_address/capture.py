"""Packet capture utilities based on Linux raw sockets."""

from __future__ import annotations

import json
import socket
import struct
import time
from dataclasses import asdict, dataclass
from pathlib import Path


ETH_P_ALL = 0x0003
ETH_HEADER_LEN = 14
IPV4_ETHERTYPE = 0x0800


@dataclass(slots=True)
class PacketRecord:
    """A minimal decoded packet record."""

    timestamp: float
    interface: str
    length: int
    src_ip: str | None
    dst_ip: str | None
    protocol: str | None


def _decode_ipv4(packet: bytes) -> tuple[str | None, str | None, str | None]:
    if len(packet) < ETH_HEADER_LEN + 20:
        return None, None, None

    ethertype = struct.unpack("!H", packet[12:14])[0]
    if ethertype != IPV4_ETHERTYPE:
        return None, None, None

    ip_start = ETH_HEADER_LEN
    ip_version_ihl = packet[ip_start]
    ihl = (ip_version_ihl & 0x0F) * 4
    if ihl < 20 or len(packet) < ip_start + ihl:
        return None, None, None

    proto_num = packet[ip_start + 9]
    src_ip = socket.inet_ntoa(packet[ip_start + 12 : ip_start + 16])
    dst_ip = socket.inet_ntoa(packet[ip_start + 16 : ip_start + 20])
    proto = {1: "ICMP", 6: "TCP", 17: "UDP"}.get(proto_num, f"IP_PROTO_{proto_num}")
    return src_ip, dst_ip, proto


class PacketSniffer:
    """Capture packets on Linux using AF_PACKET."""

    def __init__(self, interface: str = "lo") -> None:
        self.interface = interface

    def capture(
        self,
        output_path: str | Path,
        packet_count: int = 100,
        timeout_seconds: float = 10.0,
    ) -> dict[str, float | int]:
        start = time.perf_counter()
        captured = 0
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
        try:
            sock.bind((self.interface, 0))
            sock.settimeout(0.5)

            deadline = time.perf_counter() + timeout_seconds
            with output.open("w", encoding="utf-8") as fp:
                while captured < packet_count and time.perf_counter() < deadline:
                    try:
                        packet, _ = sock.recvfrom(65535)
                    except TimeoutError:
                        continue

                    src_ip, dst_ip, proto = _decode_ipv4(packet)
                    record = PacketRecord(
                        timestamp=time.time(),
                        interface=self.interface,
                        length=len(packet),
                        src_ip=src_ip,
                        dst_ip=dst_ip,
                        protocol=proto,
                    )
                    fp.write(json.dumps(asdict(record), ensure_ascii=True) + "\n")
                    captured += 1
        finally:
            sock.close()

        elapsed = time.perf_counter() - start
        return {
            "captured_packets": captured,
            "elapsed_seconds": round(elapsed, 4),
            "packets_per_second": round(captured / elapsed, 2) if elapsed else 0.0,
        }
