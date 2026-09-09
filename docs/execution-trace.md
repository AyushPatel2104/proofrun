# Execution trace format

`schemaVersion`: **1.0**

Contract: `schemas/execution-trace.schema.json`  
Producer: `proofrun_cli {sort|search|array} ... --trace file.json`  
Consumer: `viz/` player

## Shared event vocabulary

Used across families: `init`, `compare`, `swap`, `write`, `highlight`, `partition`, `found`, `not_found`, `done`.

Visualization folds events that include `payload.array` into renderer state. Highlights use `payload.i` / `payload.j` / `payload.index` (and optional `indices` / `mid`).

## Searching

- **Linear:** `compare` while scanning; `found` or `not_found`; `done` with `resultIndex`.
- **Binary:** `highlight` carries `low`/`mid`/`high` (also `i`/`j`/`index`); `compare`; `found`/`not_found`; `done`.

## Arrays

- **Two pointer:** `compare` on left/right; pointer moves via `highlight`; `found`/`not_found`; `done`.
- **Sliding window:** initial window `highlight`; expand/contract `highlight`; max update `write`; `done`.
- **Prefix sum:** accumulation `write` (visual array becomes prefix); range `highlight`; `done`.
