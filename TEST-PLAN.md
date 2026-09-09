# TEST-PLAN.md — ProofRun

## 1. Goals

Prove that ProofRun algorithms are **correct**, **edge-safe**, and **stable under generated inputs**, with evidence suitable for CI and portfolio review.

Testing is a first-class subsystem, not an afterthought.

---

## 2. Test Layers

| Layer | Owner | Purpose |
| --- | --- | --- |
| L1 Unit | C++ | Function-level correctness |
| L2 Edge | C++ + Python | Empty, single-element, duplicates, overflow-prone sizes (within limits), disconnected graphs, etc. |
| L3 Oracle Cross-Check | Python vs C++ | Semantic equivalence on shared fixtures |
| L4 Property-Based | Python (Hypothesis or equivalent) | Invariants across random seeded inputs |
| L5 Trace Validity | TS/JS tooling + Python | `ExecutionTrace` schema + monotonic steps |
| L6 Bench Smoke | Bash + harness | Runner starts, produces report schema, finishes under time cap |
| L7 Docs/Contract | CI | Manifest completeness for implemented algorithms |

---

## 3. Correctness Strategy

### 3.1 Oracle model

- Python reference implementations define expected behavior for MVP algorithms.
- C++ outputs must match oracles on fixtures and property draws (within documented equivalence rules).

### 3.2 Equivalence rules (examples)

| Algorithm family | Equivalence |
| --- | --- |
| Sorting | Output sequence equal; stability checked only for algorithms claiming stability |
| Searching | Index or “not found” sentinel consistent; document first/any match policy |
| Graphs BFS/DFS | Visit order may vary if ties exist — compare reachable sets / parent tree properties unless order is specified |
| Hash table | Lookup semantics; iteration order not required stable |

Document per-algorithm equivalence in the manifest.

---

## 4. Property-Based Testing (Selected)

Minimum MVP properties:

| Algorithm | Properties |
| --- | --- |
| All sorts | Output is sorted permutation of input |
| Binary search | If found, `a[i] == target`; if not, target absent |
| Stack valid parentheses | Random bracket strings match oracle |
| Heap ops | After ops, extract order non-decreasing for min-heap |
| BFS | Distance layers non-decreasing from source on unweighted graphs |
| Union of sorting props | Idempotence of sorting: sort(sort(x)) == sort(x) |

Property tests must use **bounded sizes** respecting `SECURITY.md` limits.

---

## 5. Edge-Case Catalog (Representative)

- Empty inputs
- Single element
- Already sorted / reverse sorted
- All equal elements
- Maximum allowed N
- Sparse vs dense graphs
- Disconnected graphs
- Negative numbers (where type allows)
- Unicode edge cases for strings (document supported subset; MVP may be ASCII-first)

---

## 6. Trace / Visualization Tests

For each visualizable MVP algorithm with traces:

- Schema validation passes
- `step` strictly increasing by 1 (or documented compacting rules)
- Final state matches oracle output
- Event types belong to allowed vocabulary for that renderer
- Trace size under demo caps

---

## 7. CI Validation Plan (When Git Authorized)

PR pipeline:

1. Configure + build C++
2. Run C++ tests
3. Run Python pytest (unit + property)
4. Validate schemas against fixtures
5. Run `bench_smoke.sh` (short, capped)
6. Fail if manifests missing for implemented algorithms

Nightly (optional later): broader property draws + larger bench matrix (still honest, still capped).

---

## 8. Test Evidence Artifacts

| Artifact | Location (future) |
| --- | --- |
| C++ test logs | CI |
| Pytest reports | CI |
| Counterexamples on failure | `reports/failures/` (gitignored) |
| Golden fixtures | `datasets/fixtures/` |
| Trace fixtures | `viz/public/traces/` + `datasets/fixtures/traces/` |

---

## 9. Coverage Expectations (Practical)

- Aim for meaningful coverage of core libraries; do not chase vanity 100%.
- Every MVP algorithm must have at least: 1 happy-path, 3 edges, 1 oracle cross-check profile, and property coverage where listed.

---

## 10. Out of Scope for Tests

- Performance SLOs as hard CI fails (use smoke only; full benches are informational unless flaking is proven)
- Executing untrusted user-provided native code
- Full browser e2e in MVP (optional later with Playwright); manual viz checklist acceptable for v0.1
