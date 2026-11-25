#!/usr/bin/env python3
"""Build a static GitHub Pages–compatible SEE-only public demo into site/.

Does not deploy. Does not touch the local product server path.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIZ = ROOT / "viz"
OUT = ROOT / "site"

FOOTER_DISCLOSURE = (
    "Public demo uses prerecorded traces. Live execution is available in the local product."
)

EXAMPLE_META = {
    "sort.bubblesort": ("Sorting", "Adjacent swaps until the array is ordered."),
    "sort.insertionsort": ("Sorting", "Insert each key into a growing sorted prefix."),
    "sort.selectionsort": ("Sorting", "Select the minimum and swap it into place."),
    "sort.mergesort": ("Sorting", "Divide, sort halves, then merge."),
    "sort.quicksort": ("Sorting", "Partition around a pivot and recurse."),
    "search.linear_search": ("Searching", "Scan left to right for the target."),
    "search.binary_search": ("Searching", "Halve the search space on a sorted array."),
    "array.two_pointer": ("Arrays", "Two pointers find a pair summing to a target."),
    "array.sliding_window": ("Arrays", "Maintain a moving fixed-length window."),
    "array.prefix_sum": ("Arrays", "Precompute prefixes for range queries."),
}


def _catalog_payload() -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "python"))
    from proofrun_py.product.workflow import catalog_payload

    return catalog_payload()


def _copy_tree() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # Static assets (relative paths preserved)
    for name in ("styles", "src", "public"):
        shutil.copytree(VIZ / name, OUT / name)


def _example_cards(algorithms: list[dict]) -> str:
    cards = []
    for a in algorithms:
        aid = a["id"]
        family, desc = EXAMPLE_META.get(aid, (a.get("family", "Algorithm"), a.get("explanation", "")))
        trace = f"public/traces/{aid}__demo.trace.json"
        cards.append(
            "\n".join(
                [
                    f'        <button type="button" class="example-card" data-example="{trace}" '
                    f'data-algo="{aid}" role="listitem">',
                    f'          <span class="ex-family">{family}</span>',
                    f'          <span class="ex-name">{a["name"]}</span>',
                    f'          <span class="ex-desc">{desc}</span>',
                    '          <span class="ex-meta">Canned demo · replay</span>',
                    "        </button>",
                ]
            )
        )
    return "\n".join(cards)


def _transform_html(html: str, *, base: str, algorithms: list[dict]) -> str:
    # Demo mode marker for main.js
    html = html.replace('<html lang="en" data-theme="dark">', '<html lang="en" data-theme="dark" data-demo="true">', 1)
    html = html.replace("<body>", '<body class="demo-mode">', 1)

    if base and base != "./" and base != "/":
        # Ensure trailing slash for relative resolution under project Pages.
        base_href = base if base.endswith("/") else base + "/"
        html = html.replace(
            '<link rel="stylesheet" href="styles/main.css" />',
            f'<base href="{base_href}" />\n  <link rel="stylesheet" href="styles/main.css" />',
            1,
        )

    html = html.replace(
        '<p class="eyebrow">Local algorithm laboratory</p>',
        '<p class="eyebrow">Public static demo</p>',
        1,
    )
    html = html.replace(
        '<p class="core-message">Run algorithms. See every step. Verify every result. Measure performance.</p>',
        '<p class="core-message">Replay real ExecutionTrace demos step by step in the browser.</p>',
        1,
    )
    html = html.replace(
        '<a class="btn btn-primary" href="#workspace">Open Workspace</a>',
        '<a class="btn btn-primary" href="#explore">Browse demos</a>',
        1,
    )
    html = html.replace(
        "Load a real canned ExecutionTrace (replay only). Live Prove / Measure still require Run in the workspace.",
        "Choose a canned ExecutionTrace to explore how each algorithm moves state.",
        1,
    )
    # Hide engine status pill on public demo (local product keeps it).
    html = html.replace(
        '<p id="serverStatus" class="engine-pill" role="status" aria-live="polite">Checking engine…</p>',
        '<p id="serverStatus" class="engine-pill" role="status" aria-live="polite" hidden></p>',
        1,
    )
    html = html.replace(
        '<p>ProofRun · local · free · MIT · v0.1.0</p>',
        (
            '<p>ProofRun · public demo · free · MIT · v0.1.0</p>\n'
            f'    <p class="demo-footer-note">{FOOTER_DISCLOSURE}</p>'
        ),
        1,
    )

    # Replace the 3-card explore grid with all catalog demos.
    cards = _example_cards(algorithms)
    html = re.sub(
        r'<div class="example-grid" role="list">.*?</div>\s*</div>\s*</section>',
        f'<div class="example-grid" role="list">\n{cards}\n      </div>\n    </div>\n  </section>',
        html,
        count=1,
        flags=re.DOTALL,
    )

    # Soften live-only empty copy for demo.
    html = html.replace(
        "Run an algorithm to inspect its execution step by step.",
        "Choose a demo to inspect its ExecutionTrace step by step.",
        1,
    )
    html = html.replace(
        "Run an algorithm to populate the execution history.",
        "Load a canned demo to populate the execution history.",
        1,
    )
    return html


def build(*, base: str) -> Path:
    catalog = _catalog_payload()
    algorithms = catalog["algorithms"]
    if len(algorithms) != 10:
        raise SystemExit(f"expected 10 algorithms, got {len(algorithms)}")

    for a in algorithms:
        trace = VIZ / "public" / "traces" / f'{a["id"]}__demo.trace.json'
        if not trace.is_file():
            raise SystemExit(f"missing demo trace: {trace}")

    _copy_tree()
    (OUT / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    html = (VIZ / "index.html").read_text(encoding="utf-8")
    html = _transform_html(html, base=base, algorithms=algorithms)
    (OUT / "index.html").write_text(html, encoding="utf-8")

    # Marker for verification / CI.
    (OUT / ".demo-build.json").write_text(
        json.dumps(
            {
                "mode": "static-see-demo",
                "algorithms": [a["id"] for a in algorithms],
                "base": base,
                "footerDisclosure": FOOTER_DISCLOSURE,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"public demo built → {OUT} (base={base!r}, algorithms={len(algorithms)})")
    return OUT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="/proofrun/",
        help="GitHub Pages base href (project site default: /proofrun/). Use ./ for relative-only local root serve.",
    )
    args = parser.parse_args()
    build(base=args.base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
