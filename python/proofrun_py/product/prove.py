"""Correctness verification via independent Python oracles."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from proofrun_py.oracles import (
    binary_search_oracle,
    linear_search_oracle,
    max_sum_window_oracle,
    prefix_range_oracle,
    sort_oracle,
    two_sum_sorted_oracle,
)
from proofrun_py.product.validate import ProductRequest


def _parse_sort_stdout(stdout: str) -> List[int]:
    if not stdout:
        return []
    return [int(x) for x in stdout.split(",") if x != ""]


def prove(req: ProductRequest, stdout: str) -> Dict[str, Any]:
    """Return correctness payload. status in PASS | FAIL | NOT_AVAILABLE."""
    aid = req.algorithm_id

    if aid.startswith("sort."):
        actual = _parse_sort_stdout(stdout)
        expected = sort_oracle(req.values)
        ok = actual == expected
        return {
            "status": "PASS" if ok else "FAIL",
            "method": "independent_python_timsort_oracle",
            "expected": expected,
            "actual": actual,
            "detail": (
                "Correctness verification against an independent Python sorted() oracle."
                if ok
                else "Correctness verification failed: output differs from the independent oracle."
            ),
        }

    if aid == "search.linear_search":
        actual = int(stdout)
        expected = linear_search_oracle(req.values, req.target)  # type: ignore[arg-type]
        ok = actual == expected
        return {
            "status": "PASS" if ok else "FAIL",
            "method": "independent_python_index_oracle",
            "expected": expected,
            "actual": actual,
            "detail": "First-index match." if ok else "Index mismatch.",
        }

    if aid == "search.binary_search":
        actual = int(stdout)
        # Presence-based check: C++ may return any matching index on duplicates.
        if actual < 0:
            ok = req.target not in req.values
            expected: Any = -1
        else:
            ok = 0 <= actual < len(req.values) and req.values[actual] == req.target
            expected = binary_search_oracle(req.values, req.target)  # type: ignore[arg-type]
        return {
            "status": "PASS" if ok else "FAIL",
            "method": "independent_python_bisect_presence_check",
            "expected": expected,
            "actual": actual,
            "detail": (
                "Found index refers to target (duplicate index may differ from leftmost oracle)."
                if ok and actual >= 0
                else ("Correct not-found." if ok else "Search result incorrect.")
            ),
        }

    if aid == "array.two_pointer":
        oracle = two_sum_sorted_oracle(req.values, req.target)  # type: ignore[arg-type]
        if stdout == "notfound":
            ok = oracle is None
            actual: Any = None
        else:
            parts = stdout.split(",")
            if len(parts) != 3 or parts[0] != "found":
                return {
                    "status": "FAIL",
                    "method": "independent_bruteforce_pair_oracle",
                    "expected": oracle,
                    "actual": stdout,
                    "detail": "Unexpected engine output.",
                }
            i, j = int(parts[1]), int(parts[2])
            actual = {"left": i, "right": j, "sum": req.values[i] + req.values[j]}
            ok = (
                0 <= i < j < len(req.values)
                and req.values[i] + req.values[j] == req.target
                and oracle is not None
            )
        return {
            "status": "PASS" if ok else "FAIL",
            "method": "independent_bruteforce_pair_oracle",
            "expected": (
                None
                if oracle is None
                else {"left": oracle[0], "right": oracle[1], "sum": req.values[oracle[0]] + req.values[oracle[1]]}
            ),
            "actual": actual,
            "detail": "Pair validity checked against brute-force oracle.",
        }

    if aid == "array.sliding_window":
        parts = stdout.split(",")
        actual_sum, start, end = int(parts[0]), int(parts[1]), int(parts[2])
        exp = max_sum_window_oracle(req.values, req.window)  # type: ignore[arg-type]
        assert exp is not None
        ok = actual_sum == exp[0] and start == exp[1] and end == exp[2]
        return {
            "status": "PASS" if ok else "FAIL",
            "method": "independent_bruteforce_window_oracle",
            "expected": {"maxSum": exp[0], "start": exp[1], "end": exp[2]},
            "actual": {"maxSum": actual_sum, "start": start, "end": end},
            "detail": "Max fixed-window sum matches brute-force scan.",
        }

    if aid == "array.prefix_sum":
        actual = int(stdout)
        expected = prefix_range_oracle(req.values, req.query_left, req.query_right)  # type: ignore[arg-type]
        ok = actual == expected
        return {
            "status": "PASS" if ok else "FAIL",
            "method": "independent_python_sum_oracle",
            "expected": expected,
            "actual": actual,
            "detail": "Range sum matches sum(a[L:R+1]).",
        }

    return {
        "status": "NOT_AVAILABLE",
        "method": None,
        "expected": None,
        "actual": stdout,
        "detail": "No oracle registered for this algorithm.",
    }


def format_result_summary(req: ProductRequest, stdout: str) -> Dict[str, Any]:
    aid = req.algorithm_id
    if aid.startswith("sort."):
        return {"kind": "array", "value": _parse_sort_stdout(stdout)}
    if aid.startswith("search."):
        idx = int(stdout)
        return {"kind": "index", "value": idx, "found": idx >= 0}
    if aid == "array.two_pointer":
        if stdout == "notfound":
            return {"kind": "pair", "found": False}
        parts = stdout.split(",")
        return {"kind": "pair", "found": True, "left": int(parts[1]), "right": int(parts[2])}
    if aid == "array.sliding_window":
        parts = stdout.split(",")
        return {
            "kind": "window",
            "maxSum": int(parts[0]),
            "start": int(parts[1]),
            "end": int(parts[2]),
        }
    if aid == "array.prefix_sum":
        return {"kind": "rangeSum", "value": int(stdout), "left": req.query_left, "right": req.query_right}
    return {"kind": "raw", "value": stdout}
