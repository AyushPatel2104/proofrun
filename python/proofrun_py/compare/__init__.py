"""Compare helpers."""

from __future__ import annotations

from typing import List, Sequence

from proofrun_py.oracles import is_permutation, sort_oracle


def assert_matches_oracle(result: Sequence[int], original: Sequence[int]) -> None:
    expected = sort_oracle(original)
    if list(result) != expected:
        raise AssertionError(f"oracle mismatch: got={list(result)!r} expected={expected!r}")
    if not is_permutation(original, result):
        raise AssertionError("result is not a permutation of input")
