"""Catalog drift and schema tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from proofrun_py.bridge import default_cli_path, project_root
from proofrun_py.catalog import algorithm_ids, load_catalog


def test_catalog_json_matches_schema():
    root = project_root()
    schema = json.loads((root / "schemas" / "algorithm-manifest.schema.json").read_text(encoding="utf-8"))
    data = load_catalog()
    Draft202012Validator(schema).validate(data)


def test_generated_header_is_current():
    root = project_root()
    script = root / "scripts" / "generate_catalog_artifacts.py"
    proc = subprocess.run(
        ["python", str(script), "--root", str(root), "--check"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_cli_catalog_matches_json():
    cli = default_cli_path()
    if not cli.exists():
        pytest.skip("CLI not built")
    proc = subprocess.run([str(cli), "catalog", "--ids-only"], check=True, capture_output=True, text=True)
    cli_ids = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    assert cli_ids == algorithm_ids(status=None)


def test_implemented_algorithms_present():
    ids = set(algorithm_ids(status="implemented"))
    expected = {
        "sort.bubblesort",
        "sort.insertionsort",
        "sort.selectionsort",
        "sort.mergesort",
        "sort.quicksort",
        "search.linear_search",
        "search.binary_search",
        "array.two_pointer",
        "array.sliding_window",
        "array.prefix_sum",
    }
    assert expected == ids
