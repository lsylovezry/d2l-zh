"""Random network address generators."""

from __future__ import annotations

import random
import secrets
import string
from dataclasses import dataclass


@dataclass(frozen=True)
class RandomAddress:
    """Structured random address payload."""

    ipv4: str
    ipv6: str
    mac: str
    hostname: str
    port: int


class RandomAddressGenerator:
    """Generate random network addresses with low overhead."""

    _HOST_CHARS = string.ascii_lowercase + string.digits

    def __init__(self, secure: bool = False) -> None:
        self._rand = secrets.SystemRandom() if secure else random.Random()

    def random_ipv4(self) -> str:
        octets = (self._rand.randrange(1, 255),)
        octets += tuple(self._rand.randrange(0, 256) for _ in range(2))
        octets += (self._rand.randrange(1, 255),)
        return f"{octets[0]}.{octets[1]}.{octets[2]}.{octets[3]}"

    def random_ipv6(self) -> str:
        return ":".join(f"{self._rand.getrandbits(16):04x}" for _ in range(8))

    def random_mac(self) -> str:
        # Set locally administered unicast MAC.
        first = (self._rand.getrandbits(8) | 0x02) & 0xFE
        rest = [self._rand.getrandbits(8) for _ in range(5)]
        return ":".join(f"{b:02x}" for b in [first, *rest])

    def random_hostname(self, min_len: int = 6, max_len: int = 16) -> str:
        length = self._rand.randint(min_len, max_len)
        head = self._rand.choice(string.ascii_lowercase)
        if length == 1:
            return head
        body = "".join(self._rand.choice(self._HOST_CHARS) for _ in range(length - 1))
        return head + body

    def random_port(self) -> int:
        return self._rand.randrange(1024, 65536)

    def generate(self) -> RandomAddress:
        return RandomAddress(
            ipv4=self.random_ipv4(),
            ipv6=self.random_ipv6(),
            mac=self.random_mac(),
            hostname=self.random_hostname(),
            port=self.random_port(),
        )
