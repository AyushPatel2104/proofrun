"""Map engine/CLI failures to user-safe messages (no paths/stack traces)."""

from __future__ import annotations

import re


_PATH_RE = re.compile(r"([A-Za-z]:\\|/)[^\s\"']+")


def sanitize_user_error(raw: str) -> str:
    """Strip filesystem paths and collapse noisy engine text."""
    text = (raw or "").strip()
    if not text:
        return (
            "The algorithm could not finish.\n"
            "Why: the engine returned an empty error.\n"
            "Fix: check your input and try Generate Input, then Run again."
        )
    text = _PATH_RE.sub("<path>", text)
    lower = text.lower()

    mappings = [
        (
            "nondecreasing",
            "Input must be sorted ascending.\n"
            "Why: Binary Search / Two Pointer only work on nondecreasing arrays.\n"
            "Fix: sort the array first, or use Generate → sorted, then Run.",
        ),
        (
            "requires --target",
            "A target value is required.\n"
            "Why: search and two-pointer need a value to look for.\n"
            "Fix: enter Target in the parameter fields.",
        ),
        (
            "requires --window",
            "Window size K is required.\n"
            "Why: Sliding Window needs a fixed window length.\n"
            "Fix: enter K with 1 ≤ K ≤ array length.",
        ),
        (
            "requires --query",
            "Range L and R are required.\n"
            "Why: Prefix Sum answers a range query.\n"
            "Fix: enter inclusive indices 0 ≤ L ≤ R < n.",
        ),
        (
            "invalid window",
            "Window size K is invalid.\n"
            "Why: K must satisfy 1 ≤ K ≤ array length.\n"
            "Fix: lower K or lengthen the array.",
        ),
        (
            "invalid query",
            "Query range [L, R] is invalid.\n"
            "Why: indices must satisfy 0 ≤ L ≤ R < n.\n"
            "Fix: adjust L and R for your array length.",
        ),
        (
            "unknown algorithm",
            "That algorithm is not supported.\n"
            "Why: only catalog algorithms can run.\n"
            "Fix: choose an algorithm from the dropdown.",
        ),
        (
            "not implemented",
            "That algorithm is not available in this build.\n"
            "Why: it is not marked implemented in the catalog.\n"
            "Fix: choose another algorithm from the list.",
        ),
        (
            "exceeds",
            "Input is too large.\n"
            "Why: visualization runs are capped for safety.\n"
            "Fix: use at most 64 elements (or Generate with a smaller n).",
        ),
        (
            "refusing n>",
            "Input is too large for a traced run.\n"
            "Why: live visualization caps array length at 64.\n"
            "Fix: shorten the input, then Run again.",
        ),
        (
            "failed to write trace",
            "Could not produce an execution trace.\n"
            "Why: the engine failed while recording steps.\n"
            "Fix: retry Run; if it persists, rebuild the C++ engine.",
        ),
        (
            "timed out",
            "The run timed out.\n"
            "Why: execution exceeded the safety limit.\n"
            "Fix: use a smaller input and try again.",
        ),
    ]
    for needle, msg in mappings:
        if needle in lower:
            return msg

    # Generic safe wrapper — do not forward raw internals.
    return (
        "Something went wrong while running the algorithm.\n"
        "Why: the trusted engine rejected the request or failed to complete.\n"
        "Fix: verify input and parameters, then try Generate Input and Run again."
    )
