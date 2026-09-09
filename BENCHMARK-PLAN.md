# BENCHMARK-PLAN.md — ProofRun

## 1. Purpose

Provide **reproducible**, **honest**, and **interpretable** performance evidence that connects algorithmic claims to empirical behavior.

Benchmarks must never be marketing theater.

---

## 2. Design Principles

1. **Fixed seeds** for generated inputs.
2. **Controlled input sizes** declared in a bench profile.
3. **Warm-up** where timers/JIT/caches would otherwise distort first runs (document per language).
4. **Repeated runs** with aggregation.
5. Report **median** and **p95** where meaningful (also mean optional, clearly labeled).
6. Capture **runtime**; **throughput** where meaningful (e.g., elements/sec).
7. Capture **memory where measurable** (best-effort; never fake precision).
8. Record **environment metadata**.
9. Record **algorithm version / commit metadata** when Git exists.
10. Record **machine/runtime metadata**.
11. Separate **smoke benches** (CI) from **full profiles** (manual/nightly).

---

## 3. Metrics

| Metric | Definition | Notes |
| --- | --- | --- |
| `runtime_ns` / `runtime_ms` | Wall time of measured region | Prefer steady-clock |
| `throughput` | elements or ops / second | Only if well-defined |
| `memory_bytes` | Peak RSS or allocator stats | Platform-dependent; label method |
| `correctness_gate` | bool | Bench invalid if output fails check |

---

## 4. Aggregation

For each (algorithm, size, seed-set):

- runs: N (MVP default 11 after warmup, adjustable)
- warmup: W (MVP default 2–5)
- aggregate: median, p95, min, max
- discard policy: none initially (document outliers; don’t silently drop)

---

## 5. Bench Profiles

### 5.1 `smoke` (CI)

- Tiny sizes only
- 1–3 seeds
- Strict time budget (e.g., < 60–120s total job slice)
- Produces schema-valid report
- Fails CI only on crash/timeout/schema/correctness_gate

### 5.2 `mvp_scaling`

Example sizes (tune per algorithm family):

| Family | Sizes (illustrative) |
| --- | --- |
| Sorting | 1e3, 5e3, 1e4, 5e4 (cap per security limits) |
| Graphs | n=100/500/1000, m proportional |
| DP tables | small grid sizes suitable for demo honesty |

### 5.3 `compare_cpp_python`

- Same seeds/sizes
- Clear caveat: Python is reference/oracle; not an apples-to-apples optimizer claim
- Present as “engineering contrast,” not “C++ always wins” slogan without context

---

## 6. Environment Metadata (Required Fields)

```json
{
  "timestamp_utc": "...",
  "git_commit": "...|unknown",
  "git_dirty": true,
  "algorithm_ids": ["sort.mergesort"],
  "profile": "mvp_scaling",
  "os": "...",
  "arch": "...",
  "cpu_model": "...",
  "cpu_count": 0,
  "memory_total_bytes": 0,
  "compiler": "g++/clang version...",
  "cpp_build_type": "Release",
  "python_version": "...",
  "benchmark_tooling_versions": {},
  "notes": "caveats..."
}
```

---

## 7. Report Format

`BenchReport` JSON + rendered Markdown/HTML including:

- profile name
- per-algorithm tables (size × median/p95)
- scaling notes
- methodology short blurb
- caveats (power mode, thermal throttling, CI shared runners, etc.)

Example reports live under `docs/reports/examples/` once generated in impl phase.

---

## 8. Runner Topology

```text
scripts/bench_smoke.sh
  → python -m proofrun_py.harness --profile smoke
      → builds/invokes cpp bench targets
      → writes reports/*.json
      → optional markdown render
```

C++ microbenchmarks remain the primary precise timer path; Python harness orchestrates matrix + reporting.

---

## 9. Avoiding Misleading Claims

Forbidden without rigorous controls:

- Quoting single-run timings as truth
- Comparing Debug vs Release without labeling
- Cross-language “winner” claims without methodology
- Claiming Big-O proof from a few points (may show empirical slope **hints** only)
- Silent omission of failures

Allowed:

- Empirical scaling plots with caveats
- Relative comparisons under identical profiles
- Complexity documentation as theory + measured behavior commentary

---

## 10. Memory Measurement Policy

| Priority | Method |
| --- | --- |
| 1 | C++ custom allocator counters around bench region (if implemented) |
| 2 | OS RSS sampling (document inaccuracy) |
| 3 | Omit memory metric rather than invent it |

---

## 11. Definition of Done (Benchmark Subsystem)

- Profiles `smoke` and `mvp_scaling` documented and runnable (impl phase)
- Reports schema-validated
- At least one example report committed for portfolio evidence
- README section explains reproduction steps exactly
