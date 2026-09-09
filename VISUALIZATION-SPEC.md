# VISUALIZATION-SPEC.md — ProofRun

## 1. Goal

Make algorithm execution **observable** through an event/state model:

> Visualization is driven by algorithm execution events, not hardcoded animation sequences.

Tagline alignment: **See the algorithm. Prove the result. Measure the run.**

---

## 2. Player Requirements

The JS runtime MUST support:

| Control | Behavior |
| --- | --- |
| Play | Advance events automatically on a timer |
| Pause | Freeze at current step |
| Step forward | Advance exactly one event |
| Reset | Return to step 0 / initial state |
| Speed control | Adjust delay between events |
| Current state | Render derived state at cursor |
| Operation/event history | Scrollable timeline of events |
| Algorithm explanation | Panel fed by manifest/docs blurb |
| Complexity information | Panel fed by manifest complexity fields |

Optional later: step backward (requires checkpoints or reversible events — Phase 2).

---

## 3. Execution-Event Model

### 3.1 Trace envelope

```json
{
  "schemaVersion": "1.0",
  "algorithmId": "sort.quicksort",
  "seed": 42,
  "fixtureId": "array.random.n32",
  "inputSummary": { "n": 32, "type": "array<i32>" },
  "manifestSnapshot": {
    "name": "Quicksort",
    "complexity": { "best": "O(n log n)", "avg": "O(n log n)", "worst": "O(n^2)", "memory": "O(log n)" },
    "explanation": "Partition around a pivot; recurse on sides."
  },
  "initialState": {},
  "events": [],
  "finalState": {},
  "meta": {
    "producer": "cpp-cli|python-oracle",
    "producerVersion": "0.1.0",
    "createdAtUtc": "..."
  }
}
```

### 3.2 Event object

```json
{
  "step": 0,
  "type": "compare",
  "ts": 0,
  "payload": {},
  "message": "compare a[i] and a[j]"
}
```

- `step`: contiguous integer starting at 0
- `type`: from controlled vocabulary (per renderer family)
- `payload`: structured data for renderers
- `message`: human-readable short text for timeline

### 3.3 Core event vocabulary (shared)

| type | Meaning |
| --- | --- |
| `init` | Initial layout |
| `compare` | Comparison between elements/nodes |
| `swap` | Swap two elements |
| `write` | Write value at index/node |
| `highlight` | Transient focus set |
| `partition` | Range/pivot markers |
| `visit` | Graph/tree node visit |
| `enqueue` / `dequeue` | Queue ops |
| `push` / `pop` | Stack ops |
| `relax` | Graph edge relax |
| `done` | Terminal event |

Families may extend with prefixed types, e.g. `dp.cell_update`, but must declare them in renderer capability maps.

---

## 4. State Model

Renderers maintain **derived state** by folding events:

```text
state_0 = initialState
state_{k+1} = apply(state_k, events[k])
```

Rules:

- `apply` must be pure in the JS runtime for canned traces.
- For live trusted emitters, the same event semantics apply.
- Do not hide important mutations in CSS-only animations without events.

---

## 5. Renderers

| Renderer | Used by | Primary state |
| --- | --- | --- |
| `array` | sorting, binary search, kadane | cells, highlights, pointers |
| `list` | linked list reverse/cycle | nodes + next pointers |
| `tree` | BST | nodes + edges + focus |
| `graph` | BFS/DFS | nodes + edges + frontier |
| `table2d` | DP | matrix cells |
| `heap` | binary heap | array + tree dual view optional |
| `generic` | fallback timeline-only | key/value state bag |

---

## 6. UI Layout (Demo Page)

```text
┌──────────────────────────────┬─────────────────────┐
│ Canvas / Renderer            │ Explanation         │
│                              │ Complexity          │
│                              │ Limits notice       │
├──────────────────────────────┼─────────────────────┤
│ Controls: play pause step…   │ Inspector (state)   │
├──────────────────────────────┴─────────────────────┤
│ Event timeline / history                           │
└────────────────────────────────────────────────────┘
```

---

## 7. Data Sources for Demo

Priority for PUBLIC DEMO:

1. **Canned trusted traces** shipped in `viz/public/traces/`
2. Optional WASM build from trusted C++ (later enhancement)
3. Never: user-uploaded native code → execute

User-adjustable inputs (if offered) must enforce size caps client-side and regenerate only via trusted WASM/local trusted tooling — not arbitrary shell.

---

## 8. Integration With Other Layers

| Producer | How traces are made |
| --- | --- |
| C++ CLI | Instrumentation hooks / trace emitter around MVP algos |
| Python | Oracle can emit pedagogical traces for some algos |
| Fixtures | Golden traces checked in for CI schema tests |

JS runtime consumes traces only; it does not reimplement algorithm correctness logic beyond rendering.

---

## 9. Accessibility & Performance Notes

- Prefer keyboard controls for play/pause/step/reset.
- Cap event counts for demo traces (e.g., N small; compact events).
- If a trace exceeds demo caps, refuse to autoplay and show a clear message.

---

## 10. Visualization Definition of Done (v0.1)

- Player controls complete
- At least four renderers used by MVP demos: array, graph, tree, heap (or list)
- Traces schema-validated in CI
- Explanations + complexity panels wired from manifest fields
