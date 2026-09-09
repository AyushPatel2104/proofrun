# Contributing to ProofRun

Thanks for interest in improving ProofRun. This project is an engineering product (SEE → PROVE → MEASURE), not a tutorial dump. Keep changes small, tested, and honest.

## Development setup

1. Clone the **standalone** ProofRun tree (repository root contains `cpp/`, `python/`, `viz/`, …).  
2. Install a C++17 toolchain, CMake ≥ 3.16, Python ≥ 3.10.  
3. Optional: Node 18+ for TypeScript contract checks.  
4. Python deps: `python -m pip install -r python/requirements.txt`

```bash
./scripts/build_cpp.sh          # or scripts/build_cpp.ps1 on Windows
export PYTHONPATH=python
export PROOFRUN_CLI=$PWD/build/cpp/proofrun_cli
```

Product UI: `./scripts/run_product.sh` → http://127.0.0.1:8080/

## Build

```bash
cmake -S cpp -B build/cpp -DCMAKE_BUILD_TYPE=Release
cmake --build build/cpp --config Release
```

## Tests

```bash
./scripts/test_all.sh
# or:
ctest --test-dir build/cpp --output-on-failure
python -m pytest -q python/tests
```

Includes GoogleTest, pytest, Hypothesis properties, product workflow tests, and catalog drift checks.

## Benchmarks

```bash
./scripts/bench_smoke.sh
./build/cpp/proofrun_sort_bench --benchmark_filter=BM_
./build/cpp/proofrun_search_array_bench --benchmark_filter=BM_
```

Read `docs/benchmark-reproduction.md` before interpreting numbers. Do not treat smoke/UI timings as universal truth.

Smoke writes local reports under `reports/` (gitignored). Committed public samples live in `docs/reports/examples/` and must stay sanitized — if regenerating those files for docs, run `python scripts/_sanitize_example_report.py` before commit.

## Schemas and catalog

```bash
./scripts/validate_schemas.sh
python scripts/generate_catalog_artifacts.py --check
cd tools && npm install && npm run validate
```

Algorithm metadata source of truth: `catalogs/algorithms.json`. Regenerate the C++ header after catalog edits.

## Coding expectations

- Prefer extending existing architecture (CLI, Emitter, oracles, product server) over parallel systems.  
- Keep visualization **event-driven** (no hardcoded algorithm animations).  
- GoogleTest + Google Benchmark remain the C++ test/bench stack.  
- Do not add arbitrary native-code execution for users.  
- Match existing style; avoid drive-by refactors.

## Pull requests

- Describe the problem and the user-visible change.  
- Include or update tests for behavior changes.  
- Update docs when workflow, security, or public claims change.  
- Keep PRs focused; do not expand algorithm families without an explicit scope decision.

## Documentation

- Public entry point: `README.md`  
- Setup: `docs/setup.md`  
- Specs under the repo root are design history — do not contradict README instructions  

## Security reporting

If you find a vulnerability (especially around execution, path handling, or input validation), please open a private report to the maintainers rather than filing a public issue with exploit details. Do not commit secrets or personal environment paths.

## Scope note

ProofRun’s broader portfolio roadmap is maintained separately and locked. Contributions should improve this repository without renumbering external portfolio projects.
