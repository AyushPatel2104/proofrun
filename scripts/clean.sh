#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf "$ROOT/build" "$ROOT/cpp/build" "$ROOT/reports"/*
mkdir -p "$ROOT/reports"
echo "Clean complete."
