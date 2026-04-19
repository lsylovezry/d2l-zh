"""Random IPv4 address generation helpers."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class RandomAddressGenerator:
    """Generate random IPv4 addresses and endpoint tuples."""

    include_private: bool = True
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rand = random.Random(self.seed)

    def generate_ipv4(self) -> str:
        """Return one random IPv4 address string."""
        while True:
            first = self._rand.randint(1, 223)
            second = self._rand.randint(0, 255)
            third = self._rand.randint(0, 255)
            fourth = self._rand.randint(1, 254)
            candidate = f"{first}.{second}.{third}.{fourth}"
            if self.include_private or self._is_public(first, second):
                return candidate

    def generate_endpoint(self) -> tuple[str, int]:
        """Return one (ip, port) pair."""
        return self.generate_ipv4(), self._rand.randint(1024, 65535)

    @staticmethod
    def _is_public(first: int, second: int) -> bool:
        if first == 10:
            return False
        if first == 172 and 16 <= second <= 31:
            return False
        if first == 192 and second == 168:
            return False
        if first == 127:
            return False
        if first >= 224:
            return False
        if first == 169 and second == 254:
            return False
        return True
