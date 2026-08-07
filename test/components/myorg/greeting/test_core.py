from myorg.greeting import greet


def test_greet_uses_the_name():
    assert greet("Ada") == "Hello, Ada!"


def test_greet_defaults_to_world_when_blank():
    assert greet("   ") == "Hello, world!"
