"""Fix controlled measure to time a single trusted invocation per sample."""

from __future__ import annotations

import os
import platform
import statistics
import time
from typing import Any, Dict, List

from proofrun_py.product.adapter import run_trusted
from proofrun_py.product.limits import (
    DEFAULT_BENCHMARK_REPEATS,
    DEFAULT_BENCHMARK_WARMUP,
    MAX_BENCHMARK_N,
    MAX_BENCHMARK_REPEATS,
)
from proofrun_py.product.validate import ProductRequest, ValidationError


def environment_info() -> Dict[str, Any]:
    return {
        "os": platform.platform(),
        "arch": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }


def controlled_measure(
    req: ProductRequest,
    *,
    warmup: int = DEFAULT_BENCHMARK_WARMUP,
    repeats: int = DEFAULT_BENCHMARK_REPEATS,
) -> Dict[str, Any]:
    if repeats < 1 or repeats > MAX_BENCHMARK_REPEATS:
        raise ValidationError(f"repeats must be in 1..{MAX_BENCHMARK_REPEATS}")
    if warmup < 0 or warmup > MAX_BENCHMARK_REPEATS:
        raise ValidationError("invalid warmup")
    if len(req.values) > MAX_BENCHMARK_N:
        raise ValidationError(f"controlled measure input capped at n≤{MAX_BENCHMARK_N}")

    times: List[float] = []
    for i in range(warmup + repeats):
        t0 = time.perf_counter()
        run_trusted(req, with_trace=False)
        elapsed = time.perf_counter() - t0
        if i >= warmup:
            times.append(elapsed)

    return {
        "kind": "controlled_process_repeats",
        "disclaimer": (
            "This is a controlled local measurement with process spawn overhead. "
            "It is NOT equivalent to in-process Google Benchmark microbenchmarks. "
            "Do not treat results as universal performance truth."
        ),
        "n": len(req.values),
        "warmup": warmup,
        "repeats": repeats,
        "runtime_s_median": statistics.median(times),
        "runtime_s_min": min(times),
        "runtime_s_max": max(times),
        "runtime_s_p95": sorted(times)[max(0, int(0.95 * (len(times) - 1)))],
        "memory_bytes": None,
        "environment": environment_info(),
    }
