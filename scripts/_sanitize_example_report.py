"""One-shot sanitizer for committed smoke example reports. Not part of product API."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs" / "reports" / "examples" / "smoke-bench-report.json"
MD_PATH = ROOT / "docs" / "reports" / "examples" / "smoke-bench-report.md"


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    data["environment"] = {
        "label": "Example benchmark environment",
        "note": (
            "Illustrative smoke timings from a single anonymous development machine. "
            "Not a universal performance claim. Usernames, absolute paths, and unique "
            "CPU model strings removed."
        ),
        "os_family": "Windows",
        "arch": "AMD64",
        "cpu_count": 12,
        "python_version": "3.11",
        "processor_class": "x86_64",
    }
    data["notes"] = (
        "Smoke timings include process spawn overhead and are not comparable to "
        "in-process Google Benchmark results. Use proofrun_sort_bench / "
        "proofrun_search_array_bench for microbenchmarks. "
        "Committed example environment is sanitized for public publication."
    )
    JSON_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# ProofRun Smoke Benchmark Summary",
        "",
        "**Example benchmark environment** (sanitized for public docs).",
        "",
        data["environment"]["note"],
        "",
        f"Profile: `{data.get('profile')}`",
        "",
        data.get("notes", ""),
        "",
        "| Algorithm | n | median_s | p95_s |",
        "| --- | ---: | ---: | ---: |",
    ]
    for r in data["results"]:
        lines.append(
            f"| {r['algorithmId']} | {r['n']} | "
            f"{r['runtime_s_median']:.6f} | {r['runtime_s_p95']:.6f} |"
        )
    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    text = JSON_PATH.read_text(encoding="utf-8")
    for bad in ("Ayush", "GenuineIntel", "Users\\\\", "C:\\\\Users"):
        if bad in text:
            raise SystemExit(f"sanitization failed: found {bad!r}")
    if "label" not in data["environment"]:
        raise SystemExit("missing environment.label")
    print("re-sanitized", JSON_PATH)


if __name__ == "__main__":
    main()
