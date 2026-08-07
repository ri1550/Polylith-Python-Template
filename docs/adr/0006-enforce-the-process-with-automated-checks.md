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

# ADR-0006: Enforce the context system with automated checks
## Context and problem statement
ADR-0005 records how context lives in the codebase, and `AGENTS.md` describes the process for keeping it accurate. But a written process that relies on people, and on AI agents, remembering to follow it will drift, especially with junior or fast-moving contributors. We need the context system to be enforced, not just described.

## Decision drivers
- The process must hold even when the contributor does not know or recall it.
- Feedback should arrive fast, ideally before a bad change is even committed.
- There must be a gate that cannot be skipped, to actually protect `main`.
- Best Simple System for Now: the least machinery that makes the correct path the easy one and blocks the wrong one. No heavyweight policy engine.

## Considered options
- Rely on code review alone
- Rely on `AGENTS.md` and the agent's good behavior alone
- Pre-commit hooks only (local)
- CI checks only (server)
- Both layers: pre-commit hooks plus CI gated by branch protection

## Decision outcome
Chosen option: Both layers. Pre-commit hooks give fast, local feedback (a warning or a blocked commit at the keyboard). CI re-runs the same checks on GitHub, and branch protection makes passing them a requirement to merge. The checks are small scripts in `scripts/checks/`: decision log lint and brick-name validation (`lint.py`), ADR index generation (`adr_index.py`), interface-change recording (`interface_change_check.py`), and a bookkeeping reminder (`remind.py`) that prints a pointer to the pre-commit checklist in `AGENTS.md` at the end of every pre-commit run so the agent sees it in context before the commit lands.

Both layers over the alternatives because review and good intentions do not scale and are exactly what fails with juniors; pre-commit alone can be bypassed (`--no-verify`) and lives only on each machine; CI alone gives slow feedback and lets a broken change get committed and pushed before catching it. Together, the local layer keeps most problems from ever being committed, and the server layer is the unskippable gate.

Code quality checks (`poly check`, `pytest`, `pyright`) follow the same two-layer approach and are covered in ADR-0007.

### Consequences
- Good: the context system is enforced regardless of who or what makes a change; the hard gate (branch protection) cannot be skipped.
- Good: fast local feedback reduces failed CI runs.
- Bad: a small amount of setup per contributor (`pre-commit install`) and one repository setting (branch protection) that an admin must enable. If branch protection is not enabled, CI advises but does not block.
- Neutral: the interface-change check is heuristic; it is satisfied by a numbered ADR file (`NNNN-*.md`) in the pull request whose affects names the changed brick, an explicit ADR reference in a commit message (`ADR-NNNN`), or an explicit `[interface-impact: none]` note. The last two are self-reported; code review is the backstop against misuse.

### Confirmation
The `checks` workflow runs in CI on every pull request and is required by branch protection on `main`. The checks enforce themselves: a misconfiguration shows up as a failing run. `scripts/checks/lint.py` validates every ADR's filename, front matter, field values, sequential numbering, and that brick names in `affects` exist. `scripts/checks/adr_index.py` keeps `docs/adr/index/` current locally; it runs as a pre-commit hook but is not enforced in CI to avoid merge conflicts on parallel branches. `scripts/checks/interface_change_check.py` blocks a merge that changes a public `__init__.py` without a recorded decision. `scripts/checks/remind.py` runs last on every pre-commit run and prints a pointer to the pre-commit checklist in `AGENTS.md`. The `CONTRIBUTING.md` documents the per-contributor and admin setup.

## More information
- ADR-0005 (the context system this enforces)
- ADR-0007 (code quality checks that use the same two-layer approach)
- `CONTRIBUTING.md` (setup and day-to-day workflow)
- `scripts/checks/README.md` (what each check does)
- `AGENTS.md` (the process these checks enforce)
- pre-commit: https://pre-commit.com/
- Best Simple System for Now (BSSN): https://dannorth.net/blog/best-simple-system-for-now/
