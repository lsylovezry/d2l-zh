"""Rate control helpers for high-frequency workloads."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class RateRunStats:
    """Execution statistics for a rate-limited run."""

    executed: int
    elapsed_seconds: float
    achieved_per_second: float
    target_per_second: int


def run_at_rate(
    operation: Callable[[], None],
    target_per_second: int,
    duration_seconds: float,
    batch_ms: float = 10.0,
) -> RateRunStats:
    """
    Run operation at approximately target_per_second.

    The loop uses batch execution because 100000/s implies ~10us per call,
    which is too fine-grained for per-operation sleep on standard Linux timers.
    """
    if target_per_second <= 0:
        raise ValueError("target_per_second must be > 0")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be > 0")
    if batch_ms <= 0:
        raise ValueError("batch_ms must be > 0")

    batch_seconds = batch_ms / 1000.0
    batch_size = max(1, int(target_per_second * batch_seconds))

    start = time.perf_counter()
    deadline = start + duration_seconds
    executed = 0

    while True:
        now = time.perf_counter()
        if now >= deadline:
            break

        batch_start = now
        for _ in range(batch_size):
            operation()
        executed += batch_size

        target_batch_cost = batch_size / target_per_second
        elapsed_batch = time.perf_counter() - batch_start
        sleep_for = target_batch_cost - elapsed_batch
        if sleep_for > 0:
            time.sleep(sleep_for)

    elapsed = time.perf_counter() - start
    return RateRunStats(
        executed=executed,
        elapsed_seconds=round(elapsed, 4),
        achieved_per_second=round(executed / elapsed, 2) if elapsed else 0.0,
        target_per_second=target_per_second,
    )

