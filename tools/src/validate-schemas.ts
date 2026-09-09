/**
 * Validate ExecutionTrace samples and catalog JSON against structural rules.
 * Build with `npm run build`, then `node dist/validate-schemas.js`.
 * No ts-node required.
 */
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { assertExecutionTrace } from "./validate-lib.js";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");

function loadJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8"));
}

function main(): void {
  const catalogPath = join(root, "catalogs", "algorithms.json");
  const catalog = loadJson(catalogPath) as {
    schemaVersion: string;
    algorithms: Array<{ id: string; status: string }>;
  };
  if (!catalog.schemaVersion || !Array.isArray(catalog.algorithms)) {
    throw new Error("invalid algorithms.json");
  }
  const ids = new Set<string>();
  for (const a of catalog.algorithms) {
    if (!a.id) throw new Error("algorithm missing id");
    if (ids.has(a.id)) throw new Error(`duplicate algorithm id: ${a.id}`);
    ids.add(a.id);
  }

  const tracesDir = join(root, "viz", "public", "traces");
  if (existsSync(tracesDir)) {
    for (const name of readdirSync(tracesDir)) {
      if (!name.endsWith(".json")) continue;
      const trace = loadJson(join(tracesDir, name));
      assertExecutionTrace(trace);
      const t = trace as { algorithmId: string };
      if (!ids.has(t.algorithmId)) {
        throw new Error(`trace ${name} references unknown algorithmId ${t.algorithmId}`);
      }
      console.log(`OK trace ${name}`);
    }
  }

  console.log(`OK catalog (${catalog.algorithms.length} algorithms)`);
}

main();
