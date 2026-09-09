# GitHub profile strategy (portfolio-wide)

**Status:** Strategy documentation only.  
**Does not create** a GitHub profile README, remotes, or repositories.

This describes how ProofRun and future completed projects relate to a public GitHub presence.

## Locked packaging model

1. **Master portfolio workspace stays separate.**  
   Development and tracking live in the local portfolio tree (e.g. `AI-ENGINEERING-PORTFOLIO/`). That workspace is **not** published as one giant monorepo of every project.

2. **Each completed project is normally its own standalone public repository.**  
   Example: ProofRun → public repo `proofrun` whose root is the project tree (`cpp/`, `python/`, `viz/`, …), not the portfolio root.

3. **Do not create empty repositories for unfinished projects.**  
   Publish when the project has a coherent product surface, tests, and honest docs — not as placeholders.

4. **Use professional repository names.**  
   Prefer clear product or system names (`proofrun`) over internal course numbering (`01-proofrun`) unless branding requires otherwise.

5. **Each public repository carries its own README and project docs.**  
   Visitors should understand problem, architecture, setup, tests, limits, and license without opening the private portfolio workspace.

6. **Use truthful GitHub topics.**  
   Reflect what the code actually does (e.g. algorithms, benchmarking, cpp). Do not add `ai`, `machine-learning`, or `saas` unless those capabilities are real.

7. **Pin a small number of strongest projects.**  
   Profile pins should highlight depth and evidence, not every experiment.

8. **Maintain a GitHub profile README as the portfolio index.**  
   Short links to featured repos and what each proves. **Not created in this packaging pass.**

9. **Use a personal portfolio website as the visual index.**  
   Site connects projects; GitHub remains the source of truth for code and CI.

10. **Keep public claims honest and evidence-based.**  
    No invented users, “production at scale,” or formal proof claims without artifacts. Prefer reproducible demos, tests, and benchmark methodology docs.

## ProofRun application

| Item | Decision |
| --- | --- |
| Public repo name | `proofrun` |
| Shape | Standalone |
| Portfolio role | Master development home only |
| Metadata | `docs/github-metadata.md` |
| Release readiness | `docs/GITHUB-RELEASE-CHECKLIST.md` |

## Anti-patterns to avoid

- Publishing the entire portfolio as one repo of unfinished folders  
- Tutorial-dump READMEs or technology checklists without a product story  
- Misleading topics or screenshots that oversell capability  
- Creating remotes for projects that are not yet release-ready  

## Next actions (when authorized separately)

- Initialize Git **inside** the ProofRun tree (or export a clean copy)  
- Create the `proofrun` remote and push  
- Optionally capture screenshots and enable static Pages demo  
- Later: author the GitHub profile README index  

None of those steps are authorized by this document alone.
