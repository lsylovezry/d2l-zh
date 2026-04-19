"""Random address generator utilities."""

from __future__ import annotations

import ipaddress
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class RandomAddress:
    """Container for generated addresses."""

    ipv4: str
    ipv6: str
    mac: str


class RandomAddressGenerator:
    """Generate random network addresses."""

    def random_ipv4(self) -> str:
        return ".".join(str(random.randint(0, 255)) for _ in range(4))

    def random_private_ipv4(self) -> str:
        # Common private ranges: 10/8, 172.16/12, 192.168/16
        selector = random.randint(0, 2)
        if selector == 0:
            return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        if selector == 1:
            return (
                f"172.{random.randint(16, 31)}."
                f"{random.randint(0, 255)}.{random.randint(1, 254)}"
            )
        return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"

    def random_ipv6(self) -> str:
        value = random.getrandbits(128)
        return str(ipaddress.IPv6Address(value))

    def random_mac(self) -> str:
        octets = [random.randint(0x00, 0xFF) for _ in range(6)]
        # Set locally administered unicast MAC.
        octets[0] = (octets[0] | 0x02) & 0xFE
        return ":".join(f"{octet:02x}" for octet in octets)

    def random_bundle(self) -> RandomAddress:
        return RandomAddress(
            ipv4=self.random_ipv4(),
            ipv6=self.random_ipv6(),
            mac=self.random_mac(),
        )
