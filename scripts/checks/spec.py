#!/usr/bin/env python3
"""The spec (docs/spec/) and the build queue (docs/queue.yaml): one lint, one status.

Two verbs, run from the workspace root with `uv run python scripts/checks/spec.py <verb>`:

    lint     Enforce the structure that docs/spec/README.md describes and the
             shape of docs/queue.yaml. Exit 1 on any problem. Runs in pre-commit
             and CI.
    status   Print what works and what is next, all derived, nothing written by
             hand: per domain, how many rules have a citing test and how many
             questions are open; then the queue in order with each step's state.
             Never fails. A SessionStart hook prints it into the agent's context.

What `lint` enforces:
  - every domain file in docs/spec/ has exactly the five headings, in order:
    Purpose, Vocabulary, Data, Behavior rules, Open questions
  - behavior rules are numbered from 1 with no gaps and no repeats
  - every `<domain> rule N` citation in test/ and docs/spec/ names a rule that
    exists in that domain file
  - no term defined in docs/spec/00-glossary.md is defined again in a domain's
    Vocabulary section
  - every relative markdown link under docs/ resolves to a file
  - docs/queue.yaml, if present, is `steps:` holding a list of mappings with the
    keys id, rules, and optionally brick and after; ids are unique kebab-case;
    rules is `<domain>: "n"` or `"lo-hi"` naming a domain file that exists;
    `after` names an earlier step

What `status` derives for each queue step:
  - waiting on spec: the step cites a rule number the domain does not have yet.
    The developer-facing question is that domain's OPEN: lines.
  - ready: every cited rule exists and none has a citing test
  - in progress: some cited rules have a citing test
  - done: every cited rule has a citing test. Delete the step; git is the record.

README.md and TEMPLATE.md in docs/spec/ are conventions, not domains, so their
headings and example citations are not checked. Generated index directories
under docs/ are skipped for link checking.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

DOCS_DIR = Path("docs")
SPEC_DIR = DOCS_DIR / "spec"
TEST_DIR = Path("test")
QUEUE = DOCS_DIR / "queue.yaml"
GLOSSARY = SPEC_DIR / "00-glossary.md"
NOT_DOMAINS = {"readme.md", "template.md", GLOSSARY.name.lower()}
GENERATED_DIRS = {DOCS_DIR / "adr" / "index"}

HEADINGS = ["Purpose", "Vocabulary", "Data", "Behavior rules", "Open questions"]
H2_RE = re.compile(r"^## (.*)$", re.MULTILINE)
RULE_RE = re.compile(r"^(\d+)\. ", re.MULTILINE)
OPEN_RE = re.compile(r"^- OPEN:", re.MULTILINE)
CITATION_RE = re.compile(r"\b([a-z0-9][a-z0-9-]*) rule (\d+)\b")
TERM_RE = re.compile(r"^\*\*([^*]+)\*\*\s*—", re.MULTILINE)
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")

STEP_KEYS = {"id", "rules", "brick", "after"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
RANGE_RE = re.compile(r"^(\d+)(?:-(\d+))?$")


# --- spec -----------------------------------------------------------------------


def domain_files() -> list[Path]:
    if not SPEC_DIR.is_dir():
        return []
    return sorted(p for p in SPEC_DIR.glob("*.md") if p.name.lower() not in NOT_DOMAINS)


def sections(text: str) -> dict[str, str]:
    """Split a domain file into its `## ` sections, in file order."""
    found: dict[str, str] = {}
    matches = list(H2_RE.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        found[m.group(1).strip()] = text[m.end():end]
    return found


def check_headings(path: Path, text: str, errors: list[str]) -> dict[str, str]:
    secs = sections(text)
    names = list(secs)
    if names != HEADINGS:
        errors.append(f"{path}: headings must be exactly {HEADINGS}, in that order; found {names}")
    return secs


def rule_numbers(path: Path, body: str, errors: list[str]) -> set[int]:
    numbers = [int(n) for n in RULE_RE.findall(body)]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        errors.append(
            f"{path}: behavior rules must be numbered 1..{len(numbers)} in order "
            f"with no gaps or repeats; found {numbers}"
        )
    return set(numbers)


def read_spec(errors: list[str]) -> tuple[dict[str, set[int]], dict[str, int]]:
    """Rule numbers and open-question counts per domain, recording structural errors."""
    rules: dict[str, set[int]] = {}
    open_counts: dict[str, int] = {}
    shared = glossary_terms()
    for path in domain_files():
        text = path.read_text(encoding="utf-8")
        secs = check_headings(path, text, errors)
        rules[path.stem] = rule_numbers(path, secs.get("Behavior rules", ""), errors)
        open_counts[path.stem] = len(OPEN_RE.findall(secs.get("Open questions", "")))
        check_vocabulary(path, secs.get("Vocabulary", ""), shared, errors)
    return rules, open_counts


def cited_rules() -> dict[str, set[int]]:
    """`<domain> rule N` citations found under test/, grouped by domain."""
    found: dict[str, set[int]] = {}
    if not TEST_DIR.is_dir():
        return found
    for path in TEST_DIR.rglob("*.py"):
        for m in CITATION_RE.finditer(path.read_text(encoding="utf-8", errors="replace")):
            found.setdefault(m.group(1), set()).add(int(m.group(2)))
    return found


def check_citations(rules: dict[str, set[int]], errors: list[str]) -> None:
    files: list[Path] = []
    if TEST_DIR.is_dir():
        files += [p for p in TEST_DIR.rglob("*") if p.is_file() and p.suffix in {".py", ".md"}]
    files += domain_files()
    if GLOSSARY.exists():
        files.append(GLOSSARY)
    for path in files:
        text = path.read_text(encoding="utf-8")
        for m in CITATION_RE.finditer(text):
            domain, number = m.group(1), int(m.group(2))
            line = text.count("\n", 0, m.start()) + 1
            if domain not in rules:
                errors.append(f"{path}:{line}: cites '{domain} rule {number}' but docs/spec/{domain}.md does not exist")
            elif number not in rules[domain]:
                errors.append(f"{path}:{line}: cites '{domain} rule {number}' but that rule does not exist")


def glossary_terms() -> set[str]:
    if not GLOSSARY.exists():
        return set()
    return {t.strip().lower() for t in TERM_RE.findall(GLOSSARY.read_text(encoding="utf-8"))}


def check_vocabulary(path: Path, body: str, shared: set[str], errors: list[str]) -> None:
    for term in TERM_RE.findall(body):
        if term.strip().lower() in shared:
            errors.append(
                f"{path}: Vocabulary redefines '{term.strip()}', which docs/spec/00-glossary.md already defines; link to it instead"
            )


def check_links(errors: list[str]) -> None:
    if not DOCS_DIR.is_dir():
        return
    for path in sorted(DOCS_DIR.rglob("*.md")):
        if any(g in path.parents for g in GENERATED_DIRS):
            continue
        text = path.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            if target.startswith(EXTERNAL_PREFIXES) or "<" in target:
                continue  # external, an anchor, or a <placeholder> in convention text
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{path}:{line}: link to '{target}' does not resolve")


# --- queue ----------------------------------------------------------------------


def load_queue(errors: list[str]) -> list[dict[str, Any]]:
    """The steps in docs/queue.yaml, in order. A missing file is an empty queue."""
    if not QUEUE.exists():
        return []
    import yaml

    try:
        data: Any = yaml.safe_load(QUEUE.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"{QUEUE}: not valid YAML: {exc}")
        return []
    if data is None:
        return []
    if not isinstance(data, dict) or set(data) - {"steps"}:
        errors.append(f"{QUEUE}: top level must be a mapping with the single key `steps`")
        return []
    steps = data.get("steps")
    if steps is None:
        return []
    if not isinstance(steps, list):
        errors.append(f"{QUEUE}: `steps` must be a list")
        return []
    for i, s in enumerate(steps, 1):
        if not isinstance(s, dict):
            errors.append(f"{QUEUE}: steps[{i}] must be a mapping with id and rules")
    return [s for s in steps if isinstance(s, dict)]


def parse_range(text: Any) -> tuple[int, int] | None:
    m = RANGE_RE.match(str(text).strip())
    if not m:
        return None
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    if lo < 1 or hi < lo:
        return None
    return lo, hi


def check_queue(steps: list[dict[str, Any]], rules: dict[str, set[int]], errors: list[str]) -> None:
    seen: list[str] = []
    for i, step in enumerate(steps, 1):
        where = f"{QUEUE}: steps[{i}]"
        extra = set(step) - STEP_KEYS
        if extra:
            errors.append(f"{where}: unknown keys {sorted(extra)}; allowed: id, rules, brick, after")
        sid = step.get("id")
        if not isinstance(sid, str) or not ID_RE.match(sid):
            errors.append(f"{where}: id must be kebab-case (got {sid!r})")
        elif sid in seen:
            errors.append(f"{where}: duplicate id {sid!r}")
        step_rules = step.get("rules")
        if not isinstance(step_rules, dict) or not step_rules:
            errors.append(f"{where}: rules must be a non-empty mapping of <domain>: \"n\" or \"lo-hi\"")
        else:
            for domain, rng in step_rules.items():
                if parse_range(rng) is None:
                    errors.append(f"{where}: rules[{domain}] must look like \"3\" or \"1-4\" (got {rng!r})")
                if str(domain) not in rules:
                    errors.append(f"{where}: rules names domain {domain!r}, but docs/spec/{domain}.md does not exist")
        after = step.get("after")
        if after is not None and after not in seen:
            errors.append(f"{where}: after names {after!r}, which is not an earlier step")
        if "brick" in step and not isinstance(step.get("brick"), str):
            errors.append(f"{where}: brick must be a string")
        if isinstance(sid, str):
            seen.append(sid)


def step_rule_set(step: dict[str, Any]) -> dict[str, set[int]]:
    out: dict[str, set[int]] = {}
    step_rules = step.get("rules")
    if isinstance(step_rules, dict):
        for domain, rng in step_rules.items():
            r = parse_range(rng)
            if r is not None:
                out[str(domain)] = set(range(r[0], r[1] + 1))
    return out


def step_state(step: dict[str, Any], rules: dict[str, set[int]], cited: dict[str, set[int]]) -> str:
    wanted = step_rule_set(step)
    if not wanted:
        return "MALFORMED, run `spec.py lint`"
    missing = {d: sorted(n for n in ns if n not in rules.get(d, set())) for d, ns in wanted.items()}
    missing = {d: ns for d, ns in missing.items() if ns}
    if missing:
        detail = "; ".join(f"{d} has no rule {', '.join(map(str, ns))}" for d, ns in missing.items())
        return f"WAITING ON SPEC ({detail}; see its OPEN: lines)"
    total = sum(len(ns) for ns in wanted.values())
    have = sum(len(ns & cited.get(d, set())) for d, ns in wanted.items())
    if have == 0:
        return "READY"
    if have < total:
        return f"IN PROGRESS ({have}/{total} rules have a citing test)"
    return "DONE, delete this step"


def fmt_rules(step: dict[str, Any]) -> str:
    step_rules = step.get("rules")
    if not isinstance(step_rules, dict):
        return "?"
    return ", ".join(f"{d} {r}" for d, r in step_rules.items())


# --- verbs ------------------------------------------------------------------------


def lint() -> int:
    errors: list[str] = []
    rules, _ = read_spec(errors)
    check_citations(rules, errors)
    check_links(errors)
    steps = load_queue(errors)
    check_queue(steps, rules, errors)
    if errors:
        print("Spec lint found problems:")
        for e in errors:
            print(f"  - {e}")
        return 1
    total = sum(len(r) for r in rules.values())
    print(f"Spec lint passed: {len(rules)} domain(s), {total} rule(s), {len(steps)} queue step(s), links resolve.")
    return 0


def status() -> int:
    errors: list[str] = []
    rules, open_counts = read_spec(errors)
    cited = cited_rules()
    steps = load_queue(errors)
    lines: list[str] = []

    if not rules:
        lines.append("[spec] no domains in docs/spec/ yet. Nothing can be built until the developer asks for one.")
    else:
        lines.append(f"[spec] {len(rules)} domain(s). Rules with a citing test are what works today.")
        for domain in sorted(rules):
            numbers = sorted(rules[domain])
            have = sorted(n for n in numbers if n in cited.get(domain, set()))
            missing = [n for n in numbers if n not in cited.get(domain, set())]
            line = f"  {domain}: {len(numbers)} rule(s), {len(have)} cited, {open_counts.get(domain, 0)} open question(s)"
            if missing:
                line += f"; uncited: {', '.join(map(str, missing))}"
            stray = sorted(n for n in cited.get(domain, set()) if n not in rules[domain])
            if stray:
                line += f"; cited but not in spec: {', '.join(map(str, stray))}"
            lines.append(line)
        for domain in sorted(set(cited) - set(rules)):
            lines.append(f"  {domain}: cited by tests but docs/spec/{domain}.md does not exist")

    if steps:
        lines.append(f"[queue] {QUEUE}: {len(steps)} step(s), in order.")
        for i, step in enumerate(steps, 1):
            head = f"  {i}. {step.get('id')}"
            if step.get("brick"):
                head += f" ({step['brick']})"
            head += f" rules: {fmt_rules(step)}"
            if step.get("after"):
                head += f" [after {step['after']}]"
            lines.append(f"{head}: {step_state(step, rules, cited)}")
    else:
        lines.append(f"[queue] {QUEUE}: empty. Add a step when a domain has rules to build and the developer wants them built.")

    if errors:
        lines.append(f"[spec] {len(errors)} lint problem(s); run `uv run python scripts/checks/spec.py lint`.")
    print("\n".join(lines))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["lint"]:
        return lint()
    if args == ["status"]:
        try:
            return status()
        except Exception as exc:  # noqa: BLE001  never break a session start
            print(f"[spec] status could not run: {exc}. Run `uv run python scripts/checks/spec.py lint`.")
            return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
