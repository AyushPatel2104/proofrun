"""Load the authoritative algorithm catalog (catalogs/algorithms.json)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from proofrun_py.bridge import project_root


@lru_cache(maxsize=1)
def load_catalog() -> Dict[str, Any]:
    path = project_root() / "catalogs" / "algorithms.json"
    return json.loads(path.read_text(encoding="utf-8"))


def algorithms() -> List[Dict[str, Any]]:
    return list(load_catalog()["algorithms"])


def algorithm_ids(*, status: str | None = "implemented") -> List[str]:
    ids = []
    for a in algorithms():
        if status is None or a.get("status") == status:
            ids.append(a["id"])
    return ids


def find(algorithm_id: str) -> Dict[str, Any] | None:
    for a in algorithms():
        if a["id"] == algorithm_id:
            return a
    return None


def benchmarkable_ids() -> List[str]:
    return [a["id"] for a in algorithms() if a.get("benchmarkable") and a.get("status") == "implemented"]
