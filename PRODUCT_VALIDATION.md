# PRODUCT_VALIDATION.md — ProofRun

**Audits:** workbench→product coherence · UX/security/public-demo readiness polish  
**Scope:** 10 workflows + local product shell  
**Dates:** 2026-09-09  

---

## 0. Pre-polish 30-second audit (new user)

| Question | Before polish | After polish |
| --- | --- | --- |
| What is ProofRun? | Tagline only | Problem + pillars in header |
| SEE / PROVE / MEASURE | Implied | Explicit bullets; Prove = verification |
| What to select / input | Partial | Callout preconditions + param fields |
| After Run? | Partial | Result summary DL + legend |
| Result meaning | Weak | Algorithm / input / result / verification / complexity / events / measure |

### Pre-polish findings (recorded before coding)

| ID | Finding | Severity |
| --- | --- | --- |
| P1 | No problem statement above the fold | HIGH |
| P2 | Highlight legend thin | HIGH |
| P3 | Result summary incomplete | HIGH |
| P4 | “Prove” risked formal-proof reading | HIGH |
| P5 | Errors uneven; some path leakage risk | HIGH |
| P6 | Health could expose CLI paths | MEDIUM |
| P7 | 500 responses could leak internals | HIGH |
| P8 | Public demo path undocumented | MEDIUM |

---

## 1. Executive verdict (post-polish)

**PASS as a coherent local product** with honest limits.

Public static deploy of the *full* live workflow is still **not** ready (by design: Pages ≠ C++ server). Canned-trace public SEE is feasible at $0 later.

---

## 2. Fixes applied

- Header: problem + SEE/PROVE/MEASURE pillars  
- Algorithm-specific **precondition callouts** + **legend** from catalog schema  
- Result summary: algorithm, input, result, correctness verification, complexity, event count  
- Measure labels: interactive vs controlled  
- Prove copy: independent oracle / not formal proof  
- Validation errors: What / Why / Fix  
- Adapter: sanitize stderr, basename allowlist, timeout, missing-trace handling, `shell=False`  
- Server: no exception `detail` in JSON 500  
- Health: no filesystem path in payload  
- Docs: README rewrite, `docs/public-demo-plan.md`  

---

## 3. Remaining findings

| ID | Finding | Severity |
| --- | --- | --- |
| R1 | Not deployed (authorized stop) | ACCEPTABLE |
| R2 | UI controlled measure includes spawn overhead | MEDIUM |
| R3 | Canvas still does not paint semantic colors per role beyond i/j/index | LOW–MEDIUM |
| R4 | Static Pages cannot host live Run without WASM/server | ACCEPTABLE (documented) |

---

## 4. Scores (not inflated)

| Lens | Score | Notes |
| --- | --- | --- |
| Engineering | **90 / 100** | Tests, catalog, traces, benches |
| Product UX | **84 / 100** | Coherent local journey; polish applied |
| Security | **88 / 100** | Catalog-only; sanitization; fixed CLI |
| Benchmark rigor | **78 / 100** | Honest labeling; gbench still separate |
| Public deployment readiness | **55 / 100** | Plan clear; live path not Pages-ready |
| **Overall product (local)** | **82 / 100** | Was ~78 pre-polish |

---

## 5. Confirmations

- 10 workflows only · roadmap locked · RAG24 untouched · no paid services · no deployment · no new algorithms · no domain · no GitHub repo created in this pass
