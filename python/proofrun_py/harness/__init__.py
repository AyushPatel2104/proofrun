"""Benchmark harness — orchestrates smoke runs and structured reports.



Does not claim universal performance truths. Results are environment-local.

"""



from __future__ import annotations



import json

import os

import platform

import statistics

import subprocess

import time

from datetime import datetime, timezone

from pathlib import Path

from typing import Any, Dict, List



from proofrun_py.bridge import default_cli_path, project_root

from proofrun_py.catalog import benchmarkable_ids, find

from proofrun_py.generators import generate_array

from proofrun_py.oracles import (

    binary_search_oracle,

    linear_search_oracle,

    max_sum_window_oracle,

    prefix_range_oracle,

    sort_oracle,

    two_sum_sorted_oracle,

)





def _git_meta() -> Dict[str, Any]:

    root = project_root()

    commit = "unknown"

    dirty = False

    try:

        commit = subprocess.check_output(

            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL

        ).strip()

        status = subprocess.check_output(

            ["git", "status", "--porcelain"], cwd=root, text=True, stderr=subprocess.DEVNULL

        )

        dirty = bool(status.strip())

    except (OSError, subprocess.SubprocessError):

        commit = "unknown"

        dirty = False

    return {"git_commit": commit, "git_dirty": dirty}





def _env_meta() -> Dict[str, Any]:

    meta = {

        "timestamp_utc": datetime.now(timezone.utc).isoformat(),

        "os": platform.platform(),

        "arch": platform.machine(),

        "cpu_count": os.cpu_count(),

        "python_version": platform.python_version(),

        "processor": platform.processor(),

    }

    meta.update(_git_meta())

    return meta





def _time_cmd(cli: Path, cmd: List[str], warmup: int, repeats: int, check) -> List[float]:

    times: List[float] = []

    for i in range(warmup + repeats):

        t0 = time.perf_counter()

        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)

        elapsed = time.perf_counter() - t0

        check(proc.stdout.strip())

        if i >= warmup:

            times.append(elapsed)

    return times





def _time_algorithm(cli: Path, algo: str, n: int, seed: int, repeats: int, warmup: int) -> List[float]:

    meta = find(algo)

    if meta is None:

        raise KeyError(algo)

    family = meta["family"]



    if family == "sorting":

        values = generate_array("random", n, seed=seed)

        csv = ",".join(str(v) for v in values)

        expected = sort_oracle(values)



        def check(out: str) -> None:

            got = [] if not out else [int(x) for x in out.split(",") if x != ""]

            if got != expected:

                raise AssertionError(f"correctness_gate failed for {algo}")



        return _time_cmd(

            cli,

            [str(cli), "sort", algo, "--input", csv, "--seed", str(seed)],

            warmup,

            repeats,

            check,

        )



    if family == "searching":

        values = generate_array("random", n, seed=seed)

        if algo == "search.binary_search":

            values = sorted(values)

        target = values[n // 2] if values else 0

        csv = ",".join(str(v) for v in values)

        if algo == "search.linear_search":

            expected = linear_search_oracle(values, target)

        else:

            expected = binary_search_oracle(values, target)



        def check(out: str) -> None:

            idx = int(out)

            if algo == "search.binary_search":

                if expected < 0:

                    if idx != -1:

                        raise AssertionError(f"correctness_gate failed for {algo}")

                elif idx < 0 or values[idx] != target:

                    raise AssertionError(f"correctness_gate failed for {algo}")

            elif idx != expected:

                raise AssertionError(f"correctness_gate failed for {algo}")



        return _time_cmd(

            cli,

            [str(cli), "search", algo, "--input", csv, "--target", str(target), "--seed", str(seed)],

            warmup,

            repeats,

            check,

        )



    if family == "arrays":

        if algo == "array.two_pointer":

            values = sorted(generate_array("random", n, seed=seed))

            target = values[0] + values[-1] if len(values) >= 2 else 0

            csv = ",".join(str(v) for v in values)

            expected = two_sum_sorted_oracle(values, target)



            def check(out: str) -> None:

                if expected is None:

                    if out != "notfound":

                        raise AssertionError(f"correctness_gate failed for {algo}")

                else:

                    parts = out.split(",")

                    if parts[0] != "found" or values[int(parts[1])] + values[int(parts[2])] != target:

                        raise AssertionError(f"correctness_gate failed for {algo}")



            return _time_cmd(

                cli,

                [

                    str(cli),

                    "array",

                    algo,

                    "--input",

                    csv,

                    "--target",

                    str(target),

                    "--seed",

                    str(seed),

                ],

                warmup,

                repeats,

                check,

            )



        if algo == "array.sliding_window":

            values = generate_array("random", n, seed=seed)

            k = max(1, n // 8)

            csv = ",".join(str(v) for v in values)

            expected = max_sum_window_oracle(values, k)

            assert expected is not None



            def check(out: str) -> None:

                parts = out.split(",")

                if int(parts[0]) != expected[0]:

                    raise AssertionError(f"correctness_gate failed for {algo}")



            return _time_cmd(

                cli,

                [

                    str(cli),

                    "array",

                    algo,

                    "--input",

                    csv,

                    "--window",

                    str(k),

                    "--seed",

                    str(seed),

                ],

                warmup,

                repeats,

                check,

            )



        if algo == "array.prefix_sum":

            values = generate_array("random", n, seed=seed)

            left, right = 0, n - 1

            csv = ",".join(str(v) for v in values)

            expected = prefix_range_oracle(values, left, right)

            assert expected is not None



            def check(out: str) -> None:

                if int(out) != expected:

                    raise AssertionError(f"correctness_gate failed for {algo}")



            return _time_cmd(

                cli,

                [

                    str(cli),

                    "array",

                    algo,

                    "--input",

                    csv,

                    "--query",

                    f"{left},{right}",

                    "--seed",

                    str(seed),

                ],

                warmup,

                repeats,

                check,

            )



    raise ValueError(f"unsupported family/algorithm for smoke: {algo}")





def run_smoke(output_path: Path) -> Dict[str, Any]:

    cli = default_cli_path()

    if not cli.exists():

        raise FileNotFoundError(f"CLI missing: {cli}")



    sizes = [32, 64]

    warmup = 2

    repeats = 5

    results = []

    for algo in benchmarkable_ids():

        for n in sizes:

            times = _time_algorithm(cli, algo, n, seed=42 + n, repeats=repeats, warmup=warmup)

            results.append(

                {

                    "algorithmId": algo,

                    "n": n,

                    "seed": 42 + n,

                    "runs": repeats,

                    "warmup": warmup,

                    "runtime_s_median": statistics.median(times),

                    "runtime_s_p95": sorted(times)[max(0, int(0.95 * (len(times) - 1)))],

                    "runtime_s_min": min(times),

                    "runtime_s_max": max(times),

                    "correctness_gate": True,

                    "memory_bytes": None,

                    "memory_note": (

                        "Memory intentionally unavailable in smoke harness. "

                        "Cross-platform RSS/allocator profiling is deferred; "

                        "see docs/benchmark-reproduction.md."

                    ),

                }

            )



    report = {

        "schemaVersion": "1.0",

        "profile": "smoke",

        "environment": _env_meta(),

        "results": results,

        "notes": (

            "Smoke timings include process spawn overhead and are not comparable to "

            "in-process Google Benchmark results. Use proofrun_sort_bench / "

            "proofrun_search_array_bench for microbenchmarks."

        ),

    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


