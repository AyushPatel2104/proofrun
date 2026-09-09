# GitHub metadata (proposed) — ProofRun

**Status:** Metadata for a future standalone public repository.  
**Do not create the remote from this document alone.** No repository has been created in the pre-publish remediation pass.

## Packaging decision

| Item | Decision |
| --- | --- |
| Public shape | **Standalone** repository |
| Proposed name | `proofrun` |
| Portfolio workspace | Remains the development home under `AI-ENGINEERING-PORTFOLIO/.../01-PROOFRUN/` |
| CI root | ProofRun project root (no `01-FOUNDATION-ENGINEERING/01-PROOFRUN` prefix) |

When publishing, copy or extract **only** the ProofRun tree so the GitHub root matches:

```text
proofrun/
├── cpp/
├── python/
├── viz/
├── schemas/
├── catalogs/
├── scripts/
├── tools/
├── docs/
├── .github/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```

## Suggested description

> Algorithm verification and performance intelligence platform for visualizing execution, validating correctness, and measuring real-world algorithm performance.

## Suggested topics

Truthful and relevant:

- `algorithms`
- `algorithm-visualization`
- `benchmarking`
- `cpp`
- `python`
- `software-engineering`
- `developer-tools`
- `data-structures`
- `performance-engineering`

**Do not** add misleading topics such as `ai`, `machine-learning`, or `production-saas` unless those capabilities exist in the repository.

## Version / release

- Code version: `0.1.0` (`PROOFRUN_VERSION_STRING`)  
- Suggested first public tag when authorized: `v0.1.0`  
- Do not label as production SaaS v1.0 without evidence  

## About / homepage (later)

- Homepage: GitHub Pages static demo **after** authorized deploy of canned traces  
- Until then: leave homepage empty or point at README  

## CI note

Workflow: `.github/workflows/ci.yml` — standalone-root paths.  
Remote green status: **unproven until the public repository exists and Actions run.**

## Related

- Profile / multi-repo strategy: `docs/github-profile-strategy.md`  
- Release checklist: `docs/GITHUB-RELEASE-CHECKLIST.md`  
- Public demo: `docs/public-demo-plan.md`  
