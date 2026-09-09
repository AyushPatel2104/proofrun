# Free-only public demo feasibility

**Status:** Planning only — **not deployed**  
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

## What can be static today

| Asset | GitHub Pages suitable? |
| --- | --- |
| Vanilla JS player | Yes |
| Canned ExecutionTrace demos | Yes |
| Algorithm explanations / complexity | Yes |
| Highlight legend (client-side) | Yes |
| Live user-input C++ execution | **No** (needs native/WASM/server) |
| Independent Python oracle Prove | **No** on static-only Pages |
| Controlled CLI benchmark | **No** on static-only Pages |

## Architecture options (future, still $0)

### A. Static public demo (recommended first public step)

- Publish `viz/` + `public/traces/*` on GitHub Pages
- Replay canned traces only (SEE)
- Label clearly: “Demo replay — live Run requires local product server”
- Prove/Measure documented as local-only

### B. Trusted WASM later (optional)

- Build C++ core to WASM in CI from this repo
- Browser runs catalog algorithms only (still no arbitrary native upload)
- Could restore live SEE (+ limited client Prove) without a paid server
- Still not a general compile-user-code service

### C. Free tier backend (not preferred now)

- Would blur the “free static first” story and add ops burden
- Not required for portfolio demo if A or B is clear

## Recommendation

1. Keep **local product server** as the full SEE→PROVE→MEASURE experience.  
2. When authorized to publish: ship **static canned-trace demo** on GitHub Pages first.  
3. Consider **WASM** only if live execution is required without asking visitors to build C++.  
4. Never claim Pages can host the current Python+CLI live path.

## Distinction

| Mode | Capability |
| --- | --- |
| **CURRENT LOCAL PRODUCT** | Select → Input → Run → See → Prove → Measure via Python server + CLI |
| **FUTURE FREE PUBLIC DEMO** | Static GitHub Pages-compatible **SEE** using canned traces |
| **FUTURE LIVE BROWSER EXECUTION** | Optional trusted WASM investigation (catalog-only; not arbitrary native code) |
| **NOT SUPPORTED ON PAGES** | Hosting or executing the current Python product server |
