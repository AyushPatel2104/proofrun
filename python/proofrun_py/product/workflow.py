"""Orchestrate SELECT → RUN → SEE → PROVE → MEASURE summary."""

from __future__ import annotations

from typing import Any, Dict

from proofrun_py.catalog import algorithms, find
from proofrun_py.generators import generate_array
from proofrun_py.product.adapter import resolve_cli, run_trusted
from proofrun_py.product.limits import MAX_ARRAY_GENERATE, MAX_BENCHMARK_N
from proofrun_py.product.measure import controlled_measure, environment_info
from proofrun_py.product.prove import format_result_summary, prove
from proofrun_py.product.validate import (
    ProductRequest,
    ValidationError,
    catalog_param_schema,
    validate_product_request,
)


def catalog_payload() -> Dict[str, Any]:
    items = []
    for a in algorithms():
        if a.get("status") != "implemented":
            continue
        items.append(
            {
                "id": a["id"],
                "name": a["name"],
                "family": a["family"],
                "complexity": a["complexity"],
                "explanation": a["explanation"],
                "visualizable": a.get("visualizable", False),
                "benchmarkable": a.get("benchmarkable", False),
                "params": catalog_param_schema(a),
            }
        )
    return {"algorithms": items}


def generate_input(body: Dict[str, Any]) -> Dict[str, Any]:
    kind = body.get("kind", "random")
    n = body.get("n", 8)
    seed = body.get("seed", 42)
    algo = body.get("algorithmId")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or n > MAX_ARRAY_GENERATE:
        raise ValidationError(f"n must be an integer in 0..{MAX_ARRAY_GENERATE}")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValidationError("seed must be an integer")
    values = generate_array(str(kind), n, seed)
    meta = find(algo) if isinstance(algo, str) else None
    if meta and meta["id"] in ("search.binary_search", "array.two_pointer"):
        values = sorted(values)
    params: Dict[str, Any] = {}
    if meta:
        if meta["family"] == "searching" or meta["id"] == "array.two_pointer":
            params["target"] = values[n // 2] if values else 0
        if meta["id"] == "array.sliding_window":
            params["window"] = max(1, n // 3) if n else 1
        if meta["id"] == "array.prefix_sum" and n > 0:
            params["left"] = 0
            params["right"] = n - 1
    return {"input": values, "params": params, "kind": kind, "seed": seed, "n": n}


def run_workflow(body: Dict[str, Any]) -> Dict[str, Any]:
    req = validate_product_request(body)
    meta = find(req.algorithm_id)
    assert meta is not None
    stdout, trace, elapsed = run_trusted(req, with_trace=True)
    correctness = prove(req, stdout)
    result = format_result_summary(req, stdout)
    return {
        "algorithm": {
            "id": meta["id"],
            "name": meta["name"],
            "family": meta["family"],
            "complexity": meta["complexity"],
            "explanation": meta["explanation"],
        },
        "input": req.values,
        "params": {
            "target": req.target,
            "window": req.window,
            "left": req.query_left,
            "right": req.query_right,
            "seed": req.seed,
        },
        "result": result,
        "correctness": correctness,
        "trace": trace,
        "measure": {
            "interactive": {
                "kind": "interactive_execution_timing",
                "disclaimer": (
                    "Wall time for this single Run (includes process start). "
                    "Not a rigorous benchmark."
                ),
                "runtime_s": elapsed,
                "n": len(req.values),
            },
            "controlled": None,
            "memory_bytes": None,
        },
        "environment": environment_info(),
    }


def benchmark_workflow(body: Dict[str, Any]) -> Dict[str, Any]:
    # Allow generating from n if input omitted
    if "input" not in body and "values" not in body:
        n = body.get("n", 32)
        seed = body.get("seed", 42)
        gen = generate_input(
            {
                "algorithmId": body.get("algorithmId"),
                "kind": body.get("kind", "random"),
                "n": n,
                "seed": seed,
            }
        )
        body = {**body, "input": gen["input"], "params": {**(body.get("params") or {}), **gen["params"]}}
    req = validate_product_request(body)
    if len(req.values) > MAX_BENCHMARK_N:
        raise ValidationError(f"Benchmark input capped at n≤{MAX_BENCHMARK_N}")
    controlled = controlled_measure(req)
    meta = find(req.algorithm_id)
    assert meta is not None
    return {
        "algorithm": {"id": meta["id"], "name": meta["name"]},
        "inputSize": len(req.values),
        "benchmark": controlled,
    }


def health() -> Dict[str, Any]:
    try:
        resolve_cli()
        return {
            "ok": True,
            "engine": "ready",
            "product": "ProofRun",
            "schemaVersion": "1.0",
            "message": "Trusted engine connected.",
        }
    except ValidationError as exc:
        return {
            "ok": False,
            "engine": "missing",
            "product": "ProofRun",
            "schemaVersion": "1.0",
            "message": str(exc),
        }
