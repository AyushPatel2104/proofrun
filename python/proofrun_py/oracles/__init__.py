"""Independent algorithm oracles.

Oracles intentionally do NOT reimplement the C++ control flow.
Sorting uses Timsort; searching uses Python membership/bisect;
array techniques use brute-force reference solutions where useful.
"""

from __future__ import annotations

import bisect
from typing import List, Optional, Sequence, Tuple


def sort_oracle(values: Sequence[int]) -> List[int]:
    """Return a new sorted list (ascending)."""
    return sorted(values)


def is_nondecreasing(values: Sequence[int]) -> bool:
    return all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def is_permutation(original: Sequence[int], candidate: Sequence[int]) -> bool:
    return sorted(original) == sorted(candidate)


def linear_search_oracle(values: Sequence[int], target: int) -> int:
    """First index of target, or -1."""
    try:
        return list(values).index(target)
    except ValueError:
        return -1


def binary_search_oracle(values: Sequence[int], target: int) -> int:
    """Index of target in a nondecreasing sequence, or -1.

    Uses bisect_left; if multiple matches, returns the leftmost index
    (C++ may return any matching index — callers should compare by value presence).
    """
    if not is_nondecreasing(values):
        raise ValueError("binary_search_oracle requires nondecreasing input")
    a = list(values)
    i = bisect.bisect_left(a, target)
    if i < len(a) and a[i] == target:
        return i
    return -1


def two_sum_sorted_oracle(values: Sequence[int], target: int) -> Optional[Tuple[int, int]]:
    """Brute-force pair (i, j) with i < j and values[i]+values[j]==target."""
    if not is_nondecreasing(values):
        raise ValueError("two_sum_sorted_oracle requires nondecreasing input")
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            if values[i] + values[j] == target:
                return (i, j)
    return None


def max_sum_window_oracle(values: Sequence[int], k: int) -> Optional[Tuple[int, int, int]]:
    """Return (max_sum, start, end) inclusive, or None if k invalid."""
    n = len(values)
    if k <= 0 or k > n:
        return None
    best_sum = None
    best_i = 0
    for i in range(0, n - k + 1):
        s = sum(values[i : i + k])
        if best_sum is None or s > best_sum:
            best_sum = s
            best_i = i
    assert best_sum is not None
    return (best_sum, best_i, best_i + k - 1)


def prefix_range_oracle(values: Sequence[int], left: int, right: int) -> Optional[int]:
    """Inclusive range sum, or None if invalid indices."""
    n = len(values)
    if left < 0 or right < 0 or left >= n or right >= n or left > right:
        return None
    return sum(values[left : right + 1])
