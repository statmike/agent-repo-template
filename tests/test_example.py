"""Example test — DELETE ME once you start building.

Shows the testing convention: tests live in ``tests/`` and import the capability
they exercise from ``src/`` — they never re-implement logic. The
``pythonpath = ["src"]`` setting in ``pyproject.toml`` makes that import work.
"""

from example import add


def test_add() -> None:
    assert add(2, 3) == 5
