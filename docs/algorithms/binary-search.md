# Binary Search

## Problem

Locate a target in a **nondecreasing** array, returning some matching index or `-1`.

## Intended user

Someone validating the classic “discard half the search space” idea against real comparison counts and against linear search scaling.

## Algorithm idea

Maintain inclusive bounds `low`/`high`. Compare `a[mid]` to the target; discard the half that cannot contain it.

## Invariant / precondition

**Precondition (enforced by CLI):** input must be sorted ascending (`a[i] <= a[i+1]`).  
Invariant: if the target exists, it lies in `a[low..high]` while the loop runs.

When duplicates exist, any matching index is acceptable (documented). Python’s oracle uses leftmost via `bisect_left`; cross-checks assert value equality / presence rather than identical indices.

## Complexity

- Time: O(log n)
- Extra space: O(1)

## Benchmark methodology

`BM_BinarySearch` sorts a seeded random buffer then searches a present mid-element. Compare scaling to `BM_LinearSearch` on the same size ladder (256–16384). Do not generalize one machine’s timings.

## Visualization

Events expose `low`/`mid`/`high` (mapped to highlights `i`/`index`/`j`).

## Limitations

Wrong answers if input is unsorted — CLI refuses unsorted input rather than silently searching.
