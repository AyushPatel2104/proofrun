# Visualization verification checklist

## Product path (preferred)

```powershell
powershell -File scripts/run_product.ps1
# or: ./scripts/run_product.sh
```

Open `http://127.0.0.1:8080/` and verify:

| Step | Expected |
| --- | --- |
| Engine status | Connected |
| Select algorithm | Display name; precondition text updates |
| Generate + Run | Live trace loads; Play/Step/Reset/Speed work |
| Result | Human-readable result + Correctness PASS/FAIL |
| Measure | Interactive ms shown; Controlled Benchmark returns median + disclaimer |
| Canned demo | Optional dropdown still replays schema 1.0 traces |

## Headless contract

```bash
python scripts/verify_viz_contract.py
```

Checks player controls exist and demo traces fold to `finalState`.
