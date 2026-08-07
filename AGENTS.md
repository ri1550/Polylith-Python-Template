# AGENTS.md
## What this is
This is a Polylith workspace. This file governs how context about the codebase (why things are the way they are, what each part does, how to work on it) lives in the codebase itself, and how you, the agent, read it before editing and write it after.

The guiding idea: a brick's full context should always be a few cheap reads, regardless of how large the codebase grows. That holds only because each kind of context has exactly one home and is reached by query or by sitting next to the code, never by reading piles, and because the content in those homes is kept honest by discipline and review — the automated checks enforce structure, not substance. Your job on the write side is distillation, not capture.

Layout:

    bases/            thin entry points (one per app or service)
    components/       business logic, shared across projects
    projects/         deployable artifacts (no business logic here)
    development/      scratch space, REPL and notebook work
    test/             tests, mirroring the brick layout under bases/ and components/
    docs/adr/         the decision log (and a generated per-brick index)
    scripts/checks/   the automated checks that keep the process honest

## Polylith rules
- Bricks are `components` and `bases`. Components hold business logic and are shared across projects. Bases are thin entry points to an app or service.
- Components must not import from bases. Dependency flows base -> components, never the reverse, so components stay reusable. Enforced by `poly check` and `poly deps`.
- Projects (`projects/`) combine a base with components into a deployable artifact. Put no business logic there, only project infrastructure (Dockerfiles, deploy scripts, `pyproject.toml`).
- The development project keeps the whole workspace importable in one virtual environment for REPL and test-driven work.

## Guiding principle: Best Simple System for Now (BSSN)
Build the simplest thing that meets the need right now, written to an appropriate standard, with no speculative future-proofing. See ADR-0003 for the rationale.

In practice:
- Do not record a decision you have not made. No ADR for a deployment shape, tool, or policy that is still open. Polylith lets you defer these on purpose.
- Do not add a layer where the code is self-evident. A trivial brick needs no README; an obvious change needs no ADR.
- Do not future-proof the context itself: no speculative fields, no per-brick scaffolding "just in case." Add structure when a real need appears, not before.
- When something can be taken away and the system still works for now, take it away. That applies to ADRs and READMEs as much as to code.

## The context layers
Five homes, each owning one kind of context:

| Layer                         | Owns                                              | Mutable? | Enforced? |
|-------------------------------|---------------------------------------------------|----------|-----------|
| `__init__.py`                 | The brick's public interface (its surface)        | yes      | `poly check` |
| Tests (per brick)             | How the brick behaves and how to call it          | yes      | CI |
| Brick `README.md` / docstring | Why the brick is shaped this way: intent, invariants | yes   | no |
| `docs/adr/`                   | Decisions with real alternatives, and their rationale | append-only | linter (front matter) |
| Commit message / PR body      | What a specific change did                         | immutable | no |

Anything that doesn't belong to one of these layers does not go in the codebase.

## Reading a brick before editing
Load the full context in this order before touching any brick:
1. **What the brick exposes (its public surface):** `__init__.py`. In Polylith this is the interface contract, enforced by `poly check`, so it cannot drift. Anything imported there without a leading underscore is public.
2. **How it behaves and how to call it:** the brick's tests. They are working examples guaranteed current, because CI fails the moment code and test disagree. Read these to learn what a brick does, before anything else.
3. **Why it is shaped this way (intent, invariants, non-obvious constraints):** the brick's `README.md` or module docstring. The one prose layer; carries only what a test cannot assert.
4. **Why a decision was made (with alternatives):** `docs/adr/`, filtered to the brick rather than read whole (see below).

Four reads, all current, at any codebase size. For what a specific change did, also check the commit message or PR description.

### Finding the decisions that touch a brick
Do not read the whole ADR log. Query it by the `affects` field:

    grep -rl "<brick_name>" docs/adr/

This returns the handful of decisions touching that brick out of however many total. If the index generator is wired in, read the prebuilt `docs/adr/index/<brick_name>.md` instead.

## Routing what you learned
How to route what you learned this session into the codebase, and what to discard. Most session material is not durable; if a thing does not clearly match one of these, discard it rather than inventing a home for it.

