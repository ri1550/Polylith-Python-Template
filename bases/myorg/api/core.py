"""API base: a thin entry point. Delegates to components, holds no business logic."""
from myorg.greeting import greet


def main() -> str:
    return greet("world")
