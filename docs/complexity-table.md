# Complexity table

Empirical timings are environment-local; see benchmark docs. Memory metrics remain null unless otherwise stated.

## Sorting

| Algorithm ID | Best | Average | Worst | Memory |
| --- | --- | --- | --- | --- |
| sort.bubblesort | O(n) | O(n^2) | O(n^2) | O(1) |
| sort.insertionsort | O(n) | O(n^2) | O(n^2) | O(1) |
| sort.selectionsort | O(n^2) | O(n^2) | O(n^2) | O(1) |
| sort.mergesort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| sort.quicksort | O(n log n) | O(n log n) | O(n^2) | O(log n) |

## Searching

| Algorithm ID | Best | Average | Worst | Memory | Notes |
| --- | --- | --- | --- | --- | --- |
| search.linear_search | O(1) | O(n) | O(n) | O(1) | Unsorted OK |
| search.binary_search | O(1) | O(log n) | O(log n) | O(1) | Requires nondecreasing input |

## Arrays

| Algorithm ID | Best | Average | Worst | Memory | Workflow |
| --- | --- | --- | --- | --- | --- |
| array.two_pointer | O(1) | O(n) | O(n) | O(1) | Two-sum on sorted array |
| array.sliding_window | O(n) | O(n) | O(n) | O(1) | Max sum of fixed window K |
| array.prefix_sum | O(n) | O(n) | O(n) | O(n) | Build + O(1) range query |
