---
status: accepted
date: YYYY-MM-DD
decision-makers: [you]
consulted: []
informed: []
affects:
  components: []
  bases: []
  projects: ["*"]
interface-impact: none
---

# ADR-0004: Use uv as the package and dependency manager
## Context and problem statement
Polylith's Python tooling supports several package managers, and the choice shapes every project's `pyproject.toml`, the lockfile, and the developer and CI workflow. We need to pick one for the workspace.

## Decision drivers
- Fast installs and resolution, since the whole workspace shares one development environment.
- Good lockfile support for reproducible builds across projects and CI.
- First-class support in the Polylith Python tooling.
- BSSN: one manager for the whole workspace, no per-project variation until something forces it.

## Considered options
- uv
- Poetry
- PDM
- Hatch
- Rye
- Pixi

## Decision outcome
Chosen option: uv, as the single package and dependency manager for the workspace and all projects.

uv over the alternatives because it is fast, has a solid lockfile, and is supported by the Polylith standalone CLI. The other managers are all viable and Polylith-supported; uv's speed and the single-tool simplicity are what tip it.

This decision is reversible: Polylith's tooling is manager-agnostic, so switching later is contained to packaging configuration, not the bricks.

### Consequences
- Good: fast, reproducible installs; one manager to learn and configure.
- Bad: uv is younger than Poetry; some niche workflows may need workarounds.
- Neutral: contributors install uv as a prerequisite.

### Confirmation
Projects build and lock with uv in CI. A green CI run is the confirmation.

## More information
- Polylith Python tooling and supported managers: https://davidvujic.github.io/python-polylith-docs/
- Best Simple System for Now (BSSN): https://dannorth.net/blog/best-simple-system-for-now/
