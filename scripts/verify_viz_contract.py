#!/usr/bin/env python3
"""Headless visualization contract check (no browser)."""

from __future__ import annotations

import json
from pathlib import Path


def fold(trace: dict) -> list[int]:
    state = list(trace.get("initialState", {}).get("array", []))
    for event in trace["events"]:
        payload = event.get("payload") or {}
        if "array" in payload:
            state = list(payload["array"])
    return state


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    player = (root / "viz" / "src" / "player.js").read_text(encoding="utf-8")
    for name in ("play", "pause", "step", "reset", "setDelay", "load"):
        if name not in player:
            raise SystemExit(f"player.js missing control: {name}")

    traces = list((root / "viz" / "public" / "traces").glob("*.trace.json"))
    if not traces:
        raise SystemExit("no demo traces found")
    for path in traces:
        trace = json.loads(path.read_text(encoding="utf-8"))
        if trace.get("schemaVersion") != "1.0":
            raise SystemExit(f"bad schemaVersion in {path.name}")
        if not trace.get("events"):
            raise SystemExit(f"empty events in {path.name}")
        if trace["events"][0]["type"] != "init":
            raise SystemExit(f"{path.name}: first event must be init")
        if trace["events"][-1]["type"] != "done":
            raise SystemExit(f"{path.name}: last event must be done")
        final = fold(trace)
        expected = list(trace["finalState"]["array"])
        if final != expected:
            raise SystemExit(f"{path.name}: folded state {final} != finalState {expected}")
        print(f"OK {path.name} events={len(trace['events'])} final={final}")
    print("visualization contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
