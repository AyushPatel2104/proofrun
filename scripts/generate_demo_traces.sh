#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${PROOFRUN_BUILD_DIR:-$ROOT/build/cpp}"
CLI="${PROOFRUN_CLI:-}"
if [[ -z "$CLI" ]]; then
  for c in "$BUILD_DIR/proofrun_cli" "$BUILD_DIR/Release/proofrun_cli.exe" "$BUILD_DIR/proofrun_cli.exe"; do
    if [[ -x "$c" ]] || [[ -f "$c" ]]; then CLI="$c"; break; fi
  done
fi
if [[ -z "$CLI" || ! -f "$CLI" ]]; then
  echo "proofrun_cli not found; build first" >&2
  exit 1
fi

OUT="$ROOT/viz/public/traces"
mkdir -p "$OUT"
INPUT="7,3,9,1,5,2,8,4"

for algo in sort.bubblesort sort.insertionsort sort.selectionsort sort.mergesort sort.quicksort; do
  "$CLI" sort "$algo" --input "$INPUT" --seed 42 --trace "$OUT/${algo}__demo.trace.json" >/dev/null
  echo "Wrote $OUT/${algo}__demo.trace.json"
done

"$CLI" search search.linear_search --input "4,8,15,16,23,42" --target 23 --seed 42 \
  --trace "$OUT/search.linear_search__demo.trace.json" >/dev/null
echo "Wrote $OUT/search.linear_search__demo.trace.json"

"$CLI" search search.binary_search --input "1,3,5,7,9,11,13,15" --target 11 --seed 42 \
  --trace "$OUT/search.binary_search__demo.trace.json" >/dev/null
echo "Wrote $OUT/search.binary_search__demo.trace.json"

"$CLI" array array.two_pointer --input "1,2,4,7,11,15" --target 9 --seed 42 \
  --trace "$OUT/array.two_pointer__demo.trace.json" >/dev/null
echo "Wrote $OUT/array.two_pointer__demo.trace.json"

"$CLI" array array.sliding_window --input "2,1,5,3,2,7,4" --window 3 --seed 42 \
  --trace "$OUT/array.sliding_window__demo.trace.json" >/dev/null
echo "Wrote $OUT/array.sliding_window__demo.trace.json"

"$CLI" array array.prefix_sum --input "2,4,6,8,1" --query 1,3 --seed 42 \
  --trace "$OUT/array.prefix_sum__demo.trace.json" >/dev/null
echo "Wrote $OUT/array.prefix_sum__demo.trace.json"
