"""Headless visual QA for ProofRun background + UI contracts."""
from __future__ import annotations

import json
import urllib.request

BASE = "http://127.0.0.1:8080"
findings: list[str] = []


def get(path: str) -> str:
    with urllib.request.urlopen(BASE + path, timeout=20) as resp:
        assert resp.status == 200, path
        return resp.read().decode("utf-8", errors="replace")


def must(cond: bool, msg: str) -> None:
    if not cond:
        findings.append(msg)


def main() -> int:
    html = get("/")
    css = get("/styles/main.css")
    bg = get("/src/bg.js")

    must("bgCanvas" in html, "bg canvas missing")
    bg_l = bg.lower()
    must(
        "computational 3d" in bg_l
        or "data field" in bg_l
        or "pseudo-3d" in bg_l
        or "depth layers" in bg_l,
        "new bg concept comment missing",
    )
    must("rebuildField" in bg and "scheduleTransit" in bg, "computational-field logic missing")
    must("parallax" in bg_l and "pointermove" in bg_l, "parallax missing")
    must("prefers-reduced-motion" in bg, "reduced-motion missing")
    must("LAYERS" in bg, "depth layers missing")

    banned = [
        "graph-paper",
        "sinusoidal",
        "full-page graph",
        "for (let x = 0; x < w; x += step)",
        "bg-grid-alpha",
        "from 'three'",
        'require("three")',
        "bg-grid-alpha",
    ]
    for b in banned:
        must(b not in bg and b not in css, f"retired concept still present: {b}")
    must("three.js" not in css.lower(), "three.js stylesheet dependency present")

    must("--flow-node" in css and "--flow-link" in css, "flow tokens missing")
    must("--bg-veil" in css, "content veil missing")
    must("--content-max" in css, "wide content max missing")
    must("--bg-grid" not in css, "old --bg-grid token still in CSS")
    must('class="btn btn-primary"' in html, "primary CTA missing")
    must("workspace-flow" in html, "workspace flow missing")
    must("Sign Up" not in html and "Login" not in html, "fake auth present")

    health = json.loads(get("/api/health"))
    must(health.get("ok") is True, "health not ok")

    print("BACKGROUND_QA:")
    if findings:
        for f in findings:
            print("FAIL:", f)
        return 1
    print("PASS — computational 3D field active; layout widened")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
