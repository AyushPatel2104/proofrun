# IMPLEMENTATION-PLAN.md — ProofRun

## 1. Phase Statement

This document plans implementation. **No implementation work is authorized by this file alone.** Spec phase ends when these docs are accepted; coding begins only on explicit go-ahead.

Roadmap project **#01** scope remains unchanged.

---

## 2. Algorithm Taxonomy (Catalog Coverage)

Families to be represented in the catalog over time:

1. Sorting  
2. Searching  
3. Arrays  
4. Strings  
5. Linked Lists  
6. Stacks  
7. Queues  
8. Trees  
9. Graphs  
10. Greedy  
11. Dynamic Programming  
12. Backtracking  
13. Divide and Conquer  
14. Hashing  
15. Heap / Priority Queue  

**Rule:** Taxonomy coverage ≠ immediate implementation of every algorithm.

---

## 3. Algorithm Sets

### 3.1 MVP Algorithm Set (must ship for v0.1)

Chosen for: visual clarity, testability, benchability, and breadth across fundamentals.

| ID | Family | Notes |
| --- | --- | --- |
| `sort.bubblesort` | Sorting | Teaching + viz-friendly (include as baseline, not “best”) |
| `sort.insertionsort` | Sorting | Viz + complexity contrast |
| `sort.mergesort` | Sorting / DaC | Stable divide-and-conquer exemplar |
| `sort.quicksort` | Sorting / DaC | Pivot/partition events; document worst case |
| `sort.heapsort` | Sorting / Heap | Connects heap family |
| `search.binary_search` | Searching | On sorted arrays |
| `array.kadane` | Arrays / Greedy-ish DP edge | Max subarray; clear state |
| `string.kmp_search` | Strings | Prefix table + match events (MVP-lite OK) |
| `list.reverse` | Linked Lists | Pointer viz |
| `stack.valid_parentheses` | Stacks | Classic state machine |
| `queue.bfs_grid_or_list` | Queues | Queue discipline (grid or graph BFS prelude) |
| `tree.bst_insert_traverse` | Trees | Insert + inorder |
| `graph.bfs` | Graphs | Layered exploration |
| `graph.dfs` | Graphs | Recursion/stack events |
| `heap.binary_heap_ops` | Heap | insert/extract-min |
| `hash.chaining_table_ops` | Hashing | insert/lookup with collision viz |
| `dp.fibonacci_tabulation` | DP | Contrast naive recursion notes (naive optional) |
| `dp.knapsack_01_small` | DP | Small N table viz |
| `greedy.activity_selection` | Greedy | Interval selection |
| `backtracking.nqueens_n4` | Backtracking | Bounded N for demo limits |

MVP count is intentionally focused (~20 entries) with full quality bar each.

### 3.2 Phase 2 Algorithm Set

| ID | Family |
| --- | --- |
| `sort.timsort_notes_demo` | Sorting (educational subset / documented behavior) |
| `search.ternary_search` | Searching |
| `array.two_sum_hash` | Arrays / Hashing |
| `array.rotate_in_place` | Arrays |
| `string.rabin_karp` | Strings |
| `string.z_algorithm` | Strings |
| `list.detect_cycle_floyd` | Linked Lists |
| `list.merge_sorted` | Linked Lists |
| `tree.avl_insert` | Trees |
| `tree.lowest_common_ancestor` | Trees |
| `graph.dijkstra` | Graphs |
| `graph.topological_sort_kahn` | Graphs |
| `graph.union_find` | Graphs |
| `dp.lcs` | DP |
| `dp.edit_distance` | DP |
| `greedy.huffman_demo` | Greedy |
| `backtracking.sudoku_small` | Backtracking |
| `dac.closest_pair_notes` | Divide and Conquer |

### 3.3 Phase 3 / Expansion Set

| ID | Family |
| --- | --- |
| `graph.bellman_ford` | Graphs |
| `graph.floyd_warshall` | Graphs |
| `graph.mst_kruskal_prim` | Graphs |
| `tree.segment_tree_range` | Trees |
| `tree.fenwick` | Trees |
| `string.suffix_array_lite` | Strings |
| `dp.digit_dp_intro` | DP |
| `geometry.ccw_convex_hull_graham` | Expansion |
| `parallel.note_only` | Docs-only until later portfolio systems work |
| Additional catalog entries as needed | All families |

