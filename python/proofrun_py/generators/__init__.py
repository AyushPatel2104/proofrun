"""Seeded deterministic array generators."""

from __future__ import annotations

import random
from typing import List


def generate_array(kind: str, n: int, seed: int) -> List[int]:
    rng = random.Random(seed)
    if kind == "empty":
        return []
    if kind == "single":
        return [rng.randint(-50, 50)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "duplicates":
        return [rng.choice([0, 1, 2, 3]) for _ in range(n)]
    if kind == "negatives":
        return [rng.randint(-100, 100) for _ in range(n)]
    if kind == "random":
        return [rng.randint(-10_000, 10_000) for _ in range(n)]
    raise ValueError(f"unknown kind: {kind}")
