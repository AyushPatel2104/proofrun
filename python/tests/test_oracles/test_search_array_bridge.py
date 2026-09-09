import json

import pytest

from proofrun_py.bridge import (
    default_cli_path,
    run_array_prefix_sum_cli,
    run_array_sliding_window_cli,
    run_array_two_pointer_cli,
    run_search_cli,
)
from proofrun_py.generators import generate_array
from proofrun_py.oracles import (
    binary_search_oracle,
    linear_search_oracle,
    max_sum_window_oracle,
    prefix_range_oracle,
    two_sum_sorted_oracle,
)


@pytest.fixture(scope="session")
def cli():
    path = default_cli_path()
    if not path.exists():
        pytest.skip(f"proofrun_cli not built: {path}")
    return path


@pytest.mark.parametrize(
    "kind,n,seed,target",
    [
        ("empty", 0, 1, 5),
        ("single", 1, 2, None),
        ("random", 20, 3, None),
        ("duplicates", 15, 4, 2),
        ("negatives", 12, 5, None),
    ],
)
def test_linear_search_bridge(cli, kind, n, seed, target, tmp_path):
    values = generate_array(kind, n, seed)
    if target is None:
        target = values[0] if values else 99
    trace = tmp_path / "linear.trace.json" if values else None
    idx = run_search_cli(
        "search.linear_search", values, target, trace_path=trace, seed=seed, cli_path=cli
    )
    assert idx == linear_search_oracle(values, target)
    if trace is not None:
        data = json.loads(trace.read_text(encoding="utf-8"))
        assert data["events"][0]["type"] == "init"
        assert data["events"][-1]["type"] == "done"


@pytest.mark.parametrize("n,seed", [(1, 1), (8, 2), (32, 3), (50, 4)])
def test_binary_search_bridge(cli, n, seed, tmp_path):
    values = sorted(generate_array("random", n, seed))
    target = values[n // 3]
    missing = max(values) + 100
    trace = tmp_path / "binary.trace.json"
    idx = run_search_cli(
        "search.binary_search", values, target, trace_path=trace, seed=seed, cli_path=cli
    )
    assert values[idx] == target
    assert run_search_cli("search.binary_search", values, missing, cli_path=cli) == -1
    assert binary_search_oracle(values, missing) == -1
    data = json.loads(trace.read_text(encoding="utf-8"))
    assert data["algorithmId"] == "search.binary_search"


def test_binary_search_rejects_unsorted(cli):
    import subprocess
    from proofrun_py.bridge import default_cli_path

    proc = subprocess.run(
        [
            str(cli),
            "search",
            "search.binary_search",
            "--input",
            "3,1,2",
            "--target",
            "1",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0


def test_two_pointer_bridge(cli, tmp_path):
    values = [-2, 0, 1, 3, 5, 8]
    pair = run_array_two_pointer_cli(values, 8, trace_path=tmp_path / "tp.trace.json", cli_path=cli)
    assert pair is not None
    assert values[pair[0]] + values[pair[1]] == 8
    oracle = two_sum_sorted_oracle(values, 8)
    assert oracle is not None
    assert values[oracle[0]] + values[oracle[1]] == 8
    assert run_array_two_pointer_cli(values, 100, cli_path=cli) is None


def test_sliding_window_bridge(cli, tmp_path):
    values = [2, 1, 5, 3, 2, 7]
    got = run_array_sliding_window_cli(
        values, 3, trace_path=tmp_path / "sw.trace.json", cli_path=cli
    )
    exp = max_sum_window_oracle(values, 3)
    assert exp is not None
    assert got[0] == exp[0]
    assert got[1] == exp[1]
    assert got[2] == exp[2]


def test_prefix_sum_bridge(cli, tmp_path):
    values = [2, 4, 6, 8]
    got = run_array_prefix_sum_cli(
        values, 1, 2, trace_path=tmp_path / "ps.trace.json", cli_path=cli
    )
    assert got == prefix_range_oracle(values, 1, 2)
