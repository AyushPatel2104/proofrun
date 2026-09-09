# Architecture (implementation)

ProofRun follows the locked specification in `ARCHITECTURE.md`.

```text
Algorithm (C++)
  → Execution Events (trace::Emitter)
  → JSON ExecutionTrace (schemaVersion 1.0)
  → JavaScript Visualization Player
```

Python provides independent oracles (`sorted()`), Hypothesis properties, CLI bridging, and smoke reports.

GoogleTest validates C++ correctness. Google Benchmark measures in-process microbenchmarks. These responsibilities remain separated.
