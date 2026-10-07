# Workspace
A Polylith monorepo. Code lives as small bricks (components and bases) that combine into deployable projects, and the repo keeps its own context so anyone, human or AI agent, can understand why things are the way they are.

## Getting started
You need [uv](https://docs.astral.sh/uv/). Then, from this directory:

    git init                     # if this is not already a git repo
    uv sync                      # create the env, install deps and the poly tool
    uv tool install pre-commit   # the check runner
    pre-commit install           # turn the checks on for this repo

`uv sync` also makes the `myorg` namespace importable, so the bricks work without any PYTHONPATH fiddling.

## Run it
The example base has an entry point that delegates to the greeting component:

    uv run python -c "from myorg.api.core import main; print(main())"
    # -> Hello, world!

## Common commands

    uv run pytest                # run all tests
    uv run poly check            # validate the workspace (boundaries, interfaces)
    uv run poly info             # overview of bricks and projects
    uv run poly diff             # show which bricks changed since the last tag
    uv run poly deps             # show dependencies between bricks
    uv run poly libs             # show third-party libraries in use
    uv run python scripts/checks/spec.py status   # what works (spec rules with a citing test) and what is queued

## Create new bricks

    uv run poly create component --name <name>   # business logic, shared
    uv run poly create base --name <name>        # a thin entry point
    uv run poly create project --name <name>     # a deployable artifact

A component's public interface is its `__init__.py`; its implementation is the other modules in the brick. Keep business logic in components, keep bases thin, and put no code in `projects/`.

## Build and deploy
A `project` under `projects/` is the deployable unit. After creating one, build it with uv from its own directory; each project has its own `pyproject.toml` that lists exactly the bricks and libraries it needs. The packaging details (the build hook that bundles the bricks into the artifact) are covered in the Polylith deployment docs: https://davidvujic.github.io/python-polylith-docs/deployment/

## Where to read more
- New contributor: `CONTRIBUTING.md` (setup and the day-to-day loop in detail).
- AI agent, or the full process and where every kind of context lives: `AGENTS.md`.
- The decisions behind this setup: `docs/adr/`.

## Layout

    bases/         thin entry points (one per app or service)
    components/    business logic, shared across projects
    projects/      deployable artifacts (no business logic here)
    development/   scratch space, REPL and notebook work
    test/          tests, mirroring the brick layout
    docs/spec/     the behavior contract: one file per product domain, numbered rules, OPEN: questions
    docs/queue.yaml the build queue: which rules to implement next, in order (agent-maintained)
    docs/adr/      the decision log (and a generated per-brick index)
    scripts/checks/ the automated checks that keep the process honest

## Example bricks
`components/myorg/greeting` and `bases/myorg/api` are examples that demonstrate the interface/implementation split, and `docs/spec/greeting.md` is the matching example spec domain whose two rules the greeting tests cite. Delete all three once you have your own.

## Namespace
The top namespace is `myorg` (see `workspace.toml`). To use your own, rename the `myorg` folders and the namespace in `workspace.toml` consistently.
