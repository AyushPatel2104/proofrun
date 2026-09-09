# Setup

## Prerequisites

- CMake ≥ 3.16
- C++17 compiler (GCC/Clang/MSVC)
- Python ≥ 3.10 (developed on 3.11)
- Internet access on first configure (FetchContent for GoogleTest + Google Benchmark)
- Optional for TS tooling: Node.js 18+

## Build C++

Linux/macOS:

```bash
./scripts/build_cpp.sh
# or:
cmake -S cpp -B build/cpp -DCMAKE_BUILD_TYPE=Release
cmake --build build/cpp --config Release
```

Windows (MinGW), preferred:

```powershell
powershell -File scripts/build_cpp.ps1
# or:
cmake -S cpp -B build/cpp -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=g++
cmake --build build/cpp --config Release
```

Artifacts:

- `build/cpp/proofrun_cli`
- `build/cpp/proofrun_sort_tests` / `proofrun_search_tests` / `proofrun_array_tests`
- `build/cpp/proofrun_sort_bench` / `proofrun_search_array_bench`

## Python tests

```bash
python -m pip install -r python/requirements.txt
export PYTHONPATH=python
export PROOFRUN_CLI=$PWD/build/cpp/proofrun_cli   # Windows: set PROOFRUN_CLI=...\proofrun_cli.exe
python -m pytest -q python/tests
```

Dependency note: `requirements.txt` pins **minimum major ranges**, not a fully locked lockfile. Bit-for-bit environment reproducibility is not claimed.

## Scripts

```bash
./scripts/build_cpp.sh
./scripts/test_all.sh
./scripts/generate_demo_traces.sh
./scripts/bench_smoke.sh
./scripts/validate_schemas.sh
./scripts/run_product.sh          # Windows: powershell -File scripts/run_product.ps1
python scripts/verify_viz_contract.py
python scripts/generate_catalog_artifacts.py --check
```

## TypeScript contract validation

```bash
cd tools
npm install
npm run validate
```

## Product UI / visualization

Preferred (unified workflow — requires built CLI):

```bash
./scripts/run_product.sh
# Windows: powershell -File scripts/run_product.ps1
```

Visit `http://127.0.0.1:8080/` — Select → Input → Run → See → Prove → Measure.

Architecture: `docs/product-architecture.md`. Checklist: `docs/visualization-checklist.md`.

Static-only replay (no Run/Prove API):

```bash
python -m http.server 8080 --directory viz
```

## Known limitations

- Product controlled benchmarks include process spawn overhead (not Google Benchmark).
- Smoke harness timings likewise include spawn overhead.
- Memory bytes are intentionally unavailable/null (see `docs/benchmark-reproduction.md`).
- Public deploy not started; local product server is the coherent UX path.
- Implemented families: sorting, searching, array techniques (10 workflows).
- CI is written for a **standalone** repository root (see `docs/github-metadata.md`).
