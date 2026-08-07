#!/usr/bin/env python3
"""Lint the ADR decision log.

Checks every file in docs/adr/ that looks like an ADR (NNNN-*.md) for:
  - a filename of the form NNNN-kebab-title.md
  - YAML front matter between --- fences
  - the required fields, with valid values
  - no duplicate ADR numbers (numbers are never reused)
  - that any bricks named in `affects` actually exist, when the
    components/ or bases/ directories are present

Exit code 0 means all good. A non-zero exit means there is something to fix;
the printed message says what and where.

Run it yourself any time:
    python scripts/checks/lint.py

It also runs automatically via pre-commit and CI (see CONTRIBUTING.md).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml  # installed for this check by pre-commit / CI

ADR_DIR = Path("docs/adr")
TEMPLATE = "0000-adr-template.md"
FILENAME_RE = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
REQUIRED = ["status", "date", "decision-makers", "affects", "interface-impact"]
VALID_IMPACT = {"none", "new", "breaking"}
STATUS_PREFIXES = ("proposed", "accepted", "deprecated", "superseded by adr-")


def read_front_matter(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, "no YAML front matter (the file must start with ---)"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "front matter is not closed with a second ---"
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        return None, f"front matter is not valid YAML: {exc}"
    if not isinstance(data, dict):
        return None, "front matter did not parse to a set of fields"
    return data, None


def known_bricks() -> dict[str, set[str] | None]:
    bricks = {}
    for kind in ("components", "bases"):
        directory = Path(kind)
        if directory.is_dir():
            bricks[kind] = {
                p.name
                for ns in directory.iterdir() if ns.is_dir()
                for p in ns.iterdir() if p.is_dir()
            }
        else:
            bricks[kind] = None  # directory absent: skip existence checks
    return bricks


def check_affects(affects: Any, bricks: dict[str, set[str] | None], errors: list[str], name: str) -> None:
    if not isinstance(affects, dict):
        errors.append(f"{name}: `affects` must have components/bases/projects lists")
        return
    for kind in ("components", "bases", "projects"):
        if kind not in affects:
            errors.append(f"{name}: `affects` is missing `{kind}`")
            continue
        values = affects[kind] or []
        if not isinstance(values, list):
            errors.append(f"{name}: `affects.{kind}` must be a list")
            continue
        brick_set = bricks.get(kind) if kind in ("components", "bases") else None
        if brick_set is not None:
            for value in values:
                if value == "*":
                    continue
                if value not in brick_set:
                    errors.append(
                        f"{name}: `affects.{kind}` names '{value}', "
                        f"but no such {kind[:-1]} exists"
                    )


def main() -> int:
    if not ADR_DIR.is_dir():
        print(f"No {ADR_DIR}/ directory found, nothing to lint.")
        return 0

    errors = []
    seen_numbers = {}
    bricks = known_bricks()

    for path in sorted(ADR_DIR.glob("*.md")):
        name = path.name
        if name == TEMPLATE or name.lower() == "readme.md":
            continue

        match = FILENAME_RE.match(name)
        if not match:
            errors.append(f"{name}: filename must look like NNNN-kebab-title.md")
            continue

        number = match.group(1)
        if number in seen_numbers:
            errors.append(
                f"{name}: ADR number {number} is already used by "
                f"{seen_numbers[number]}; numbers are never reused"
            )
        else:
            seen_numbers[number] = name

        data, err = read_front_matter(path)
        if err or data is None:
            if err:
                errors.append(f"{name}: {err}")
            continue

        for field in REQUIRED:
            if field not in data or data[field] in (None, ""):
                errors.append(f"{name}: missing required field `{field}`")

        status = str(data.get("status", "")).strip().lower()
        if status and not status.startswith(STATUS_PREFIXES):
            errors.append(
                f"{name}: status '{data.get('status')}' is not one of "
                "proposed / accepted / deprecated / superseded by ADR-NNNN"
            )

        impact = data.get("interface-impact")
        if impact is not None and str(impact).strip().lower() not in VALID_IMPACT:
            errors.append(
                f"{name}: interface-impact '{impact}' must be one of "
                "none / new / breaking"
            )

        if "affects" in data:
            check_affects(data["affects"], bricks, errors, name)

    if errors:
        print("ADR lint found problems:\n")
        for err in errors:
            print(f"  - {err}")
        print(
            "\nFix the files above. Each ADR must follow "
            "docs/adr/0000-adr-template.md. If you are unsure what a field "
            "means, see CONTRIBUTING.md."
        )
        return 1

    print(f"ADR lint passed: {len(seen_numbers)} record(s) look good.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
