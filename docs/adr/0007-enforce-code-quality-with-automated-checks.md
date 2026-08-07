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

# ADR-0007: Enforce code quality with automated checks
## Context and problem statement
The codebase needs to stay architecturally sound and type-correct as it grows. Relying on code review alone to catch broken brick boundaries, failing tests, or type errors does not scale and is exactly what fails under time pressure. We need code quality to be enforced at the gate.

## Decision drivers
- Brick boundaries and the no-base-import rule must be structurally enforced, not just documented.
- Behavioral guarantees must be verified on every change, not assumed.
- Type errors should be caught before they reach code review.
- Best Simple System for Now: use established tools, wire them into the same two-layer gate as ADR-0006.

## Considered options
- Rely on code review alone
- Run checks locally by convention only
- Pre-commit hooks only (local)
- CI checks only (server)
- Both layers: pre-commit hooks plus CI gated by branch protection

## Decision outcome
Chosen option: Both layers, following the same approach as ADR-0006. The checks are `poly check` (brick boundaries and interface contracts), `pytest` (behavioral guarantees), and `pyright` (type correctness). Pyright is chosen over mypy because it is faster, has strong IDE integration across editors, and gives developers inline feedback that matches what CI blocks. Pyright runs in `basic` mode, configured via `pyrightconfig.json`.

### Consequences
- Good: architectural violations, test failures, and type errors are all caught before code reaches `main`.
- Good: fast local feedback reduces failed CI runs.
- Good: editor and gate use the same type checker (pyright), so inline feedback matches what CI blocks.
- Bad: a small amount of setup per contributor (`pre-commit install`) and one repository setting (branch protection) that an admin must enable.
- Neutral: pyright runs in `basic` mode; stricter modes can be adopted as the codebase grows and annotations become more complete.

### Confirmation
`poly check` enforces brick boundaries and the interface contract on every commit. `pytest` runs the test suite in CI. `pyright` type-checks all code under `scripts/checks/`, `components/`, `bases/`, and `test/`, configured via `pyrightconfig.json`. All three run in CI as part of the `checks` workflow required by branch protection on `main`.

## More information
- ADR-0002 (the Polylith architecture `poly check` enforces)
- ADR-0006 (context system checks that use the same two-layer approach)
- `CONTRIBUTING.md` (setup and day-to-day workflow)
- `scripts/checks/README.md` (what each check does)
- Best Simple System for Now (BSSN): https://dannorth.net/blog/best-simple-system-for-now/
