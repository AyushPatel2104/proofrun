"""Scan committed public-ish trees for secrets / personal paths."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    "node_modules",
    "dist",
    "_deps",
    "__pycache__",
    ".hypothesis",
    "build",
    ".git",
}
# Local smoke outputs are gitignored; still skip if present.
SKIP_PARTS.add("reports")

NEEDLES = [
    re.compile(r"Ayush", re.I),
    re.compile(r"C:\\Users\\", re.I),
    re.compile(r"/Users/Ayush", re.I),
    re.compile(r"GenuineIntel"),
    re.compile(r"BEGIN (RSA |OPENSSH )?PRIVATE KEY"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]+"),
    re.compile(r"(?i)secret\s*[:=]\s*['\"][^'\"]+"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]

ALLOW_NAME_SUBSTR = (
    "GITHUB-RELEASE-CHECKLIST",
    "benchmark-reproduction",
    "github-metadata",
    "_sanitize_example_report",
    "_security_scan_public",
    "_live_product_qa",
    "_final_acceptance_audit",
    "test_security_ux",  # synthetic C:\Users\secret\... fixture for path scrubbing
)


def main() -> None:
    hits: list[str] = []
    roots = [
        ROOT / "cpp",
        ROOT / "python",
        ROOT / "viz",
        ROOT / "schemas",
        ROOT / "catalogs",
        ROOT / "scripts",
        ROOT / "tools",
        ROOT / "docs",
        ROOT / ".github",
    ]
    files = [
        ROOT / "README.md",
        ROOT / "README-DRAFT.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "LICENSE",
        ROOT / ".gitignore",
    ]

    def scan_file(path: Path) -> None:
        if any(part in SKIP_PARTS for part in path.parts):
            return
        if any(a in path.name for a in ALLOW_NAME_SUBSTR):
            return
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return
        for needle in NEEDLES:
            if needle.search(text):
                hits.append(f"{path.relative_to(ROOT)} :: {needle.pattern}")

    for r in roots:
        if not r.exists():
            continue
        for p in r.rglob("*"):
            if p.is_file():
                scan_file(p)
    for f in files:
        if f.exists():
            scan_file(f)

    # Explicit check for example report hygiene
    ex = ROOT / "docs" / "reports" / "examples" / "smoke-bench-report.json"
    text = ex.read_text(encoding="utf-8")
    for bad in ("Ayush", "GenuineIntel", r"C:\Users", "/Users/"):
        if bad in text:
            hits.append(f"examples polluted: {bad}")

    if hits:
        print("SECURITY_SCAN: HITS")
        for h in hits[:50]:
            print(h)
        raise SystemExit(1)
    print("SECURITY_SCAN: CLEAN")


if __name__ == "__main__":
    main()