- **Made a choice with real alternatives someone might later reverse?** ADR. If the choice changes behavior, the test that pins the new behavior is part of recording it.
- **Changed a brick's public surface?** The `__init__.py` change itself, a test asserting the new contract behaves as intended, plus an ADR if it was a genuine decision and a README update if the prose needs it.
- **Established or changed how a brick is supposed to behave** (an edge case, an input/output guarantee, a regression you just fixed)? A test. This is the executable half of "how it works," and it is preferred over prose whenever the behavior can be asserted.
- **Learned a durable gotcha or invariant that no assertion can capture**, something about intent or rationale rather than behavior? Brick README or docstring.
- **Just describes what this diff does?** Commit or PR body.
- **Exploration that concluded nothing durable?** Discard. Do not write it anywhere.

When something could live as either a test or a README line, the test wins. It is enforced; the prose is not. Prose only catches what an assertion structurally cannot, which is why intent and rationale are the README's job.

## Working with the developer
This file is guidance you follow while working; it catches most process gaps in conversation. It cannot by itself force anyone to do anything. The hard guarantee comes from the automated gates under "What is enforced vs trusted" (CI and pre-commit hooks). Use both: you guide while the work happens, the gates block what slips through.

Assume the developer may be junior or moving fast and may not know Polylith vocabulary. The system works only if you carry the process, not them.

How to behave:
- **Do the bookkeeping yourself.** When a change needs an ADR, a test, or a README update, draft it and ask the developer to confirm. Do not tell them to go write it. Make the correct path the easy one.
- **Explain the term as you use it.** When you say base, brick interface, or `interface-impact`, add a one-line plain explanation. Do not assume the vocabulary is known.
- **One question at a time.** Do not interrogate. Ask the single most important confirmation, act on the answer, move on.
- **Prefer the simplest action (BSSN).** If a brick is trivial, say a README is not needed rather than creating one "to be safe." Ask before adding structure.