---

## 4. Workstreams (Implementation Order When Authorized)

### Wave 0 — Skeleton (no algorithms yet)

1. Create folder tree from `FOLDER-STRUCTURE.md`
2. CMake hello library + one Catch2/GoogleTest smoke test
3. Python package skeleton + pytest smoke
4. Schema files + TS/JS validator stub
5. Bash `test_all.sh` / `bench_smoke.sh` stubs
6. Docs stubs + complexity table skeleton
7. Choose test framework (Catch2 **xor** GoogleTest) and record in README

### Wave 1 — Contracts + Generators

1. Finalize JSON schemas
2. Algorithm manifest format
3. Seeded generators for arrays/strings/graphs
4. Report schema + empty report renderer

### Wave 2 — MVP Core Algorithms (non-viz first)

Priority order:

1. Sorting family (bubble, insertion, merge, quick, heap)
2. Binary search + heap ops + hash ops
3. Stack/queue/list fundamentals
4. Graph BFS/DFS
5. Tree BST basics
6. DP/greedy/backtracking bounded demos

For each: C++ impl → Python oracle → tests → bench definition → complexity notes.

### Wave 3 — Tracing + Visualization

1. C++/Python trace emission for visualizable MVP subset
2. JS player + array/graph/tree renderers
3. Canned traces for Pages demo
4. Inspector + timeline + complexity panel wiring

### Wave 4 — Benchmark Honesty Pack

1. Warmup/repeats/median/p95
2. Scaling sweeps
3. Memory best-effort path on C++
4. Example reports committed under `docs/reports/examples/`

### Wave 5 — CI + Public Demo Prep

1. GitHub Actions (when Git authorized)
2. Static site assembly
3. Screenshots + security/limits pages
4. Definition-of-done audit

---

## 5. Per-Algorithm Implementation Checklist

For each implemented algorithm:

- [ ] C++ API + implementation
- [ ] Python oracle (or justified shared-spec equivalence)
- [ ] Correctness tests
- [ ] Edge-case tests
- [ ] Property tests where applicable
- [ ] Complexity documentation in manifest
- [ ] Benchmark definition (sizes/seeds/metrics)
- [ ] Seeded input generation profile
- [ ] Visualization state/event model **if visualizable**
- [ ] Catalog entry + docs blurb

---

## 6. Definition of Done (Project #01 v0.1)

v0.1 is done when:

1. MVP algorithm set implemented with the checklist above (viz required for the visualizable majority; document any deferred viz explicitly).
2. C++ builds via CMake; tests green.
3. Python tests green including property tests for sorting/searching at minimum.
4. Bench smoke reproducible via Bash script; example report published in docs.
5. JS viz demos work for at least: one sorting algo, BFS or DFS, BST insert, binary heap ops.
6. `SECURITY.md` limits enforced in CLI/demo input paths.
7. README meets GitHub standard (see `README-DRAFT.md`).
8. No public arbitrary native code execution.
9. Deployment class satisfied as **ready** for PUBLIC DEMO (actual deploy may be a separate authorization).

---

## 7. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Scope explosion across 15 families | Delays | Hard MVP list; taxonomy ≠ implementation |
| Misleading benchmarks | Credibility loss | Warmup, repeats, median/p95, env metadata, caveats |
| Viz becomes hardcoded animations | Weak architecture | Mandatory event model (`VISUALIZATION-SPEC.md`) |
| pybind11 complexity early | Slowdown | CLI/JSON bridge for MVP |
| Memory measurement portability | Incomplete metrics | Mark memory as best-effort; document platform notes |
| Public demo abuse | Security | Canned traces, input caps, no user native exec |
| Dual test framework temptation | Inconsistency | Pick Catch2 **or** GoogleTest once |
| WASM effort overrun | Demo delay | Ship JS+canned traces first; WASM optional enhancement |

---

## 8. Explicit Non-Work in Spec Phase

- No source files under `cpp/`, `python/`, `viz/`, `tools/`
- No dependency installs
- No Git init
- No deployment
- No master roadmap edits
