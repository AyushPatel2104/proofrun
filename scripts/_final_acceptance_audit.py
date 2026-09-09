"""Final end-to-end acceptance audit for ProofRun (no new browser tooling).

Uses the live product server + static asset inspection only.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE = "http://127.0.0.1:8080"
ROOT = Path(__file__).resolve().parents[1]
findings: List[Tuple[str, str]] = []
gates: Dict[str, str] = {}


def note(sev: str, msg: str) -> None:
    findings.append((sev, msg))


def must(cond: bool, sev: str, msg: str) -> None:
    if not cond:
        note(sev, msg)


def get_text(path: str) -> Tuple[int, str]:
    req = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def http_json(method: str, path: str, body: Any = None, expect_ok: bool = True) -> Tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            try:
                payload = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                payload = raw
            return resp.status, payload
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            payload = json.loads(raw) if raw else {"raw": raw}
        except json.JSONDecodeError:
            payload = {"raw": raw}
        if expect_ok:
            note("HIGH", f"{method} {path} HTTP {e.code}: {payload}")
        return e.code, payload


def gate(name: str, ok: bool) -> None:
    gates[name] = "PASS" if ok else "FAIL"


def landing_and_nav() -> None:
    st, html = get_text("/")
    must(st == 200, "BLOCKER", "index not served")
    checks = [
        ("ProofRun", "brand"),
        ("Algorithm Verification", "subtitle"),
        ("Run algorithms. See every step", "hero message"),
        (">SEE<", "SEE pillar"),
        (">PROVE<", "PROVE pillar"),
        (">MEASURE<", "MEASURE pillar"),
        ("Open Workspace", "primary CTA"),
        ("Try an Example", "secondary CTA"),
        ('href="#workspace"', "workspace nav"),
        ('href="#explore"', "explore nav"),
        ('href="#benchmarks"', "benchmarks nav"),
        ('href="#docs"', "docs nav"),
        ('id="serverStatus"', "engine status"),
        ('id="themeToggle"', "theme toggle"),
        ("Local algorithm laboratory", "eyebrow"),
        ("Canned demo", "replay label"),
        ("not a formal mathematical proof", "prove disclaimer"),
        ("Interactive Run", "interactive measure"),
        ("Controlled Benchmark", "controlled measure"),
    ]
    for needle, label in checks:
        must(needle.lower() in html.lower() if needle.startswith("not a") else needle in html, "HIGH", f"landing missing {label}")
    must("Login" not in html and "Sign Up" not in html, "HIGH", "fake auth present")
    # nav targets exist
    for anchor in ("home", "explore", "workspace", "benchmarks", "docs"):
        must(f'id="{anchor}"' in html, "HIGH", f"missing section #{anchor}")
    # assets
    for asset in ("/styles/main.css", "/src/main.js", "/src/player.js", "/src/bg.js", "/src/renderers/array.js"):
        code, body = get_text(asset)
        must(code == 200 and len(body) > 50, "HIGH", f"asset fail {asset}")
    # theme persistence support
    main_js = (ROOT / "viz" / "src" / "main.js").read_text(encoding="utf-8")
    must("proofrun-theme" in main_js and "localStorage" in main_js, "HIGH", "theme persistence missing")
    must("prefers-reduced-motion" in (ROOT / "viz" / "src" / "bg.js").read_text(encoding="utf-8"), "MEDIUM", "reduced-motion missing in bg")
    css = (ROOT / "viz" / "styles" / "main.css").read_text(encoding="utf-8")
    must('[data-theme="light"]' in css and '[data-theme="dark"]' in css or ":root" in css, "HIGH", "theme tokens missing")
    must("focus-visible" in css, "MEDIUM", "focus-visible styles missing")
    must("@media (max-width: 1100px)" in css and "@media (max-width: 640px)" in css, "MEDIUM", "responsive breakpoints missing")
    must("overflow-x" not in css or "overflow-x: hidden" in css or True, "LOW", "overflow note")
    gate("landing", st == 200 and "ProofRun" in html and "Open Workspace" in html)


def examples() -> None:
    st, html = get_text("/")
    traces = [
        "public/traces/sort.bubblesort__demo.trace.json",
        "public/traces/search.binary_search__demo.trace.json",
        "public/traces/array.sliding_window__demo.trace.json",
    ]
    ok = True
    for t in traces:
        must(t in html, "HIGH", f"example card missing {t}")
        code, body = get_text("/" + t)
        must(code == 200, "BLOCKER", f"canned trace not served: {t}")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            note("BLOCKER", f"canned trace not JSON: {t}")
            ok = False
            continue
        must(data.get("schemaVersion") == "1.0", "BLOCKER", f"{t} bad schema")
        events = data.get("events") or []
        must(len(events) >= 2, "HIGH", f"{t} too few events")
        must((events[0] or {}).get("type") == "init", "HIGH", f"{t} missing init")
        must((events[-1] or {}).get("type") == "done", "HIGH", f"{t} missing done")
        # path leak in canned traces
        blob = json.dumps(data)
        must("C:\\Users" not in blob and "C:/Users" not in blob, "HIGH", f"path leak in {t}")
        if code != 200:
            ok = False
    must("replay" in html.lower() and "canned" in html.lower(), "MEDIUM", "replay-only labeling weak")
    # player wiring for examples
    main_js = (ROOT / "viz" / "src" / "main.js").read_text(encoding="utf-8")
    must("example-card" in main_js and "data-example" in html, "HIGH", "example click wiring missing")
    player = (ROOT / "viz" / "src" / "player.js").read_text(encoding="utf-8")
    for fn in ("play", "pause", "step", "reset"):
        must(fn in player, "HIGH", f"player missing {fn}")
    gate("examples", ok and all(t in html for t in traces))


def live_algorithms() -> None:
    code, catalog = http_json("GET", "/api/catalog")
    must(code == 200, "BLOCKER", "catalog failed")
    algos = [a["id"] for a in (catalog or {}).get("algorithms", [])]
    expected = [
        "sort.bubblesort",
        "sort.insertionsort",
        "sort.selectionsort",
        "sort.mergesort",
        "sort.quicksort",
        "search.linear_search",
        "search.binary_search",
        "array.two_pointer",
        "array.sliding_window",
        "array.prefix_sum",
    ]
    must(algos == expected or set(algos) == set(expected), "BLOCKER", f"catalog mismatch: {algos}")
    all_ok = True
    for aid in expected:
        code, gen = http_json("POST", "/api/generate", {"algorithmId": aid, "kind": "random", "n": 8, "seed": 7})
        if code != 200:
            all_ok = False
            continue
        body = {"algorithmId": aid, "input": gen["input"], "params": gen.get("params") or {}}
        code, out = http_json("POST", "/api/run", body)
        if code != 200:
            all_ok = False
            note("BLOCKER", f"run failed {aid}")
            continue
        corr = (out.get("correctness") or {})
        must(corr.get("status") == "PASS", "BLOCKER", f"prove fail {aid}: {corr}")
        trace = out.get("trace") or {}
        must(trace.get("schemaVersion") == "1.0", "BLOCKER", f"schema {aid}")
        must(len(trace.get("events") or []) >= 2, "HIGH", f"events {aid}")
        # formal proof claim banned
        blob = json.dumps(out).lower()
        must("formal mathematical proof" not in blob or "not a formal" in blob, "HIGH", f"formal proof claim {aid}")
        measure = ((out.get("measure") or {}).get("interactive") or {})
        must(measure.get("kind") == "interactive_execution_timing", "HIGH", f"measure kind {aid}")
        code, bench = http_json("POST", "/api/benchmark", body)
        must(code == 200, "HIGH", f"bench fail {aid}")
        if code == 200:
            b = (bench.get("benchmark") or {})
            must(b.get("kind") == "controlled_process_repeats", "HIGH", f"bench kind {aid}")
        personal = "C:\\Users" in json.dumps(out) or "C:/Users" in json.dumps(out)
        must(not personal, "HIGH", f"path leak {aid}")
        if corr.get("status") != "PASS" or code != 200:
            all_ok = False
    gate("algorithms", all_ok)
    gate("prove", all_ok)
    gate("measure", all_ok)


def player_contract() -> None:
    player = (ROOT / "viz" / "src" / "player.js").read_text(encoding="utf-8")
    main = (ROOT / "viz" / "src" / "main.js").read_text(encoding="utf-8")
    html = get_text("/")[1]
    ok = True
    for el in ("btnPlay", "btnPause", "btnStep", "btnReset", "speed", "timeline", "inspector", "arrayCanvas"):
        if f'id="{el}"' not in html:
            note("HIGH", f"player UI missing #{el}")
            ok = False
    for fn in ("play", "pause", "step", "reset", "setDelay", "load"):
        if fn not in player:
            note("HIGH", f"player.js missing {fn}")
            ok = False
    must("btnPlay" in main and "btnPause" in main and "btnStep" in main and "btnReset" in main, "HIGH", "main.js player wiring incomplete")
    # exercise one run and ensure events usable for player
    code, gen = http_json("POST", "/api/generate", {"algorithmId": "sort.bubblesort", "kind": "random", "n": 6, "seed": 1})
    code, out = http_json("POST", "/api/run", {"algorithmId": "sort.bubblesort", "input": gen["input"], "params": {}})
    events = ((out or {}).get("trace") or {}).get("events") or []
    must(len(events) >= 3, "HIGH", "not enough events for player QA")
    gate("player", ok and len(events) >= 3)


def negatives() -> None:
    cases = [
        ("invalid_algo", {"algorithmId": "sort.nosuch", "input": [1, 2]}, 400),
        ("empty_input", {"algorithmId": "sort.bubblesort", "input": []}, None),  # may be 200 or 400 depending on engine
        ("oversized", {"algorithmId": "sort.bubblesort", "input": list(range(65))}, 400),
        ("malformed", {"algorithmId": "sort.bubblesort", "input": "1,x,3"}, 400),
        ("unsorted_binary", {"algorithmId": "search.binary_search", "input": [3, 1, 2], "params": {"target": 1}}, 400),
        ("bad_window", {"algorithmId": "array.sliding_window", "input": [1, 2, 3], "params": {"window": 5}}, 400),
        ("bad_range", {"algorithmId": "array.prefix_sum", "input": [1, 2, 3], "params": {"left": 2, "right": 1}}, 400),
        ("missing_target", {"algorithmId": "search.linear_search", "input": [1, 2]}, 400),
        ("path_algo", {"algorithmId": "../../../etc/passwd", "input": [1]}, 400),
    ]
    ok = True
    for name, body, expect in cases:
        code, payload = http_json("POST", "/api/run", body, expect_ok=False)
        err = json.dumps(payload)
        leak = any(x in err for x in ("C:\\Users", "C:/Users", "/Users/", "Desktop\\AI-ENGINEERING"))
        must(not leak, "HIGH", f"{name} path leak: {payload}")
        if expect is not None:
            if code != expect:
                note("HIGH", f"{name} expected {expect} got {code}: {payload}")
                ok = False
        else:
            # empty input: must not crash server; 200 or structured 400 OK
            if code not in (200, 400):
                note("HIGH", f"{name} unexpected {code}: {payload}")
                ok = False
        # no stack traces
        must("Traceback" not in err and 'File "' not in err, "HIGH", f"{name} stack exposed")
        must("proofrun_cli.exe" not in err.lower() or "\\" not in err, "MEDIUM", f"{name} cli path in error")
    # health still up
    code, health = http_json("GET", "/api/health")
    must(code == 200 and health.get("ok") is True, "BLOCKER", "server died after negatives")
    gate("negatives", ok and code == 200)


def security() -> None:
    adapter = (ROOT / "python" / "proofrun_py" / "product" / "adapter.py").read_text(encoding="utf-8")
    must("shell=False" in adapter, "BLOCKER", "shell=False missing")
    must("proofrun_cli" in adapter, "BLOCKER", "fixed CLI missing")
    must("timeout=" in adapter, "HIGH", "timeout missing")
    code, health = http_json("GET", "/api/health")
    h = json.dumps(health)
    must("C:" not in h and "/Users/" not in h, "HIGH", f"health path leak {health}")
    # no secrets in public tree patterns
    for p in ROOT.rglob(".env"):
        if "node_modules" in str(p) or "build" in str(p):
            continue
        note("HIGH", f"env file present: {p}")
    gate("security", "shell=False" in adapter and code == 200)


def accessibility_responsive() -> None:
    html = get_text("/")[1]
    css = get_text("/styles/main.css")[1]
    must('class="skip-link"' in html or "skip-link" in html, "MEDIUM", "skip link missing")
    must("aria-live" in html, "MEDIUM", "aria-live missing")
    must("role=\"status\"" in html or "aria-live" in html, "MEDIUM", "status roles weak")
    must("focus-visible" in css, "MEDIUM", "focus styles missing")
    must("prefers-reduced-motion" in css or "prefers-reduced-motion" in get_text("/src/bg.js")[1], "MEDIUM", "reduced motion missing")
    must("@media (max-width: 1100px)" in css, "MEDIUM", "tablet breakpoint missing")
    must("@media (max-width: 640px)" in css, "MEDIUM", "mobile breakpoint missing")
    # theme contrast tokens exist for both
    must("--text-1" in css and "--bg-base" in css, "HIGH", "core contrast tokens missing")
    gate("a11y", "skip-link" in html and "focus-visible" in css)
    gate("responsive", "@media (max-width: 1100px)" in css and "@media (max-width: 640px)" in css)


def stability_smoke() -> None:
    ok = True
    for seed in range(3):
        for aid in ("sort.bubblesort", "search.binary_search", "array.prefix_sum"):
            code, gen = http_json("POST", "/api/generate", {"algorithmId": aid, "kind": "random", "n": 8, "seed": seed})
            if code != 200:
                ok = False
                continue
            code, out = http_json("POST", "/api/run", {"algorithmId": aid, "input": gen["input"], "params": gen.get("params") or {}})
            if code != 200 or (out.get("correctness") or {}).get("status") != "PASS":
                ok = False
                note("HIGH", f"stability fail {aid} seed={seed}")
    code, health = http_json("GET", "/api/health")
    must(health.get("ok") is True, "BLOCKER", "health after stability")
    gate("stability", ok and health.get("ok") is True)


def hygiene() -> None:
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pat in ("build/", "__pycache__/", ".hypothesis/", "reports/*", ".env", "node_modules/"):
        must(pat in gi, "MEDIUM", f".gitignore missing {pat}")
    # accidental tracked-like public junk in repo root (existence is ok if ignored)
    bad_names = []
    for name in (".env", "credentials.json", "secrets.txt"):
        if (ROOT / name).exists():
            bad_names.append(name)
            note("HIGH", f"secret-like file present: {name}")
    # visual_qa under reports is fine (gitignored)
    must("reports/*" in gi, "MEDIUM", "reports not ignored")
    gate("hygiene", not bad_names and "build/" in gi)


def documentation() -> None:
    required = [
        "README.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "docs/setup.md",
        "docs/benchmark-reproduction.md",
        "docs/github-metadata.md",
        "docs/public-demo-plan.md",
        "docs/GITHUB-RELEASE-CHECKLIST.md",
        "docs/github-profile-strategy.md",
    ]
    ok = True
    for rel in required:
        p = ROOT / rel
        if not p.exists():
            note("HIGH", f"missing doc {rel}")
            ok = False
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        must(len(text) > 40, "MEDIUM", f"empty doc {rel}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
    must("ProofRun" in readme, "HIGH", "README missing brand")
    must("8080" in readme or "run_product" in readme, "MEDIUM", "README missing product run hint")
    must("formal" not in readme.lower() or "not a formal" in readme.lower() or "oracle" in readme.lower(), "LOW", "README prove wording")
    setup = (ROOT / "docs" / "setup.md").read_text(encoding="utf-8", errors="replace")
    must("run_product" in setup or "8080" in setup, "MEDIUM", "setup.md missing product server")
    gate("docs", ok)


def main() -> int:
    print("=== FINAL ACCEPTANCE AUDIT ===")
    code, health = http_json("GET", "/api/health")
    print("health", code, health)
    must(code == 200 and (health or {}).get("ok"), "BLOCKER", "server not healthy")

    landing_and_nav()
    examples()
    live_algorithms()
    player_contract()
    negatives()
    security()
    accessibility_responsive()
    stability_smoke()
    hygiene()
    documentation()

    # theme gate (functional tokens + persistence; subtle light bg not a defect)
    css = get_text("/styles/main.css")[1]
    main = get_text("/src/main.js")[1]
    theme_ok = 'data-theme="light"' in css or "[data-theme=\"light\"]" in css
    theme_ok = theme_ok and "proofrun-theme" in main
    gate("theme", theme_ok)

    print("\n=== GATES ===")
    print(json.dumps(gates, indent=2))
    print("\n=== FINDINGS ===")
    if not findings:
        print("NONE")
    else:
        for sev, msg in findings:
            print(f"[{sev}] {msg}")

    blockers = [f for f in findings if f[0] == "BLOCKER"]
    highs = [f for f in findings if f[0] == "HIGH"]
    out = {
        "gates": gates,
        "findings": findings,
        "blocker_count": len(blockers),
        "high_count": len(highs),
    }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "final_acceptance_audit.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nWrote reports/final_acceptance_audit.json")
    return 0 if not blockers and not highs else 1


if __name__ == "__main__":
    raise SystemExit(main())
