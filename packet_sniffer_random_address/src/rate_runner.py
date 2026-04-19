"""Rate-controlled runner for high-frequency task execution."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class RateRunResult:
    """Execution report for one rate-controlled run."""

    target_rate: int
    duration_seconds: float
    total_operations: int
    actual_rate: float
    overload_windows: int

    def summary(self) -> str:
        return (
            "[runner] "
            f"target={self.target_rate}/s "
            f"actual={self.actual_rate:.0f}/s "
            f"ops={self.total_operations} "
            f"duration={self.duration_seconds:.3f}s "
            f"overload_windows={self.overload_windows}"
        )


def run_with_target_rate(
    task: Callable[[], None],
    target_rate: int,
    duration_seconds: float,
) -> RateRunResult:
    """Run `task` at approximately `target_rate` per second."""
    if target_rate <= 0:
        raise ValueError("target_rate must be > 0")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be > 0")

    run_start = time.perf_counter()
    deadline = run_start + duration_seconds
    total_ops = 0
    window_index = 0
    overload_windows = 0

    while True:
        now = time.perf_counter()
        remaining = deadline - now
        if remaining <= 0:
            break

        window_seconds = 1.0 if remaining >= 1.0 else remaining
        iterations = max(1, int(target_rate * window_seconds))

        window_index += 1
        window_start = time.perf_counter()
        for _ in range(iterations):
            task()
        total_ops += iterations

        work_elapsed = time.perf_counter() - window_start
        sleep_for = window_seconds - work_elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)
        else:
            overload_windows += 1

        print(
            f"[runner] window={window_index} "
            f"target_ops={iterations} "
            f"work_elapsed={work_elapsed:.4f}s "
            f"sleep={max(sleep_for, 0):.4f}s"
        )

    elapsed = time.perf_counter() - run_start
    actual_rate = total_ops / max(elapsed, 1e-9)
    return RateRunResult(
        target_rate=target_rate,
        duration_seconds=elapsed,
        total_operations=total_ops,
        actual_rate=actual_rate,
        overload_windows=overload_windows,
    )
