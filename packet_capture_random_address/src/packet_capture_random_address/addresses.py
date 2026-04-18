"""Random address generation utilities."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(slots=True)
class Endpoint:
    """Container for generated IP endpoint."""

    ip: str
    port: int

    def as_udp_uri(self) -> str:
        return f"udp://{self.ip}:{self.port}"


class RandomAddressGenerator:
    """Generate random IPv4 endpoints with lightweight helpers."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def random_ipv4(self) -> str:
        """Generate a random IPv4 address."""
        return ".".join(str(self._rng.randint(1, 254)) for _ in range(4))

    def random_loopback_ipv4(self) -> str:
        """Generate an address in loopback range to keep traffic local."""
        return "127.{0}.{1}.{2}".format(
            self._rng.randint(0, 255),
            self._rng.randint(0, 255),
            self._rng.randint(1, 254),
        )

    def random_port(self) -> int:
        return self._rng.randint(1024, 65535)

    def random_endpoint(self, loopback_only: bool = False) -> Endpoint:
        ip = self.random_loopback_ipv4() if loopback_only else self.random_ipv4()
        return Endpoint(ip=ip, port=self.random_port())

    def random_uri(self, loopback_only: bool = False) -> str:
        return self.random_endpoint(loopback_only=loopback_only).as_udp_uri()

