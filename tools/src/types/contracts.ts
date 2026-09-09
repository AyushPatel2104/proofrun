/** Typed ExecutionTrace contract (schemaVersion 1.0). */
export interface ComplexityInfo {
  best?: string;
  avg?: string;
  worst?: string;
  memory?: string;
}

export interface ManifestSnapshot {
  name?: string;
  complexity?: ComplexityInfo;
  explanation?: string;
}

export interface TraceEvent {
  step: number;
  type: string;
  ts?: number;
  payload?: Record<string, unknown>;
  message?: string;
}

export interface ExecutionTrace {
  schemaVersion: "1.0";
  algorithmId: string;
  seed?: number | null;
  fixtureId?: string;
  inputSummary?: Record<string, unknown>;
  manifestSnapshot?: ManifestSnapshot;
  initialState?: Record<string, unknown>;
  events: TraceEvent[];
  finalState: Record<string, unknown>;
  meta: {
    producer: string;
    producerVersion: string;
    createdAtUtc?: string;
    capped?: boolean;
  };
}

export interface BenchReport {
  schemaVersion: "1.0";
  profile: string;
  environment: Record<string, unknown>;
  results: unknown[];
  notes?: string;
}
