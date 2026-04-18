"""Random network address generators for authorized testing only."""

from __future__ import annotations

import ipaddress
import random
from dataclasses import dataclass


# RFC1918 private IPv4 ranges for safer local testing.
_PRIVATE_V4_RANGES = [
    (ipaddress.IPv4Address("10.0.0.0"), ipaddress.IPv4Address("10.255.255.255")),
    (ipaddress.IPv4Address("172.16.0.0"), ipaddress.IPv4Address("172.31.255.255")),
    (ipaddress.IPv4Address("192.168.0.0"), ipaddress.IPv4Address("192.168.255.255")),
]


@dataclass(frozen=True)
class RandomAddressGenerator:
    """Generate random addresses for test/simulation usage.

    The generator intentionally defaults to private IPv4 ranges so it can be
    used in internal, authorized environments without touching public IP space.
    """

    rng: random.Random = random.Random()

    def random_private_ipv4(self) -> str:
        """Return a random RFC1918 IPv4 address."""
        start, end = self.rng.choice(_PRIVATE_V4_RANGES)
        value = self.rng.randint(int(start), int(end))
        return str(ipaddress.IPv4Address(value))

    def random_public_ipv4(self) -> str:
        """Return a random globally routable IPv4 address."""
        while True:
            value = self.rng.getrandbits(32)
            addr = ipaddress.IPv4Address(value)
            if not (
                addr.is_private
                or addr.is_multicast
                or addr.is_loopback
                or addr.is_reserved
                or addr.is_link_local
                or addr.is_unspecified
            ):
                return str(addr)

    def random_mac(self) -> str:
        """Return a random locally administered unicast MAC address."""
        first_octet = self.rng.randint(0x00, 0xFF)
        # Set local bit (bit1) and unset multicast bit (bit0)
        first_octet = (first_octet | 0x02) & 0xFE
        octets = [first_octet] + [self.rng.randint(0x00, 0xFF) for _ in range(5)]
        return ":".join(f"{item:02x}" for item in octets)
