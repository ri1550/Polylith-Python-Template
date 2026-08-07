#!/usr/bin/env python3
"""Check that public interface changes are recorded.

In Polylith, a brick's public interface is its __init__.py. Changing it can
affect every project that uses the brick, so the change should come with an ADR
(or a clear note that it is not really a contract change).

Two modes:

  --mode pre-commit   Runs on your machine before a commit. It only WARNS, so it
                      never blocks you. Think of it as a friendly heads-up.

  --mode ci           Runs on GitHub for a pull request. It BLOCKS the merge if a
                      public __init__.py changed without an ADR in the same pull
                      request and without an override note in a commit message.

How to satisfy the CI check when you changed a public interface:
  1. Best: add or update an ADR under docs/adr/ describing the change and
     include it in the same pull request (the agent can draft it for you), or
  2. mention an ADR in a commit message, for example "ADR-0007: rename charge()",
     or
  3. if the edit does NOT change the public surface (a comment, formatting), add
     "[interface-impact: none]" to a commit message.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path


def run(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True).stdout


def is_public_init(path: str) -> bool:
    # A public interface is an __init__.py inside a component or base brick.
    return Path(path).name == "__init__.py" and (
        path.startswith("components/") or path.startswith("bases/")
    )


def staged_files() -> list[str]:
    return run(["git", "diff", "--cached", "--name-only"]).splitlines()


def diff_files(base_ref: str) -> list[str]:
    return run(["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"]).splitlines()


def commit_messages(base_ref: str) -> str:
    return run(["git", "log", "--format=%B", f"origin/{base_ref}...HEAD"]).lower()


def adr_in(files: list[str]) -> bool:
    return any(re.match(r"docs/adr/\d{4}-.+\.md$", f) for f in files)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pre-commit", "ci"], default="pre-commit")
    parser.add_argument("files", nargs="*", help="staged files (pre-commit passes these)")
    args = parser.parse_args()

    if args.mode == "pre-commit":
        hits = [f for f in args.files if is_public_init(f)]
        if hits and not adr_in(staged_files()):
            print("Heads-up: you changed a public interface (__init__.py):")
            for f in hits:
                print(f"  - {f}")
            print(
                "This changes what other code depends on. If it is a real "
                "interface change, add an ADR under docs/adr/ in this commit "
                "(the agent can draft it). CI will ask for this later. "
                "Not blocking you now."
            )
        return 0  # never block locally

    # ci mode
    base_ref = os.environ.get("BASE_REF") or os.environ.get("GITHUB_BASE_REF") or "main"
    files = diff_files(base_ref)
    hits = [f for f in files if is_public_init(f)]

    if not hits:
        print("No public interface changes. OK.")
        return 0
    if adr_in(files):
        print("Public interface changed and an ADR is included. OK.")
        return 0
    messages = commit_messages(base_ref)
    if "adr-" in messages or "[interface-impact:" in messages:
        print("Public interface changed and a commit message records it. OK.")
        return 0

    print("This pull request changes a public interface but records no decision:\n")
    for f in hits:
        print(f"  - {f}")
    print(
        "\nDo one of these, then push again:\n"
        "  1. Add or update an ADR under docs/adr/ describing the change "
        "(best option; the agent can draft it).\n"
        "  2. Reference an ADR in a commit message, e.g. 'ADR-NNNN: ...'.\n"
        "  3. If this is NOT a contract change (a comment or formatting), add "
        "'[interface-impact: none]' to a commit message.\n"
        "See CONTRIBUTING.md for details."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
