"""Random network address generation utilities."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import random


@dataclass(frozen=True)
class SocketEndpoint:
    """Simple endpoint container."""

    ip: str
    port: int


class RandomAddressGenerator:
    """Generate random network addresses for testing and load simulation."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def random_ipv4(self, public_only: bool = False) -> str:
        """Return a random IPv4 address."""
        while True:
            candidate = ipaddress.IPv4Address(self._rng.getrandbits(32))
            if not public_only or candidate.is_global:
                return str(candidate)

    def random_ipv6(self, public_only: bool = False) -> str:
        """Return a random IPv6 address."""
        while True:
            candidate = ipaddress.IPv6Address(self._rng.getrandbits(128))
            if not public_only or candidate.is_global:
                return str(candidate)

    def random_mac(self) -> str:
        """Return a locally-administered unicast MAC address."""
        first_octet = (self._rng.randrange(0, 256) | 0x02) & 0xFE
        octets = [first_octet, *[self._rng.randrange(0, 256) for _ in range(5)]]
        return ":".join(f"{octet:02x}" for octet in octets)

    def random_port(self, min_port: int = 1024, max_port: int = 65535) -> int:
        """Return a random TCP/UDP port in range [min_port, max_port]."""
        if min_port < 1 or max_port > 65535 or min_port > max_port:
            raise ValueError("Invalid port range.")
        return self._rng.randint(min_port, max_port)

    def random_endpoint(self, public_ip: bool = False) -> SocketEndpoint:
        """Return a random IPv4:port endpoint."""
        return SocketEndpoint(
            ip=self.random_ipv4(public_only=public_ip),
            port=self.random_port(),
        )


if __name__ == "__main__":
    generator = RandomAddressGenerator()
    print("IPv4:", generator.random_ipv4())
    print("IPv6:", generator.random_ipv6())
    print("MAC :", generator.random_mac())
    print("Endpoint:", generator.random_endpoint())
