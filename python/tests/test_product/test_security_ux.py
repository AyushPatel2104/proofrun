"""Security-oriented product boundary tests."""

from __future__ import annotations

from proofrun_py.product.errors import sanitize_user_error
from proofrun_py.product.workflow import catalog_payload, health


def test_sanitize_strips_paths_and_maps_sorted():
    msg = sanitize_user_error(
        r"binary_search requires nondecreasing (sorted) --input C:\Users\secret\proj"
    )
    assert "C:\\Users" not in msg
    assert "sorted" in msg.lower()
    assert "Fix:" in msg


def test_sanitize_does_not_echo_raw_unknown():
    msg = sanitize_user_error("weird internal boom /home/runner/x")
    assert "/home/runner" not in msg
    assert "Fix:" in msg


def test_health_omits_filesystem_paths_when_ok():
    h = health()
    if h["ok"]:
        assert "cli" not in h or not str(h.get("cli", "")).startswith("/")
        blob = str(h)
        assert ":\\" not in blob


def test_catalog_exposes_legend_and_preconditions():
    algos = {a["id"]: a for a in catalog_payload()["algorithms"]}
    assert algos["search.binary_search"]["params"]["requiresSorted"] is True
    assert "sorted" in algos["search.binary_search"]["params"]["precondition"].lower()
    assert algos["search.binary_search"]["params"]["legend"]
    assert "K" in algos["array.sliding_window"]["params"]["precondition"]
    assert "L" in algos["array.prefix_sum"]["params"]["precondition"] or "Range" in algos["array.prefix_sum"]["params"]["precondition"]
