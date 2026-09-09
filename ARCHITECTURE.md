# ARCHITECTURE.md — ProofRun

## 1. Architectural Intent

ProofRun is layered so that:

- **C++** owns high-performance trusted implementations and microbenchmarks,
- **Python** owns oracles, property tests, and orchestration of reproducibility,
- **JavaScript** owns interactive visualization driven by an **execution-event model**,
- **TypeScript** owns typed tooling around docs/viz packaging,
- **Bash** owns CI/matrix automation.

No layer should become a “tutorial script pile.” Interfaces are explicit and versioned.

---

## 2. Logical Component Map

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Docs / Demo Site (static)                    │
│         (Markdown docs + JS viz pages + bench report HTML)       │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────┐   ┌─────────────────────────────────┐
│  TypeScript Tooling       │   │  JS Visualization Runtime       │
│  - schema validation      │   │  - player (play/pause/step)     │
│  - docs site helpers      │   │  - state inspector              │
│  - event JSON typing      │   │  - event timeline               │
└───────────────┬───────────┘   └────────────────▲────────────────┘
                │                                 │
                │                         event traces (JSON)
                │                                 │
┌───────────────▼─────────────────────────────────┴───────────────┐
│                 Trace / Dataset / Report Contracts               │
│     (schemas for inputs, events, metrics, environment meta)      │
└───────┬───────────────────────┬─────────────────────┬───────────┘
        │                       │                     │
        ▼                       ▼                     ▼
┌───────────────┐     ┌─────────────────┐   ┌─────────────────────┐
│ C++ Core Lib  │     │ Python Layer    │   │ Bash Automation     │
│ algos + benches│◄──►│ oracles/pytest  │   │ CI / matrix / smoke │
│ + optional    │     │ property tests  │   │ report packaging    │
│ trace emit    │     │ harness drivers │   └─────────────────────┘
└───────────────┘     └─────────────────┘
```

---

## 3. Layer Responsibilities

### 3.1 C++ Core / Library Layer (`proofrun_cpp`)

**Owns:**

- Canonical high-performance algorithm implementations
- Stable C++ APIs (headers + library)
- Unit tests (GoogleTest **or** Catch2 — choose one in implementation kickoff and stay consistent)
- Microbenchmark targets (e.g., Google Benchmark or equivalent CMake-integrated harness)
- Optional **trace emitter** hooks that produce visualization events for supported algorithms
- Input validation at API boundaries (size limits, null checks)

**Does not own:**

- Browser UI
- Arbitrary user code execution
- Website theming

### 3.2 Python Verification / Reference Layer (`proofrun_py`)

**Owns:**

- Reference/oracle implementations for correctness comparison
- `pytest` suites (unit, edge, cross-check vs C++ outputs where bridged)
- Property-based testing (e.g., Hypothesis) for selected algorithms
- Benchmark harness drivers (invoke C++ bench binaries / compare timings carefully)
- Dataset generation (seeded)
- Report assembly (JSON → Markdown/HTML summaries)

**Interface to C++:**

- Prefer: subprocess invocation of C++ CLI tools with structured stdin/stdout/files
- Optional later: pybind11 — **not required for MVP** unless bridging becomes a bottleneck

### 3.3 JavaScript Visualization Layer (`proofrun_viz`)

**Owns:**

- Framework-independent visualization runtime
- Player controls: play, pause, step forward, reset, speed
- Rendering of algorithm state from event traces
- Operation/event history panel
- Complexity + explanation panels (content from docs/metadata)

**Principle:** Visualization is **event-driven**, not hardcoded animation timelines per algorithm beyond mapping events → draw calls.

### 3.4 TypeScript Tooling Layer (`proofrun_tools`)

**Owns:**

- Typed models for event schemas / report schemas
- Docs site build helpers (static site packaging)
- Validation of trace JSON against schema (CI check)

**Does not replace** the JS viz runtime; it supports it.

### 3.5 Benchmark Subsystem

**Components:**

- C++ microbench binaries
- Python harness (parameter matrix, seeds, aggregation)
- Bash runners for local + CI smoke
- Report writer (machine-readable + human-readable)

### 3.6 Test Subsystem

**Components:**

- C++ unit/edge tests
- Python oracle + property tests
- Schema validation tests
- CI gate: build + test + bench-smoke

### 3.7 Dataset / Input Generation Subsystem

**Owns:**

- Seeded generators: random, adversarial, sorted/reverse, nearly-sorted, duplicates-heavy, sparse graphs, etc.
- Versioned generator configs (JSON/YAML)
- Deterministic fixture files for golden tests

### 3.8 Report Generation Subsystem

**Owns:**

- `bench-report.json` schema
- Derived Markdown/HTML summaries
- Environment + git commit metadata fields (when Git exists later)
- Complexity table generation from algorithm metadata

### 3.9 CI Pipeline

**Owns:**

- Build C++ (Debug/Release as appropriate)
- Run C++ tests
- Run Python tests
- Validate schemas
- Run **smoke** benchmarks only on PR (not misleading full benches)
- Optional nightly job later for fuller matrices

### 3.10 Documentation / Demo Layer

**Owns:**

- Architecture docs, complexity tables, security/limits
- Static demo pages embedding viz runtime
- Screenshots and reproduction instructions

---

## 4. Interfaces Between Components

| From → To | Contract | Format |
| --- | --- | --- |
| Generators → Tests/Benches | `DatasetSpec` | JSON |
| C++ algo → Tests | function results / status codes | native + CLI JSON lines |
| C++/Python → Viz | `ExecutionTrace` | JSON (event array + final state) |
| Benches → Reports | `BenchReport` | JSON (+ rendered MD/HTML) |
| Metadata catalog → Docs/Viz | `AlgorithmManifest` | JSON/YAML |
| TS tools → CI | schema validation exit codes | CLI |

### 4.1 Algorithm Manifest (conceptual)

Each algorithm entry declares:

- id, family, name
- complexity best/avg/worst + memory notes
- implementations available (`cpp`, `python`)
- visualizable: bool
- bench profiles
- test profiles
- input limits

### 4.2 Execution Trace (high level)

See `VISUALIZATION-SPEC.md` for full event model.

Minimum:

- `algorithmId`, `seed`, `inputSummary`
- `events[]` with monotonic `step`
- `finalState`
- `meta` (version, generator id)

---

## 5. Data Flow

### 5.1 Correctness flow

```text
DatasetSpec + seed
    → Generator
    → Input
    → C++ implementation → Output_A
    → Python oracle      → Output_B
    → Comparator (equality / semantic equivalence)
    → Pass/Fail + counterexample artifact
