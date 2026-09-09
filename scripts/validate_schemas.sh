#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Windows Python needs a native path; Git Bash paths (/c/...) break pathlib.
if command -v cygpath >/dev/null 2>&1; then
  ROOT_NATIVE="$(cygpath -w "$ROOT")"
else
  ROOT_NATIVE="$ROOT"
fi

export PYTHONPATH="${ROOT_NATIVE}/python${PYTHONPATH:+:$PYTHONPATH}"
export PROOFRUN_PROJECT_ROOT="$ROOT_NATIVE"

python "$ROOT/scripts/generate_catalog_artifacts.py" --root "$ROOT_NATIVE" --check
PROOFRUN_ROOT="$ROOT_NATIVE" python - <<'PY'
import json
import os
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path(os.environ["PROOFRUN_ROOT"])
pairs = [
    ("execution-trace.schema.json", list((root / "viz" / "public" / "traces").glob("*.json"))),
    ("bench-report.schema.json", list((root / "docs" / "reports" / "examples").glob("*-report.json"))),
    ("algorithm-manifest.schema.json", [root / "catalogs" / "algorithms.json"]),
]
for schema_name, files in pairs:
    schema = json.loads((root / "schemas" / schema_name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for f in files:
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"Schema errors in {f}: {errors[0].message}")
        print(f"OK {f.relative_to(root)}")
print("Schema validation passed.")
PY
