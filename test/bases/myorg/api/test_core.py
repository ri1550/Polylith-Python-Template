from myorg.api import core


def test_main_delegates_to_greeting():
    assert core.main() == "Hello, world!"
