# PROJECT-SPEC.md — ProofRun (Project #01)

| Field | Value |
| --- | --- |
| Roadmap Project Number | **01** |
| Roadmap Name | AlgoBench Studio |
| Working Brand Name | **ProofRun** |
| Product Title | ProofRun — Algorithm Verification & Performance Intelligence Platform |
| Tagline | See the algorithm. Prove the result. Measure the run. |
| Category | `01-FOUNDATION-ENGINEERING` |
| Project Type | Foundation |
| Difficulty | Intermediate |
| Deployment Class | LOCAL-FIRST PRODUCT + static public SEE demo (Pages enablement separate) |
| Version | **0.1.0** |
| Status | **SHIPPED v0.1** — local product complete for locked scope; GitHub-published as standalone `proofrun` |

---

## 1. Purpose

ProofRun is a serious algorithm engineering platform that makes algorithm behavior **observable**, **verifiable**, and **measurable**.

It is **not** a DSA tutorial dump. It is an engineering artifact that connects:

- theoretical complexity,
- correctness evidence,
- empirical runtime/memory behavior,
- interactive execution visualization,
- reproducible benchmark reports.

## 2. Problem Statement

Developers often know Big-O notation but lack a reproducible way to:

1. visualize algorithm execution,
2. verify correctness against oracles and properties,
3. compare implementations (e.g., C++ vs Python reference),
4. benchmark runtime (and memory where practical),
5. observe scaling across input sizes,
6. connect claimed complexity with measured performance.

## 3. Product Capabilities (Target vs Shipped)

Historical target matrix is preserved. **Shipped** column reflects ProofRun **v0.1** only.

| # | Capability | MVP target | Shipped in v0.1 | Later (not in release scope) |
| --- | --- | --- | --- | --- |
| 1 | Algorithm Library | Yes | **Yes** — 10 catalog algorithms | Expand families (e.g. trees/graphs) when authorized |
| 2 | Interactive Step-by-Step Visualization | Yes (core set) | **Yes** — ExecutionTrace player | More algos / advanced viz |
| 3 | Execution State Inspection | Yes | **Yes** — inspector + timeline | Richer inspectors / diff views |
| 4 | Correctness Verification | Yes | **Yes** — independent Python oracles | Cross-impl matrix / formal extras |
| 5 | Property-Based Testing | Yes (selected) | **Yes** — Hypothesis (selected) | Broader continuous corpus |
| 6 | Complexity Analysis (documented + empirical checks) | Yes | **Yes** — catalog notes + UI sync | Stronger automated regression gates |
| 7 | Benchmark Runner | Yes | **Yes** — interactive + controlled + Google Benchmark binaries | Matrix CI / historical trends |
| 8 | Runtime Comparison | Yes (C++ vs Python oracle timing where fair) | **Partial** — C++ engine vs Python prove; honest timing labels | Multi-impl / cross-machine |
| 9 | Input-Size Scaling | Yes | **Partial** — smoke sizes + generate presets | Curves UI / fit heuristics |
| 10 | Memory Measurement | Best-effort MVP | **Not shipped** — `memory_bytes` remains `null` | Trustworthy cross-platform method |
| 11 | Reproducible Benchmark Reports | Yes | **Yes** — smoke report + reproduction docs | HTML pack / CI artifacts site |
| 12 | Algorithm Comparison | Yes (same family) | **Partial** — same-family catalog selection | Cross-family comparison UI |
| 13 | Documentation / Learning | Yes | **Yes** — README, setup, architecture, security | Deeper curriculum packs |
| 14 | CI Validation | Yes (build/test/bench-smoke) | **Yes** — GitHub Actions CI | Full matrix / nightly benches |

## 4. Roadmap Technology Mapping (LOCKED)

Do **not** replace this stack.

| Technology | Mode | Responsibility |
| --- | --- | --- |
| **C++** | PRIMARY | Core algorithm library, CMake project, GoogleTest, Google Benchmark microbenchmarks, `proofrun_cli` |
| **Python** | PRIMARY | Reference/oracle implementations, pytest, property-based tests, local product server + adapter |
| **JavaScript** | PRIMARY | Interactive visualization runtime (vanilla JS player; framework-independent) |
| **TypeScript** | SECONDARY | Typed viz/docs tooling wrappers (`tools/`) |
| **Bash** / **PowerShell** | SECONDARY | Build, product run, benchmark smoke, CI scripts |

**AI/ML:** None in v1 (per locked roadmap). Unchanged for v0.1.

## 5. Non-Goals (This Project / v0.1)

- Not a competitive programming judge that executes arbitrary user-uploaded native code publicly.
- Not an online IDE for untrusted code execution.
- Not a full course platform / LMS.
- Not replacing later portfolio projects’ ML/GenAI scope.
- Not multi-tenant SaaS, accounts/login, cloud workspaces, or paid hosting in this release.
- Not GitHub Pages live Python/C++ execution (Pages, if ever added, would be canned-trace replay only).

Historical note: early phases forbade package installs / Git init until authorized. Those gates have since been authorized; v0.1 is implemented, tested, and published as a standalone public repository.

## 6. Users

| Persona | Need |
| --- | --- |
| Student / early engineer | Understand *how* algorithms move state |
| Interview-prep engineer | Prove correctness + complexity claims with evidence |
| Systems-minded engineer | Reproducible benches and scaling curves |
| Portfolio reviewer / employer | See engineering discipline: tests, benches, docs, limits |

## 7. Success Metrics (Definition of Product Quality)

- Every MVP algorithm has tests + complexity notes + bench definition + viz event model (where visualizable).
- Benchmarks are seed-controlled and regenerable from CI scripts.
- Live product runs locally with hard input limits; public static demo (if added) stays canned-trace only.
- README allows a new engineer to build, test, and reproduce a smoke benchmark without tribal knowledge.

**v0.1 verification posture:** GoogleTest + pytest + catalog drift check + visualization contract + security scan + local product UI workflow (SEE / PROVE / MEASURE) for all 10 algorithms.

## 8. Relationship to Master Roadmap

- Roadmap project **#01 AlgoBench Studio** remains the canonical identity.
- **ProofRun** is the public/product brand for the same project and scope.
- Master roadmap architecture must not be renumbered or redesigned by this project’s branding.

## 9. Phase Boundary — Shipped v0.1

**Historical:** This document began as specification-only. Implementation, Git, and publication were out of scope until authorized.

**Current (v0.1):** Scope for this release is **closed** as a local-first product:

| Delivered | Detail |
| --- | --- |
| Algorithms | Bubble, Insertion, Selection, Merge, Quick; Linear / Binary search; Two Pointer, Sliding Window, Prefix Sum |
| Engine | C++17 library + trusted `proofrun_cli` + ExecutionTrace schema **1.0** |
| Product | Python localhost server (`127.0.0.1:8080`) + vanilla JS UI (dark/light) |
| Workflow | Select → Input → Run → See → Prove → Measure |
| Quality | GoogleTest, pytest/Hypothesis, viz contract, catalog generation check, CI |
| Security model | Catalog-only; validated inputs; size caps; fixed CLI; `shell=False`; no secrets required |
| Distribution | Standalone public GitHub repository; MIT; no login |

**Explicitly deferred (not v0.1 core product scope):** additional algorithm families; trustworthy memory measurement; accounts/persistence; hosted/multi-tenant execution; WASM live-in-browser engine. Static Pages SEE demo is implemented as a build + workflow; enabling GitHub Pages hosting remains an operator step.

Further work requires separate authorization and must not silently expand this locked v0.1 boundary.
