import json
from pathlib import Path

from jsonschema import validate


def test_sample_trace_schema():
    root = Path(__file__).resolve().parents[3]
    schema = json.loads(
        (root / "schemas" / "execution-trace.schema.json").read_text(encoding="utf-8")
    )
    sample = root / "viz" / "public" / "traces" / "sort.bubblesort__demo.trace.json"
    if not sample.exists():
        return
    data = json.loads(sample.read_text(encoding="utf-8"))
    validate(instance=data, schema=schema)
