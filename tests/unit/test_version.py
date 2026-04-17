from importlib.metadata import version

from recnys import __version__


def test_version() -> None:
    assert __version__ == version("recnys")
