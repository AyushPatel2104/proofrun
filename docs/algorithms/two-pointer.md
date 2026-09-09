# Two Pointer — Two Sum on a Sorted Array

## Problem solved

Given a nondecreasing array and a target sum, find indices `i < j` such that `a[i] + a[j] == target`, or report that no such pair exists.

This is the classic workflow where two pointers replace an O(n²) nested scan.

## Why two pointers applies

On a sorted array, the sum of the extreme pair is monotonic in the pointer moves: too small → advance left; too large → retreat right. Each step shrinks the candidate interval, so at most O(n) comparisons.

## Invariant

While `left < right`, any feasible pair still in play lies in `a[left..right]` under the sorted-sum argument above.

**Precondition:** nondecreasing input (CLI enforced).

## Complexity

- Time: O(n)
- Extra space: O(1)

Oracle uses brute-force O(n²) pairs so an intentionally broken pointer walk fails the bridge tests.

## Trace / visualization

Highlights `i`/`j` as left/right; `compare` shows current sum vs target; movement events update pointers.

## Benchmark

`BM_TwoSumSorted` on sorted seeded inputs; target = first + last (pair exists).

## Limitations

Does not apply unchanged to unsorted arrays (hashing would be a different algorithm — out of scope for this slice).
