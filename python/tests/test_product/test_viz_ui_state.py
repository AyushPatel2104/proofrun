"""Focused UI-state contracts for timeline empty-state and analysis complexity sync."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAIN_JS = (ROOT / "viz" / "src" / "main.js").read_text(encoding="utf-8")
MAIN_CSS = (ROOT / "viz" / "styles" / "main.css").read_text(encoding="utf-8")
INDEX = (ROOT / "viz" / "index.html").read_text(encoding="utf-8")


def test_empty_state_hidden_overrides_display_flex() -> None:
    """Author .empty-state { display:flex } must not defeat the HTML hidden attribute."""
    assert ".empty-state[hidden]" in MAIN_CSS
    assert "display: none" in MAIN_CSS.split(".empty-state[hidden]")[1].split("}")[0]


def test_timeline_empty_tracks_event_presence() -> None:
    assert 'id="timelineEmpty"' in INDEX
    assert "setTimelineEmptyVisible" in MAIN_JS
    assert "setTimelineEmptyVisible(list.length === 0)" in MAIN_JS
    assert "setTimelineEmptyVisible(true)" in MAIN_JS
    # Cleared / inactive path restores empty and clears leftover rows.
    assert 'timeline.innerHTML = ""' in MAIN_JS


def test_algorithm_change_refreshes_analysis_complexity() -> None:
    """Selecting another algorithm must refresh Analysis Complexity, not leave a prior run's values."""
    assert "function updateAlgoContext()" in MAIN_JS
    assert "function setComplexity(c)" in MAIN_JS
    # Complexity sync lives inside updateAlgoContext (called from renderParams / algoSelect.onchange).
    block = MAIN_JS.split("function updateAlgoContext()")[1].split("function renderLegend")[0]
    assert "setComplexity(c)" in block
    assert "sel.onchange = renderParams" in MAIN_JS


def test_complexity_grid_ids_present() -> None:
    assert 'id="complexityGrid"' in INDEX
    for cid in ("cxBest", "cxAvg", "cxWorst", "cxMem"):
        assert f'id="{cid}"' in INDEX
        assert cid in MAIN_JS
