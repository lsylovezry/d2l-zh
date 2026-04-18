"""CLI tool to print random addresses."""

from __future__ import annotations

import argparse

from network_traffic_tools.address_generator import RandomAddressGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate random network addresses")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument(
        "--mode",
        choices=["private_ipv4", "public_ipv4", "mac"],
        default="private_ipv4",
    )
    args = parser.parse_args()

    gen = RandomAddressGenerator()
    fn_map = {
        "private_ipv4": gen.random_private_ipv4,
        "public_ipv4": gen.random_public_ipv4,
        "mac": gen.random_mac,
    }
    generate = fn_map[args.mode]

    for _ in range(args.count):
        print(generate())


if __name__ == "__main__":
    main()
