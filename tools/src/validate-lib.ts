/** Shared runtime assertions for ProofRun contracts. */
import type { ExecutionTrace } from "./types/contracts.js";

export function assertExecutionTrace(value: unknown): asserts value is ExecutionTrace {
  if (!value || typeof value !== "object") throw new Error("trace must be object");
  const t = value as Record<string, unknown>;
  if (t.schemaVersion !== "1.0") throw new Error("schemaVersion must be 1.0");
  if (typeof t.algorithmId !== "string") throw new Error("algorithmId required");
  if (!Array.isArray(t.events)) throw new Error("events must be array");
  if (!t.finalState || typeof t.finalState !== "object") throw new Error("finalState required");
  if (!t.meta || typeof t.meta !== "object") throw new Error("meta required");
  const events = t.events as Array<Record<string, unknown>>;
  for (let i = 0; i < events.length; i++) {
    if (typeof events[i].step !== "number") throw new Error(`events[${i}].step required`);
    if (typeof events[i].type !== "string") throw new Error(`events[${i}].type required`);
  }
}
