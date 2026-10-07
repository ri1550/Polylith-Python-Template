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

# ADR-0008: Add a behavior spec and a build queue as context layers
## Context and problem statement
ADR-0005 gives the codebase five context layers, all of which describe code that exists: its interface, its behavior, its intent, the decisions behind it, and what each change did. None of them holds what the product is supposed to do before the code exists, so an agent asked to build a brick has nowhere to look for the target and nothing to stop it from inventing one. Nor does any layer hold the order of work across sessions, so each session re-derives what to do next from the conversation. A sibling project ran a fuller version of this before it reached the template: a spec directory, an ideas directory, and a plan file with in-flight state and a blocked list. The spec held up; the plan drifted and duplicated other layers; the ideas directory was useful to that project but did not generalise.

## Decision drivers
- An agent must implement intended behavior and nothing else, and must be able to tell the two apart without asking.
- Undecided questions need one home and one grep, so they are never silently resolved by the agent.
- Current state must not be written down by hand, because hand-maintained state drifts (ADR-0005, BSSN).
- The order of work has to survive a session ending and an agent's context being compacted.
- Agents offer architecture decision records far more often than they are wanted, and an unwanted ADR is noise in an append-only log.

## Considered options
- A behavior spec with numbered rules and `OPEN:` lines, plus a minimal queue of rule ranges whose state is derived from test citations (chosen).
- A spec plus a full plan file holding in-flight state, a queue with done-when sentences, and a blocked list, maintained through a CLI.
- A spec only, with order kept in the developer's head or an issue tracker.
- No spec; tests as the only behavior layer, with intent agreed in conversation each session.
- An ideas directory alongside the spec for parked, not-yet-intended work.

## Decision outcome
Chosen option: a behavior spec and a derived-state build queue, as two new context layers alongside the five from ADR-0005.

The spec is `docs/spec/`, one file per product domain with five fixed headings. Behavior rules are numbered sentences a test could assert, numbers are permanent, and unsettled questions are `- OPEN:` lines. A test pins a rule by citing it as `<domain> rule N`. Rules come from the developer; anything the agent derives on its own is an `OPEN:` line. What works today is not written anywhere: it is the set of rules with a passing test citing them, derived by `scripts/checks/spec.py status`.

The queue is `docs/queue.yaml`, an ordered list of steps, each a range of spec rules for one brick with an optional dependency on an earlier step. A step's state (waiting on spec, ready, in progress, done) is derived from whether its rules exist and whether tests cite them. Finished steps are deleted. There is no in-flight state, no done-when prose, and no blocked list: in-flight state belongs to the session, done-when is the rule text, and a blocked step is one waiting on a domain's `OPEN:` lines.

ADRs stay the developer's instrument. An `OPEN:` line is not a pending ADR, and the agent never drafts or offers one unless the developer asks. The template previously had the agent propose ADRs; that is withdrawn here.

Over the full plan file because each of its extra parts duplicated a layer that already existed, and the duplicate drifted: in-flight state duplicated the session, done-when prose restated the spec, and the blocked list filled with decisions that no queued step depended on, which ADR-0003 says not to record. Over a spec-only approach because order does not survive a session boundary. Over no spec because the agent then has no way to distinguish intended behavior from its own guesses. The ideas directory is not adopted: in trial use it leaked `OPEN:` lines and dead links into files whose job was to prevent exactly that, and its value was specific to one project's way of thinking.

### Consequences
- Good: an agent can tell what is intended, what is undecided, and what works, each by one grep or one command, with nothing maintained by hand except the rule text and the order.
- Good: the one thing the queue holds that nothing else does, order, is cheap to keep honest because its state is computed.
- Good: fewer unwanted ADRs. The decision log stays a record of architectural direction.
- Bad: a product question the developer has not answered blocks the brick that needs it. This is intended; it is the cost of never inventing a rule.
- Bad: the spec's substance (whether a rule is true and worth having) is trusted, not enforced. The lint checks shape and citations; the developer's confirmation is the backstop.
- Neutral: chores that cite no rule have no home in the queue. They are done now, dropped, or tracked in an issue tracker.

### Confirmation
`scripts/checks/spec.py lint` runs in pre-commit and CI and fails on wrong headings, broken rule numbering, a citation of a rule that does not exist, a broken link under `docs/`, a glossary term redefined in a domain, or a malformed queue. `pytest` holds every pinned rule. `spec.py status` is printed into the agent's context by a SessionStart hook so the derived state is read, not reconstructed. The example `greeting` component ships with a two-rule domain and tests citing both, so the loop is exercised on every fresh clone.

## More information
- ADR-0005 (the five original layers; this ADR extends it and does not supersede it)
- ADR-0006 (enforcing the process with automated checks)
- `docs/spec/README.md` (the spec's conventions and lifecycles)
- `docs/queue.yaml` (the queue's shape, in its header) and `scripts/checks/spec.py` (lint and status)
- `AGENTS.md` (the living specification these layers plug into)
