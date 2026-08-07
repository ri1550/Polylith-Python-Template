"""Greeting component.

Public interface (the contract other bricks depend on):
    greet(name) -> str

EXAMPLE brick demonstrating the interface/implementation split. Delete it once
you have your own components.
"""
from myorg.greeting.core import greet

__all__ = ["greet"]
