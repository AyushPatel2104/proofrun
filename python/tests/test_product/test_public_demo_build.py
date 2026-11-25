"""Contracts for the static SEE-only public demo build."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from build_public_demo import DEMO_BANNER, build  # noqa: E402


def test_build_public_demo_emits_static_site(tmp_path, monkeypatch) -> None:
    # Build into the real site/ path (gitignored); assert structure.
    out = build(base="/proofrun/")
    assert out.is_dir()
    assert (out / "index.html").is_file()
    assert (out / "catalog.json").is_file()
    assert (out / "styles" / "main.css").is_file()
    assert (out / "src" / "main.js").is_file()
    assert (out / "src" / "player.js").is_file()
    assert (out / "public" / "traces").is_dir()

    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'data-demo="true"' in html
    assert 'class="demo-mode"' in html
    assert DEMO_BANNER in html
    assert '<base href="/proofrun/"' in html
    assert "/api/" not in html

    catalog = json.loads((out / "catalog.json").read_text(encoding="utf-8"))
    ids = [a["id"] for a in catalog["algorithms"]]
    assert len(ids) == 10
    for aid in ids:
        trace = out / "public" / "traces" / f"{aid}__demo.trace.json"
        assert trace.is_file(), aid
        assert f'data-algo="{aid}"' in html

    main_js = (out / "src" / "main.js").read_text(encoding="utf-8")
    assert "DEMO_MODE" in main_js
    assert "assetUrl" in main_js

    marker = json.loads((out / ".demo-build.json").read_text(encoding="utf-8"))
    assert marker["mode"] == "static-see-demo"
    assert marker["algorithms"] == ids


def test_local_product_html_is_not_demo_by_default() -> None:
    html = (ROOT / "viz" / "index.html").read_text(encoding="utf-8")
    assert 'data-demo="true"' not in html
    assert "demo-banner" not in html
