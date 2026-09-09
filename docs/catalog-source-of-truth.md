# Algorithm catalog — source of truth

## Decision

**Authoritative file:** `catalogs/algorithms.json`

This JSON catalog is the single source of truth for:

- algorithm ID / display name / family
- complexity
- explanation
- `visualizable` / `benchmarkable` / `traceable`
- `status` (`implemented` | `planned` | `deprecated`)

## Consumers

| Consumer | How it stays consistent |
| --- | --- |
| C++ CLI | `scripts/generate_catalog_artifacts.py` → `cpp/include/proofrun/catalog/generated_algorithms.hpp` (CMake regenerates) |
| Python harness/tests | `proofrun_py.catalog` loads the JSON directly |
| TypeScript tooling | `tools` validate traces against catalog IDs |

Do **not** hand-edit the generated C++ header.

## Drift detection

```bash
python scripts/generate_catalog_artifacts.py --check
python -m pytest python/tests/test_catalog -q
```

CI also runs the catalog check and TypeScript validation.
