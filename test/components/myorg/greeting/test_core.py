from myorg.greeting import greet


def test_greet_uses_the_name():
    """Asserts greeting rule 1."""
    assert greet("Ada") == "Hello, Ada!"


def test_greet_defaults_to_world_when_blank():
    """Asserts greeting rule 2."""
    assert greet("   ") == "Hello, world!"
