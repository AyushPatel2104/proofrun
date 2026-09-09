import json

import pytest

from proofrun_py.bridge import default_cli_path, run_sort_cli
from proofrun_py.catalog import algorithm_ids
from proofrun_py.compare import assert_matches_oracle
from proofrun_py.generators import generate_array

SORT_ALGOS = [a for a in algorithm_ids(status="implemented") if a.startswith("sort.")]

CASES = [
    ("empty", 0, 1),
    ("single", 1, 2),
    ("sorted", 8, 3),
    ("reverse", 8, 4),
    ("duplicates", 12, 5),
    ("negatives", 12, 6),
    ("random", 20, 7),
    ("random", 50, 8),
]


@pytest.fixture(scope="session")
def cli():
    path = default_cli_path()
    if not path.exists():
        pytest.skip(f"proofrun_cli not built: {path}")
    return path


@pytest.mark.parametrize("algo", SORT_ALGOS)
@pytest.mark.parametrize("kind,n,seed", CASES)
def test_cpp_matches_python_oracle(cli, algo, kind, n, seed, tmp_path):
    values = generate_array(kind, n, seed)
    trace = None
    if 0 < len(values) <= 64:
        trace = tmp_path / f"{algo.replace('.', '_')}.trace.json"
    result = run_sort_cli(algo, values, trace_path=trace, seed=seed, cli_path=cli)
    assert_matches_oracle(result, values)
    if trace is not None:
        data = json.loads(trace.read_text(encoding="utf-8"))
        assert data["schemaVersion"] == "1.0"
        assert data["algorithmId"] == algo
        assert data["events"][0]["type"] == "init"
        assert data["events"][-1]["type"] == "done"


def test_intentional_mismatch_detector():
    with pytest.raises(AssertionError):
        assert_matches_oracle([1, 3, 2], [3, 1, 2])
