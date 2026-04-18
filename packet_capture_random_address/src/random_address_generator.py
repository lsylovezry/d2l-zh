#!/usr/bin/env python3
"""Random address generator for IPv4/IPv6/MAC/URL."""

from __future__ import annotations

import argparse
import ipaddress
import random
import string
from pathlib import Path


def generate_ipv4() -> str:
    return str(ipaddress.IPv4Address(random.getrandbits(32)))


def generate_ipv6() -> str:
    return str(ipaddress.IPv6Address(random.getrandbits(128)))


def generate_mac() -> str:
    octets = [random.randint(0x00, 0xFF) for _ in range(6)]
    # Set locally administered and unicast bits.
    octets[0] = (octets[0] | 0x02) & 0xFE
    return ":".join(f"{value:02x}" for value in octets)


def generate_url() -> str:
    subdomain = "".join(random.choices(string.ascii_lowercase, k=6))
    domain = "".join(random.choices(string.ascii_lowercase, k=8))
    tld = random.choice(["com", "net", "org", "io", "ai"])
    path = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"https://{subdomain}.{domain}.{tld}/{path}"


def generate_random_address(kind: str = "mixed") -> str:
    if kind == "ipv4":
        return generate_ipv4()
    if kind == "ipv6":
        return generate_ipv6()
    if kind == "mac":
        return generate_mac()
    if kind == "url":
        return generate_url()

    choice = random.choice(["ipv4", "ipv6", "mac", "url"])
    return generate_random_address(choice)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random addresses.")
    parser.add_argument(
        "--type",
        choices=["mixed", "ipv4", "ipv6", "mac", "url"],
        default="mixed",
        help="Address type to generate.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of addresses to generate.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output file path. Print to stdout when omitted.",
    )
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    if args.count < 0:
        raise ValueError("--count must be >= 0")

    addresses = [generate_random_address(args.type) for _ in range(args.count)]
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(addresses) + ("\n" if addresses else ""), encoding="utf-8")
        print(f"Wrote {len(addresses)} addresses to {output_path}")
        return

    for address in addresses:
        print(address)


if __name__ == "__main__":
    main()
