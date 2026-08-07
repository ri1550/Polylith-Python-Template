"""Implementation of the greeting component (private).

Only the names re-exported from __init__.py are the public interface. Everything
here is free to change as long as that interface keeps behaving as the tests say.
See ADR-0002 (Polylith) and ADR-0005 (context system).
"""


def greet(name: str) -> str:
    """Return a friendly greeting for `name`."""
    return f"Hello, {_clean(name)}!"


def _clean(name: str) -> str:
    # Leading underscore: private, not part of the public interface.
    return name.strip() or "world"
