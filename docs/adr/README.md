# Architecture Decision Records
This directory is the single decision log for the workspace. Every architecturally significant decision lives here as a numbered, immutable Markdown file.

## Why a central log (and not per-brick)
- Most significant decisions span multiple bricks or the whole workspace (deployment shape, dependency rules, tooling, interface compatibility policy). They have no single brick home.
- Bricks move: components get split, merged, renamed, or promoted across projects. ADRs are immutable records that must outlive the current shape of the code.
- One global sequence means one greppable decision log and compatibility with ADR tooling (MADR, adr-tools, log4brains), which all assume one directory.

Discoverability per brick is preserved by:
1. The `affects:` field in each ADR's front matter, which names the bricks and projects the decision touches. `grep -rl "my_component" docs/adr` finds them.
2. An optional one-line pointer in a brick's `__init__.py` docstring when the decision changes that brick's public contract, e.g. `"""See ADR-0007 for the public interface contract."""`.

## Conventions
- Filenames: `NNNN-short-kebab-title.md`, zero padded, e.g. `0012-deploy-projects-as-lambdas.md`.
- Numbers are assigned sequentially and never reused.
- ADRs are immutable. To reverse or change a decision, write a new ADR and set the old one's status to `superseded by ADR-NNNN`.
- `0000-adr-template.md` is the template. Copy it, do not edit it in place.
- ADRs are started by the developer. An agent drafts one only when asked, and never offers one unprompted. A choice that is still open is an `OPEN:` line in `docs/spec/`, not a proposed ADR (see `docs/spec/README.md`, "Decisions", and ADR-0008).

## Status lifecycle
`proposed` -> `accepted` -> (`deprecated` | `superseded by ADR-NNNN`)

## Polylith-specific fields
- `affects`: the components, bases, and projects the decision touches.
- `interface-impact`: whether the decision changes a public brick interface (the `__init__.py` contract). `none`, `new`, or `breaking`. This is the field that matters most in a Polylith workspace, because an interface change ripples to every project that consumes the brick, while an implementation change behind a stable interface stays local.

## Enforcement
Where a decision can be checked by tooling, record how in the ADR's `Confirmation` section. Polylith gives you `poly check` and `poly deps` for dependency and interface rules; lean on those rather than prose where you can.
