"""Random address generation utilities."""

from __future__ import annotations

import ipaddress
import random
from dataclasses import dataclass


@dataclass
class RandomAddressGenerator:
    """Generate random IPv4 addresses."""

    public_only: bool = False

    def generate_ipv4(self) -> str:
        """Generate one IPv4 address string."""
        while True:
            value = random.getrandbits(32)
            ip = ipaddress.IPv4Address(value)
            if not self.public_only or ip.is_global:
                return str(ip)

