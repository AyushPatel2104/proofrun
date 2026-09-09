# Sliding Window — Maximum Sum of Fixed Length K

## Problem solved

Find a contiguous subarray of length exactly `K` with the maximum sum (and its start/end indices).

## Window state / invariant

Maintain the sum of `a[start..end]` where `end - start + 1 == K`. Sliding right by one: add `a[end+1]`, subtract `a[start]`, then `start++`.

Invariant: after each slide, `windowSum` equals the sum of the current length-`K` segment; `maxSum` is the best sum observed so far.

## Complexity

- Time: O(n) after O(K) to build the first window (overall O(n))
- Extra space: O(1)

Brute-force oracle recomputes every window sum to catch off-by-one contraction bugs.

## Trace / visualization

Shows expand (include right) and contract (drop left) with `i`/`j` as window ends; updates when the max improves.

## Benchmark

`BM_SlidingWindow` with `K = max(1, n/8)` on seeded random arrays.

## Limitations

Fixed `K` only (variable windows / constraint windows are a later technique). Invalid when `K <= 0` or `K > n`.
