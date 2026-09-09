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
| Deployment Class | PUBLIC DEMO (not deployed in this phase) |
| Status | **SPECIFICATION PHASE ONLY** — implementation has NOT started |

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

## 3. Product Capabilities (Target)

| # | Capability | MVP | Phase 2 | Phase 3 |
| --- | --- | --- | --- | --- |
| 1 | Algorithm Library | Yes | Expand | Expand |
| 2 | Interactive Step-by-Step Visualization | Yes (core set) | More algos | Advanced viz |
| 3 | Execution State Inspection | Yes | Richer inspectors | Diff views |
| 4 | Correctness Verification | Yes | Cross-impl matrix | Formal extras |
| 5 | Property-Based Testing | Yes (selected) | Broader | Continuous corpus |
| 6 | Complexity Analysis (documented + empirical checks) | Yes | Automated checks | Regression gates |
| 7 | Benchmark Runner | Yes | Matrix CI | Historical trends |
| 8 | Runtime Comparison | Yes (C++ vs Python oracle timing where fair) | Multi-impl | Cross-machine |
| 9 | Input-Size Scaling | Yes | Curves UI | Fit heuristics |
| 10 | Memory Measurement | Best-effort MVP | Stronger C++ path | Cross-platform |
| 11 | Reproducible Benchmark Reports | Yes | HTML/JSON pack | CI artifacts site |
| 12 | Algorithm Comparison | Yes (same family) | Cross-family | Catalog UI |
| 13 | Documentation / Learning | Yes | Deeper guides | Curriculum packs |
| 14 | CI Validation | Yes (build/test/bench-smoke) | Full matrix | Nightly benches |

## 4. Roadmap Technology Mapping (LOCKED)

Do **not** replace this stack.

| Technology | Mode | Responsibility |
| --- | --- | --- |
| **C++** | PRIMARY | Core algorithm library, CMake project, GoogleTest **or** Catch2, microbenchmarks |
| **Python** | PRIMARY | Reference/oracle implementations, pytest, property-based tests, bench harness drivers |
| **JavaScript** | PRIMARY | Interactive visualization runtime (framework-independent core) |
| **TypeScript** | SECONDARY | Typed viz/docs tooling wrappers |
| **Bash** | SECONDARY | Benchmark automation, CI scripts, matrix runners |

**AI/ML:** None in v1 (per locked roadmap).

## 5. Non-Goals (This Project)

- Not a competitive programming judge that executes arbitrary user-uploaded native code publicly.
- Not an online IDE for untrusted code execution.
- Not a full course platform / LMS.
- Not replacing later portfolio projects’ ML/GenAI scope.
- No package installs or Git init in the specification phase.

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
- Public demo is static (docs + JS/WASM viz) with hard input limits.
- README allows a new engineer to build, test, and reproduce a smoke benchmark without tribal knowledge.

## 8. Relationship to Master Roadmap

- Roadmap project **#01 AlgoBench Studio** remains the canonical identity.
- **ProofRun** is the public/product brand for the same project and scope.
- Master roadmap architecture must not be renumbered or redesigned by this project’s branding.

## 9. Phase Boundary

**This phase delivers specification documents only.**

Implementation code, dependency installation, Git initialization, and deployment are explicitly out of scope until authorized.
