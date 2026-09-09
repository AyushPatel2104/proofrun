# Prefix Sum — Range Sum Queries

## Problem solved

Answer inclusive range sums `sum(a[L..R])` efficiently after a linear preprocess.

## Preprocessing

Build `prefix[0] = 0`, `prefix[i] = a[0] + ... + a[i-1]` for `i = 1..n`.

## Query workflow

`sum(a[L..R]) = prefix[R+1] - prefix[L]` in O(1), after O(n) build.

## Complexity

- Build: O(n) time, O(n) extra space
- Query: O(1) time

This slice’s CLI performs one build + one query per invocation (representative workflow).

## Trace / visualization

Accumulation events rewrite the visualized array to the growing prefix table; the query highlights `[L,R]` and reports the sum. Demo traces use small integers so bars remain meaningful.

## Benchmark

`BM_PrefixRange` builds prefixes and queries the full range `[0, n-1]` (stresses the O(n) build).

## Limitations

Does not yet batch many queries in one CLI call. Overflow: sums use 64-bit accumulators in C++; viz bars cast to `int` for small demos only. Memory metric fields remain null.
