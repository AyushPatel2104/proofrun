# Benchmark reproduction

## Measurement modes

| Mode | Tool | Notes |
| --- | --- | --- |
| Interactive runtime | Product UI `/api/run` | Single wall clock; includes process start. Not a rigorous benchmark. |
| Controlled product measure | Product UI `/api/benchmark` or harness | Warmup + repeats; still process-level. |
| Smoke harness | `scripts/bench_smoke.sh` | Small `n`, seeded inputs; spawn overhead dominates. |
| Google Benchmark | `proofrun_sort_bench`, `proofrun_search_array_bench` | Prefer for algorithm microbenchmarks. |

## Microbenchmarks (preferred timers)

```bash
cmake -S cpp -B build/cpp -DCMAKE_BUILD_TYPE=Release
cmake --build build/cpp --config Release
./build/cpp/proofrun_sort_bench --benchmark_filter=BM_
./build/cpp/proofrun_search_array_bench --benchmark_filter=BM_
```

Use Release builds. Document filter, sizes, and machine class when comparing.

## Smoke harness (process-level)

```bash
export PYTHONPATH=python
export PROOFRUN_CLI=$PWD/build/cpp/proofrun_cli
./scripts/bench_smoke.sh
```

Typical smoke sizes: `n ∈ {32, 64}` with deterministic seeds. Warmup and repeat counts are recorded in the JSON report.

Outputs (local/CI — gitignored under `reports/`):

- `reports/smoke-bench-report.json`
- `reports/smoke-bench-report.md`

Committed public examples (sanitized; not overwritten by smoke script):

- `docs/reports/examples/smoke-bench-report.json`
- `docs/reports/examples/smoke-bench-report.md`

Committed examples carry `environment.label = "Example benchmark environment"` with personal paths/usernames/CPU model strings removed.

## Honesty notes

- Do not treat CI shared-runner or smoke timings as universal truth.
- Compare only under identical profiles and build types (Release).
- Python smoke timings are not comparable to Google Benchmark medians.
- Environment metadata is for reproducibility context, not ranking.

## Memory metrics

**Current status:** `memory_bytes` is intentionally `null` in smoke/product reports.

**Why:** A trustworthy, cross-platform peak-memory measurement is not implemented. Fabricating values would violate the quality bar.

**Distinction:**

- **Runtime benchmarking** is supported (interactive / controlled / gbench).
- **Memory profiling** is deferred until a method can be documented and tested without misleading precision.
