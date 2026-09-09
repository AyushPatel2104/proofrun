# Linear Search

## Problem

Find the first index of a target value in an unordered array of integers, or report that it is absent (`-1`).

## Intended user

A developer or learner who needs to connect a sequential scan (what they write first) with measured cost and a visible comparison trail.

## Algorithm idea

Walk indices `0 .. n-1`. At each index, compare `a[i]` to the target. Stop at the first equality.

## Invariant / precondition

No ordering precondition. Correctness: if the function returns `i >= 0`, then `a[i] == target` and no earlier index matches; if `-1`, target is absent.

## Complexity

- Time: best O(1), average/worst O(n)
- Extra space: O(1)

## Benchmark methodology

Google Benchmark `BM_LinearSearch` with deterministic PRNG inputs (seed 42), sizes 256–16384, target present at the last element of the generated buffer. Python smoke harness times CLI process spawn separately.

## Visualization

Each comparison highlights index `i`. Completion records found/not-found.

## Limitations

Does not exploit sorted structure. Not competitive with binary search on large sorted inputs.
