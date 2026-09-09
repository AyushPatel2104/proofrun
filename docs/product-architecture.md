# Product architecture — unified workflow

**Status:** Implemented for local trusted product shell  
**Date:** 2026-09-09  
**Constraint:** No arbitrary native code; catalog algorithms only  
**Publishing:** Standalone public repo root = this project directory (see `docs/github-metadata.md`)

## Problem

SEE / PROVE / MEASURE previously lived in separate toolchains (static viz, pytest, benchmark binaries). The product shell unifies them for the existing **10** algorithms.

## Trust model

```text
Browser (untrusted input data only)
        │  JSON over localhost HTTP
        ▼
Product server (Python, trusted process)
        │  validate request against catalog + limits
        ▼
Trusted Algorithm Adapter
        │  argv list → fixed proofrun_cli path (env/default only)
        ▼
C++ algorithms (repo-built binary)
        │  stdout result + ExecutionTrace JSON (schemaVersion 1.0)
        ▼
Prove  ← Python independent oracles
Measure ← interactive timing vs controlled repeats (distinct labels)
        ▼
JSON response → JS event-driven player (SEE)
```

## What users may control

- Algorithm **selection** from catalog `status=implemented` only (by id internally; UI shows display names)
- Numeric array input (length ≤ `kMaxArrayViz` = 64 for product Run+trace)
- Algorithm params: `target`, `window` (K), `query` `{left,right}`
- Deterministic generate presets (seeded)

## What users may NOT control

- Executable path
- Shell commands
- Filesystem paths for reading/writing (server uses temp files it owns)
- Arbitrary algorithm code
- Array length above product viz cap for traced Run

## API (local product server)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | CLI present + version |
| GET | `/api/catalog` | Algorithms + param schema + preconditions |
| POST | `/api/generate` | Seeded input generation |
| POST | `/api/run` | Validate → execute → trace → prove → interactive timing |
| POST | `/api/benchmark` | Controlled repeated measurement (not Google Benchmark) |

Static UI is served from `viz/`.

## Compatibility

- Canned demo traces remain loadable
- schemaVersion **1.0** unchanged
- Existing CLI / tests / benches unchanged in contract

## Non-goals (current release)

Deploy, domain, authentication, database, paid cloud, new algorithms, LLM.

## Future product capabilities (not implemented)

Accounts / login should only appear when real persistence exists, for example:

- saved experiments
- benchmark history
- shareable runs
- personal workspaces

This release deliberately has **no** Sign Up / Login UI.

## Product UI shell

Local `viz/` presents a sticky application shell (Workspace, Explore, Benchmarks, Docs), dark/light themes with local preference, and canned Explore examples that load real ExecutionTrace demos. Engineering contracts above are unchanged.
