# ProofRun Smoke Benchmark Summary

**Example benchmark environment** (sanitized for public docs).

Illustrative smoke timings from a single anonymous development machine. Not a universal performance claim. Usernames, absolute paths, and unique CPU model strings removed.

Profile: `smoke`

Smoke timings include process spawn overhead and are not comparable to in-process Google Benchmark results. Use proofrun_sort_bench / proofrun_search_array_bench for microbenchmarks. Committed example environment is sanitized for public publication.

| Algorithm | n | median_s | p95_s |
| --- | ---: | ---: | ---: |
| sort.bubblesort | 32 | 0.027565 | 0.027736 |
| sort.bubblesort | 64 | 0.032814 | 0.033004 |
| sort.insertionsort | 32 | 0.031469 | 0.031712 |
| sort.insertionsort | 64 | 0.027389 | 0.027617 |
| sort.selectionsort | 32 | 0.026470 | 0.026504 |
| sort.selectionsort | 64 | 0.029307 | 0.029622 |
| sort.mergesort | 32 | 0.022406 | 0.026225 |
| sort.mergesort | 64 | 0.014840 | 0.016527 |
| sort.quicksort | 32 | 0.017110 | 0.019365 |
| sort.quicksort | 64 | 0.010888 | 0.010987 |
| search.linear_search | 32 | 0.012406 | 0.013760 |
| search.linear_search | 64 | 0.013659 | 0.014146 |
| search.binary_search | 32 | 0.012906 | 0.013419 |
| search.binary_search | 64 | 0.013533 | 0.013880 |
| array.two_pointer | 32 | 0.015258 | 0.018128 |
| array.two_pointer | 64 | 0.020351 | 0.021078 |
| array.sliding_window | 32 | 0.017927 | 0.020330 |
| array.sliding_window | 64 | 0.017570 | 0.019116 |
| array.prefix_sum | 32 | 0.023557 | 0.025288 |
| array.prefix_sum | 64 | 0.012058 | 0.012873 |
