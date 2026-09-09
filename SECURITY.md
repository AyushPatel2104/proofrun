# SECURITY.md — ProofRun

## 1. Security Posture

ProofRun is a foundation/engineering project with a **PUBLIC DEMO** surface. Even so, it must follow clear trust boundaries.

Core rules:

1. **Never execute arbitrary untrusted native code publicly.**
2. Define and enforce **input limits**.
3. Define **resource limits** for runners.
4. Document **sandbox assumptions**.
5. **Avoid exposing arbitrary shell execution** to users.
6. Separate **trusted benchmark runners** from **user-controlled inputs**.

---

## 2. Trust Zones

| Zone | Trust level | Examples |
| --- | --- | --- |
| Repository source | Trusted | C++/Python algorithms in git |
| CI runners | Trusted (platform-shared) | GitHub Actions |
| Static GitHub Pages assets | Trusted publish artifacts | docs, JS, canned traces, optional WASM from CI |
| User-provided numeric/array inputs in demo | Untrusted data | Must be validated/capped |
| User-uploaded `.cpp/.py` source in public demo | **Forbidden in v1** | Out of scope |

---

## 3. Input Limits (Baseline Policy)

Exact numbers may be tuned at implementation, but limits must exist and be documented in UI + CLI.

| Domain | MVP baseline cap (proposal) |
| --- | --- |
| Array length for viz | ≤ 64 (demo), ≤ 10^5 (local trusted bench profiles as configured) |
| Array length for public demo generation | ≤ 64 |
| String length (demo) | ≤ 256 |
| Graph nodes (viz) | ≤ 40 |
| Graph edges (viz) | ≤ 80 |
| DP table cells (viz) | ≤ 400 |
| Trace events (demo autoplay) | ≤ 5,000 |
| Bench smoke wall time | hard timeout in scripts |
| CLI max file size for input fixtures | small fixed cap (e.g., 2–8 MiB) |

All public paths fail closed when caps exceeded.

---

## 4. Resource Limits

Trusted local/CI runners should set:

- CPU time timeouts per bench case
- Maximum matrix dimensions in smoke profiles
- No unbounded recursion demos without caps (e.g., N-Queens N≤4/8 with explicit limit)

---

## 5. Sandbox Assumptions

### Public demo (GitHub Pages)

- Assumed: browser sandbox only
- No server-side execution
- No user shell
- Assets are static

### Local CLI benches/tests

- Assumed: developer machine trust
- Scripts may invoke compilers and binaries already built from this repo
- Developers should not point scripts at untrusted binaries

### Future WASM (optional)

- Built in CI from trusted sources
- Still subject to input caps
- Not a general compile-user-code service

---

## 6. Dangerous Capabilities — Explicit Denylist (v1 Public)

- Upload and compile user C++/Python
- Arbitrary `eval` of user JS beyond JSON parse of capped traces
- Fetching remote traces from arbitrary URLs without allowlist (MVP: local/packaged traces only)
- Exposing docker/socket APIs
- Running shell from the browser demo

---

## 7. Separation: Benchmarks vs User Inputs

```text
Trusted path:
  catalogs + generators(seeds) → cpp benches → reports

Untrusted data path (demo):
  user array (capped) → trusted WASM/algorithm only → viz
  OR canned traces → viz

Forbidden path:
  user source code → compile/execute
```

---

## 8. Data Handling

- No collection of personal data required for MVP demo
- Do not log user inputs to external services
- Fixture datasets should avoid proprietary/sensitive content

---

## 9. Supply Chain Notes (Impl Phase)

When dependencies are introduced later:

- Prefer pinned versions
- Document CMake FetchContent / package sources
- Avoid installing packages during specification phase (current rule)

---

## 10. Security Documentation Requirements for Release

README / docs must include:

- limits table
- trust boundary diagram (can be text)
- “no arbitrary native execution” statement
- how to run benches safely locally

---

## 11. Incident / Abuse Expectations

If hosted demo is abused (e.g., attempt to post huge payloads):

- client-side rejection
- no server to exhaust (static hosting)
- if later a backend exists (out of scope for #01), add rate limits — **not planned for ProofRun MVP**
