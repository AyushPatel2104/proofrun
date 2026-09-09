"""Live HTTP acceptance QA against the local ProofRun product server.

Not a unit test file — run manually during pre-publish QA.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE = "http://127.0.0.1:8080"
ROOT = Path(__file__).resolve().parents[1]
findings: List[Tuple[str, str]] = []  # (severity, message)
results: Dict[str, Any] = {"algorithms": {}, "negatives": {}, "security": {}, "ui": {}}


def http_json(method: str, path: str, body: Any = None, expect_ok: bool = True) -> Tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            payload: Any
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
            findings.append(("HIGH", f"{method} {path} HTTP {e.code}: {payload}"))
        return e.code, payload


def http_text(path: str) -> Tuple[int, str]:
    req = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8")


def assert_true(cond: bool, sev: str, msg: str) -> None:
    if not cond:
        findings.append((sev, msg))


def check_ui_assets() -> None:
    status, html = http_text("/")
    assert_true(status == 200, "BLOCKER", "UI index not 200")
    assert_true("ProofRun" in html, "BLOCKER", "UI missing ProofRun brand")
    assert_true("btnPlay" in html and "btnPause" in html, "HIGH", "UI missing Play/Pause")
    assert_true("btnStep" in html and "btnReset" in html, "HIGH", "UI missing Step/Reset")
    assert_true('id="speed"' in html, "HIGH", "UI missing speed control")
    assert_true(
        "not a formal mathematical proof" in html.lower() or "not a formal math proof" in html.lower(),
        "MEDIUM",
        "UI missing practical prove disclaimer",
    )
    assert_true("Ready to visualize" in html, "HIGH", "UI missing empty-state copy")
    assert_true("Try an Example" in html or "Try an example" in html, "HIGH", "UI missing example CTA")
    assert_true('id="themeToggle"' in html, "HIGH", "UI missing theme toggle")
    assert_true("Interactive Run" in html and "Controlled Benchmark" in html, "MEDIUM", "UI measure distinction weak")
    assert_true("Sign Up" not in html and "Login" not in html and "Sign in" not in html, "HIGH", "Fake auth UI present")
    results["ui"]["index"] = "PASS" if status == 200 else "FAIL"

    for asset in ("/styles/main.css", "/src/main.js", "/src/player.js", "/src/bg.js"):
        st, _ = http_text(asset)
        assert_true(st == 200, "HIGH", f"Asset {asset} not served")
    player = (ROOT / "viz" / "src" / "player.js").read_text(encoding="utf-8")
    for fn in ("play", "pause", "step", "reset", "setDelay"):
        assert_true(f"function {fn}" in player or f"{fn}(" in player, "HIGH", f"player missing {fn}")
    results["ui"]["player_controls"] = "PASS"


def exercise_algo(algo_id: str) -> None:
    status = {"generate": False, "run": False, "trace": False, "prove": False, "measure": False, "bench": False}
    # SELECT via catalog already checked
    code, gen = http_json("POST", "/api/generate", {"algorithmId": algo_id, "kind": "random", "n": 8, "seed": 42})
    assert_true(code == 200 and isinstance(gen.get("input"), list), "BLOCKER", f"{algo_id} generate failed")
    status["generate"] = code == 200

    body = {"algorithmId": algo_id, "input": gen["input"], "params": gen.get("params") or {}}
    code, out = http_json("POST", "/api/run", body)
    assert_true(code == 200, "BLOCKER", f"{algo_id} run HTTP {code}")
    if code != 200:
        results["algorithms"][algo_id] = status
        return
    status["run"] = True
    trace = out.get("trace") or {}
    events = trace.get("events") or []
    assert_true(trace.get("schemaVersion") == "1.0", "BLOCKER", f"{algo_id} bad schemaVersion")
    assert_true(len(events) >= 2, "HIGH", f"{algo_id} too few events")
    assert_true(events[0].get("type") == "init", "HIGH", f"{algo_id} missing init")
    assert_true(events[-1].get("type") == "done", "HIGH", f"{algo_id} missing done")
    assert_true(trace.get("algorithmId") == algo_id, "HIGH", f"{algo_id} trace id mismatch")
    status["trace"] = True

    corr = out.get("correctness") or {}
    assert_true(corr.get("status") == "PASS", "BLOCKER", f"{algo_id} prove not PASS: {corr}")
    detail = (corr.get("detail") or "") + (corr.get("method") or "")
    assert_true("oracle" in detail.lower() or "independent" in detail.lower() or "presence" in detail.lower()
                or "bisect" in detail.lower() or "index" in detail.lower() or "window" in detail.lower()
                or "prefix" in detail.lower() or "pair" in detail.lower() or "First-index" in detail
                or "Correct" in detail,
                "MEDIUM", f"{algo_id} prove wording thin: {detail}")
    status["prove"] = corr.get("status") == "PASS"

    measure = out.get("measure") or {}
    interactive = measure.get("interactive") or {}
    assert_true(interactive.get("kind") == "interactive_execution_timing", "HIGH", f"{algo_id} interactive kind")
    assert_true("disclaimer" in interactive, "MEDIUM", f"{algo_id} missing interactive disclaimer")
    assert_true(isinstance(interactive.get("runtime_s"), (int, float)), "HIGH", f"{algo_id} no runtime")
    assert_true(measure.get("memory_bytes") is None, "LOW", f"{algo_id} unexpected memory")
    # path leakage
    blob = json.dumps(out)
    personal = ("Desktop" in blob and "Users" in blob) or "C:/Users" in blob or "C:\\\\Users" in blob
    assert_true(not personal, "HIGH", f"{algo_id} path leakage in run response")
    status["measure"] = True

    # RESULT present
    assert_true("result" in out, "HIGH", f"{algo_id} missing result")

    code, bench = http_json("POST", "/api/benchmark", body)
    assert_true(code == 200, "HIGH", f"{algo_id} benchmark failed")
    if code == 200:
        b = bench.get("benchmark") or {}
        assert_true(b.get("kind") == "controlled_process_repeats", "HIGH", f"{algo_id} bench kind")
        assert_true(b.get("kind") != interactive.get("kind"), "MEDIUM", f"{algo_id} measure modes not distinct")
        status["bench"] = True

    results["algorithms"][algo_id] = {**status, "overall": all(status[k] for k in ("generate", "run", "trace", "prove", "measure", "bench"))}


def negatives() -> None:
    cases = [
        ("invalid_algo", {"algorithmId": "sort.nosuch", "input": [1, 2]}, 400),
        ("oversized", {"algorithmId": "sort.bubblesort", "input": list(range(65))}, 400),
        ("malformed", {"algorithmId": "sort.bubblesort", "input": "1,x,3"}, 400),
        ("unsorted_binary", {"algorithmId": "search.binary_search", "input": [3, 1, 2], "params": {"target": 1}}, 400),
        ("bad_window", {"algorithmId": "array.sliding_window", "input": [1, 2, 3], "params": {"window": 5}}, 400),
        ("bad_range", {"algorithmId": "array.prefix_sum", "input": [1, 2, 3], "params": {"left": 2, "right": 1}}, 400),
        ("missing_target", {"algorithmId": "search.linear_search", "input": [1, 2]}, 400),
    ]
    for name, body, expect in cases:
        code, payload = http_json("POST", "/api/run", body, expect_ok=False)
        ok = code == expect
        err = json.dumps(payload)
        # no path leakage in errors
        leak = "Ayush" in err or "C:\\Users" in err or "C:/Users" in err
        assert_true(ok, "HIGH", f"negative {name}: expected {expect} got {code} {payload}")
        assert_true(not leak, "HIGH", f"negative {name}: path leak in error")
        # error should be understandable
        text = err.lower()
        assert_true(any(k in text for k in ("what", "why", "fix", "error", "invalid", "unsupported", "sorted", "malformed", "too long", "target", "window", "range")),
                    "MEDIUM", f"negative {name}: opaque error {payload}")
        results["negatives"][name] = "PASS" if ok and not leak else "FAIL"


def security_checks() -> None:
    # Attempt path injection via algorithmId / weird body
    code, payload = http_json(
        "POST",
        "/api/run",
        {"algorithmId": "../../../etc/passwd", "input": [1]},
        expect_ok=False,
    )
    assert_true(code == 400, "HIGH", "path-like algorithmId not rejected")
    results["security"]["catalog_only"] = "PASS" if code == 400 else "FAIL"

    # health must not expose CLI filesystem path when ok
    code, health = http_json("GET", "/api/health")
    assert_true(code == 200 and health.get("ok") is True, "BLOCKER", f"health not ok: {health}")
    h = json.dumps(health)
    assert_true("proofrun_cli" not in h or "build" not in h.lower() or "\\" not in h,
                "MEDIUM", f"health may expose paths: {health}")
    # stronger: no absolute path
    assert_true("C:" not in h and "/Users/" not in h and "Desktop" not in h,
                "HIGH", f"health absolute path leak: {health}")
    results["security"]["health_no_paths"] = "PASS"

    # shell=False / fixed cli — inspect source
    adapter = (ROOT / "python" / "proofrun_py" / "product" / "adapter.py").read_text(encoding="utf-8")
    assert_true("shell=False" in adapter, "BLOCKER", "adapter missing shell=False")
    assert_true("proofrun_cli" in adapter, "BLOCKER", "adapter not fixed to proofrun_cli")
    assert_true("timeout=" in adapter, "HIGH", "adapter missing timeout")
    results["security"]["adapter"] = "PASS"


def main() -> int:
    print("=== LIVE PRODUCT QA ===")
    code, health = http_json("GET", "/api/health")
    print("health:", code, health)
    assert_true(code == 200 and health and health.get("ok"), "BLOCKER", "server health failed")

    code, catalog = http_json("GET", "/api/catalog")
    algos = [a["id"] for a in catalog["algorithms"]]
    print("catalog:", len(algos), algos)
    assert_true(len(algos) == 10, "BLOCKER", f"expected 10 algos got {len(algos)}")
    results["select"] = "PASS"

    check_ui_assets()

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
    for aid in expected:
        print("exercising", aid)
        exercise_algo(aid)

    negatives()
    security_checks()

    # hygiene note: gitignore presence
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pat in ("build/", "__pycache__/", ".hypothesis/", ".env"):
        assert_true(pat in gi, "MEDIUM", f".gitignore missing {pat}")

    print("\n=== FINDINGS ===")
    if not findings:
        print("NONE")
    else:
        for sev, msg in findings:
            print(f"[{sev}] {msg}")

    blockers = [f for f in findings if f[0] == "BLOCKER"]
    highs = [f for f in findings if f[0] == "HIGH"]
    print("\n=== SUMMARY JSON ===")
    out = {
        "findings": findings,
        "results": results,
        "blocker_count": len(blockers),
        "high_count": len(highs),
        "verdict": "READY FOR HUMAN ACCEPTANCE" if not blockers and not highs else "NOT READY",
    }
    print(json.dumps(out, indent=2))
    Path("reports/live_qa_phase1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0 if not blockers and not highs else 1


if __name__ == "__main__":
    sys.exit(main())
