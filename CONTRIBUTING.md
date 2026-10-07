# Contributing
This repository keeps its own context: why things are the way they are, what each part does, and how to work on it. A few small automated checks keep that context honest so the codebase stays understandable as it grows.

You do not need to memorize how it all works. The checks guide you, and the AI agent does most of the paperwork (tests, spec lines, queue updates, and the ADRs you ask for) for you. Your job is mostly to follow the setup below once, then answer the agent's questions as you work.

If you want the full reasoning, read `AGENTS.md`. This file is just how to get set up and what to do day to day.

## One-time setup (do this once after cloning)
1. **Install uv** (our package manager). Follow the instructions at https://docs.astral.sh/uv/. On macOS or Linux this is usually one command in your terminal.

2. **Install everything the project needs:**

       uv sync

   This creates the project's environment and installs the tools, including `poly` (the Polylith command) and the check dependencies.

3. **Install pre-commit** (the tool that runs checks when you commit):

       uv tool install pre-commit

4. **Turn the checks on for this repo:**

       pre-commit install

That is it. From now on, the checks run automatically every time you commit.
To check everything at once at any time:

    pre-commit run --all-files

## The everyday loop
1. **Edit your code.** Ask the agent for help; it knows the rules in `AGENTS.md`.
2. **Commit.** When you run `git commit`, the checks run first. If something is wrong, the commit stops and tells you what to fix. Fix it and commit again.
3. **Push** your branch to GitHub.
4. **Open a pull request.** GitHub runs the same checks on its servers.
5. **Merge** once the checks are green. With branch protection on (see below), the button stays locked until they pass.

The checks on your machine are the fast warning. The checks on GitHub are the real gate. Same checks, two moments.

## When a check stops you, here is what it means
You do not need to understand the internals. Read the message, do the fix, try again.

- **"Polylith check" failed.** A brick boundary was crossed, usually a component importing from a base, or a broken interface. The message names the problem. Ask the agent to help move the code to the right place.

- **Tests failed.** One or more tests are failing. The output names the file and test. Fix the code or the test, then commit again.

- **"ADR front matter lint" failed.** A decision record under `docs/adr/` is missing a field or has an invalid value. The message says which file and which field. Copy `docs/adr/0000-adr-template.md` if you are starting one from scratch, or ask the agent to fix the fields.

- **"Interface change heads-up" (local).** You changed a brick's public `__init__.py`. This is a warning, not a block. If it is a real change to what other code depends on, ask the agent to draft an ADR for it. You will need one before the pull request can merge.

- **"Interface change must be recorded" (on GitHub) failed.** Same situation, but now it blocks the merge. Do one of: add an ADR describing the change (best, the agent can draft it), mention an ADR in a commit message like `ADR-NNNN: ...`, or if the edit was not really a contract change (a comment or formatting), add `[interface-impact: none]` to a commit message. Note: `[interface-impact: none]` is self-reported — code review is the backstop against misuse.

- **"Spec and queue lint" failed.** A product spec file under `docs/spec/` has the wrong headings or rule numbering, a test cites a rule that does not exist, a link under `docs/` is broken, or `docs/queue.yaml` (the agent's build queue) is malformed. The message names the file and line. Ask the agent to fix it; you do not need to read the queue yourself.

- **"Type check (pyright)" failed.** A type error was found in the code. The message names the file, line, and what the type checker expected. Ask the agent to fix it, or fix it yourself and commit again.

- **"Refresh the ADR index" changed files.** The check updated the generated index under `docs/adr/index/`. Nothing is wrong. Just `git add` the changed files and commit again. (This only runs locally; CI does not enforce index freshness to avoid merge conflicts on parallel branches.)

- **"trailing whitespace" or "end of file" fixed something.** A tidy-up hook cleaned the file. Re-add it and commit again.

## If you are setting up the repository (admin, one time)
Before anything else, replace the placeholders left by the starter:
- **Namespace**: rename `myorg` to your organisation or project name throughout `components/`, `bases/`, `test/`, and `workspace.toml`.
- **ADR dates**: fill in the `date:` field in each ADR under `docs/adr/` with the date you are formally adopting the decision.
- **ADR decision-makers**: replace `[you]` in each ADR's front matter with the actual names or roles.
- **Example bricks**: delete `components/myorg/greeting` and `bases/myorg/api` (and their tests), and the matching example spec domain `docs/spec/greeting.md`, once you have your own bricks.
- **Inherited tags**: if you cloned or forked this repository instead of using GitHub's **Use this template** button, delete the template's own baseline tags. Otherwise `poly diff` compares your bricks against the template's baseline instead of your own.

      git tag -d $(git tag -l 'stable-*')

Then, make the checks a hard gate by configuring GitHub branch protection:
1. Go to **Settings > Branches**.
2. Under **Branch protection rules**, click **Add rule**.
3. Branch name pattern: `main`.
4. Tick **Require a pull request before merging**.
5. Tick **Require status checks to pass before merging**, then select the **checks** workflow.
6. Click **Create** (or **Save changes**).

Now no change can reach `main` without passing the checks, no matter who or what made it. This is the piece that actually enforces the process; everything else is guidance that makes following it easy.

## Why all of this
The short version: context that lives next to the code and stays accurate is worth far more than docs that drift. The checks stop the context from drifting. The full reasoning, and the map of where every kind of context lives, is in `AGENTS.md`. The decisions behind the setup are in `docs/adr/`.
