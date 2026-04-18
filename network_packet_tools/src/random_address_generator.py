#!/usr/bin/env python3
"""Random address generator utilities.

This module provides a CLI and reusable class for generating random addresses:
- IPv4
- IPv6
- MAC
- Socket address (ip:port)
- URL
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass


def _random_label(rng: random.Random, min_len: int = 3, max_len: int = 10) -> str:
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    length = rng.randint(min_len, max_len)
    return "".join(rng.choice(chars) for _ in range(length))


@dataclass
class RandomAddressGenerator:
    """Generate random address-like strings."""

    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def ipv4(self) -> str:
        return ".".join(str(self._rng.randint(1, 254)) for _ in range(4))

    def ipv6(self) -> str:
        return ":".join(f"{self._rng.randint(0, 0xFFFF):04x}" for _ in range(8))

    def mac(self) -> str:
        return ":".join(f"{self._rng.randint(0, 255):02x}" for _ in range(6))

    def socket_address(self) -> str:
        return f"{self.ipv4()}:{self._rng.randint(1, 65535)}"

    def url(self) -> str:
        scheme = self._rng.choice(["http", "https"])
        domain = f"{_random_label(self._rng)}.{self._rng.choice(['com', 'net', 'org', 'io'])}"
        path_depth = self._rng.randint(0, 3)
        path = "/".join(_random_label(self._rng, 2, 8) for _ in range(path_depth))
        if path:
            path = "/" + path

        if self._rng.random() < 0.5:
            query_count = self._rng.randint(1, 3)
            query = "&".join(
                f"{_random_label(self._rng, 2, 6)}={_random_label(self._rng, 2, 8)}"
                for _ in range(query_count)
            )
            return f"{scheme}://{domain}{path}?{query}"

        return f"{scheme}://{domain}{path}"

    def generate(self, mode: str) -> str:
        if mode == "ipv4":
            return self.ipv4()
        if mode == "ipv6":
            return self.ipv6()
        if mode == "mac":
            return self.mac()
        if mode == "socket":
            return self.socket_address()
        if mode == "url":
            return self.url()
        raise ValueError(f"Unsupported mode: {mode}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random network addresses.")
    parser.add_argument(
        "--mode",
        default="ipv4",
        choices=["ipv4", "ipv6", "mac", "socket", "url"],
        help="Type of random address to generate.",
    )
    parser.add_argument("--count", type=int, default=10, help="Number of addresses to generate.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    generator = RandomAddressGenerator(seed=args.seed)

    for _ in range(args.count):
        print(generator.generate(args.mode))


if __name__ == "__main__":
    main()
