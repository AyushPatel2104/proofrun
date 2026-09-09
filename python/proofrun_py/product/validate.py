"""Safe request validation for the product workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from proofrun_py.catalog import find
from proofrun_py.oracles import is_nondecreasing
from proofrun_py.product.limits import MAX_ARRAY_PRODUCT, MAX_INT, MIN_INT


class ValidationError(ValueError):
    """User-facing validation failure."""


@dataclass
class ProductRequest:
    algorithm_id: str
    values: List[int]
    target: Optional[int] = None
    window: Optional[int] = None
    query_left: Optional[int] = None
    query_right: Optional[int] = None
    seed: int = 0


def _require_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        if isinstance(value, bool):
            raise ValidationError(
                f"{name} must be an integer.\n"
                "Why: boolean values are not valid numbers here.\n"
                "Fix: enter a whole number."
            )
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        else:
            raise ValidationError(
                f"{name} must be an integer.\n"
                "Why: the engine only accepts whole numbers.\n"
                "Fix: enter a value without decimals or text."
            )
    if value < MIN_INT or value > MAX_INT:
        raise ValidationError(
            f"{name} is out of range.\n"
            f"Why: values must be between {MIN_INT} and {MAX_INT}.\n"
            "Fix: choose a smaller-magnitude integer."
        )
    return value


def parse_values(raw: Any) -> List[int]:
    if raw is None:
        raise ValidationError(
            "Input is missing.\n"
            "Why: Run needs an integer array.\n"
            "Fix: type comma-separated integers (e.g. 3,1,2) or click Generate Input."
        )
    if isinstance(raw, str):
        text = raw.strip()
        if text == "":
            return []
        parts = [p.strip() for p in text.split(",")]
        out: List[int] = []
        for p in parts:
            if p == "":
                raise ValidationError(
                    "Input has an empty value between commas.\n"
                    "Why: each entry must be an integer.\n"
                    "Fix: remove extra commas (use 1,2,3 not 1,,3)."
                )
            try:
                out.append(_require_int("input element", int(p, 10)))
            except ValueError as exc:
                raise ValidationError(
                    f"Malformed input: {p!r} is not an integer.\n"
                    "Why: only whole numbers are allowed.\n"
                    "Fix: use values like -2,0,5 (no letters or decimals)."
                ) from exc
        return out
    if isinstance(raw, list):
        out = []
        for i, item in enumerate(raw):
            if isinstance(item, str):
                try:
                    item = int(item, 10)
                except ValueError as exc:
                    raise ValidationError(
                        f"Malformed input at position {i}: {item!r}.\n"
                        "Why: array elements must be integers.\n"
                        "Fix: replace that entry with a whole number."
                    ) from exc
            out.append(_require_int(f"input[{i}]", item))
        return out
    raise ValidationError(
        "Input format is wrong.\n"
        "Why: expected a list of integers or a comma-separated string.\n"
        "Fix: example — 7,3,9,1,5"
    )


def validate_product_request(body: Dict[str, Any]) -> ProductRequest:
    algo = body.get("algorithmId") or body.get("algorithm_id")
    if not isinstance(algo, str) or not algo:
        raise ValidationError(
            "No algorithm selected.\n"
            "Why: ProofRun only runs catalog algorithms.\n"
            "Fix: choose an algorithm from the dropdown."
        )
    meta = find(algo)
    if meta is None:
        raise ValidationError(
            "Unsupported algorithm.\n"
            "Why: that id is not in the trusted catalog.\n"
            "Fix: choose an algorithm from the dropdown."
        )
    if meta.get("status") != "implemented":
        raise ValidationError(
            "Algorithm not available.\n"
            "Why: it is not implemented in this build.\n"
            "Fix: pick another algorithm from the list."
        )

    values = parse_values(body.get("input", body.get("values")))
    if len(values) > MAX_ARRAY_PRODUCT:
        raise ValidationError(
            f"Input is too long ({len(values)} elements).\n"
            f"Why: live visualization is capped at {MAX_ARRAY_PRODUCT} elements for safety.\n"
            "Fix: shorten the array or Generate with a smaller n."
        )

    params = body.get("params") or {}
    if not isinstance(params, dict):
        raise ValidationError(
            "Parameters are invalid.\n"
            "Why: params must be a set of named fields.\n"
            "Fix: use the parameter inputs shown for this algorithm."
        )

    seed = body.get("seed", 0)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValidationError(
            "Seed must be an integer.\n"
            "Why: generated inputs need a numeric seed.\n"
            "Fix: enter a whole number seed (e.g. 42)."
        )

    family = meta["family"]
    target = None
    window = None
    q_left = None
    q_right = None

    if family == "searching" or algo == "array.two_pointer":
        t = params.get("target", body.get("target"))
        if t is None:
            raise ValidationError(
                "Target is required.\n"
                "Why: this algorithm searches for / matches a specific value.\n"
                "Fix: fill the Target field before Run."
            )
        try:
            target = _require_int("target", t if not isinstance(t, str) else int(t))
        except ValueError as exc:
            if isinstance(exc, ValidationError):
                raise
            raise ValidationError(
                "Target is invalid.\n"
                "Why: target must be an integer.\n"
                "Fix: enter a whole number target."
            ) from exc

    if algo == "search.binary_search" or algo == "array.two_pointer":
        if not is_nondecreasing(values):
            raise ValidationError(
                "Input must be sorted ascending.\n"
                "Why: this algorithm requires a nondecreasing array.\n"
                "Fix: sort the values first, or use Generate → sorted."
            )

    if algo == "array.sliding_window":
        k = params.get("window", body.get("window", body.get("k")))
        if k is None:
            raise ValidationError(
                "Window size K is required.\n"
                "Why: Sliding Window needs a fixed window length.\n"
                "Fix: enter K with 1 ≤ K ≤ array length."
            )
        try:
            window = _require_int("window", k if not isinstance(k, str) else int(k))
        except ValueError as exc:
            if isinstance(exc, ValidationError):
                raise
            raise ValidationError(
                "Window size K is invalid.\n"
                "Why: K must be an integer.\n"
                "Fix: enter a whole number for K."
            ) from exc
        n = len(values)
        if window <= 0 or window > n:
            raise ValidationError(
                f"Window size K={window} is invalid for n={n}.\n"
                "Why: need 1 ≤ K ≤ array length.\n"
                "Fix: lower K or add more elements to the array."
            )

    if algo == "array.prefix_sum":
        q = params.get("query", body.get("query"))
        if isinstance(q, dict):
            left = q.get("left", q.get("L"))
            right = q.get("right", q.get("R"))
        else:
            left = params.get("left", body.get("left"))
            right = params.get("right", body.get("right"))
        if left is None or right is None:
            raise ValidationError(
                "Range [L, R] is required.\n"
                "Why: Prefix Sum answers an inclusive index range.\n"
                "Fix: enter L and R with 0 ≤ L ≤ R < n."
            )
        try:
            q_left = _require_int("L", left if not isinstance(left, str) else int(left))
            q_right = _require_int("R", right if not isinstance(right, str) else int(right))
        except ValueError as exc:
            if isinstance(exc, ValidationError):
                raise
            raise ValidationError(
                "L or R is invalid.\n"
                "Why: range bounds must be integers.\n"
                "Fix: enter whole-number indices."
            ) from exc
        n = len(values)
        if n == 0:
            raise ValidationError(
                "Array is empty.\n"
                "Why: Prefix Sum needs at least one element to query.\n"
                "Fix: provide a non-empty array, then set L and R."
            )
        if q_left < 0 or q_right < 0 or q_left >= n or q_right >= n or q_left > q_right:
            raise ValidationError(
                f"Range L={q_left}, R={q_right} is invalid for n={n}.\n"
                f"Why: need 0 ≤ L ≤ R ≤ {n - 1}.\n"
                "Fix: adjust L and R to fall inside the array."
            )

    if family == "sorting":
        if target is not None or window is not None or q_left is not None:
            pass  # ignore stray params

    return ProductRequest(
        algorithm_id=algo,
        values=values,
        target=target,
        window=window,
        query_left=q_left,
        query_right=q_right,
        seed=seed,
    )


def catalog_param_schema(algo: Dict[str, Any]) -> Dict[str, Any]:
    aid = algo["id"]
    family = algo["family"]
    schema: Dict[str, Any] = {
        "requiresSorted": aid in ("search.binary_search", "array.two_pointer"),
        "fields": [],
        "precondition": None,
        "legend": [],
    }
    if family == "searching" or aid == "array.two_pointer":
        schema["fields"].append({"name": "target", "label": "Target", "type": "integer"})
    if aid == "search.binary_search":
        schema["precondition"] = "Input must be sorted ascending (nondecreasing)."
        schema["legend"] = [
            {"swatch": "accent", "label": "Default cell"},
            {"swatch": "warn", "label": "low / high bounds (ends)"},
            {"swatch": "warn", "label": "mid (current probe)"},
            {"swatch": "ok", "label": "Found (see event message)"},
        ]
    if aid == "array.two_pointer":
        schema["precondition"] = (
            "Input must be sorted ascending. Finds indices i < j with a[i] + a[j] = target."
        )
        schema["legend"] = [
            {"swatch": "accent", "label": "Default cell"},
            {"swatch": "warn", "label": "left / right pointers"},
            {"swatch": "ok", "label": "Pair found (see event message)"},
        ]
    if aid == "array.sliding_window":
        schema["fields"].append({"name": "window", "label": "Window size K", "type": "integer"})
        schema["precondition"] = "Window size K is required (1 ≤ K ≤ array length)."
        schema["legend"] = [
            {"swatch": "accent", "label": "Outside window"},
            {"swatch": "warn", "label": "Active window ends (start / end)"},
        ]
    if aid == "array.prefix_sum":
        schema["fields"].append({"name": "left", "label": "Query L (inclusive)", "type": "integer"})
        schema["fields"].append({"name": "right", "label": "Query R (inclusive)", "type": "integer"})
        schema["precondition"] = "Range [L, R] is required (0 ≤ L ≤ R < n)."
        schema["legend"] = [
            {"swatch": "accent", "label": "Prefix table values (after build)"},
            {"swatch": "warn", "label": "Highlighted L / R during query"},
        ]
    if family == "sorting":
        schema["precondition"] = "Provide an integer array. Result is sorted ascending."
        schema["legend"] = [
            {"swatch": "accent", "label": "Default cell"},
            {"swatch": "warn", "label": "Compared / written indices"},
        ]
    if aid == "search.linear_search":
        schema["precondition"] = "Unsorted input is OK. Returns first matching index or not found."
        schema["legend"] = [
            {"swatch": "accent", "label": "Default cell"},
            {"swatch": "warn", "label": "Current index being inspected"},
            {"swatch": "ok", "label": "Found (see event message)"},
        ]
    return schema
