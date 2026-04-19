#!/usr/bin/env python3
"""High-speed random address generation utilities."""

from __future__ import annotations

import argparse
import json
import random
import string
from dataclasses import asdict, dataclass


DEFAULT_TOP_LEVEL_DOMAINS = ("com", "net", "org", "io", "dev")


@dataclass(frozen=True)
class RandomAddress:
    ipv4: str
    ipv6: str
    mac: str
    url: str


class RandomAddressGenerator:
    """Generate random network-style addresses with low overhead."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def random_ipv4(self) -> str:
        return ".".join(str(self._rng.randint(1, 254)) for _ in range(4))

    def random_ipv6(self) -> str:
        value = f"{self._rng.getrandbits(128):032x}"
        return ":".join(value[index : index + 4] for index in range(0, 32, 4))

    def random_mac(self) -> str:
        first_octet = (self._rng.randint(0, 255) & 0b11111100) | 0b00000010
        octets = [first_octet] + [self._rng.randint(0, 255) for _ in range(5)]
        return ":".join(f"{octet:02x}" for octet in octets)

    def random_url(self) -> str:
        scheme = "https" if self._rng.random() > 0.2 else "http"
        domain = self._random_domain()
        path = self._random_path()
        return f"{scheme}://{domain}/{path}"

    def generate(self) -> RandomAddress:
        return RandomAddress(
            ipv4=self.random_ipv4(),
            ipv6=self.random_ipv6(),
            mac=self.random_mac(),
            url=self.random_url(),
        )

    def _random_domain(self) -> str:
        length = self._rng.randint(6, 14)
        alphabet = string.ascii_lowercase + string.digits
        label = "".join(self._rng.choices(alphabet, k=length))
        tld = self._rng.choice(DEFAULT_TOP_LEVEL_DOMAINS)
        return f"{label}.{tld}"

    def _random_path(self) -> str:
        segment_count = self._rng.randint(1, 3)
        alphabet = string.ascii_lowercase + string.digits + "-_"
        segments = []
        for _ in range(segment_count):
            length = self._rng.randint(4, 12)
            segment = "".join(self._rng.choices(alphabet, k=length))
            segments.append(segment)
        return "/".join(segments)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random addresses.")
    parser.add_argument("--count", type=int, default=5, help="Number of rows to emit.")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional deterministic seed for reproducibility.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    generator = RandomAddressGenerator(seed=args.seed)
    for _ in range(args.count):
        print(json.dumps(asdict(generator.generate()), ensure_ascii=True))


if __name__ == "__main__":
    main()
