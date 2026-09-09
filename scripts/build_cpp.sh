#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${PROOFRUN_BUILD_DIR:-$ROOT/build/cpp}"
mkdir -p "$BUILD_DIR"
python "$ROOT/scripts/generate_catalog_artifacts.py" --root "$ROOT"
cmake -S "$ROOT/cpp" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release
cmake --build "$BUILD_DIR" --config Release -j
echo "Build complete: $BUILD_DIR"
