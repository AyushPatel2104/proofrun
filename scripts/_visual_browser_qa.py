"""Real Chromium visual QA for ProofRun redesign (Playwright)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

BASE = "http://127.0.0.1:8080"
OUT = Path(__file__).resolve().parents[1] / "reports" / "visual_qa"
findings: list[str] = []


def must(cond: bool, msg: str) -> None:
    if not cond:
        findings.append(msg)


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP — playwright not installed")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    sizes = [
        ("desktop_1920", 1920, 1080),
        ("laptop_1366", 1366, 768),
        ("tablet_834", 834, 1112),
        ("mobile_390", 390, 844),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE + "/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(800)

        # Theme cycle
        for theme in ("dark", "light", "dark"):
            page.evaluate(
                """(t) => {
                  document.documentElement.setAttribute('data-theme', t);
                  localStorage.setItem('proofrun-theme', t);
                  document.documentElement.dispatchEvent(new CustomEvent('proofrun:theme'));
                }""",
                theme,
            )
            page.wait_for_timeout(350)
            got = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
            must(got == theme, f"theme not applied: {theme}")

        # Persist check
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(400)
        persisted = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        must(persisted == "dark", f"theme persistence failed: {persisted}")

        # Screenshots across viewports
        for name, w, h in sizes:
            page.set_viewport_size({"width": w, "height": h})
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUT / f"{name}_home.png"), full_page=False)
            page.locator("#workspace").scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / f"{name}_workspace.png"), full_page=False)

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(BASE + "/", wait_until="networkidle")
        page.wait_for_timeout(600)

        # Layout width check — content should use more than ~1240 on 1920
        metrics = page.evaluate(
            """() => {
              const shell = document.querySelector('.shell-inner');
              const ws = document.querySelector('.workspace');
              const canvas = document.getElementById('bgCanvas');
              return {
                shellW: shell ? shell.getBoundingClientRect().width : 0,
                wsW: ws ? ws.getBoundingClientRect().width : 0,
                bgW: canvas ? canvas.clientWidth : 0,
                bgH: canvas ? canvas.clientHeight : 0,
                hasFlow: !!document.querySelector('.workspace-flow'),
                hasPillars: document.querySelectorAll('.pillar').length,
                examples: document.querySelectorAll('.example-card').length,
                login: document.body.innerText.includes('Login') || document.body.innerText.includes('Sign Up'),
              };
            }"""
        )
        must(metrics["shellW"] >= 1500, f"shell too narrow at 1920: {metrics['shellW']}")
        must(metrics["wsW"] >= 1500, f"workspace too narrow at 1920: {metrics['wsW']}")
        must(metrics["bgW"] >= 1800 and metrics["bgH"] >= 900, f"bg canvas size odd: {metrics}")
        must(metrics["hasFlow"], "workspace flow missing")
        must(metrics["hasPillars"] == 3, "pillars missing")
        must(metrics["examples"] == 3, "examples missing")
        must(not metrics["login"], "fake auth visible")

        # Example load + player
        page.locator(".example-card").first.click()
        page.wait_for_timeout(900)
        canvas_visible = page.evaluate("() => !document.getElementById('arrayCanvas').hidden")
        must(canvas_visible, "example did not reveal visualization canvas")
        page.locator("#btnPlay").click()
        page.wait_for_timeout(700)
        page.locator("#btnPause").click()
        page.locator("#btnStep").click()
        page.locator("#btnReset").click()
        page.screenshot(path=str(OUT / "desktop_1920_example.png"), full_page=False)

        # Live run
        page.locator("#algoSelect").select_option(label="Bubble Sort")
        page.fill("#inputEditor", "7, 3, 9, 1, 5, 2, 8, 4")
        page.locator("#btnRun").click()
        page.wait_for_timeout(2500)
        prove = page.locator("#proveStatus").inner_text()
        must("Verified" in prove or "verified" in prove.lower() or "✓" in prove, f"prove failed: {prove}")
        page.locator("#timeline li").first.click()
        page.wait_for_timeout(200)
        insp = page.locator("#inspector").inner_text()
        must(len(insp.strip()) > 5, "inspector empty after selection")
        page.screenshot(path=str(OUT / "desktop_1920_run.png"), full_page=False)

        # Light theme workspace shot
        page.evaluate(
            """() => {
              document.documentElement.setAttribute('data-theme', 'light');
              localStorage.setItem('proofrun-theme', 'light');
              document.documentElement.dispatchEvent(new CustomEvent('proofrun:theme'));
            }"""
        )
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "desktop_1920_light.png"), full_page=False)

        # Reduced motion static still attractive path
        page.emulate_media(reduced_motion="reduce")
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / "desktop_1920_reduced_motion.png"), full_page=False)

        browser.close()

    report = {"ok": not findings, "findings": findings, "out": str(OUT)}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("VISUAL_QA:")
    if findings:
        for f in findings:
            print("FAIL:", f)
        return 1
    print("PASS — screenshots in", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
