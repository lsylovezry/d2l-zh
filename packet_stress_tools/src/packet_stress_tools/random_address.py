"""Random IPv4 address utilities."""

from __future__ import annotations

import ipaddress
import random
from typing import Generator, Optional


def _random_ipv4_int(rng: random.Random) -> int:
    return rng.getrandbits(32)


def generate_random_ipv4(
    rng: Optional[random.Random] = None,
    *,
    allow_reserved: bool = False,
) -> str:
    """Generate a random IPv4 address string.

    By default, special/reserved addresses are filtered out so generated
    addresses are more likely to be usable in common network tests.
    """

    rand = rng or random
    while True:
        candidate = ipaddress.IPv4Address(_random_ipv4_int(rand))
        if allow_reserved:
            return str(candidate)

        if (
            candidate.is_multicast
            or candidate.is_reserved
            or candidate.is_unspecified
            or candidate.is_link_local
        ):
            continue
        return str(candidate)


def generate_random_loopback_ipv4(rng: Optional[random.Random] = None) -> str:
    """Generate a random loopback IPv4 address in 127.0.0.0/8."""

    rand = rng or random
    return f"127.{rand.randint(0, 255)}.{rand.randint(0, 255)}.{rand.randint(1, 254)}"


def iter_random_ipv4(
    count: int,
    *,
    loopback_only: bool = False,
    rng: Optional[random.Random] = None,
) -> Generator[str, None, None]:
    """Yield ``count`` random IPv4 addresses."""

    rand = rng or random
    for _ in range(count):
        if loopback_only:
            yield generate_random_loopback_ipv4(rand)
        else:
            yield generate_random_ipv4(rand)
