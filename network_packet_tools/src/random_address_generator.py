#!/usr/bin/env python3
"""
Random address generator.

Supports:
- IPv4
- IPv6
- MAC
- URL
"""

from __future__ import annotations

import argparse
import ipaddress
import random
import string
from typing import Callable


def random_ipv4() -> str:
    """Generate a random valid IPv4 address."""
    return str(ipaddress.IPv4Address(random.getrandbits(32)))


def random_ipv6() -> str:
    """Generate a random valid IPv6 address."""
    return str(ipaddress.IPv6Address(random.getrandbits(128)))


def random_mac() -> str:
    """Generate a random unicast locally administered MAC address."""
    first_octet = random.randint(0x00, 0xFF)
    # Force locally administered (bit1=1) and unicast (bit0=0)
    first_octet = (first_octet | 0x02) & 0xFE
    tail = [random.randint(0x00, 0xFF) for _ in range(5)]
    octets = [first_octet, *tail]
    return ":".join(f"{octet:02x}" for octet in octets)


def random_url() -> str:
    """Generate a pseudo-random URL-like address."""
    label_chars = string.ascii_lowercase + string.digits
    tlds = ["com", "net", "org", "io", "dev", "ai", "cn"]
    path_chars = string.ascii_lowercase + string.digits + "-_"

    domain_len = random.randint(5, 12)
    domain = "".join(random.choice(label_chars) for _ in range(domain_len))
    tld = random.choice(tlds)

    depth = random.randint(1, 3)
    parts = []
    for _ in range(depth):
        segment_len = random.randint(3, 10)
        segment = "".join(random.choice(path_chars) for _ in range(segment_len))
        parts.append(segment)
    path = "/".join(parts)
    return f"https://{domain}.{tld}/{path}"


GENERATOR_MAP: dict[str, Callable[[], str]] = {
    "ipv4": random_ipv4,
    "ipv6": random_ipv6,
    "mac": random_mac,
    "url": random_url,
}


def generate_random_address(address_type: str) -> str:
    """Generate one address by type."""
    try:
        generator = GENERATOR_MAP[address_type]
    except KeyError as exc:
        valid = ", ".join(sorted(GENERATOR_MAP.keys()))
        raise ValueError(f"Unsupported address type: {address_type}. Valid: {valid}") from exc
    return generator()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate random network addresses.")
    parser.add_argument(
        "--type",
        choices=sorted(GENERATOR_MAP.keys()),
        default="ipv4",
        help="Address type to generate.",
    )
    parser.add_argument("--count", type=int, default=1, help="Number of addresses to generate.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count <= 0:
        raise ValueError("--count must be > 0")

    for _ in range(args.count):
        print(generate_random_address(args.type))


if __name__ == "__main__":
    main()
