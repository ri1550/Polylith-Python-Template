# Workspace checks
Small scripts that enforce the development process described in `AGENTS.md`. They are run automatically by pre-commit (locally) and CI (on GitHub), and you can also run any of them by hand.

| Check | What it does | Blocks? |
|-------|--------------|---------|
| `lint.py` | Validates every ADR's filename, front matter, status, `interface-impact`, and `affects`, checks for duplicate numbers, and verifies that brick names in `affects` exist in the filesystem. | Yes, locally and in CI |
| `interface_change_check.py` | Flags a changed public `__init__.py` that has no ADR. Warns locally, blocks in CI. | Local: no. CI: yes |
| `adr_index.py` | Regenerates `docs/adr/index/`, a per-brick view of which ADRs affect which brick. | Refreshes files locally; not enforced in CI (avoids merge conflicts on parallel branches) |
| `pyright` (external tool) | Type-checks all code under `scripts/checks/`, `components/`, `bases/`, and `test/`. | Yes, locally and in CI |
| `remind.py` | Prints a pointer to the definition of done in AGENTS.md at the end of every pre-commit run. | Never blocks; always runs last |

Run any of them directly from the workspace root:

    python scripts/checks/lint.py
    python scripts/checks/adr_index.py
    python scripts/checks/interface_change_check.py --mode pre-commit
    python scripts/checks/remind.py

## Dependencies
These scripts need `pyyaml`. Pre-commit and CI install it automatically. To run them by hand in your own environment, make sure `pyyaml` is available (it is listed as a dev dependency, so `uv sync` covers it).

## Editing a check
These are intentionally simple (Best Simple System for Now). If you change what a check enforces, update `AGENTS.md` and `CONTRIBUTING.md` to match, and consider whether the change deserves an ADR.

