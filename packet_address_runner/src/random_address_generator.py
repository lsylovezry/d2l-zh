#!/usr/bin/env python3
"""Random address generator utilities."""

from __future__ import annotations

import argparse
import ipaddress
import random
import string
from typing import Callable, Dict


PRIVATE_IPV4_RANGES = (
    ("10.0.0.0", "10.255.255.255"),
    ("172.16.0.0", "172.31.255.255"),
    ("192.168.0.0", "192.168.255.255"),
)


def random_ipv4(private_only: bool = False) -> str:
    """Return a random IPv4 address."""
    if not private_only:
        value = random.randint(0, (1 << 32) - 1)
        return str(ipaddress.IPv4Address(value))

    start_str, end_str = random.choice(PRIVATE_IPV4_RANGES)
    start = int(ipaddress.IPv4Address(start_str))
    end = int(ipaddress.IPv4Address(end_str))
    value = random.randint(start, end)
    return str(ipaddress.IPv4Address(value))


def random_mac() -> str:
    """Return a random unicast MAC address."""
    first_octet = random.randint(0x00, 0xFF) & 0xFC
    tail = [random.randint(0x00, 0xFF) for _ in range(5)]
    octets = [first_octet, *tail]
    return ":".join(f"{item:02x}" for item in octets)


def random_url() -> str:
    """Return a random URL-like address."""
    host = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    tld = random.choice(["com", "net", "org", "io", "ai", "dev"])
    return f"https://{host}.{tld}"


GENERATORS: Dict[str, Callable[[], str]] = {
    "ipv4": random_ipv4,
    "private_ipv4": lambda: random_ipv4(private_only=True),
    "mac": random_mac,
    "url": random_url,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate random addresses.")
    parser.add_argument(
        "--type",
        choices=sorted(GENERATORS.keys()),
        default="ipv4",
        help="Address type to generate.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of addresses to generate.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generator = GENERATORS[args.type]
    for _ in range(args.count):
        print(generator())


if __name__ == "__main__":
    main()
