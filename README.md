# ProofRun

**Algorithm Verification & Performance Intelligence Platform**

> See the algorithm. Prove the result. Measure the run.

## What is ProofRun?

ProofRun is a **local-first, open-source developer tool** for algorithm **execution visualization**, **correctness verification**, and **performance measurement**.

You select a trusted catalog algorithm, supply validated input, run it through a C++ engine, watch a real ExecutionTrace, compare the result to an independent oracle, and measure runtime with honest labels.

**Live execution runs on your machine** at `http://127.0.0.1:8080/`. That is intentional: the trusted engine stays local so arbitrary native code is never exposed over the public internet.

Version: **0.1.0** · License: **MIT** · **No account / login required**

## Why does it exist?

Correctness, step-by-step behavior, and empirical performance are usually taught or checked separately. That gap hides bugs: wrong preconditions, misunderstood control flow, or timings that include process noise mistaken for “algorithm speed.”

## Who is it for?

- Developers validating implementations and regressions  
- Learners connecting steps ↔ result ↔ cost  
- Educators demonstrating reproducible algorithm runs  

## SEE / PROVE / MEASURE

| Pillar | Meaning in ProofRun |
| --- | --- |
| **SEE** | Real engine events → vanilla JS player (Play / Pause / Step / Reset) |
| **PROVE** | Independent oracle check → PASS / FAIL / NOT_AVAILABLE (not a formal mathematical proof) |
| **MEASURE** | Interactive wall time vs optional controlled repeats; separate from Google Benchmark microbenchmarks |

## Supported algorithms (10)

| Family | Algorithms |
| --- | --- |
| Sorting | Bubble, Insertion, Selection, Merge, Quick |
| Searching | Linear, Binary (sorted input required) |
| Arrays | Two Pointer (sorted two-sum), Sliding Window (max sum fixed K), Prefix Sum (range query) |

## Architecture

```text
UI / API request
  → validation (catalog + limits + preconditions)
  → trusted proofrun_cli (fixed binary)
  → C++ algorithm
  → ExecutionTrace JSON
  → SEE (player) + PROVE (oracle) + MEASURE (timings)
```

Users never supply native code or executable paths. Details: `docs/product-architecture.md`, `docs/architecture.md`, `SECURITY.md`.

Local-first execution is a **security and architecture choice**, not a temporary stub. A future static GitHub Pages demo (canned-trace replay) or free online execution backend would be separate decisions and are **not** the same as this repository’s live Python/C++ product server.

**Publishing note:** ProofRun is developed inside a portfolio workspace but ships as a **standalone** public repository (`proofrun/`). CI and scripts are rooted at this project directory — not a parent portfolio path. See `docs/github-metadata.md`.

## How do I run it locally?

```bash
# Build C++ engine
./scripts/build_cpp.sh                 # Linux/macOS
# Windows: powershell -File scripts/build_cpp.ps1

# Product UI (Select → Input → Run → See → Prove → Measure)
./scripts/run_product.sh               # or scripts/run_product.ps1
# Open http://127.0.0.1:8080/
```

Prerequisites and details: `docs/setup.md`.

There is **no signup**. Open the local URL and use the workspace.

## How do I test it?

| Layer | Tooling |
| --- | --- |
| C++ | GoogleTest |
| Python | pytest |
| Property-based | Hypothesis |
| Schemas / traces | JSON Schema + `scripts/validate_schemas.sh` |
| Catalog drift | `scripts/generate_catalog_artifacts.py --check` |
| Product workflow | `python/tests/test_product/` |
| Visualization contract | `scripts/verify_viz_contract.py` |
| TypeScript contracts | `tools/` (`npm run validate`) |

```bash
./scripts/test_all.sh
```

Expect: CTest and pytest exit 0. Local suites currently report on the order of **77** GoogleTest cases and **91** pytest cases; counts evolve with the tree.

## How do benchmarks work?

Three distinct measurement modes:

| Mode | What it is | Use for |
| --- | --- | --- |
| Interactive runtime | Single Run wall time (includes process start) | Quick feedback in the UI |
| Controlled product benchmark | Warmup + repeats via trusted CLI | Local comparison with disclaimers |
| Google Benchmark | In-process microbenchmarks | Prefer for algorithm-level timing |

Controlled/smoke runs use deterministic seeds and documented sizes (e.g. smoke `n ∈ {32,64}`). Reports may include environment metadata. Committed examples are **sanitized** and labeled as an *example benchmark environment* — not a claim of universal ranking.

Reproduction: `docs/benchmark-reproduction.md` · smoke: `./scripts/bench_smoke.sh`

**Memory:** `memory_bytes` remains `null` until a trustworthy cross-platform method exists.

## What are the security limitations?

- Catalog algorithms only  
- Validated inputs and hard size caps for traced runs  
- Fixed `proofrun_cli` basename; no user-controlled executable paths  
- `shell=False` process invocation; no secrets or API keys required  
- Live engine is **local** — not exposed as a public multi-tenant execution API  

See `SECURITY.md` and `docs/security-and-limits.md`.

## What are the current limitations?

- Live Run requires a built CLI + local product server (`127.0.0.1:8080`)  
- Interactive / smoke timings include process overhead  
- Not a multi-tenant SaaS; no accounts, cloud workspaces, or hosted execution in this release  
- GitHub Pages (if added later) would replay **canned traces only** — it is **not** the live Python execution environment  

## What is the future roadmap?

| Status | Scope |
| --- | --- |
| Done | Sorting + searching + array techniques (10 workflows), product shell, tests, benches |
| Next (authorized separately) | Additional algorithm families (e.g. trees/graphs) when scoped |
| Later | Optional static public demo; optional free/secure online execution only if it stays reliable and never exposes arbitrary native code |

Portfolio master roadmap remains external and locked; this list is ProofRun-local only. Authentication would only be considered if real user-specific persistence (saved experiments, history, sharing) is built — **not** in this release.

## Public demo plan

| Mode | Status |
| --- | --- |
| **Local product** | Select → Input → Run → See → Prove → Measure (Python server + CLI) |
| **Future free public demo** | Static GitHub Pages **SEE** via canned traces |
| **Future live browser run** | Optional trusted WASM / free secure backend investigation |
| **Not on Pages** | The current Python product server |

Details: `docs/public-demo-plan.md`. **Nothing deployed yet.**

## License

MIT — see [`LICENSE`](./LICENSE).

## Spec vs instructions

| Use for | Documents |
| --- | --- |
| How to run / contribute | `README.md`, `docs/setup.md`, `CONTRIBUTING.md` |
| Design / history | Root `PROJECT-SPEC.md`, `ARCHITECTURE.md`, `*-PLAN.md`, historical `README-DRAFT.md` |