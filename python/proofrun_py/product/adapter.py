"""Trusted adapter: invokes fixed proofrun_cli only (never user-supplied paths)."""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from proofrun_py.bridge import default_cli_path
from proofrun_py.catalog import find
from proofrun_py.product.errors import sanitize_user_error
from proofrun_py.product.validate import ProductRequest, ValidationError


def resolve_cli() -> Path:
    cli = default_cli_path()
    if not cli.exists():
        raise ValidationError(
            "The ProofRun engine is not built yet.\n"
            "Why: live Run needs the trusted C++ CLI.\n"
            "Fix: build with scripts/build_cpp.ps1 (Windows) or scripts/build_cpp.sh, "
            "then restart the product server."
        )
    if cli.name not in ("proofrun_cli", "proofrun_cli.exe"):
        raise ValidationError(
            "Engine configuration is invalid.\n"
            "Why: only the trusted proofrun_cli binary may run.\n"
            "Fix: unset PROOFRUN_CLI overrides that point elsewhere, then restart."
        )
    return cli.resolve()


def _csv(values: List[int]) -> str:
    return ",".join(str(v) for v in values)


def build_cli_argv(cli: Path, req: ProductRequest, trace_path: Optional[Path]) -> List[str]:
    meta = find(req.algorithm_id)
    assert meta is not None
    family = meta["family"]
    cmd: List[str] = [str(cli)]

    if family == "sorting":
        cmd += ["sort", req.algorithm_id, "--input", _csv(req.values), "--seed", str(req.seed)]
    elif family == "searching":
        cmd += [
            "search",
            req.algorithm_id,
            "--input",
            _csv(req.values),
            "--target",
            str(req.target),
            "--seed",
            str(req.seed),
        ]
    elif family == "arrays":
        cmd += ["array", req.algorithm_id, "--input", _csv(req.values), "--seed", str(req.seed)]
        if req.algorithm_id == "array.two_pointer":
            cmd += ["--target", str(req.target)]
        elif req.algorithm_id == "array.sliding_window":
            cmd += ["--window", str(req.window)]
        elif req.algorithm_id == "array.prefix_sum":
            cmd += ["--query", f"{req.query_left},{req.query_right}"]
        else:
            raise ValidationError(
                "Unsupported algorithm.\n"
                "Why: only catalog array algorithms are wired.\n"
                "Fix: choose an algorithm from the dropdown."
            )
    else:
        raise ValidationError(
            "Unsupported algorithm family.\n"
            "Why: the request is outside the trusted catalog families.\n"
            "Fix: choose a supported algorithm."
        )

    if trace_path is not None:
        cmd += ["--trace", str(trace_path)]
    return cmd


def run_trusted(req: ProductRequest, *, with_trace: bool = True) -> Tuple[str, Optional[Dict[str, Any]], float]:
    """Run trusted CLI. Returns (stdout, trace_dict_or_None, elapsed_seconds)."""
    cli = resolve_cli()
    trace_obj = None
    with tempfile.TemporaryDirectory(prefix="proofrun_product_") as td:
        trace_path = Path(td) / "trace.json" if with_trace else None
        cmd = build_cli_argv(cli, req, trace_path)
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValidationError(
                "The run timed out.\n"
                "Why: execution exceeded the 30s safety limit.\n"
                "Fix: use a smaller input and try again."
            ) from exc
        elapsed = time.perf_counter() - t0
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "execution failed").strip()
            raise ValidationError(sanitize_user_error(err))
        stdout = (proc.stdout or "").strip()
        if with_trace:
            if trace_path is None or not trace_path.exists():
                raise ValidationError(
                    "Execution finished but no trace was produced.\n"
                    "Why: visualization needs an ExecutionTrace.\n"
                    "Fix: retry Run; if it persists, rebuild the C++ engine."
                )
            trace_obj = json.loads(trace_path.read_text(encoding="utf-8"))
            if trace_obj.get("schemaVersion") != "1.0":
                raise ValidationError(
                    "Unsupported trace format.\n"
                    "Why: the UI expects schemaVersion 1.0.\n"
                    "Fix: rebuild the engine from this repository."
                )
            if not trace_obj.get("events"):
                raise ValidationError(
                    "Trace is empty.\n"
                    "Why: there are no steps to visualize.\n"
                    "Fix: retry with a different input."
                )
        return stdout, trace_obj, elapsed
