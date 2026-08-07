---
status: accepted
date: YYYY-MM-DD
decision-makers: [you]
consulted: []
informed: []
affects:
  components: ["*"]
  bases: ["*"]
  projects: ["*"]
interface-impact: none
---

# ADR-0002: Adopt the Polylith architecture
## Context and problem statement
We are starting a new codebase that will likely grow to several deployable services or apps sharing a lot of code. We need a structure that makes sharing code easy, keeps clear boundaries between features, and lets us defer the choice of deployment shape (monolith, services, serverless) until we need it.

## Decision drivers
- Share code across multiple apps or services without copy-paste or a sprawl of library repos.
- Clear separation between a feature's public interface and its implementation.
- Defer deployment decisions; focus on code and features first.
- Best Simple System for Now: avoid speculative infrastructure; one workspace, one environment, grow structure only as needed.

## Considered options
- Polylith monorepo (components, bases, projects; the Python tooling)
- A flat or `src/` layout single package
- Multiple repositories, one per service, with shared code as published libraries
- A generic monorepo without Polylith's brick model

## Decision outcome
Chosen option: Polylith, using the Python tooling (`poly`). Code lives as bricks (components for business logic, bases as thin entry points) under `components/` and `bases/`, combined into deployable artifacts under `projects/`. A brick's public interface is its `__init__.py`; its implementation is private behind that.

Polylith over the alternatives because it gives code sharing and clear boundaries in one monorepo and one environment, separates interface from implementation by construction, and lets us defer deployment shape. A flat package does not scale to multiple services cleanly. Multiple repos reintroduce the duplication and versioning problems we want to avoid. A generic monorepo would have us reinvent the brick model and its tooling.

### Consequences
- Good: shared code with clear boundaries; interface/implementation separation is structural; deployment shape stays deferrable.
- Good: one virtual environment for the whole workspace via the development project, which suits REPL- and test-driven work and gives agents full context.
- Bad: contributors must learn Polylith's model and the `poly` tooling.
- Neutral: business logic must not live in `projects/`, only project infrastructure (Dockerfiles, deploy scripts, `pyproject.toml`).

### Confirmation
`poly check` and `poly deps` run in CI and enforce the brick boundaries: in particular, components must not import from bases, so the dependency direction stays base to components and components remain reusable. A violation fails the build.

## More information
- ADR-0007 (the decision to enforce these boundaries with automated checks)
- Python tools for Polylith (the implementation we use): https://davidvujic.github.io/python-polylith-docs/
- Original Polylith documentation (Clojure; concepts apply, tooling and examples do not): https://polylith.gitbook.io/polylith/
- Best Simple System for Now (BSSN): https://dannorth.net/blog/best-simple-system-for-now/
