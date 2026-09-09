#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${PROOFRUN_BUILD_DIR:-$ROOT/build/cpp}"
mkdir -p "$ROOT/reports"

if [[ ! -d "$BUILD_DIR" ]]; then
  "$ROOT/scripts/build_cpp.sh"
fi

BENCH_BIN=""
for c in \
  "$BUILD_DIR/proofrun_sort_bench.exe" \
  "$BUILD_DIR/Release/proofrun_sort_bench.exe" \
  "$BUILD_DIR/proofrun_sort_bench" \
  "$BUILD_DIR/Release/proofrun_sort_bench"
do
  if [[ -f "$c" ]]; then
    BENCH_BIN="$c"
    break
  fi
done

if [[ -z "$BENCH_BIN" ]]; then
  echo "ERROR: proofrun_sort_bench executable not found under $BUILD_DIR" >&2
  exit 1
fi

echo "Running microbenchmark smoke: $BENCH_BIN"
"$BENCH_BIN" --benchmark_filter=BM_Quick/64 --benchmark_min_time=0.05s

SEARCH_BENCH=""
for c in \
  "$BUILD_DIR/proofrun_search_array_bench.exe" \
  "$BUILD_DIR/Release/proofrun_search_array_bench.exe" \
  "$BUILD_DIR/proofrun_search_array_bench" \
  "$BUILD_DIR/Release/proofrun_search_array_bench"
do
  if [[ -f "$c" ]]; then
    SEARCH_BENCH="$c"
    break
  fi
done
if [[ -z "$SEARCH_BENCH" ]]; then
  echo "ERROR: proofrun_search_array_bench executable not found under $BUILD_DIR" >&2
  exit 1
fi
echo "Running search/array microbenchmark smoke: $SEARCH_BENCH"
"$SEARCH_BENCH" --benchmark_filter=BM_BinarySearch/256 --benchmark_min_time=0.05s

CLI=""
for c in \
  "$BUILD_DIR/proofrun_cli.exe" \
  "$BUILD_DIR/Release/proofrun_cli.exe" \
  "$BUILD_DIR/proofrun_cli" \
  "$BUILD_DIR/Release/proofrun_cli"
do
  if [[ -f "$c" ]]; then
    CLI="$c"
    break
  fi
done
if [[ -z "$CLI" ]]; then
  echo "ERROR: proofrun_cli not found for harness smoke" >&2
  exit 1
fi
export PROOFRUN_CLI="$CLI"

# Windows Python needs a native path; Git Bash paths (/c/...) break imports.
if command -v cygpath >/dev/null 2>&1; then
  export PROOFRUN_PROJECT_ROOT="$(cygpath -w "$ROOT")"
  export PROOFRUN_CLI="$(cygpath -w "$CLI")"
else
  export PROOFRUN_PROJECT_ROOT="$ROOT"
fi

PYTHON_BIN="${PYTHON_BIN:-python}"
"$PYTHON_BIN" -c "
import os, sys
from pathlib import Path
root = Path(os.environ['PROOFRUN_PROJECT_ROOT'])
sys.path.insert(0, str(root / 'python'))
from proofrun_py.harness import run_smoke
from proofrun_py.report import write_markdown_summary
# Local/CI outputs go under reports/ (gitignored). Do not overwrite
# sanitized docs/reports/examples/* committed for public documentation.
out = root / 'reports' / 'smoke-bench-report.json'
report = run_smoke(out)
write_markdown_summary(report, root / 'reports' / 'smoke-bench-report.md')
print('Wrote', out)
print('Note: committed examples live in docs/reports/examples/ (sanitized; not overwritten here).')
"

echo "Benchmark smoke complete."