```

### 5.2 Benchmark flow

```text
BenchPlan (sizes, seeds, repeats, warmup)
    → Generator
    → C++ microbench binary
    → Raw timings (+ memory if enabled)
    → Aggregator (median/p95)
    → BenchReport (+ env metadata)
    → Docs site artifact
```

### 5.3 Visualization flow

```text
Trusted precomputed OR local trusted runner
    → ExecutionTrace JSON
    → JS runtime player
    → Renderers (array/tree/graph/...)
    → Inspector + timeline UI
```

**Public demo constraint:** Prefer **precomputed trusted traces** and/or WASM built from **trusted** C++ sources. Do not accept arbitrary native uploads.

---

## 6. Execution Boundaries (Trust)

| Zone | Trust | Allowed |
| --- | --- | --- |
| Repo algorithms + CI runners | Trusted | Full benches/tests |
| Static GitHub Pages demo | Trusted assets only | Viz + docs + canned traces |
| Future “user paste input” in demo | Untrusted input data | Hard size limits; no shell; no native compile of user code |

---

## 7. Architecture Decisions (Locked for Spec)

| Decision | Choice | Rationale |
| --- | --- | --- |
| AD-01 | Multi-language monorepo layout under `01-PROOFRUN` | Matches roadmap PRIMARY stack |
| AD-02 | Event-driven visualization | Avoids hardcoded fake animations |
| AD-03 | Python oracles + C++ core | Separates proof vs performance |
| AD-04 | JSON contracts between layers | Language-agnostic, CI-validatable |
| AD-05 | CLI/file bridge MVP (not mandatory pybind11) | Faster reliable integration |
| AD-06 | Catch2 **or** GoogleTest — single framework | Consistency; pick at impl kickoff |
| AD-07 | Public demo = static docs + JS/(optional)WASM | Matches PUBLIC DEMO class |
| AD-08 | No arbitrary public native execution | Security baseline |

---

## 8. Architecture Diagram (Text)

```text
                 [User / Reviewer]
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
     Static Docs Site        Viz Player (JS)
            │                       ▲
            │                       │ ExecutionTrace
            ▼                       │
     Algorithm Manifest ◄──── Trace Store / fixtures
            │
            ├──────────────► C++ Library + Microbench
            ├──────────────► Python Oracles + pytest + Hypothesis
            └──────────────► Bash CI Matrix + Report Packager
```

---

## 9. Non-Functional Architecture

| Concern | Approach |
| --- | --- |
| Reproducibility | Seeds, pinned generator versions, env metadata |
| Honesty in benches | Warmup, repeats, median/p95, caveats in reports |
| Portability | CMake + Python venv workflow (impl phase); avoid OS-specific assumptions without docs |
| Observability of algos | Traces + inspectors |
| Security | Limits + trusted runners only in public surfaces |
