#!/usr/bin/env python3
"""Random network address generator with rate control."""

from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass
from typing import Callable


AddressFn = Callable[[], str]


@dataclass
class GenerationStats:
    total_generated: int
    elapsed_seconds: float

    @property
    def rate(self) -> float:
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.total_generated / self.elapsed_seconds


class RandomAddressGenerator:
    """Generate random IPv4/IPv6/MAC addresses efficiently."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def generate_ipv4(self) -> str:
        return ".".join(str(self._rng.randint(0, 255)) for _ in range(4))

    def generate_ipv6(self) -> str:
        return ":".join(f"{self._rng.getrandbits(16):04x}" for _ in range(8))

    def generate_mac(self) -> str:
        first_octet = self._rng.randint(0x00, 0xFF) | 0x02
        octets = [first_octet] + [self._rng.randint(0x00, 0xFF) for _ in range(5)]
        return ":".join(f"{octet:02x}" for octet in octets)

    def _resolve(self, address_type: str) -> AddressFn:
        mapping = {
            "ipv4": self.generate_ipv4,
            "ipv6": self.generate_ipv6,
            "mac": self.generate_mac,
        }
        if address_type not in mapping:
            raise ValueError(f"Unsupported address_type: {address_type}")
        return mapping[address_type]

    def run_at_rate(
        self,
        target_per_second: int = 100000,
        duration_seconds: int = 5,
        address_type: str = "ipv4",
        sample_output: bool = False,
    ) -> GenerationStats:
        if target_per_second <= 0:
            raise ValueError("target_per_second must be > 0")
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be > 0")

        generator = self._resolve(address_type)
        total_generated = 0
        start = time.perf_counter()

        for second in range(duration_seconds):
            tick_start = time.perf_counter()
            samples = []

            for _ in range(target_per_second):
                value = generator()
                if sample_output and len(samples) < 5:
                    samples.append(value)

            total_generated += target_per_second
            elapsed = time.perf_counter() - tick_start
            remaining = 1.0 - elapsed
            if remaining > 0:
                time.sleep(remaining)

            if sample_output:
                print(
                    f"[sec={second + 1}] generated={target_per_second}, "
                    f"sample={samples}"
                )

        total_elapsed = time.perf_counter() - start
        return GenerationStats(
            total_generated=total_generated,
            elapsed_seconds=total_elapsed,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Random address generator benchmark")
    parser.add_argument(
        "--address-type",
        choices=["ipv4", "ipv6", "mac"],
        default="ipv4",
        help="Type of random address to generate.",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=100000,
        help="Target generated addresses per second.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Duration in seconds.",
    )
    parser.add_argument(
        "--sample-output",
        action="store_true",
        help="Print a few sample addresses each second.",
    )
    args = parser.parse_args()

    generator = RandomAddressGenerator()
    stats = generator.run_at_rate(
        target_per_second=args.rate,
        duration_seconds=args.duration,
        address_type=args.address_type,
        sample_output=args.sample_output,
    )

    print(
        f"Total generated: {stats.total_generated} in {stats.elapsed_seconds:.2f}s, "
        f"actual rate: {stats.rate:.2f}/s"
    )


if __name__ == "__main__":
    main()
