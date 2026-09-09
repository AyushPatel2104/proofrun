"""Bridge to trusted proofrun_cli."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union


def project_root() -> Path:
    env = os.environ.get("PROOFRUN_PROJECT_ROOT")
    if env:
        return Path(env)
    # python/proofrun_py/bridge -> repo root 01-PROOFRUN
    return Path(__file__).resolve().parents[3]


def default_cli_path() -> Path:
    root = project_root()
    candidates = [
        root / "build" / "cpp" / "proofrun_cli.exe",
        root / "build" / "cpp" / "proofrun_cli",
        root / "cpp" / "build" / "proofrun_cli.exe",
        root / "cpp" / "build" / "proofrun_cli",
        root / "build" / "proofrun_cli.exe",
        root / "build" / "proofrun_cli",
    ]
    env = os.environ.get("PROOFRUN_CLI")
    if env:
        return Path(env)
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def _run_cli(cmd: List[str]) -> str:
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def run_sort_cli(
    algorithm_id: str,
    values: Sequence[int],
    *,
    trace_path: Optional[Path] = None,
    seed: int = 0,
    cli_path: Optional[Path] = None,
) -> List[int]:
    cli = Path(cli_path) if cli_path else default_cli_path()
    if not cli.exists():
        raise FileNotFoundError(
            f"proofrun_cli not found at {cli}. Build C++ first or set PROOFRUN_CLI."
        )
    csv = ",".join(str(v) for v in values)
    cmd = [str(cli), "sort", algorithm_id, "--input", csv, "--seed", str(seed)]
    if trace_path is not None:
        cmd.extend(["--trace", str(trace_path)])
    line = _run_cli(cmd)
    if not line:
        return []
    return [int(x) for x in line.split(",") if x != ""]


def run_search_cli(
    algorithm_id: str,
    values: Sequence[int],
    target: int,
    *,
    trace_path: Optional[Path] = None,
    seed: int = 0,
    cli_path: Optional[Path] = None,
) -> int:
    cli = Path(cli_path) if cli_path else default_cli_path()
    if not cli.exists():
        raise FileNotFoundError(f"proofrun_cli not found at {cli}")
    csv = ",".join(str(v) for v in values)
    cmd = [
        str(cli),
        "search",
        algorithm_id,
        "--input",
        csv,
        "--target",
        str(target),
        "--seed",
        str(seed),
    ]
    if trace_path is not None:
        cmd.extend(["--trace", str(trace_path)])
    return int(_run_cli(cmd))


def run_array_two_pointer_cli(
    values: Sequence[int],
    target: int,
    *,
    trace_path: Optional[Path] = None,
    seed: int = 0,
    cli_path: Optional[Path] = None,
) -> Union[Tuple[int, int], None]:
    cli = Path(cli_path) if cli_path else default_cli_path()
    if not cli.exists():
        raise FileNotFoundError(f"proofrun_cli not found at {cli}")
    csv = ",".join(str(v) for v in values)
    cmd = [
        str(cli),
        "array",
        "array.two_pointer",
        "--input",
        csv,
        "--target",
        str(target),
        "--seed",
        str(seed),
    ]
    if trace_path is not None:
        cmd.extend(["--trace", str(trace_path)])
    line = _run_cli(cmd)
    if line == "notfound":
        return None
    parts = line.split(",")
    if len(parts) != 3 or parts[0] != "found":
        raise ValueError(f"unexpected two_pointer output: {line}")
    return int(parts[1]), int(parts[2])


def run_array_sliding_window_cli(
    values: Sequence[int],
    window: int,
    *,
    trace_path: Optional[Path] = None,
    seed: int = 0,
    cli_path: Optional[Path] = None,
) -> Tuple[int, int, int]:
    cli = Path(cli_path) if cli_path else default_cli_path()
    if not cli.exists():
        raise FileNotFoundError(f"proofrun_cli not found at {cli}")
    csv = ",".join(str(v) for v in values)
    cmd = [
        str(cli),
        "array",
        "array.sliding_window",
        "--input",
        csv,
        "--window",
        str(window),
        "--seed",
        str(seed),
    ]
    if trace_path is not None:
        cmd.extend(["--trace", str(trace_path)])
    parts = _run_cli(cmd).split(",")
    return int(parts[0]), int(parts[1]), int(parts[2])


def run_array_prefix_sum_cli(
    values: Sequence[int],
    left: int,
    right: int,
    *,
    trace_path: Optional[Path] = None,
    seed: int = 0,
    cli_path: Optional[Path] = None,
) -> int:
    cli = Path(cli_path) if cli_path else default_cli_path()
    if not cli.exists():
        raise FileNotFoundError(f"proofrun_cli not found at {cli}")
    csv = ",".join(str(v) for v in values)
    cmd = [
        str(cli),
        "array",
        "array.prefix_sum",
        "--input",
        csv,
        "--query",
        f"{left},{right}",
        "--seed",
        str(seed),
    ]
    if trace_path is not None:
        cmd.extend(["--trace", str(trace_path)])
    return int(_run_cli(cmd))
