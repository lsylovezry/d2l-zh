"""Random address generation utilities."""

from __future__ import annotations

import ipaddress
import random
import time
from dataclasses import asdict, dataclass
from typing import Dict, Tuple


@dataclass
class AddressRecord:
    """Single generated address sample."""

    timestamp: float
    src_ipv4: str
    dst_ipv4: str
    src_ipv6: str
    dst_ipv6: str
    src_mac: str
    dst_mac: str
    src_port: int
    dst_port: int

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def random_ipv4() -> str:
    """Return a random IPv4 string."""
    return str(ipaddress.IPv4Address(random.getrandbits(32)))


def random_ipv6() -> str:
    """Return a random IPv6 string."""
    return str(ipaddress.IPv6Address(random.getrandbits(128)))


def random_mac() -> str:
    """Return a random unicast MAC address."""
    octets = [random.getrandbits(8) for _ in range(6)]
    octets[0] = octets[0] & 0xFE  # Ensure unicast
    return ":".join(f"{octet:02x}" for octet in octets)


def random_port() -> int:
    """Return a random TCP/UDP port."""
    return random.randint(1, 65535)


def random_ipv4_endpoint() -> Tuple[str, int]:
    """Return random IPv4 address and port."""
    return random_ipv4(), random_port()


def generate_address_record() -> AddressRecord:
    """Generate one random record containing multiple address types."""
    src_ipv4, src_port = random_ipv4_endpoint()
    dst_ipv4, dst_port = random_ipv4_endpoint()
    return AddressRecord(
        timestamp=time.time(),
        src_ipv4=src_ipv4,
        dst_ipv4=dst_ipv4,
        src_ipv6=random_ipv6(),
        dst_ipv6=random_ipv6(),
        src_mac=random_mac(),
        dst_mac=random_mac(),
        src_port=src_port,
        dst_port=dst_port,
    )
