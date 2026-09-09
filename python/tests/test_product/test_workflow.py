"""Product workflow integration tests."""

from __future__ import annotations

import json

import pytest

from proofrun_py.bridge import default_cli_path
from proofrun_py.product.validate import ValidationError, validate_product_request
from proofrun_py.product.workflow import (
    benchmark_workflow,
    catalog_payload,
    generate_input,
    health,
    run_workflow,
)


@pytest.fixture(scope="module")
def require_cli():
    if not default_cli_path().exists():
        pytest.skip("proofrun_cli not built")


def test_catalog_has_ten_algorithms():
    cats = catalog_payload()["algorithms"]
    assert len(cats) == 10
    names = {a["name"] for a in cats}
    assert "Bubble Sort" in names
    assert "Binary Search" in names
    for a in cats:
        assert "params" in a
        assert a["id"]


def test_reject_unknown_algorithm():
    with pytest.raises(ValidationError, match="Unsupported"):
        validate_product_request({"algorithmId": "sort.nosuch", "input": [1, 2]})


def test_reject_oversized_input():
    with pytest.raises(ValidationError, match="too long"):
        validate_product_request({"algorithmId": "sort.bubblesort", "input": list(range(65))})


def test_reject_malformed_input():
    with pytest.raises(ValidationError, match="Malformed"):
        validate_product_request({"algorithmId": "sort.bubblesort", "input": "1,x,3"})


def test_binary_search_precondition():
    with pytest.raises(ValidationError, match="sorted"):
        validate_product_request(
            {"algorithmId": "search.binary_search", "input": [3, 1, 2], "params": {"target": 1}}
        )


def test_two_pointer_precondition():
    with pytest.raises(ValidationError, match="sorted"):
        validate_product_request(
            {"algorithmId": "array.two_pointer", "input": [3, 1, 2], "params": {"target": 4}}
        )


def test_sliding_window_k_validation():
    with pytest.raises(ValidationError, match="invalid"):
        validate_product_request(
            {"algorithmId": "array.sliding_window", "input": [1, 2, 3], "params": {"window": 5}}
        )


def test_prefix_sum_range_validation():
    with pytest.raises(ValidationError, match="invalid"):
        validate_product_request(
            {
                "algorithmId": "array.prefix_sum",
                "input": [1, 2, 3],
                "params": {"left": 2, "right": 1},
            }
        )


def test_missing_target():
    with pytest.raises(ValidationError, match="Target"):
        validate_product_request({"algorithmId": "search.linear_search", "input": [1, 2]})


def test_run_sort_workflow(require_cli):
    out = run_workflow({"algorithmId": "sort.bubblesort", "input": [3, 1, 2]})
    assert out["correctness"]["status"] == "PASS"
    assert out["result"]["value"] == [1, 2, 3]
    assert out["trace"]["schemaVersion"] == "1.0"
    assert out["trace"]["events"][0]["type"] == "init"
    assert out["trace"]["events"][-1]["type"] == "done"
    assert out["measure"]["interactive"]["runtime_s"] >= 0
    assert out["measure"]["memory_bytes"] is None


def test_run_binary_search_workflow(require_cli):
    out = run_workflow(
        {
            "algorithmId": "search.binary_search",
            "input": [1, 3, 5, 7],
            "params": {"target": 5},
        }
    )
    assert out["correctness"]["status"] == "PASS"
    assert out["result"]["found"] is True
    assert out["trace"]["algorithmId"] == "search.binary_search"


def test_run_sliding_and_prefix(require_cli):
    sw = run_workflow(
        {"algorithmId": "array.sliding_window", "input": [2, 1, 5, 3], "params": {"window": 2}}
    )
    assert sw["correctness"]["status"] == "PASS"
    ps = run_workflow(
        {
            "algorithmId": "array.prefix_sum",
            "input": [2, 4, 6],
            "params": {"left": 0, "right": 2},
        }
    )
    assert ps["correctness"]["status"] == "PASS"
    assert ps["result"]["value"] == 12


def test_run_two_pointer(require_cli):
    out = run_workflow(
        {"algorithmId": "array.two_pointer", "input": [1, 2, 4, 7], "params": {"target": 6}}
    )
    assert out["correctness"]["status"] == "PASS"
    assert out["result"]["found"] is True


def test_generate_respects_sorted_algos():
    data = generate_input(
        {"algorithmId": "search.binary_search", "kind": "random", "n": 10, "seed": 1}
    )
    vals = data["input"]
    assert vals == sorted(vals)
    assert "target" in data["params"]


def test_benchmark_workflow(require_cli):
    out = benchmark_workflow(
        {"algorithmId": "sort.quicksort", "input": list(range(16, 0, -1))}
    )
    assert out["benchmark"]["kind"] == "controlled_process_repeats"
    assert out["benchmark"]["memory_bytes"] is None
    assert out["benchmark"]["runtime_s_median"] > 0


def test_health_reports_cli(require_cli):
    h = health()
    assert h["ok"] is True


def test_fault_injection_prove_detects_mismatch(require_cli, monkeypatch):
    from proofrun_py.product import prove as prove_mod
    from proofrun_py.product.validate import ProductRequest

    req = ProductRequest(algorithm_id="sort.bubblesort", values=[3, 1, 2])
    bad = prove_mod.prove(req, "3,1,2")  # unsorted stdout
    assert bad["status"] == "FAIL"


def test_trace_json_roundtrip_schema(require_cli):
    out = run_workflow({"algorithmId": "sort.insertionsort", "input": [4, 2]})
    raw = json.dumps(out["trace"])
    trace = json.loads(raw)
    assert "events" in trace and "finalState" in trace