### Stop and confirm before
- **Changing a public interface** (a brick's `__init__.py` surface). Say plainly: "this changes what other code depends on; every project using `<brick>` is affected. Intended?" If yes, set `interface-impact`, draft the ADR, add or adjust the test.
- **Making a decision with real alternatives.** Say: "this is a choice with other options (A, B). Want me to record a short ADR so it is not relitigated later?" Draft it if yes. Drop it if it is not actually significant (BSSN).
- **Anything destructive or hard to reverse:** deleting or renaming a brick or a public name, merging or splitting components, moving a dependency boundary. Confirm intent and name the blast radius (`poly diff` shows the affected bricks).
- **Putting business logic in a base or a project.** Remind: logic lives in components, bases stay thin, projects hold no code.
- **Adding a dependency.** Ask whether it is needed now or whether a few lines do the job for now.

### Remind, but do not block, when
- A behavior changed and no test was added for it.
- A public interface changed and no ADR is linked.
- A brick's README or docstring now contradicts the code.
- Scratch or exploration is left in `development/` that should be cleaned up.

### Pre-commit checklist
The automated checks enforce structure. This covers what they cannot:
1. **Behavior added or changed → a test asserts it.** If you changed what a brick does or fixed a bug, there should be a test that would fail without that change. A test that only passes incidentally teaches nothing and breaks on refactor.

2. **A real decision was made → ADR drafted, or explicitly declined.** A real decision is one with genuine alternatives that someone might later reverse. If yes, draft the ADR and confirm with the developer. If it was not actually significant, note that explicitly rather than leaving it implicit (BSSN: do not write ADRs for non-decisions either).

3. **README / docstring still matches the code.** If the public surface or the brick's intent changed, check that the prose still accurately describes it. Stale prose is worse than no prose — it actively misleads.

4. **Scratch work discarded from `development/`.** Exploration, temporary scripts, and notebook work that concluded nothing durable should be removed. If something durable was found, route it to the right layer instead of leaving it in `development/`.

## Conventions
### ADRs
- Location: `docs/adr/`, a single global numbered sequence. Not per brick.
- Template: copy `docs/adr/0000-adr-template.md`. Do not edit it in place. It is MADR 4.0 (see References) extended with the `affects` and `interface-impact` fields.
- Filenames: `NNNN-short-kebab-title.md`, zero padded.
- Numbers are sequential and never reused.
- Body prose: single line per paragraph (no hard-wrapping). Markdown renders it the same; keeps grep -rl matches to a single line per hit.
- ADRs are immutable. To reverse a decision, write a new ADR and set the old one's status to `superseded by ADR-NNNN`.
- Status lifecycle: `proposed` -> `accepted` -> (`deprecated` | `superseded`).
- Front matter carries `affects` (the components, bases, and projects the decision touches) and `interface-impact` (`none` | `new` | `breaking`).
- A change that breaks a public `__init__.py` contract requires an ADR. An interface change is exactly the kind of decision worth recording.
- ADRs are for decisions. Do not write one to describe current state, and do not write one for a brick whose shape involved no contested choice.

### Tests
- Live per brick. Run them with `pytest`. `poly diff` shows which bricks a change affects; that signal also tells you the blast radius of what you touched.
- Assert the contract and documented behavior, not implementation internals. A test pinning an incidental detail breaks on every refactor and teaches the next reader nothing. Test at the interface; leave the implementation free to change.

### README / docstring
- Use a module docstring in `__init__.py` for the short "what this exposes and how to call it" note (shows up in `help()` and IDE hovers). Promote to a `README.md` in the brick when the description runs longer or needs examples.
- Do not write both saying the same thing; they will drift.
- Not mandatory per brick. A trivial one-function component is self-explanatory; a README there is noise. Write one when the brick has enough surface or non-obvious behavior to warrant it.

## Guardrails
- The interface contract lives only in `__init__.py`. Never copy it into prose; the copy drifts and the prose is not enforced.
- Behavioral guarantees live in tests, not in README prose. If it can be asserted, assert it.
- Raw session narrative does not go in the codebase. Only the distilled, routed artifacts above.
- Keep the prose layer to slow-changing things: purpose, invariants, non-obvious constraints. Volatile specifics belong in the contract and the tests, where they are enforced. The more you push into prose, the more drift you buy.

## What is enforced vs trusted
Two layers hold the process together. The agent behavior above is the soft layer: it catches gaps in conversation, while the work happens. The gates below are the hard layer: they block non-compliant changes regardless of who or what made them. For junior or fast-moving developers, the gates are what actually force the process; the agent guidance only makes following it the easy path. Wire the gates up early.

Hard gates (block the change):
- `poly check` / `poly deps`: interface contracts and the no-base-import rule.
- Tests (`pytest`) in CI: behavioral guarantees in tests.
- Type check (`pyright`): Python types are valid across all checked code.
- Decision log lint (`scripts/checks/lint.py`): front matter parses, statuses are valid, numbering is sequential and unique, `affects` names real bricks.
- Interface-change check (`scripts/checks/interface_change_check.py`): a PR changing a public `__init__.py` surface must link an ADR or justify `interface-impact`. This keeps the why-layer honest.
- Pre-commit hooks (`.pre-commit-config.yaml`): run `poly check`, the linter, the ADR index refresh, and the type check locally before a commit lands, so feedback comes in seconds rather than from a failed CI run. Highest-leverage gate for juniors.
- CI (`.github/workflows/checks.yml`) plus branch protection on `main`: the unskippable server-side gate. See CONTRIBUTING.md for the one-time setup.

The per-brick ADR index is generated by `scripts/checks/adr_index.py` into `docs/adr/index/`. Setup and the day-to-day loop for developers live in CONTRIBUTING.md; the decisions behind this enforcement are in `docs/adr/`.

Trusted (convention, made easy but not blocked):
- Good commit and PR messages, the discard discipline, README and docstring accuracy. Distillation quality cannot be fully enforced; this file and the agent behavior make the correct path the easy one.
- The `[interface-impact: none]` escape in the interface-change check is self-reported. The check enforces that something was said; code review is the backstop against an agent or developer using it to avoid recording a real interface change.

