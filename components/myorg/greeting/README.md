# greeting (example component)
Example brick included to show the structure. Delete it once you have your own.

Purpose: turn a name into a friendly greeting.

Public interface: `greet(name) -> str`, defined in `__init__.py`.

Why it is shaped this way: blank input is normalized here so every caller gets the same behavior rather than each re-implementing it. The tests pin the exact guarantees. See ADR-0005 for how this README fits the context system.
