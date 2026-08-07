#!/usr/bin/env python3
"""Print a bookkeeping reminder at the end of every pre-commit run."""


def main() -> int:
    print(
        'Before committing: walk the "Pre-commit checklist" section in AGENTS.md.'
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
