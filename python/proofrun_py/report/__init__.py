"""Report helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def write_markdown_summary(report: Dict[str, Any], path: Path) -> None:
    lines = [
        "# ProofRun Smoke Benchmark Summary",
        "",
        f"Profile: `{report.get('profile')}`",
        "",
        report.get("notes", ""),
        "",
        "| Algorithm | n | median_s | p95_s |",
        "| --- | ---: | ---: | ---: |",
    ]
    for r in report.get("results", []):
        lines.append(
            f"| {r['algorithmId']} | {r['n']} | {r['runtime_s_median']:.6f} | {r['runtime_s_p95']:.6f} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_report(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
