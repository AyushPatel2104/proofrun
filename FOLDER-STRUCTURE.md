# FOLDER-STRUCTURE.md — ProofRun

## 1. Spec-Phase Reality (NOW)

Only specification documents exist. **No source-code tree has been created yet.**

Current path:

```text
01-FOUNDATION-ENGINEERING/
└── 01-PROOFRUN/
    ├── PROJECT-SPEC.md
    ├── ARCHITECTURE.md
    ├── FOLDER-STRUCTURE.md
    ├── IMPLEMENTATION-PLAN.md
    ├── TEST-PLAN.md
    ├── BENCHMARK-PLAN.md
    ├── VISUALIZATION-SPEC.md
    ├── SECURITY.md
    └── README-DRAFT.md
```

---

## 2. Proposed Implementation Tree (FUTURE — do not create in this phase)

This is the **exact proposed folder tree** for when implementation is authorized:

```text
01-FOUNDATION-ENGINEERING/01-PROOFRUN/
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml                 # build + tests + schema validate + bench-smoke
│       └── bench-nightly.yml      # optional later
│
├── docs/
│   ├── architecture.md
│   ├── complexity-table.md
│   ├── security-and-limits.md
│   ├── benchmark-reproduction.md
│   ├── setup.md
│   ├── diagrams/
│   │   └── overview.mmd           # or PNG exported from text diagram
│   └── reports/                   # generated bench report snapshots
│       └── examples/
│
├── schemas/
│   ├── algorithm-manifest.schema.json
│   ├── dataset-spec.schema.json
│   ├── execution-trace.schema.json
│   └── bench-report.schema.json
│
├── catalogs/
│   └── algorithms.yaml            # algorithm manifests (metadata)
│
├── cpp/                           # C++ PRIMARY core
│   ├── CMakeLists.txt
│   ├── cmake/
│   ├── include/proofrun/
│   │   ├── version.hpp
│   │   ├── limits.hpp
│   │   ├── sort/
│   │   ├── search/
│   │   ├── array/
│   │   ├── string/
│   │   ├── list/
│   │   ├── stack/
│   │   ├── queue/
│   │   ├── tree/
│   │   ├── graph/
│   │   ├── greedy/
│   │   ├── dp/
│   │   ├── backtracking/
│   │   ├── dac/                   # divide and conquer
│   │   ├── hash/
│   │   ├── heap/
│   │   └── trace/
│   │       └── event.hpp          # trace event types / emitter API
│   ├── src/
│   │   ├── sort/
│   │   ├── search/
│   │   ├── ...
│   │   ├── trace/
│   │   └── tools/
│   │       └── proofrun_cli.cpp   # trusted CLI: run/verify/trace emit
│   ├── tests/
│   │   ├── sort/
│   │   ├── search/
│   │   └── ...
│   ├── benches/
│   │   ├── sort_bench.cpp
│   │   └── ...
│   └── third_party/               # vendored or FetchContent policy documented
│
├── python/                        # Python PRIMARY verification layer
│   ├── pyproject.toml             # created only in impl phase
│   ├── README.md
│   ├── proofrun_py/
│   │   ├── __init__.py
│   │   ├── oracles/
│   │   ├── generators/
│   │   ├── compare/
│   │   ├── harness/
│   │   ├── report/
│   │   └── bridge/                # CLI invocation helpers
│   └── tests/
│       ├── test_oracles/
│       ├── test_properties/
│       └── test_reports/
│
├── viz/                           # JavaScript PRIMARY visualization runtime
│   ├── package.json               # created only in impl phase
│   ├── index.html                 # local demo shell
│   ├── src/
│   │   ├── player.js
│   │   ├── timeline.js
│   │   ├── inspector.js
│   │   ├── renderers/
│   │   │   ├── array.js
│   │   │   ├── tree.js
│   │   │   ├── graph.js
│   │   │   └── generic.js
│   │   ├── loadTrace.js
│   │   └── ui/
│   │       ├── controls.js
│   │       └── panels.js
│   ├── styles/
│   │   └── main.css
│   ├── public/
│   │   └── traces/                # canned trusted traces for Pages demo
│   └── tests/                     # lightweight JS tests if added later
│
├── tools/                         # TypeScript SECONDARY tooling
│   ├── package.json               # created only in impl phase
│   ├── tsconfig.json
│   ├── src/
│   │   ├── validate-schemas.ts
│   │   ├── types/
│   │   └── site/
│   └── dist/                      # build output (gitignored)
│
├── scripts/                       # Bash SECONDARY automation
│   ├── bootstrap.sh
│   ├── build_cpp.sh
│   ├── test_all.sh
│   ├── bench_smoke.sh
│   ├── bench_matrix.sh
│   └── package_reports.sh
│
├── datasets/
│   ├── fixtures/                  # golden inputs/outputs
│   └── configs/                   # generator configs
│
├── reports/                       # local generated reports (gitignored except examples)
│   └── .gitkeep
│
└── site/                          # static site assembly for GitHub Pages (later)
    ├── index.html
    ├── algorithms/
    └── assets/
```

---

## 3. Component ↔ Folder Mapping

| Component | Path |
| --- | --- |
| C++ core/library | `cpp/` |
| Python verification/reference | `python/` |
| JS visualization | `viz/` |
| TS tooling | `tools/` |
| Benchmark subsystem | `cpp/benches/` + `python/proofrun_py/harness/` + `scripts/bench_*.sh` |
| Test subsystem | `cpp/tests/` + `python/tests/` + CI workflows |
| Dataset/input generation | `python/proofrun_py/generators/` + `datasets/` |
| Report generation | `python/proofrun_py/report/` + `docs/reports/` |
| CI pipeline | `.github/workflows/` + `scripts/` |
| Documentation/demo | `docs/` + `site/` + `viz/public/traces/` |
| Contracts/schemas | `schemas/` + `catalogs/` |

---

## 4. Naming Conventions

| Area | Convention |
| --- | --- |
| Algorithm ids | `family.algorithm` e.g. `sort.quicksort`, `graph.bfs` |
| Trace files | `{algorithmId}__{fixtureId}__{seed}.trace.json` |
| Bench reports | `bench__{profile}__{timestamp}.json` |
| C++ namespaces | `proofrun::sort`, `proofrun::graph`, ... |
| Python packages | `proofrun_py.oracles`, `proofrun_py.generators` |

---

## 5. What Must NOT Be Created in Spec Phase

- `cpp/`, `python/`, `viz/`, `tools/` source trees
- `package.json`, `pyproject.toml`, `CMakeLists.txt`
- `.git/`
- `node_modules/`, virtualenvs, build directories
- Live GitHub Pages deployment
