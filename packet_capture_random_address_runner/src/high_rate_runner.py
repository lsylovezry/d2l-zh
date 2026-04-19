"""High-rate random address generation runner."""

from __future__ import annotations

import time
from dataclasses import dataclass

from .random_address_generator import RandomAddressGenerator


@dataclass
class RunResult:
    generated_total: int
    elapsed_seconds: float
    actual_per_second: float
    sample_output: dict[str, str]


class HighRateRunner:
    """Generate random addresses at a target frequency."""

    def __init__(
        self,
        generator: RandomAddressGenerator,
        target_per_second: int = 100_000,
    ) -> None:
        if target_per_second <= 0:
            raise ValueError("target_per_second must be > 0")
        self.generator = generator
        self.target_per_second = target_per_second

    def run_for_duration(self, seconds: int) -> RunResult:
        if seconds <= 0:
            raise ValueError("seconds must be > 0")

        generated_total = 0
        last_bundle = self.generator.random_bundle()
        start = time.perf_counter()

        for _ in range(seconds):
            second_start = time.perf_counter()
            for _ in range(self.target_per_second):
                last_bundle = self.generator.random_bundle()
                generated_total += 1
            spent = time.perf_counter() - second_start
            if spent < 1.0:
                time.sleep(1.0 - spent)

        elapsed = time.perf_counter() - start
        return RunResult(
            generated_total=generated_total,
            elapsed_seconds=elapsed,
            actual_per_second=generated_total / max(elapsed, 1e-9),
            sample_output={
                "ipv4": last_bundle.ipv4,
                "ipv6": last_bundle.ipv6,
                "mac": last_bundle.mac,
            },
        )
