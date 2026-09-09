#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${PROOFRUN_BUILD_DIR:-$ROOT/build/cpp}"

if [[ ! -d "$BUILD_DIR" ]]; then
  "$ROOT/scripts/build_cpp.sh"
fi

ctest --test-dir "$BUILD_DIR" --output-on-failure

export PYTHONPATH="$ROOT/python${PYTHONPATH:+:$PYTHONPATH}"
# Prefer built CLI for bridge tests
if [[ -x "$BUILD_DIR/proofrun_cli" ]]; then
  export PROOFRUN_CLI="$BUILD_DIR/proofrun_cli"
elif [[ -x "$BUILD_DIR/Release/proofrun_cli.exe" ]]; then
  export PROOFRUN_CLI="$BUILD_DIR/Release/proofrun_cli.exe"
elif [[ -x "$BUILD_DIR/proofrun_cli.exe" ]]; then
  export PROOFRUN_CLI="$BUILD_DIR/proofrun_cli.exe"
fi

python -m pytest -q "$ROOT/python/tests"
echo "All tests passed."
