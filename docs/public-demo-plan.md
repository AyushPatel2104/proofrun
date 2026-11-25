# Free-only public demo feasibility

**Status:** Implementation ready — static build + Pages workflow present; **Pages hosting not enabled until authorized**  
**Constraint:** $0 infrastructure; no paid backends, domains, or cloud billing

## Current local product

Full workflow (requires local build + product server):

```text
Select → Input → Run → See → Prove → Measure
```

```text
Browser UI  ↔  Python product server  ↔  trusted proofrun_cli (C++)
```

Live **Run / Prove / Measure** require the local Python adapter and built CLI.  
This **cannot** run as-is on GitHub Pages (Pages is static hosting only).  
Do **not** claim that GitHub Pages can execute the current Python server.

## Static public demo (authorized)

| Asset | GitHub Pages suitable? |
| --- | --- |
| Vanilla JS player | Yes |
| Canned ExecutionTrace demos (10) | Yes |
| Algorithm explanations / complexity | Yes (static `catalog.json`) |
| Highlight legend (client-side) | Yes |
| Live user-input C++ execution | **No** (needs native/WASM/server) |
| Independent Python oracle Prove | **No** on static-only Pages |
| Controlled CLI benchmark | **No** on static-only Pages |

### How to build locally

```bash
export PYTHONPATH=python
python scripts/build_public_demo.py --base /proofrun/
# output → site/  (gitignored)

# Root serve (no project base):
python scripts/build_public_demo.py --base ./
python -m http.server 8765 --directory site

# Project-base simulation (matches GitHub project Pages):
# place site/* under a folder named proofrun/ and serve the parent
```

Banner (required, exact intent):

> Demo replay — live Run, Prove and Measure require the local product.

### Deploy path (when Pages is enabled)

1. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**
2. Workflow: `.github/workflows/pages.yml` (`ProofRun Pages Demo`)
3. Expected URL: `https://<owner>.github.io/proofrun/`
4. Existing `ci.yml` is unchanged and remains the product regression gate

## Architecture options (future, still $0)

### A. Static public demo (this phase)

- Publish built `site/` (from `viz/` + `public/traces/*` + static catalog) on GitHub Pages
- Replay canned traces only (SEE)
- Label clearly with the demo banner above
- Prove/Measure documented as local-only

### B. Trusted WASM later (optional — **not this phase**)

- Build C++ core to WASM in CI from this repo
- Browser runs catalog algorithms only (still no arbitrary native upload)
- Could restore live SEE (+ limited client Prove) without a paid server
- Still not a general compile-user-code service

### C. Free tier backend (not preferred now)

- Would blur the “free static first” story and add ops burden
- Not required for portfolio demo if A or B is clear

## Recommendation

1. Keep **local product server** as the full SEE→PROVE→MEASURE experience.  
2. Ship **static canned-trace demo** on GitHub Pages (this phase).  
3. Consider **WASM** only if live execution is required without asking visitors to build C++.  
4. Never claim Pages can host the current Python+CLI live path.

## Distinction

| Mode | Capability |
| --- | --- |
| **CURRENT LOCAL PRODUCT** | Select → Input → Run → See → Prove → Measure via Python server + CLI |
| **FREE PUBLIC DEMO** | Static GitHub Pages-compatible **SEE** using canned traces |
| **FUTURE LIVE BROWSER EXECUTION** | Optional trusted WASM investigation (catalog-only; not arbitrary native code) |
| **NOT SUPPORTED ON PAGES** | Hosting or executing the current Python product server |
