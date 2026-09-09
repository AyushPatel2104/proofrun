"""Capture ProofRun screenshots via local Chrome/Edge headless (no pip deps)."""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "visual_qa"
BASE = "http://127.0.0.1:8080"

CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]


def browser() -> Path:
    for p in CANDIDATES:
        if p.exists():
            return p
    raise SystemExit("No Chrome/Edge found")


def shot(exe: Path, name: str, url: str, w: int, h: int) -> None:
    out = OUT / name
    if out.exists():
        try:
            out.unlink()
        except OSError:
            pass
    profile = OUT / f"_chrome_profile_{name}"
    profile.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(exe),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={profile}",
        "--virtual-time-budget=4000",
        f"--window-size={w},{h}",
        f"--screenshot={out}",
        url,
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 28
    while time.time() < deadline:
        if out.exists() and out.stat().st_size > 5000:
            time.sleep(0.6)
            break
        if proc.poll() is not None:
            break
        time.sleep(0.3)
    if proc.poll() is None:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    print(f"{'OK' if out.exists() else 'MISS'} {out.name} ({out.stat().st_size if out.exists() else 0})")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    exe = browser()
    print("BROWSER", exe)
    shots = [
        ("desktop_1920_dark.png", f"{BASE}/?theme=dark", 1920, 1080),
        ("desktop_1920_light.png", f"{BASE}/?theme=light", 1920, 1080),
        ("laptop_1366_dark.png", f"{BASE}/?theme=dark", 1366, 768),
        ("tablet_834_dark.png", f"{BASE}/?theme=dark", 834, 1112),
        ("mobile_390_dark.png", f"{BASE}/?theme=dark", 390, 844),
        ("desktop_1920_workspace.png", f"{BASE}/?theme=dark#workspace", 1920, 1080),
        ("desktop_1920_explore_light.png", f"{BASE}/?theme=light#explore", 1920, 1080),
    ]
    for name, url, w, h in shots:
        shot(exe, name, url, w, h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
