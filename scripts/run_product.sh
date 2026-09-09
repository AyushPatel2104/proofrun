#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/python${PYTHONPATH:+:$PYTHONPATH}"
if command -v cygpath >/dev/null 2>&1; then
  export PROOFRUN_PROJECT_ROOT="$(cygpath -w "$ROOT")"
  export PYTHONPATH="$(cygpath -w "$ROOT/python")${PYTHONPATH:+:$PYTHONPATH}"
else
  export PROOFRUN_PROJECT_ROOT="$ROOT"
fi
BUILD_DIR="${PROOFRUN_BUILD_DIR:-$ROOT/build/cpp}"
for c in "$BUILD_DIR/proofrun_cli.exe" "$BUILD_DIR/proofrun_cli" "$BUILD_DIR/Release/proofrun_cli.exe"; do
  if [[ -f "$c" ]]; then
    if command -v cygpath >/dev/null 2>&1; then
      export PROOFRUN_CLI="$(cygpath -w "$c")"
    else
      export PROOFRUN_CLI="$c"
    fi
    break
  fi
done
PORT="${1:-8080}"
exec python -m proofrun_py.product.server "$PORT"
